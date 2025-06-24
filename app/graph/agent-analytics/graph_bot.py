

import logging

from typing import List, Tuple, Dict, Any
from typing_extensions import TypedDict

from functools import partial

from langchain.schema import Document

from langgraph.graph import StateGraph, START, END

from .graph_node import (
    sql_query, 
    sql_charts, 
)

from .graph_edge import (
    query_router, 
)

from ..response_graph_node import (
    request_refined_query, 
    generate_simple, 
    generate, 
)

from ..utils_graph_node import (
    image_parsing, 
    final_answer, 
)

from ..utils_graph_edge import (
    decide_how_to_respond, 
)

from ...prompt.agent_analytics.bot import prompt as enterprise_context

logger = logging.getLogger(__name__)


### Graph State
class GraphState(TypedDict):
    """
    Represents the state of the graph.
    """

    query: str
    username: str
    timestamp: str
    user_id: str
    image_type_data: Tuple[List[str]]
    chat_history: List[str]
    
    # Attributes populated within the graph
    enterprise_context: str
    image_context: str
    graph_query: str
    context: List[Document]
    answer: str
    sql_search: bool
    sql_result: str
    sql_charts: Dict[str, Any]
    num_generations: int


class InputState(TypedDict):
    """
    Represents the input state of the graph.
    """
    query: str
    username: str
    timestamp: str
    user_id: str
    image_type_data: Tuple[List[str]]
    chat_history: List[str]


class OutputState(TypedDict):
    """
    Represents the output state of the graph.
    """
    context: List[Document]
    answer: str
    sql_search: bool
    sql_charts: Dict[str, Any]


## Graph flow
workflow = StateGraph(
    GraphState, 
    input=InputState, 
    output=OutputState,
)

# Define the nodes
workflow.add_node(
    "image_parsing", 
    partial(image_parsing, enterprise_context=enterprise_context), 
    )  # add enterprise and image context info
workflow.add_node(
    "request_refined_query", 
    request_refined_query
    )  # request refined query
workflow.add_node("generate_simple", generate_simple)  # generate
workflow.add_node("sql_query", sql_query)  # sql query
workflow.add_node("sql_charts_node", sql_charts)  # sql charts
workflow.add_node("generate", generate)  # generate
workflow.add_node("final_answer", final_answer)  # final accepted answer

# Build graph
workflow.add_edge(START, "image_parsing")
workflow.add_conditional_edges(
    "image_parsing",
    query_router,
    {
        "need refined query": "request_refined_query",
        "sql retrieval": "sql_query",
        "generate simple answer": "generate_simple",
    },
)
workflow.add_edge("sql_query", "generate")
workflow.add_edge("sql_query", "sql_charts_node")
workflow.add_edge("sql_charts_node", END)
workflow.add_conditional_edges(
    "generate",
    decide_how_to_respond,
    {
        "need refined query": "request_refined_query", 
        "not supported": "generate", 
        "useful": "final_answer", 
        "not useful": "generate", 
    },
)
workflow.add_edge("request_refined_query", END)
workflow.add_edge("generate_simple", END)
workflow.add_edge("final_answer", END)

# Compile
app = workflow.compile()
