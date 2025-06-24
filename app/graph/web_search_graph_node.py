import json
import logging

from langchain.schema import Document
from langchain_core.callbacks.manager import adispatch_custom_event
from langchain_core.runnables import RunnableConfig

from ..chain.query_web_search_rewriter import query_rewriter
from ..chain.retrieval_grader import retrieval_grader
from ..tools.web_search_tool import web_search_tool

logger = logging.getLogger(__name__)


def preprocess_json_string(json_string):
    # Replace single quotes with double quotes
    json_string = json_string.replace("'", '"')

    # Escape backslashes
    json_string = json_string.replace("\\", "\\\\")

    return json_string


async def transform_query_for_web_search(
    state,
    config: RunnableConfig,
):
    """
    Transform the query to produce a question for web search.

    Args:
        state (dict): The current graph state

    Returns:
        state (dict): Updates question key with a re-phrased question
    """

    logger.info("---TRANSFORM QUERY FOR WEB SEARCH---")
    query = state["query"]
    timestamp = state["timestamp"]
    chat_history = state["chat_history"]
    enterprise_context = state["enterprise_context"]
    image_context = state["image_context"]

    # Notify user that web search process has started
    await adispatch_custom_event(
        "web_search_triggered",
        {"web_search": True},
        config=config,
    )

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
    return {"web_query": better_query}


async def web_search(state):
    """
    Web search based on the re-phrased question.

    Args:
        state (dict): The current graph state

    Returns:
        state (dict): Updates documents key with appended web results
    """

    logger.info("---WEB SEARCH---")
    query = state["web_query"]
    context = []

    # Web search
    web_results = await web_search_tool.ainvoke({"query": query})
    if "HTTPError('403 Client Error: Quota Exceeded" not in str(web_results):
        try:
            prepared_json_string = preprocess_json_string(web_results)
            web_results = json.loads(prepared_json_string)
            if len(web_results) > 0:
                web_results_docs = [
                    Document(
                        page_content=f"On the website titled: '{r['title']}' "
                        f"(URL '{r['link']}'), "
                        f"the following information was found: '{r['snippet']}'.",
                        metadata={
                            "title": r["title"],
                            "URL": r["link"],
                            "snippet": r["snippet"],
                            "context_type": "web_search_result",
                        },
                    )
                    for r in web_results
                    if ("title" in r.keys())
                    and ("link" in r.keys())
                    and ("snippet" in r.keys())
                ]
                context.extend(web_results_docs)
        except json.JSONDecodeError as e:
            logger.error("JSONDecodeError:", e)
        except Exception as e:
            logger.error("An unexpected error occurred:", e)

    return {"web_context": context}


async def grade_web(state):
    """
    Determines whether the retrieved documents are relevant to the question.

    Args:
        state (dict): The current graph state

    Returns:
        state (dict): Updates documents key with only filtered relevant documents
    """

    logger.info("---CHECK WEB RESULTS RELEVANCE TO QUESTION---")
    query = state["web_query"]
    context = state.get("web_context", [])

    # Score each doc
    filtered_context = []

    for d in context:
        score = await retrieval_grader.ainvoke(
            {
                "query": query,
                "document": d.page_content,
            }
        )
        grade = score.binary_score
        if grade == "yes":
            logger.info("---GRADE: WEB RESULT RELEVANT---")
            filtered_context.append(d)
        else:
            logger.info("---GRADE: WEB RESULT NOT RELEVANT---")
            continue

    return {"context": filtered_context}
