import logging

from typing import Tuple, List, Annotated
from typing_extensions import TypedDict

from operator import add

from functools import partial

from langchain.schema import Document

from langgraph.graph import StateGraph, START, END

from ..rag_graph_node import (
    transform_query_for_rag,
    doc_retrieve,
    retrieve,
    grade_rag,
)

from ..web_search_graph_node import (
    transform_query_for_web_search,
    web_search,
    grade_web,
)

from ..file_gen_graph_node import (
    transform_query_for_image_gen,
    image_generation,
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
    simple_rag_web_img_query_router as query_router,
    rag_router,
    decide_to_search_web,
    decide_how_to_respond,
)

from ..utils import get_update

from ...prompt.agent_general.bot import prompt as enterprise_context

from ...vector_db.agent_general import kbm

logger = logging.getLogger(__name__)


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
    doc_ids: List[str]
    user_id: str

    # Attributes populated within the graph
    enterprise_context: str
    image_context: str
    rag_query: str
    web_query: str
    img_gen_query: str
    rag_context: List[Document]
    web_context: List[Document]
    context: Annotated[List[Document], add]
    answer: Annotated[str, get_update]
    num_generations: int
    image_blob_url: str


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
    doc_ids: List[str]
    user_id: str


class OutputState(TypedDict):
    """
    Represents the output state of the graph.
    """

    context: List[Document]
    answer: str
    web_search: bool
    image_blob_url: str


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
workflow.add_node("public_retrieve", partial(retrieve, kbm=kbm))  # retrieve
workflow.add_node("doc_retrieve", partial(doc_retrieve, kbm=kbm))  # retrieve
workflow.add_node("grade_rag_docs", grade_rag)  # grade documents
workflow.add_node(
    "transform_query_for_image_gen", transform_query_for_image_gen
)  # transform query
workflow.add_node("image_generation_node", image_generation)  # web search
workflow.add_node(
    "transform_query_for_web_search", transform_query_for_web_search
)  # transform query
workflow.add_node("web_search_node", web_search)  # web search
workflow.add_node("grade_web_docs", grade_web)  # grade documents
workflow.add_node("generate", generate)  # generate
workflow.add_node("final_answer", final_answer)  # final accepted answer

# Build graph
workflow.add_edge(START, "image_parsing")
workflow.add_conditional_edges(
    "image_parsing",
    partial(query_router, kbm=kbm),
    {
        "need refined query": "request_refined_query",
        "retrieval augmented": "transform_query_for_rag",
        "image generation": "transform_query_for_image_gen",
        "web search retrieval": "transform_query_for_web_search",
        "generate simple answer": "generate_simple",
    },
)
workflow.add_conditional_edges(
    "transform_query_for_rag",
    rag_router,
    {
        "public retrieval": "public_retrieve",
        "doc retrieval": "doc_retrieve",
    },
)
workflow.add_edge("public_retrieve", "grade_rag_docs")
workflow.add_edge("doc_retrieve", "grade_rag_docs")
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
workflow.add_edge("transform_query_for_image_gen", "image_generation_node")
workflow.add_edge("image_generation_node", END)
workflow.add_edge("request_refined_query", END)
workflow.add_edge("generate_simple", END)
workflow.add_edge("final_answer", END)

# Compile
app = workflow.compile()


# # Define the input message with audio
# messages = [
#     (
#         "human",
#         [
#             {
#                 "type": "text",
#                 "text": "Transcribe the following:"
#                 },
#             {
#                 "type": "input_audio",
#                 "input_audio": {"data": audio_b64, "format": "wav"}
#                 },
#         ],
#     )
# ]

# # Send the request to the model and get the transcription
# output_message = llm.invoke(messages)
# print(output_message.content)
