
import logging

from .utils import (
    generate_public_docs_filter, 
    generate_individual_docs_filter, 
    )

from ..chain.query_rag_rewriter import (
    query_rewriter
    )

from ..chain.retrieval_grader import retrieval_grader

from ..vector_db.utils import KnowledgeBaseManager

logger = logging.getLogger(__name__)


async def transform_query_for_rag(state):
    """
    Transform the query to produce a better query for Retrieval Augmentation.

    Args:
        state (dict): The current graph state

    Returns:
        state (dict): Updates question key with a re-phrased question
    """

    logger.info("---TRANSFORM QUERY FOR RAG---")
    query = state["query"]
    timestamp = state["timestamp"]
    chat_history = state["chat_history"]
    enterprise_context = state["enterprise_context"]
    image_context = state["image_context"]

    # Re-write query
    better_query = await query_rewriter.ainvoke({
        "query": query, 
        "timestamp": timestamp, 
        "chat_history": chat_history, 
        "enterprise_context": enterprise_context, 
        "image_context": image_context, 
        })
    return {"rag_query": better_query}


async def doc_retrieve(
    state, 
    kbm: KnowledgeBaseManager, 
    ):
    """
    Retrieve document

    Args:
        state (dict): The current graph state

    Returns:
        state (dict):   Update key to state, context, 
                        that contains retrieved documents
    """
    logger.info("---RETRIEVE DOCUMENT---")
    query = state["rag_query"]
    doc_ids = state["doc_ids"]

    # Retrieval
    results = await kbm.vectorstore.asimilarity_search_with_relevance_scores(
        query=query, 
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
    return {"rag_context": documents}


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

    # Retrieval
    results = await kbm.vectorstore.asimilarity_search_with_relevance_scores(
        query=query, 
        k=kbm.search_kwargs["k"], 
        filter=generate_public_docs_filter(), 
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


async def grade_rag(state):
    """
    Determines whether the retrieved documents are relevant to the question.

    Args:
        state (dict): The current graph state

    Returns:
        state (dict): Updates documents key with only filtered relevant documents
    """

    logger.info("---CHECK DOCUMENT RELEVANCE TO QUESTION---")
    query = state["rag_query"]
    context = state.get("rag_context", [])

    # Score each doc
    filtered_context = []
    
    for d in context:
        score = await retrieval_grader.ainvoke({
                "query": query, 
                "document": d.page_content, 
                })
        grade = score.binary_score
        if grade == "yes":
            logger.info("---GRADE: DOCUMENT RELEVANT---")
            filtered_context.append(d)
        else:
            logger.info("---GRADE: DOCUMENT NOT RELEVANT---")
            continue
    
    return {"context": filtered_context}
