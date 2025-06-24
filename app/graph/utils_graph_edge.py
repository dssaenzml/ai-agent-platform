import logging

from openai import BadRequestError

from ..chain.answer_grader import answer_grader
from ..chain.documents_summarizer import summarizer
from ..chain.hallucination_grader import hallucination_grader
from ..chain.moderator import query_grader as moderator
from ..chain.query_classifier import (
    simple_rag_web_img_pdf_query_classifier,
    simple_rag_web_img_query_classifier,
    simple_rag_web_query_classifier,
)
from ..chain.query_rag_rewriter import query_rewriter
from ..vector_db.utils import KnowledgeBaseManager
from .utils import generate_individual_docs_filter

logger = logging.getLogger(__name__)


async def simple_rag_web_query_router(
    state,
    kbm: KnowledgeBaseManager,
):
    """
    Determines whether a question needs moderation, documents,
    or no extra information to be answered.

    Args:
        state (dict): The current graph state

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
            # Retrieval
            results = await kbm.vectorstore.asimilarity_search_with_relevance_scores(
                query=better_query,
                k=kbm.search_kwargs["k"] * 2,
                filter=generate_individual_docs_filter(doc_ids),
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

        score = await simple_rag_web_query_classifier.ainvoke(
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

        if query_type == "rag_query":
            # Query is complex enough that requires extra information
            # to be resolved
            logger.info("---DECISION: QUESTION REQUIRES DOCUMENTS, RETRIEVE---")

            return "retrieval augmented"
        elif web_search and (query_type == "web_search_query"):
            # Query is complex enough that requires web search
            # to be resolved
            logger.info("---DECISION: QUESTION REQUIRES WEB SEARCH---")

            return "web search retrieval"
        else:
            # No extra information needed, generate a simple answer
            logger.info("---DECISION: GENERATE SIMPLE ANSWER---")

            return "generate simple answer"


async def simple_rag_web_img_query_router(
    state,
    kbm: KnowledgeBaseManager,
):
    """
    Determines whether a question needs moderation, documents,
    image generation, web search, or no extra information to be answered.

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
            # Retrieval
            results = await kbm.vectorstore.asimilarity_search_with_relevance_scores(
                query=better_query,
                k=kbm.search_kwargs["k"] * 2,
                filter=generate_individual_docs_filter(doc_ids),
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

        score = await simple_rag_web_img_query_classifier.ainvoke(
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

        if query_type == "rag_query":
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


async def simple_rag_web_img_pdf_query_router(
    state,
    kbm: KnowledgeBaseManager,
):
    """
    Determines whether a question needs moderation, documents,
    image generation, web search, PDF document generation,
    or no extra information to be answered.

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
            # Retrieval
            results = await kbm.vectorstore.asimilarity_search_with_relevance_scores(
                query=better_query,
                k=kbm.search_kwargs["k"] * 2,
                filter=generate_individual_docs_filter(doc_ids),
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

        score = await simple_rag_web_img_pdf_query_classifier.ainvoke(
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

        if query_type == "rag_query":
            # Query is complex enough that requires extra information
            # to be resolved
            logger.info("---DECISION: QUESTION REQUIRES DOCUMENTS, RETRIEVE---")

            return "retrieval augmented"
        elif query_type == "img_gen_query":
            # Query is requesting for image generation to be resolved
            logger.info("---DECISION: QUESTION REQUIRES IMAGE GENERATION---")

            return "image generation"
        elif query_type == "pdf_gen_query":
            # Query is requesting for PDF document generation to be resolved
            logger.info("---DECISION: QUESTION REQUIRES PDF GENERATION---")

            return "pdf generation"
        elif web_search and (query_type == "web_search_query"):
            # Query is complex enough that requires web search
            # to be resolved
            logger.info("---DECISION: QUESTION REQUIRES WEB SEARCH---")

            return "web search retrieval"
        else:
            # No extra information needed, generate a simple answer
            logger.info("---DECISION: GENERATE SIMPLE ANSWER---")

            return "generate simple answer"


def rag_router(state):
    """
    Determines whether a question needs individual document, session-based
    documents, or public documents to be answered.

    Args:
        state (dict): The current graph state

    Returns:
        str: Decision for the next node to call.
    """

    logger.info("---ASSESS QUERY---")
    doc_ids = state["doc_ids"]

    if len(doc_ids) > 0:
        logger.info("---DECISION: RETRIEVE INDIVIDUAL DOCUMENT---")
        return "doc retrieval"
    else:
        logger.info("---DECISION: RETRIEVE PUBLIC DOCUMENTS---")
        return "public retrieval"


def decide_to_search_web(state):
    """
    Determines whether to add web search results or not.

    Args:
        state (dict): The current graph state

    Returns:
        str: Decision for the next node to call.
    """

    logger.info("---ASSESS GRADED DOCUMENTS---")
    web_search = state["web_search"]

    if web_search:
        # We will re-generate a new query for web search
        logger.info("---DECISION: TRANSFORM QUERY FOR WEB SEARCH---")
        return "web search needed"
    else:
        # We have relevant information without web search
        logger.info("---DECISION: NO WEB SEARCH---")
        return "no web search"


async def decide_how_to_respond(state):
    """
    Determines whether the generation is grounded in the document
    and answers question.

    Args:
        state (dict): The current graph state

    Returns:
        str: Decision for the next node to call.
    """

    logger.info("---CHECK HALLUCINATIONS---")
    query = state["query"]
    timestamp = state["timestamp"]
    chat_history = state["chat_history"]
    enterprise_context = state["enterprise_context"]
    image_context = state["image_context"]
    context = state["context"]
    generation = state["answer"]
    num_generations = state["num_generations"]

    if num_generations > 2:
        # Exceeded generation attempt limit
        logger.info(
            "---DECISION: COULD NOT GENERATE USEFUL ANSWER, REQUEST REFINED QUERY---"
        )
        return "need refined query"

    else:
        score = await hallucination_grader.ainvoke(
            {
                "query": query,
                "timestamp": timestamp,
                "chat_history": chat_history,
                "enterprise_context": enterprise_context,
                "image_context": image_context,
                "context": context,
                "generation": generation,
            }
        )
        grade = score.binary_score

        # Check hallucination
        if grade == "yes":
            logger.info("---DECISION: GENERATION IS GROUNDED IN DOCUMENTS---")
            # Check question-answering
            logger.info("---GRADE GENERATION vs QUESTION---")
            score = await answer_grader.ainvoke(
                {
                    "query": query,
                    "timestamp": timestamp,
                    "chat_history": chat_history,
                    "enterprise_context": enterprise_context,
                    "image_context": image_context,
                    "context": context,
                    "generation": generation,
                }
            )
            grade = score.binary_score
            if grade == "yes":
                logger.info("---DECISION: GENERATION ADDRESSES QUESTION---")
                return "useful"
            else:
                logger.info("---DECISION: GENERATION DOES NOT ADDRESS QUESTION---")
                return "not useful"
        else:
            logger.info(
                "---DECISION: GENERATION IS NOT GROUNDED IN DOCUMENTS, RE-TRY---"
            )
            return "not supported"
