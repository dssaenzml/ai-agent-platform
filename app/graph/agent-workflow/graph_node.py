
import logging

import re
import json

from langchain.schema import Document

from langchain_core.runnables import RunnableConfig
from langchain_core.callbacks.manager import adispatch_custom_event
from langchain_core.messages import (
    AIMessage, 
    HumanMessage, 
)
from langchain_core.tools.base import ToolException

from ...tools.agent_workflow.sql_query_tool import (
    tool as sql_query_tool
    )

from ...memory.session_factory import create_session_factory

logger = logging.getLogger(__name__)

BOT_NAME = "WorkflowAgent"

get_session_history = create_session_factory(
    table_name=(
        f"{re.sub('-', '_', BOT_NAME).upper()}_"
        "CORTEX_ANALYST_MESSAGES_STORE"
        ),
    max_len_history=5,
    )


async def sql_query(
    state,
    config: RunnableConfig,
    ):
    """
    SQL query based on the re-phrased question.

    Args:
        state (dict): The current graph state

    Returns:
        state (dict): Updates documents key with appended SQL results
    """

    logger.info("---SQL QUERYING---")
    query = state["query"]
    oauth_token = state["oauth_token"]
    context = []
    
    # Notify user that sql search process has started
    await adispatch_custom_event(
        "sql_search_triggered",
        {
            "sql_search": True
        },
        config=config,
        )
    
    configurable = config.get("configurable", {})
    user_id = configurable["user_id"]
    session_id = configurable["session_id"]
    message_timereceived = configurable["message_timereceived"]
    
    messages = get_session_history(
        user_id=user_id, 
        session_id=session_id, 
        message_timereceived=message_timereceived, 
        ).messages
    
    if len(messages) == 0:
        messages = [HumanMessage(content=query)]
    else:
        messages.append(HumanMessage(content=query))

    # SQL query
    try:
        sql_result = await sql_query_tool.ainvoke({
            "messages": messages, 
            "user": user_id, 
            "oauth_token": oauth_token, 
            })
        context.append(Document(
                    page_content=
                    f"Given the human query: '{query}', "
                    "the following interpretation of the query was given: "
                    f"<<<\n{sql_result['human_query']}\n>>>, "
                    "the following SQL query was generated: "
                    f"<<<\n{sql_result['sql_query']}\n>>>, "
                    "and the following information was retrieved:\n\n"
                    f"{sql_result['sql_result']}.",
                    metadata={
                        "sql_request_id": sql_result["request_id"], 
                        "human_query": sql_result["human_query"], 
                        "sql_query": sql_result["sql_query"], 
                        "sql_result": sql_result["sql_result"], 
                        "context_type": "sql_search", 
                    }))
    except ToolException as e:
        logger.error(e)
        sql_result = {
            "request_id": "", 
            "human_query": "We could not interpret your question.", 
            "sql_query": "SELECT * FROM table", 
            "sql_result": "[]", 
        }
        context.append(Document(
                    page_content=
                    f"Given the human query: '{query}', "
                    "no possible interpretation was made for SQL querying. "
                    "Kindly rephrase the human query.",
                    metadata={
                        "sql_request_id": sql_result["request_id"], 
                        "human_query": sql_result["human_query"], 
                        "sql_query": sql_result["sql_query"], 
                        "sql_result": sql_result["sql_result"], 
                        "context_type": "sql_search", 
                    }))
    except Exception as e:
        logger.error(e)
        sql_result = {
            "request_id": "", 
            "human_query": "We could not interpret your question.", 
            "sql_query": "SELECT * FROM table", 
            "sql_result": "[]", 
        }

        return {
            "context": [], 
            "sql_search": False, 
            "sql_result": "[]", 
            }
    
    # Add messages to store
    get_session_history(
        user_id=user_id, 
        session_id=session_id, 
        message_timereceived=message_timereceived, 
        ).add_message(HumanMessage(
        content=query
    ))
    
    get_session_history(
        user_id=user_id, 
        session_id=session_id, 
        message_timereceived=message_timereceived, 
        ).add_message(AIMessage(
        content=json.dumps({
            "text": sql_result["human_query"], 
            "sql": sql_result["sql_query"], 
            })
    ))

    return {
        "context": context, 
        "sql_search": True, 
        "sql_result": sql_result["sql_result"], 
        }
