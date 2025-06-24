
import logging

from typing import Callable

from langchain_core.runnables import RunnableConfig
from langchain_core.callbacks.manager import adispatch_custom_event
from langchain_core.messages import AIMessage

from ...chain.filename_generator import (
    filename_generator
)

from ...chain.agent_procurement.sow_info_gatherer import (
    sow_type_gatherer, 
    consultancy_services_sow_details_gatherer, 
    )

from ...chain.file_gen_assistant import (
    assistant
    )

from ...tools.agent_procurement.doc_gen_tool import (
    consultancy_services_sow_tool, 
    )

# from ...tools.agent_procurement.send_email_tool import (
#     tool as send_email_tool, 
#     )

from ...memory.checkpointer_snowflake import SnowflakeSaver

logger = logging.getLogger(__name__)


async def gather_sow_type(
    state,
    config: RunnableConfig,
    ):

    logger.info("---GATHERING REQUIRED DETAILS FOR SoW---")
    query = state["query"]
    timestamp = state["timestamp"]
    chat_history = state["chat_history"]
    enterprise_context = state["enterprise_context"]
    image_context = state["image_context"]
    
    # Gather information from human conversation
    response = await sow_type_gatherer.ainvoke({
        "query": query,
        "timestamp": timestamp,
        "chat_history": chat_history,
        "enterprise_context": enterprise_context,
        "image_context": image_context,
        })
    
    if response.tool_calls:
        return {
            "sow_type": response,
            }
    else:
        return {
            "answer": response,
            "context": [],
            }

async def gather_sow_details(
    state,
    config: RunnableConfig,
    ):
    """
    Gather all required information for SoW document.

    Args:
        state (dict): The current graph state

    Returns:
        state (dict): Updates SoW details key based on shared info
    """

    logger.info("---GATHERING REQUIRED DETAILS FOR SoW---")
    query = state["query"]
    username = state["username"]
    timestamp = state["timestamp"]
    chat_history = state["chat_history"]
    enterprise_context = state["enterprise_context"]
    image_context = state["image_context"]
    sow_type = state["sow_type"]
    sow_type = sow_type.tool_calls[0]["args"]["sow_type"]
    
    sow_gatherers = {
        "Consultancy Services": consultancy_services_sow_details_gatherer, 
    }
    sow_gatherer = sow_gatherers[sow_type]
    
    # Gather information from human conversation
    response = await sow_gatherer.ainvoke({
        "query": query,
        "timestamp": timestamp,
        "chat_history": chat_history,
        "enterprise_context": enterprise_context,
        "image_context": image_context,
        })
    
    if response.tool_calls:
        # Write chunks of final answer
        generation = []
        async for msg in assistant.astream({
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
                {
                    "answer": msg.content
                },
                config=config,
            )
    
        # Aggregate the content
        full_content = ''.join(chunk.content for chunk in generation)

        # Create the AIMessage object
        generation = AIMessage(
            content=full_content,
            additional_kwargs=generation[-1].additional_kwargs,
            id=generation[-1].id,
            response_metadata=generation[-1].response_metadata,
            usage_metadata=generation[-1].usage_metadata,
            )
        return {
            "sow_details": response,
            "answer": generation,
            }
    else:
        return {
            "answer": response,
            "context": [],
            }


async def sow_doc_generation(
    state,
    config: RunnableConfig,
    checkpoint_saver: Callable[[str], Callable[[str, str], SnowflakeSaver]],
    ):
    """
    Generate an SOW document.

    Args:
        state (dict): The current graph state

    Returns:
        state (dict): Updates SOW doc key based on shared info
    """

    logger.info("---GENERATING SOW DOCUMENT---")
    query = state["query"]
    username = state["username"]
    timestamp = state["timestamp"]
    chat_history = state["chat_history"]
    enterprise_context = state["enterprise_context"]
    image_context = state["image_context"]
    sow_details = state["sow_details"]
    answer = state["answer"]
    
    configurable = config.get("configurable", {})
    user_id = configurable["user_id"]
    session_id = configurable["session_id"]
    
    # Generate SOW document with gathered information
    sow_filename = None
    sow_blob_url = None
    try:
        doc_gen_result = await consultancy_services_sow_tool.ainvoke({
            "document_input": sow_details.tool_calls[0]["args"], 
            "user_id": user_id, 
            "session_id": session_id, 
            })
        if doc_gen_result['status'] == 'success':
            sow_blob_url = doc_gen_result['generated_document_blob_url']
            conversation_stage = (
                "Scenario 2: The document has been successfully generated.\n\n"
                "Let the user know."
                )
            sow_filename = await filename_generator.ainvoke({
                "query": query,
                "image_context": image_context,
                "chat_history": chat_history,
                "timestamp": timestamp,
                "enterprise_context": enterprise_context,
            })
            sow_filename += ".docx"
        else:
            raise Exception(doc_gen_result['message'])
    except Exception as e:
        logger.error("An unexpected error occurred:", e)
        conversation_stage = (
            f"Scenario 3: The document was not generated because: '{e}'\n\n"
            "Let the user know."
            )
    
    # Write chunks of final answer
    await adispatch_custom_event(
        "final_context",
        {
            "context": []
        },
        config=config,
    )
    await adispatch_custom_event(
        "final_generated_document",
        {
            "sow_filename": sow_filename
        },
        config=config,
    )
    await adispatch_custom_event(
        "final_generated_document",
        {
            "sow_blob_url": sow_blob_url
        },
        config=config,
    )
    await adispatch_custom_event(
        "final_answer",
        {
            "answer": "\n\n"
        },
        config=config,
    )
    
    generation = []
    async for msg in assistant.astream({
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
            {
                "answer": msg.content
            },
            config=config,
        )
    
    # Aggregate the content
    full_content = ''.join(chunk.content for chunk in generation)

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
    checkpoint["LatestGeneratedSoWFileName"] = sow_filename
    checkpoint["LatestGeneratedSoWBlobURL"] = sow_blob_url
    if "ListGeneratedSoWBlobURL" in checkpoint.keys():
        checkpoint["ListGeneratedSoWFileName"].append(sow_filename)
        checkpoint["ListGeneratedSoWBlobURL"].append(sow_blob_url)
    else:
        checkpoint["ListGeneratedSoWFileName"] = [sow_filename]
        checkpoint["ListGeneratedSoWBlobURL"] = [sow_blob_url]
    checkpoint_saver(user_id, session_id).add_checkpoint(checkpoint)
    
    return {
        "sow_filename": sow_filename,
        "sow_blob_url": sow_blob_url,
        "answer": generation,
        "context": [],
        }


# async def send_rfp_email(
#     state, 
#     config: RunnableConfig, 
#     ):
#     """
#     Send an SOW document through email.

#     Args:
#         state (dict): The current graph state

#     Returns:
#         state (dict): Updates SOW doc key based on shared info
#     """

#     logger.info("---GENERATING SOW DOCUMENT---")
#     query = state["query"]
#     username = state["username"]
#     timestamp = state["timestamp"]
#     chat_history = state["chat_history"]
#     enterprise_context = state["enterprise_context"]
#     image_context = state["image_context"]
#     sow_blob_url = state["sow_blob_url"]
    
#     # Send SOW document with gathered information
#     message = {
#         "content": {
#             "subject": 
#                 "Generated Request for Proposal (SOW) Document | MorRFP ",
#             "plainText": "Please find attached the generated SOW document.",
#             "html": 
#                 "<html><h1>Please find attached the SOW document.</h1></html>",
#         },
#         "recipients": {
#             "to": [
#                 {
#                     "address": username,
#                     "displayName": "Recipient Name"
#                 }
#             ]
#         },
#         "attachments": [
#             {
#                 "name": "Generated SOW.docx",
#                 "attachmentType": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
#                 "contentBytesBase64": sow_blob_url
#             }
#         ],
#         "senderAddress": "sender@contoso.com"
#     }
    
#     try:
#         tool_response = send_email_tool.ainvoke({
#             "message": message, 
#             })
#         if tool_response['status'] == 'success':
#             status_response = tool_response['status_response']
#             conversation_stage = (
#                 "The document has been successfully sent. "
#                 "Let the user know."
#                 )
#         else:
#             raise Exception(tool_response['message'])
#     except Exception as e:
#         logger.error("An unexpected error occurred:", e)
#         conversation_stage = (
#             f"The document was not sent because: '{e}'\n\n"
#             "Let the user know."
#             )
#         status_response = None
    
#     # Write chunks of final answer
#     await adispatch_custom_event(
#         "final_context",
#         {
#             "context": []
#         },
#         config=config,
#     )
    
#     generation = []
#     async for msg in assistant.astream({
#         "conversation_stage": conversation_stage,
#         "query": query, 
            # "username": username, 
#         "timestamp": timestamp, 
#         "chat_history": chat_history, 
#         "enterprise_context": enterprise_context, 
#         "image_context": image_context, 
#         }, 
#         config=config,
#         ):
#         generation.append(msg)
#         await adispatch_custom_event(
#             "final_answer",
#             {
#                 "answer": msg.content
#             },
#             config=config,
#         )
    
#     # Aggregate the content
#     full_content = ''.join(chunk.content for chunk in generation)

#     # Create the AIMessage object
#     generation = AIMessage(
#         content=full_content, 
#         additional_kwargs=generation[-1].additional_kwargs, 
#         id=generation[-1].id,
#         response_metadata=generation[-1].response_metadata,
#         usage_metadata=generation[-1].usage_metadata,
#         )
    
#     return {
#         "sow_blob_url": sow_blob_url, 
#         "answer": generation, 
#         "context": [], 
#         }
