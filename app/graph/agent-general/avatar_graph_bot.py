import logging

from typing import List

from typing_extensions import TypedDict

from langchain_core.runnables import RunnableConfig
from langchain_core.callbacks.manager import adispatch_custom_event
from langchain_core.messages import AIMessage

from langchain.schema import Document

from langgraph.graph import StateGraph, START, END

from qdrant_client import models

from ...chain.agent_general.avatar_query_rag_rewriter import (
    query_rewriter as query_rag_rewriter,
)

from ...chain.agent_general.avatar_response_generator import (
    response_generator,
)

from ...prompt.agent_general.bot import prompt as enterprise_context

from ...vector_db.agent_general import avatar_kbm as kbm

logger = logging.getLogger(__name__)


### Graph State
class GraphState(TypedDict):
    """
    Represents the state of the graph.
    """

    query: str
    timestamp: str
    chat_history: List[str]

    # Attributes populated within the graph
    enterprise_context: str
    rag_query: str
    rag_context: List[Document]
    answer: str


class InputState(TypedDict):
    """
    Represents the input state of the graph.
    """

    query: str
    timestamp: str
    chat_history: List[str]


class OutputState(TypedDict):
    """
    Represents the output state of the graph.
    """

    answer: str


### Nodes
async def transform_query_for_rag(state):
    """
    Transform the query to produce a better query for Retrieval Augmentation.

    Args:
        state (dict): The current graph state

    Returns:
        state (dict): Updates question key with a re-phrased question
    """

    logger.info("---TRANSFORM QUERY---")
    query = state["query"]
    timestamp = state["timestamp"]
    chat_history = state["chat_history"]

    # Re-write query
    better_query = await query_rag_rewriter.ainvoke(
        {
            "query": query,
            "timestamp": timestamp,
            "chat_history": chat_history,
            "enterprise_context": enterprise_context,
        }
    )
    return {
        "rag_query": better_query,
        "enterprise_context": enterprise_context,
    }


async def retrieve(
    state,
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

    # Add filter
    filter = models.Filter(
        must=[
            models.FieldCondition(
                key="metadata.public_doc",
                match=models.MatchValue(value="true"),
            ),
        ]
    )

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


async def generate(
    state,
    config: RunnableConfig,
):
    """
    Generate answer

    Args:
        state (dict): The current graph state

    Returns:
        state (dict):   New key added to state, generation, that
                        contains LLM generation
    """
    logger.info("---GENERATE---")
    query = state["query"]
    timestamp = state["timestamp"]
    chat_history = state["chat_history"]
    enterprise_context = state["enterprise_context"]
    context = state["rag_context"]

    # Simple generation
    generation = []
    async for msg in response_generator.astream(
        {
            "query": query,
            "timestamp": timestamp,
            "chat_history": chat_history,
            "enterprise_context": enterprise_context,
            "context": context,
        },
        config=config,
    ):
        generation.append(msg)
        await adispatch_custom_event(
            "final_answer",
            {"answer": msg.content},
            config=config,
        )

    # Aggregate the content
    full_content = "".join(chunk.content for chunk in generation)

    # Create the AIMessage object
    generation = AIMessage(
        content=full_content,
        additional_kwargs=generation[-1].additional_kwargs,
        id=generation[-1].id,
        response_metadata=generation[-1].response_metadata,
        usage_metadata=generation[-1].usage_metadata,
    )

    return {
        "answer": generation,
    }


## Graph flow
workflow = StateGraph(
    GraphState,
    input=InputState,
    output=OutputState,
)

# Define the nodes
workflow.add_node("transform_query_for_rag", transform_query_for_rag)  # transform query
workflow.add_node("retrieve", retrieve)  # retrieve
workflow.add_node("generate", generate)  # generate

# Build graph
workflow.add_edge(START, "transform_query_for_rag")
workflow.add_edge("transform_query_for_rag", "retrieve")
workflow.add_edge("retrieve", "generate")
workflow.add_edge("generate", END)

# Compile
app = workflow.compile()
