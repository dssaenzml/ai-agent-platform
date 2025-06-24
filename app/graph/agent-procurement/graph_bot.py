import logging
import re
from functools import partial
from operator import add
from typing import Annotated, List, Tuple

from langchain.schema import Document
from langgraph.graph import END, START, StateGraph
from typing_extensions import TypedDict

from ...memory.checkpoint_factory import create_checkpoint_factory
from ...prompt.agent_procurement.bot import prompt as enterprise_context
from ...vector_db.agent_procurement import kbm
from ..rag_graph_node import grade_rag, retrieve, transform_query_for_rag
from ..response_graph_node import generate, generate_simple, request_refined_query
from ..utils import get_update
from ..utils_graph_edge import decide_how_to_respond, decide_to_search_web
from ..utils_graph_node import final_answer, image_parsing
from ..web_search_graph_node import (
    grade_web,
    transform_query_for_web_search,
    web_search,
)
from .graph_edge import get_info_gathering_state, query_router
from .graph_node import gather_sow_details, gather_sow_type, sow_doc_generation

logger = logging.getLogger(__name__)

BOT_NAME = "ProcurementAgent"


### Graph State
class GraphState(TypedDict):
    """
    Represents the state of the graph.
    """

    query: str
    username: str
    timestamp: str
    image_type_data: Tuple[List[str]]
    chat_history: List[str]
    web_search: bool

    # Attributes populated within the graph
    enterprise_context: str
    image_context: str
    sow_type: str
    sow_details: str
    sow_filename: str
    sow_blob_url: str
    rag_query: str
    web_query: str
    rag_context: List[Document]
    web_context: List[Document]
    context: Annotated[List[Document], add]
    answer: Annotated[str, get_update]
    num_generations: int


class InputState(TypedDict):
    """
    Represents the input state of the graph.
    """

    query: str
    username: str
    timestamp: str
    image_type_data: Tuple[List[str]]
    chat_history: List[str]
    web_search: bool


class OutputState(TypedDict):
    """
    Represents the output state of the graph.
    """

    context: List[Document]
    answer: str
    web_search: bool
    sow_filename: str
    sow_blob_url: str


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
    "request_refined_query", request_refined_query
)  # request refined query
workflow.add_node("generate_simple", generate_simple)  # generate
workflow.add_node("transform_query_for_rag", transform_query_for_rag)  # transform query
workflow.add_node("retrieve", partial(retrieve, kbm=kbm))  # retrieve
workflow.add_node("grade_rag_docs", grade_rag)  # grade documents
workflow.add_node(
    "transform_query_for_web_search", transform_query_for_web_search
)  # transform query
workflow.add_node("web_search_node", web_search)  # web search
workflow.add_node("grade_web_docs", grade_web)  # grade documents
workflow.add_node("gather_sow_type", gather_sow_type)  # gather info
workflow.add_node("gather_sow_details", gather_sow_details)  # gather info
workflow.add_node(
    "sow_doc_generation",
    partial(
        sow_doc_generation,
        checkpoint_saver=create_checkpoint_factory(
            table_name=f"{re.sub('-', '_', BOT_NAME).upper()}_SAVER",
        ),
    ),
)  # generate
workflow.add_node("generate", generate)  # generate
workflow.add_node("final_answer", final_answer)  # final accepted answer

# Build graph
workflow.add_edge(START, "image_parsing")
workflow.add_conditional_edges(
    "image_parsing",
    partial(query_router, kbm=kbm),
    {
        "need refined query": "request_refined_query",
        "sow document generation": "gather_sow_type",
        "retrieval augmented": "transform_query_for_rag",
        "web search retrieval": "transform_query_for_web_search",
        "generate simple answer": "generate_simple",
    },
)
workflow.add_edge("transform_query_for_rag", "retrieve")
workflow.add_edge("retrieve", "grade_rag_docs")
workflow.add_conditional_edges(
    "grade_rag_docs",
    decide_to_search_web,
    {
        "web search needed": "transform_query_for_web_search",
        "no web search": "generate",
    },
)
workflow.add_edge("transform_query_for_web_search", "web_search_node")
workflow.add_edge("web_search_node", "grade_web_docs")
workflow.add_edge("grade_web_docs", "generate")
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
workflow.add_conditional_edges(
    "gather_sow_type",
    get_info_gathering_state,
    {
        "request SoW type": "final_answer",
        "request SoW details": "gather_sow_details",
        "generate SoW": "sow_doc_generation",
    },
)
workflow.add_edge("gather_sow_details", "final_answer")
workflow.add_edge("sow_doc_generation", END)
workflow.add_edge("request_refined_query", END)
workflow.add_edge("final_answer", END)

# Compile
app = workflow.compile()
