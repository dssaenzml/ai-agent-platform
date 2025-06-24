import logging

from langchain_core.callbacks.manager import adispatch_custom_event
from langchain_core.messages import AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnableConfig
from openai import BadRequestError

from ..llm_model.azure_llm import chat_model
from ..prompt.response_generator import (context_system_prompt,
                                         refined_response_system_prompt,
                                         simple_system_prompt)

logger = logging.getLogger(__name__)


async def request_refined_query(
    state,
    config: RunnableConfig,
):
    """
    Return system response to requesting to user to rephrase query.

    Args:
        state (dict): The current graph state

    Returns:
        state (dict): Request refined query response from the system
    """

    logger.info("---REQUEST FOR A REFINED QUERY---")
    query = state["query"]
    username = state["username"]
    timestamp = state["timestamp"]
    image_type, image_data = state["image_type_data"]
    enterprise_context = state["enterprise_context"]
    chat_history = state["chat_history"]
    web_search = state.get("web_search", False)
    web_search = "Yes, you are able." if web_search else "No, you are not."

    # Write chunks of final answer
    await adispatch_custom_event(
        "final_context",
        {"context": []},
        config=config,
    )
    # Refined query request generation
    generation = []
    try:
        human_input = {
            "query": query,
            "username": username,
            "timestamp": timestamp,
            "chat_history": chat_history,
            "enterprise_context": enterprise_context,
            "web_search": web_search,
        }
        human_prompt = [
            {
                "type": "text",
                "text": "{query}",
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
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", refined_response_system_prompt),
                MessagesPlaceholder("chat_history"),
                ("human", human_prompt),
            ]
        )
        # Chain
        response_generator = prompt | chat_model
        async for msg in response_generator.astream(
            human_input,
            config=config,
        ):
            generation.append(msg)
            await adispatch_custom_event(
                "final_answer",
                {"answer": msg.content},
                config=config,
            )
    except BadRequestError:
        content_safety_fallback_message = AIMessage(
            content=(
                "Thank you for reaching out. Your query does not seem to be "
                "related to professional or work-related topics. Please "
                "ensure your questions are relevant to your role at Abu "
                "Dhabi Ports Group. I'm here to assist you with any "
                "work-related issues you may have.\n\n"
                "Kindly start a new chat. Goodbye!"
            )
        )
        for chunk in content_safety_fallback_message.content.split(" "):
            await adispatch_custom_event(
                "final_answer",
                {"answer": chunk + " "},
                config=config,
            )

        return {
            "context": [],
            "image_gen_base64": "",
            "answer": content_safety_fallback_message,
        }

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
        "context": [],
        "image_gen_base64": "",
        "answer": generation,
    }


async def generate_simple(
    state,
    config: RunnableConfig,
):
    """
    Generate simple answer

    Args:
        state (dict): The current graph state

    Returns:
        state (dict):   New key added to state, generation, that
                        contains LLM generation
    """
    logger.info("---GENERATE---")
    query = state["query"]
    username = state["username"]
    timestamp = state["timestamp"]
    image_type, image_data = state["image_type_data"]
    enterprise_context = state["enterprise_context"]
    chat_history = state["chat_history"]
    web_search = state.get("web_search", False)
    web_search = "Yes, you are able." if web_search else "No, you are not."

    # Write chunks of final answer
    await adispatch_custom_event(
        "final_context",
        {"context": []},
        config=config,
    )
    # Simple generation
    generation = []
    try:
        human_input = {
            "query": query,
            "username": username,
            "timestamp": timestamp,
            "chat_history": chat_history,
            "enterprise_context": enterprise_context,
            "web_search": web_search,
        }
        human_prompt = [
            {
                "type": "text",
                "text": "{query}",
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
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", simple_system_prompt),
                MessagesPlaceholder("chat_history"),
                ("human", human_prompt),
            ]
        )
        # Chain
        response_generator = prompt | chat_model
        async for msg in response_generator.astream(
            human_input,
            config=config,
        ):
            generation.append(msg)
            await adispatch_custom_event(
                "final_answer",
                {"answer": msg.content},
                config=config,
            )
    except BadRequestError:
        content_safety_fallback_message = AIMessage(
            content=(
                "Thank you for reaching out. Your query does not seem to be "
                "related to professional or work-related topics. Please "
                "ensure your questions are relevant to your role at Abu "
                "Dhabi Ports Group. I'm here to assist you with any "
                "work-related issues you may have.\n\n"
                "Kindly start a new chat. Goodbye!"
            )
        )
        for chunk in content_safety_fallback_message.content.split(" "):
            await adispatch_custom_event(
                "final_answer",
                {"answer": chunk + " "},
                config=config,
            )

        return {
            "context": [],
            "image_gen_base64": "",
            "answer": content_safety_fallback_message,
        }

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
        "context": [],
        "image_gen_base64": "",
        "answer": generation,
    }


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
    username = state["username"]
    timestamp = state["timestamp"]
    image_type, image_data = state["image_type_data"]
    chat_history = state["chat_history"]
    enterprise_context = state["enterprise_context"]
    web_search = state.get("web_search", False)
    web_search = "Yes, you are able." if web_search else "No, you are not."
    context = state.get("context", [])
    num_generations = state.get("num_generations", 0)
    num_generations += 1

    # RAG generation
    try:
        human_input = {
            "query": query,
            "username": username,
            "timestamp": timestamp,
            "chat_history": chat_history,
            "enterprise_context": enterprise_context,
            "context": context,
            "web_search": web_search,
        }
        human_prompt = [
            {
                "type": "text",
                "text": "{query}",
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
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", context_system_prompt),
                MessagesPlaceholder("chat_history"),
                ("human", human_prompt),
            ]
        )
        # Chain
        response_generator = prompt | chat_model
        generation = await response_generator.ainvoke(human_input)
    except BadRequestError:
        content_safety_fallback_message = AIMessage(
            content=(
                "Thank you for reaching out. Your query does not seem to be "
                "related to professional or work-related topics. Please "
                "ensure your questions are relevant to your role at Abu "
                "Dhabi Ports Group. I'm here to assist you with any "
                "work-related issues you may have.\n\n"
                "Kindly start a new chat. Goodbye!"
            )
        )
        for chunk in content_safety_fallback_message.content.split(" "):
            await adispatch_custom_event(
                "final_answer",
                {"answer": chunk + " "},
                config=config,
            )

        return {
            "image_gen_base64": "",
            "answer": content_safety_fallback_message,
            "num_generations": num_generations,
        }
    return {
        "answer": generation,
        "image_gen_base64": "",
        "num_generations": num_generations,
    }
