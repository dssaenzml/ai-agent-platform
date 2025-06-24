import logging

from langchain_core.callbacks.manager import adispatch_custom_event
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnableConfig
from openai import BadRequestError

from ..llm_model.azure_llm import helper_model

logger = logging.getLogger(__name__)

image_system_prompt = (
    "You are an image information extractor designed to analyze an input of "
    "an LLM-based chat application. The input may contain one, two or three "
    "images. You must extract or describe "
    "all possible contextual information accurately and comprehensively from "
    "each image. You are provided with any available "
    "conversation history and the latest user query, which might reference "
    "previously mentioned context. Your users are employees at "
    "the enterprise organization. You are provided the organization guidelines and the "
    "LLM application purpose and capabilities for your reference.\n\n"
    "Enterprise guidelines and LLM purpose: \n\n {enterprise_context} \n\n"
    "Current timestamp: \n\n {timestamp} \n\n"
    "Please ensure the extracted information is relevant, detailed, and "
    "considers the unique geography, politics, economics, environment, "
    "culture, and international relations of the GCC region. "
    "Present the extracted information in a clear and structured format."
)


async def image_parsing(
    state,
    enterprise_context: str,
):
    """
    Add the organization contextual information in documents

    Args:
        state (dict): The current graph state

    Returns:
        state (dict):   New key added to state, documents,
                        that contains the organization documents
    """
    logger.info("---ADDING the organization CONTEXT---")
    query = state["query"]
    timestamp = state["timestamp"]
    image_type, image_data = state["image_type_data"]
    chat_history = state["chat_history"]

    # Extract any relevant information from image
    if len(image_data) > 0:
        logger.info("---ADDING IMAGE CONTEXT---")
        human_input = {
            "query": query,
            "timestamp": timestamp,
            "chat_history": chat_history,
            "enterprise_context": enterprise_context,
        }
        human_prompt = [
            {
                "type": "text",
                "text": (
                    "Here is the latest query: \n\n {query} \n\n"
                    "Please analyze the provided image(s) and "
                    "extract all relevant contextual information."
                ),
            },
        ]
        for i in range(len(image_data)):
            human_input[f"image_type_{str(i)}"] = image_type[i]
            human_input[f"image_data_{str(i)}"] = image_data[i]
            human_prompt.append(
                {
                    "type": "image_url",
                    "image_url": {
                        "url": "data:image/{image_type_"
                        + str(i)
                        + "};base64,{image_data_"
                        + str(i)
                        + "}",
                    },
                },
            )
        # Image Prompt
        image_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", image_system_prompt),
                MessagesPlaceholder("chat_history"),
                ("human", human_prompt),
            ]
        )
        # Chain
        image_context_extractor = image_prompt | helper_model | StrOutputParser()
        try:
            image_context = await image_context_extractor.ainvoke(human_input)
        except BadRequestError:
            return {
                "enterprise_context": enterprise_context,
                "image_context": "The image context could not be extracted because the "
                "prompt triggered content management policy. Please "
                "modify your prompt and retry.",
            }
    else:
        logger.info("---NO INPUT IMAGE---")
        image_context = (
            "No image was provided. Please proceed with "
            "the any other available contextual information."
        )
    return {
        "enterprise_context": enterprise_context,
        "image_context": image_context,
    }


async def final_answer(
    state,
    config: RunnableConfig,
):
    """
    Return the final system response to the user query.

    Args:
        state (dict): The current graph state

    Returns:
        state (dict): Final response from the system
    """

    logger.info("---SEND FINAL ANSWER---")
    context = state["context"]
    answer = state["answer"]

    # Write chunks of final answer
    final_context = [doc.dict() for doc in context]
    await adispatch_custom_event(
        "final_context",
        {"context": final_context},
        config=config,
    )
    for chunk in answer.content.split(" "):
        await adispatch_custom_event(
            "final_answer",
            {"answer": chunk + " "},
            config=config,
        )
