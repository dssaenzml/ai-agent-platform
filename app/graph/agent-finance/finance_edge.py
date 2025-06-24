
import logging

from openai import BadRequestError

from ...chain.moderator import (
    query_grader as moderator,
    )

from ...chain.query_classifier import (
    simple_rag_web_query_classifier, 
    )

logger = logging.getLogger(__name__)


async def moderation_router(state):
    """
    Determines whether a question needs moderation to be answered.

    Args:
        state (dict): The current graph state.

    Returns:
        str: Decision for the next node to call.
    """

    logger.info("---ASSESS QUERY---")
    query = state["query"]
    timestamp = state["timestamp"]
    chat_history = state["chat_history"]
    enterprise_context = state["enterprise_context"]
    image_context = state["image_context"]
    
    try:
        score = await moderator.ainvoke({
                "query": query, 
                "timestamp": timestamp,
                "chat_history": chat_history, 
                "enterprise_context": enterprise_context, 
                "image_context": image_context, 
                })
        grade = score.binary_score
    except BadRequestError:
        return "need refined query"

    if grade == "no":
        # Query needs to be moderated
        logger.info(
            "---DECISION: QUESTION REQUIRES MODERATION---"
        )
        return "need refined query"
    
    else:
        return "no moderation required"


async def get_info_gathering_state(state):
    query = state["query"]
    doc_ids = state.get("doc_ids", [])
    timestamp = state["timestamp"]
    chat_history = state["chat_history"]
    enterprise_context = state["enterprise_context"]
    image_context = state["image_context"]
    web_search = state["web_search"]
    finance_details = state["finance_details"]
    
    if finance_details.tool_calls:
        if len(doc_ids) > 0:
            # User is asking regarding an uploaded document
            logger.info(
                "---DECISION: QUESTION REQUIRES DOCUMENTS, RETRIEVE---"
            )
            return "retrieval augmented"
    
        score = await simple_rag_web_query_classifier.ainvoke({
                "query": query, 
                "timestamp": timestamp, 
                "chat_history": chat_history, 
                "enterprise_context": enterprise_context, 
                "image_context": image_context, 
                })
        query_type = score.query_type
    
        if query_type == "rag_query":
            # Query is complex enough that requires extra information
            # to be resolved
            logger.info(
                "---DECISION: QUESTION REQUIRES DOCUMENTS, RETRIEVE---"
            )
            
            return "retrieval augmented"
        elif web_search and (query_type == "web_search_query"):
            # Query is complex enough that requires web search
            # to be resolved
            logger.info(
                "---DECISION: QUESTION REQUIRES WEB SEARCH---"
            )
            
            return "web search retrieval"
        else:
            # No extra information needed, generate a simple answer
            logger.info("---DECISION: GENERATE SIMPLE ANSWER---")
            
            return "generate simple answer"
    else:
        logger.info(
            "---DECISION: REQUEST FOR DATA---"
        )
        return "request data"