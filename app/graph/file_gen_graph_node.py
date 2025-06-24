import logging

from typing import Callable

from langchain_core.runnables import RunnableConfig
from langchain_core.callbacks.manager import adispatch_custom_event
from langchain_core.messages import AIMessage

from ..chain.filename_generator import html_filename_generator as filename_generator

from ..chain.file_generator import html_writer

from ..chain.query_image_gen_rewriter import query_rewriter

from ..chain.file_gen_assistant import assistant

from ..tools.agent_general.file_gen_tool import (
    image_gen_tool,
    pdf_gen_tool,
)

from ..memory.checkpointer_snowflake import SnowflakeSaver

logger = logging.getLogger(__name__)


async def transform_query_for_image_gen(
    state,
    config: RunnableConfig,
):
    """
    Transform the query to produce an optimized query for image generation.

    Args:
        state (dict): The current graph state

    Returns:
        state (dict): Updates question key with a re-phrased question
    """

    logger.info("---TRANSFORM QUERY FOR IMAGE GENERATION---")
    query = state["query"]
    username = state["username"]
    timestamp = state["timestamp"]
    chat_history = state["chat_history"]
    enterprise_context = state["enterprise_context"]
    image_context = state["image_context"]

    # Notify user that image generation process has started
    await adispatch_custom_event(
        "image_gen_triggered",
        {"image_generation": True},
        config=config,
    )
    generation = []
    async for msg in assistant.astream(
        {
            "conversation_stage": "Scenario 1: You just received the human request.",
            "query": query,
            "username": username,
            "timestamp": timestamp,
            "chat_history": chat_history,
            "enterprise_context": enterprise_context,
            "image_context": image_context,
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
    return {
        "img_gen_query": better_query,
        "context": [],
        "answer": generation,
    }


async def image_generation(
    state,
    config: RunnableConfig,
    checkpoint_saver: Callable[[str], Callable[[str, str], SnowflakeSaver]],
):
    """
    Image generation based on the re-phrased question.

    Args:
        state (dict): The current graph state

    Returns:
        state (dict): URL for image generated
    """

    logger.info("---IMAGE GENERATION---")
    query = state["query"]
    username = state["username"]
    timestamp = state["timestamp"]
    chat_history = state["chat_history"]
    enterprise_context = state["enterprise_context"]
    image_context = state["image_context"]
    answer = state["answer"]
    img_gen_query = state["img_gen_query"]
    user_id = state["user_id"]

    configurable = config.get("configurable", {})
    user_id = configurable["user_id"]
    session_id = configurable["session_id"]

    # Write chunks of final answer
    await adispatch_custom_event(
        "final_context",
        {"context": []},
        config=config,
    )

    # Image generation
    image_blob_url = None
    try:
        image_gen_result = await image_gen_tool.ainvoke(
            {
                "query": img_gen_query,
                "user_id": user_id,
                "session_id": session_id,
            }
        )
        if image_gen_result["status"] == "success":
            image_gen_message = image_gen_result["image_generation_message"]
            image_blob_url = image_gen_result["image_blob_url"]
            conversation_stage = (
                "Scenario 2: The image has been successfully generated using "
                f"the revised prompt: '{image_gen_message}'\n\n"
                "Let the user know."
            )
        else:
            raise Exception(image_gen_result["message"])
    except Exception as e:
        logger.error("An unexpected error occurred:", e)
        conversation_stage = (
            f"Scenario 3: The image was not generated because: '{e}'\n\n"
            "Let the user know."
        )
        image_blob_url = None

    # Write chunks of final answer
    await adispatch_custom_event(
        "final_answer",
        {"image_generation_revised_prompt": image_gen_message},
        config=config,
    )
    await adispatch_custom_event(
        "final_answer",
        {"image_blob_url": image_blob_url},
        config=config,
    )
    await adispatch_custom_event(
        "final_answer",
        {"answer": "\n\n"},
        config=config,
    )
    generation = []
    async for msg in assistant.astream(
        {
            "conversation_stage": conversation_stage,
            "query": query,
            "username": username,
            "timestamp": timestamp,
            "chat_history": chat_history,
            "enterprise_context": enterprise_context,
            "image_context": image_context,
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
        content=answer.content + "\n\n" + full_content,
        additional_kwargs=generation[-1].additional_kwargs,
        id=generation[-1].id,
        response_metadata=generation[-1].response_metadata,
        usage_metadata=generation[-1].usage_metadata,
    )

    # Update checkpoint
    checkpoint = checkpoint_saver(user_id, session_id)._load_checkpoint
    checkpoint["LatestGeneratedImageBlobURL"] = image_blob_url
    checkpoint["LatestGeneratedImageRevisedPrompt"] = image_gen_message
    if "ListGeneratedImageBlobURL" in checkpoint.keys():
        checkpoint["ListGeneratedImageBlobURL"].append(image_blob_url)
        checkpoint["ListGeneratedImageRevisedPrompt"].append(image_gen_message)
    else:
        checkpoint["ListGeneratedImageBlobURL"] = [image_blob_url]
        checkpoint["ListGeneratedImageRevisedPrompt"] = [image_gen_message]
    checkpoint_saver(user_id, session_id).add_checkpoint(checkpoint)

    return {
        "context": [],
        "answer": generation,
        "image_blob_url": image_blob_url,
    }


async def pdf_generation(
    state,
    config: RunnableConfig,
    checkpoint_saver: Callable[[str], Callable[[str, str], SnowflakeSaver]],
):
    """
    PDF document generation based on the user's requirement.

    Args:
        state (dict): The current graph state

    Returns:
        state (dict): URL for PDF generated
    """

    logger.info("---PDF GENERATION---")
    query = state["query"]
    username = state["username"]
    timestamp = state["timestamp"]
    chat_history = state["chat_history"]
    enterprise_context = state["enterprise_context"]
    image_context = state["image_context"]
    user_id = state["user_id"]

    configurable = config.get("configurable", {})
    user_id = configurable["user_id"]
    session_id = configurable["session_id"]

    # Write chunks of final answer
    await adispatch_custom_event(
        "final_context",
        {"context": []},
        config=config,
    )

    # Notify user that image generation process has started
    await adispatch_custom_event(
        "pdf_gen_triggered",
        {"pdf_generation": True},
        config=config,
    )
    generation = []
    async for msg in assistant.astream(
        {
            "conversation_stage": "Scenario 1: You just received the human request.",
            "query": query,
            "username": username,
            "timestamp": timestamp,
            "chat_history": chat_history,
            "enterprise_context": enterprise_context,
            "image_context": image_context,
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
    answer = AIMessage(
        content=full_content,
        additional_kwargs=generation[-1].additional_kwargs,
        id=generation[-1].id,
        response_metadata=generation[-1].response_metadata,
        usage_metadata=generation[-1].usage_metadata,
    )

    # PDF generation
    attemps = 0
    pdf_filename = None
    pdf_blob_url = None
    while attemps < 2:
        try:
            html_input = await html_writer.ainvoke(
                {
                    "query": query,
                    "username": username,
                    "image_context": image_context,
                    "chat_history": chat_history,
                    "timestamp": timestamp,
                    "enterprise_context": enterprise_context,
                }
            )

            pdf_gen_result = await pdf_gen_tool.ainvoke(
                {
                    "html_input": html_input,
                    "user_id": user_id,
                    "session_id": session_id,
                }
            )
            if pdf_gen_result["status"] == "success":
                pdf_blob_url = pdf_gen_result["generated_pdf_blob_url"]
                conversation_stage = (
                    "Scenario 2: The PDF file has been successfully generated.\n\n"
                    "Let the user know."
                )
                pdf_filename = await filename_generator.ainvoke(
                    {
                        "enterprise_context": enterprise_context,
                        "timestamp": timestamp,
                        "html_input": html_input,
                    }
                )
                pdf_filename += ".pdf"
            else:
                raise Exception(pdf_gen_result["message"])
        except Exception as e:
            logger.error("An unexpected error occurred:", e)
            conversation_stage = (
                f"Scenario 3: The PDF file was not generated because: '{e}'\n\n"
                "Let the user know."
            )
        attemps += 1

    # Write chunks of final answer
    await adispatch_custom_event(
        "final_answer",
        {"pdf_filename": pdf_filename},
        config=config,
    )
    await adispatch_custom_event(
        "final_answer",
        {"pdf_blob_url": pdf_blob_url},
        config=config,
    )
    await adispatch_custom_event(
        "final_answer",
        {"answer": "\n\n"},
        config=config,
    )
    generation = []
    async for msg in assistant.astream(
        {
            "conversation_stage": conversation_stage,
            "query": query,
            "username": username,
            "timestamp": timestamp,
            "chat_history": chat_history,
            "enterprise_context": enterprise_context,
            "image_context": image_context,
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
        content=answer.content + "\n\n" + full_content,
        additional_kwargs=generation[-1].additional_kwargs,
        id=generation[-1].id,
        response_metadata=generation[-1].response_metadata,
        usage_metadata=generation[-1].usage_metadata,
    )

    # Update checkpoint
    checkpoint = checkpoint_saver(user_id, session_id)._load_checkpoint
    checkpoint["LatestGeneratedPDFFileName"] = pdf_filename
    checkpoint["LatestGeneratedPDFBlobURL"] = pdf_blob_url
    if "ListGeneratedPDFBlobURL" in checkpoint.keys():
        checkpoint["ListGeneratedPDFFileName"].append(pdf_filename)
        checkpoint["ListGeneratedPDFBlobURL"].append(pdf_blob_url)
    else:
        checkpoint["ListGeneratedPDFFileName"] = [pdf_filename]
        checkpoint["ListGeneratedPDFBlobURL"] = [pdf_blob_url]
    checkpoint_saver(user_id, session_id).add_checkpoint(checkpoint)

    return {
        "context": [],
        "answer": generation,
        "pdf_filename": pdf_filename,
        "pdf_blob_url": pdf_blob_url,
    }
