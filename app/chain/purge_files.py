import logging
import re

from azure.identity import ClientSecretCredential
from azure.storage.blob import ContainerClient
from fastapi import HTTPException
from langchain_core.callbacks.manager import adispatch_custom_event
from langchain_core.runnables import RunnableConfig
from langserve import CustomUserType
from qdrant_client import models

from ..vector_db.utils import KnowledgeBaseManager

logger = logging.getLogger(__name__)


def _is_valid_doc_id(value: str) -> bool:
    """Check if the doc ID is in a valid format."""
    # Use a regular expression to match the allowed characters
    valid_characters = re.compile(r"^[a-zA-Z0-9-_]+$")
    return bool(valid_characters.match(value))


def _is_valid_user_id(value: str) -> bool:
    """Check if the given string is a valid email address."""
    # Regular expression pattern for a valid email address
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    # Use re.match to check if the email matches the pattern
    return bool(re.match(pattern, value))


def _delete_blob(
    kbm: KnowledgeBaseManager,
    user_doc: bool = False,
    filename: str = None,
    user_id: str = None,
    doc_id: str = None,
):
    """
    Delete any blobs in Azure Container
    that match the given user_id and doc_id.
    """

    # Create the ClientSecretCredential object
    credential = ClientSecretCredential(
        kbm.tenant_id,
        kbm.client_id,
        kbm.client_secret,
    )
    container_client = ContainerClient(
        account_url=kbm.blob_account_url,
        container_name=kbm.blob_container_name,
        credential=credential,
    )

    if user_doc:
        if doc_id:
            prefix_main = (
                f"{kbm.ai_agent_app_name.lower()}/"
                + "users_docs/"
                + f"{user_id}/"
                + f"{doc_id}"
            )
        else:
            prefix_main = (
                f"{kbm.ai_agent_app_name.lower()}/" + "users_docs/" + f"{user_id}"
            )
    else:
        prefix_main = (
            f"{kbm.ai_agent_app_name.lower()}/"
            + "public_docs/Additional Documents/"
            + filename
        )

    all_blobs = list(container_client.list_blob_names(name_starts_with=prefix_main))
    if not all_blobs:
        if user_doc:
            return {
                "User ID": user_id,
                "Document ID": doc_id,
                "Total": 0,
                "Successful": 0,
                "Unsuccessful": 0,
                "Deleted Blobs": [],
                "Errors": [{"Blob": prefix_main, "Error": "Not Found"}],
            }
        else:
            return {
                "AI Agent app": kbm.ai_agent_app_name,
                "Document Filename": filename,
                "Total": 0,
                "Successful": 0,
                "Unsuccessful": 0,
                "Deleted Blobs": [],
                "Errors": [{"Blob": prefix_main, "Error": "Not Found"}],
            }

    total = all_blobs.__len__()
    succcessful = 0
    deleted_blobs = []

    while True:
        all_blobs = list(container_client.list_blob_names(name_starts_with=prefix_main))
        if not all_blobs:
            break
        total_blobs = len(all_blobs)
        log_interval = 10
        for i, blob in enumerate(all_blobs):
            # , desc='Purging blobs...'):
            blob_client = container_client.get_blob_client(blob)
            try:
                blob_client.delete_blob()
                blob_client.close()
                deleted_blobs.append(blob)
                succcessful += 1
            except:
                continue

            # Calculate the percentage of completion
            progress = (i + 1) / total_blobs * 100

            # Log the progress at specified intervals
            if progress % log_interval == 0 or i == total_blobs - 1:
                logger.info(f"Purging blobs... " f"{progress:.2f}% complete")

    container_client.close()

    if user_doc:
        final_response = {
            "User ID": user_id,
            "Document ID": doc_id,
            "Total": total,
            "Successful": succcessful,
            "Unsuccessful": total - succcessful,
            "Deleted Blobs": deleted_blobs,
            "Errors": [],
        }
    else:
        final_response = {
            "AI Agent app": kbm.ai_agent_app_name,
            "Document Filename": filename,
            "Total": total,
            "Successful": succcessful,
            "Unsuccessful": total - succcessful,
            "Deleted Blobs": deleted_blobs,
            "Errors": [],
        }

    return final_response


async def _delete_qdrant(
    kbm: KnowledgeBaseManager,
    user_doc: bool = False,
    filename: str = None,
    user_id: str = None,
    doc_id: str = None,
):
    """
    Delete any elements in VectorStore
    that match the given user_id and doc_id.
    """
    if user_doc:
        if doc_id:
            points_selector = models.Filter(
                must=[
                    models.FieldCondition(
                        key="metadata.user_id",
                        match=models.MatchValue(value=user_id),
                    ),
                    models.FieldCondition(
                        key="metadata.doc_id",
                        match=models.MatchValue(value=doc_id),
                    ),
                ]
            )
        else:
            points_selector = models.Filter(
                must=[
                    models.FieldCondition(
                        key="metadata.user_id",
                        match=models.MatchValue(value=user_id),
                    ),
                ]
            )
    else:
        points_selector = models.Filter(
            must=[
                models.FieldCondition(
                    key="metadata.public_doc",
                    match=models.MatchValue(value="true"),
                ),
                models.FieldCondition(
                    key="metadata.filename",
                    match=models.MatchValue(value=filename),
                ),
            ]
        )
    result = await kbm.aclient.delete(
        collection_name=kbm.collection_name,
        points_selector=points_selector,
    )
    resp_status = result.status.lower()

    return {"Status": resp_status, "Details": result.dict()}


async def _purge_files(
    request: CustomUserType,
    config: RunnableConfig,
    kbm: KnowledgeBaseManager,
    user_doc: bool = False,
) -> str:
    """
    Main Handler to delete session data from both VectorStore and Cloud Storage
    """
    if user_doc:
        user_id = request.user_id
        if not _is_valid_user_id(user_id):
            error_message = (
                f"User ID {user_id} is not in a valid format. "
                "User ID must only contain alphanumeric characters, "
                "hyphens, and underscores."
                "Please include a valid cookie in the request headers "
                "called 'user-id'."
            )
            # Log the error and raise an exception
            logger.error(error_message)
            raise HTTPException(
                status_code=400,
                detail=error_message,
            )
        doc_id = request.doc_id
        if doc_id:
            if not _is_valid_doc_id(doc_id):
                error_message = (
                    f"Conversation doc ID `{doc_id}` is not in a valid format. "
                    "Document ID must only contain alphanumeric characters, "
                    "hyphens, and underscores."
                )
                raise HTTPException(
                    status_code=400,
                    detail=error_message,
                )

        # Notify user the purge progress
        logger.info(f"Purging user's {user_id} files... {0.0}% complete")
    else:
        filename = request.filename

        # Notify user the purge progress
        logger.info(f"Purging file: {filename}... {0.0}% complete")
    await adispatch_custom_event(
        "doc_processing",
        {"processing_progress": 0.0},
        config=config,
    )

    try:
        if user_doc:
            if doc_id:
                blob_deletion_response = _delete_blob(
                    kbm=kbm,
                    user_doc=user_doc,
                    doc_id=doc_id,
                    user_id=user_id,
                )
                # Notify user the purge progress
                logger.info(f"Purging file: {user_id}... {50.0}% complete")
                await adispatch_custom_event(
                    "doc_processing",
                    {"processing_progress": 50.0},
                    config=config,
                )
                vs_deletion_response = await _delete_qdrant(
                    kbm=kbm,
                    user_doc=user_doc,
                    doc_id=doc_id,
                    user_id=user_id,
                )
                # Notify user the purge progress
                logger.info(f"Purging file: {user_id}... {100.0}% complete")
                await adispatch_custom_event(
                    "doc_processing",
                    {"processing_progress": 100.0},
                    config=config,
                )
            else:
                blob_deletion_response = _delete_blob(
                    kbm=kbm,
                    user_doc=user_doc,
                    user_id=user_id,
                )
                # Notify user the purge progress
                logger.info(f"Purging file: {user_id}... {50.0}% complete")
                await adispatch_custom_event(
                    "doc_processing",
                    {"processing_progress": 50.0},
                    config=config,
                )
                vs_deletion_response = await _delete_qdrant(
                    kbm=kbm,
                    user_doc=user_doc,
                    user_id=user_id,
                )
                # Notify user the purge progress
                logger.info(f"Purging file: {user_id}... {100.0}% complete")
                await adispatch_custom_event(
                    "doc_processing",
                    {"processing_progress": 100.0},
                    config=config,
                )
        else:
            blob_deletion_response = _delete_blob(
                kbm=kbm,
                filename=filename,
            )
            # Notify user the purge progress
            logger.info(f"Purging file: {filename}... {50.0}% complete")
            await adispatch_custom_event(
                "doc_processing",
                {"processing_progress": 50.0},
                config=config,
            )
            vs_deletion_response = await _delete_qdrant(
                kbm=kbm,
                filename=filename,
            )
            # Notify user the purge progress
            logger.info(f"Purging file: {filename}... {100.0}% complete")
            await adispatch_custom_event(
                "doc_processing",
                {"processing_progress": 100.0},
                config=config,
            )

        final_response = {
            "detail": "Data successfully deleted!",
            "blob_deletion_details": blob_deletion_response,
            "vectorstore_deletion_details": vs_deletion_response,
        }

        # Notify user the purge progress
        await adispatch_custom_event(
            "doc_processing",
            {
                "processing_progress": 100.0,
                "message": final_response,
            },
            config=config,
        )

        return {"message": final_response}

    except Exception as error_message:
        # Log the error and raise an exception
        logger.error(error_message)
        raise HTTPException(
            status_code=400,
            detail=error_message,
        )
