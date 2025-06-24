import logging

from qdrant_client import models

from openai import BadRequestError

from ...chain.moderator import (
    query_grader as moderator,
)

from ...chain.query_rag_rewriter import query_rewriter

from ...chain.documents_summarizer import summarizer

from ...chain.agent_workflow.query_classifier import (
    classifier as query_classifier,
)

from ...vector_db.utils import KnowledgeBaseManager

logger = logging.getLogger(__name__)


async def query_router(
    state,
    kbm: KnowledgeBaseManager,
):
    """
    Determines whether a question needs moderation, documents,
    image generation, web search, SQL query, or no extra information
    to be answered.

    Args:
        state (dict): The current graph state.

    Returns:
        str: Decision for the next node to call.
    """

    logger.info("---ASSESS QUERY---")
    query = state["query"]
    doc_ids = state.get("doc_ids", [])
    timestamp = state["timestamp"]
    chat_history = state["chat_history"]
    enterprise_context = state["enterprise_context"]
    image_context = state["image_context"]
    web_search = state["web_search"]

    try:
        score = await moderator.ainvoke(
            {
                "query": query,
                "timestamp": timestamp,
                "chat_history": chat_history,
                "enterprise_context": enterprise_context,
                "image_context": image_context,
            }
        )
        grade = score.binary_score
    except BadRequestError:
        return "need refined query"

    if grade == "no":
        # Query needs to be moderated
        logger.info("---DECISION: QUESTION REQUIRES MODERATION---")
        return "need refined query"

    else:
        if len(doc_ids) > 0:
            # User is asking regarding an uploaded document
            logger.info("---SUMMARIZE SHARED DOCUMENTS---")
            # Re-write query
            better_query = await query_rewriter.ainvoke(
                {
                    "query": query,
                    "timestamp": timestamp,
                    "chat_history": chat_history,
                    "enterprise_context": enterprise_context,
                    "image_context": image_context,
                }
            )
            user_id = state["user_id"]
            filter = models.Filter(
                must=[
                    models.FieldCondition(
                        key="metadata.doc_id",
                        match=models.MatchAny(any=doc_ids),
                    ),
                    models.FieldCondition(
                        key="metadata.user_id",
                        match=models.MatchValue(value=user_id),
                    ),
                ],
                must_not=[
                    models.FieldCondition(
                        key="metadata.public_doc", match=models.MatchValue(value="true")
                    ),
                ],
            )
            # Retrieval
            results = await kbm.vectorstore.asimilarity_search_with_relevance_scores(
                query=better_query,
                k=kbm.search_kwargs["k"] * 2,
                filter=filter,
            )
            documents = []
            unique_page_contents = set()

            for r in results:
                doc = r[0]
                similarity_score = r[1]
                if similarity_score >= kbm.search_kwargs["score_threshold"]:
                    if "original_page_content" in doc.metadata.keys():
                        doc.page_content = doc.metadata["original_page_content"]
                        doc.metadata.pop("original_page_content")

                    if doc.page_content not in unique_page_contents:
                        documents.append(doc)
                        unique_page_contents.add(doc.page_content)
                else:
                    continue
            summary_docs = await summarizer.ainvoke(
                {
                    "documents": documents,
                }
            )
        else:
            summary_docs = "No uploaded or shared documents by the user."

        score = await query_classifier.ainvoke(
            {
                "query": query,
                "timestamp": timestamp,
                "chat_history": chat_history,
                "enterprise_context": enterprise_context,
                "summary_docs": summary_docs,
                "image_context": image_context,
            }
        )
        query_type = score.query_type

        if query_type == "sql_query":
            # Query is complex enough that requires SQL query
            # to be resolved
            logger.info("---DECISION: QUESTION REQUIRES SQL QUERYING---")

            return "sql retrieval"
        elif query_type == "rag_query":
            # Query is complex enough that requires extra information
            # to be resolved
            logger.info("---DECISION: QUESTION REQUIRES DOCUMENTS, RETRIEVE---")

            return "retrieval augmented"
        elif query_type == "img_gen_query":
            # Query is requesting for image generation to be resolved
            logger.info("---DECISION: QUESTION REQUIRES IMAGE GENERATION---")

            return "image generation"
        elif web_search and (query_type == "web_search_query"):
            # Query is complex enough that requires web search
            # to be resolved
            logger.info("---DECISION: QUESTION REQUIRES WEB SEARCH---")

            return "web search retrieval"
        else:
            # No extra information needed, generate a simple answer
            logger.info("---DECISION: GENERATE SIMPLE ANSWER---")

            return "generate simple answer"
