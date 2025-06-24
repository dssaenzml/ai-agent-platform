import logging

from openai import BadRequestError

from ...chain.agent_analytics.query_classifier import classifier as query_classifier
from ...chain.moderator import query_grader as moderator

logger = logging.getLogger(__name__)


async def query_router(state):
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
    timestamp = state["timestamp"]
    chat_history = state["chat_history"]
    enterprise_context = state["enterprise_context"]
    image_context = state["image_context"]

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
        score = await query_classifier.ainvoke(
            {
                "query": query,
                "timestamp": timestamp,
                "chat_history": chat_history,
                "enterprise_context": enterprise_context,
                "image_context": image_context,
            }
        )
        query_type = score.query_type

        if query_type == "sql_query":
            # Query is complex enough that requires SQL query
            # to be resolved
            logger.info("---DECISION: QUESTION REQUIRES SQL QUERYING---")

            return "sql retrieval"
        else:
            # We do not need extra information, so generate answer
            logger.info("---DECISION: GENERATE SIMPLE ANSWER---")

            return "generate simple answer"
