import logging

from qdrant_client import models

from ...chain.agent_finance.finance_info_gatherer import gatherer
from ...vector_db.utils import KnowledgeBaseManager

logger = logging.getLogger(__name__)


async def gather_information(state):
    """
    Gather all required information about Finance details.

    Args:
        state (dict): The current graph state

    Returns:
        state (dict): Updates Finance details key based on shared info
    """

    logger.info("---GATHERING REQUIRED DETAILS FOR FINANCE---")
    query = state["query"]
    timestamp = state["timestamp"]
    chat_history = state["chat_history"]
    enterprise_context = state["enterprise_context"]
    image_context = state["image_context"]

    # Gather information from human conversation
    response = await gatherer.ainvoke(
        {
            "query": query,
            "timestamp": timestamp,
            "chat_history": chat_history,
            "enterprise_context": enterprise_context,
            "image_context": image_context,
        }
    )

    if response.tool_calls:
        return {"finance_details": response}
    else:
        return {
            "finance_details": response,
            "answer": response,
            "context": [],
        }


async def retrieve(
    state,
    kbm: KnowledgeBaseManager,
):
    """
    Retrieve public documents only

    Args:
        state (dict): The current graph state

    Returns:
        state (dict):   New key added to state, documents,
                        that contains retrieved documents
    """
    logger.info("---RETRIEVE---")
    query = state["rag_query"]
    finance_details = state["finance_details"]

    # Add filter
    public_doc_fitlers = [
        models.FieldCondition(
            key="metadata.public_doc",
            match=models.MatchValue(value="true"),
        ),
    ]
    if finance_details.tool_calls:
        finance_details = finance_details.tool_calls[0]["args"]
        if "cluster" in finance_details.keys():
            public_doc_fitlers.append(
                models.FieldCondition(
                    key="metadata.filename",
                    match=models.MatchText(text=finance_details["cluster"]),
                )
            )
    filter = models.Filter(must=public_doc_fitlers)

    # Retrieval
    results = await kbm.vectorstore.asimilarity_search_with_relevance_scores(
        query=query, k=kbm.search_kwargs["k"], filter=filter
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
    return {"rag_context": documents}
