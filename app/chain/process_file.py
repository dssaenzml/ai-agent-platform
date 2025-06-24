import os

import logging

import re
import magic
import base64

import aiofiles

from datetime import datetime
from zoneinfo import ZoneInfo

from fastapi import HTTPException

from langchain_core.runnables import RunnableConfig
from langchain_core.callbacks.manager import adispatch_custom_event

from qdrant_client import models

from langserve import CustomUserType

from ..vector_db.utils import KnowledgeBaseManager

logger = logging.getLogger(__name__)

# get timezone for standard timestamps
tzinfo = ZoneInfo("Asia/Dubai")

# Supported file types
supported_llm_image_types = ["png", "jpeg"]
supported_mime_types = {
    "image/png": "png",
    "image/jpeg": "jpeg",
    "application/pdf": "pdf",
    "application/msword": "doc",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "docx",
    "application/vnd.ms-excel": "xls",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": "xlsx",
    "application/vnd.ms-powerpoint": "ppt",
    "application/vnd.openxmlformats-officedocument.presentationml.presentation": "pptx",
}

# Supported doc partition processing types
partition_extract_type = {
    "high_resolution": "hi_res",
    "fast": "fast",
}


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


def _is_valid_extraction_strategy(extraction_strategy: str) -> bool:
    """Check if the information extraction strategy is a valid option."""
    return bool(extraction_strategy in partition_extract_type.keys())


def recognize_file_type(file_bytes, supported_mime_types):
    """
    Recognize the file extension from bytes information, if any.
    """
    mime_type = magic.from_buffer(file_bytes, mime=True)

    if mime_type in supported_mime_types.keys():
        return supported_mime_types[mime_type], mime_type


async def _process_file(
    request: CustomUserType,
    config: RunnableConfig,
    kbm: KnowledgeBaseManager,
    user_doc: bool = False,
) -> dict:
    """
    Extract the elements from the file and upload them into the vectorstore.
    """
    logger.info(
        f"Processing file: {request.filename} with extraction strategy: "
        f"{request.extract_type}"
    )

    # Notify user that doc processing has started
    logger.info(f"Processing file: {request.filename}... {0.0}% complete")
    await adispatch_custom_event(
        "doc_processing",
        {"processing_progress": 0.0},
        config=config,
    )

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
        if not _is_valid_doc_id(doc_id):
            error_message = (
                f"Conversation doc ID `{doc_id}` is not in a valid format. "
                "Document ID must only contain alphanumeric characters, "
                "hyphens, and underscores."
            )
            # Log the error and raise an exception
            logger.error(error_message)
            raise HTTPException(
                status_code=400,
                detail=error_message,
            )

    extraction_strategy = request.extract_type
    if not _is_valid_extraction_strategy(extraction_strategy):
        error_message = (
            f"Information extraction strategy "
            "`{extraction_strategy}` is not valid. "
            "Please choose one of the options: "
            f"{list(partition_extract_type.keys())}."
        )
        # Log the error and raise an exception
        logger.error(error_message)
        raise HTTPException(
            status_code=400,
            detail=error_message,
        )

    # Notify user the doc processing progress
    logger.info(f"Processing file: {request.filename}... {10.0}% complete")
    await adispatch_custom_event(
        "doc_processing",
        {"processing_progress": 10.0},
        config=config,
    )

    try:
        filename = request.filename
        content = base64.b64decode(request.file.encode("utf-8"))
        file_ext, content_type = recognize_file_type(
            file_bytes=content,
            supported_mime_types=supported_mime_types,
        )
        partition_strategy = partition_extract_type[extraction_strategy]

        # Create a temporary file
        async with aiofiles.tempfile.NamedTemporaryFile(delete=False) as temp_file:
            await temp_file.write(content)
            file_path = temp_file.name

        # Notify user the doc processing progress
        logger.info(f"Processing file: {request.filename}... {15.0}% complete")
        await adispatch_custom_event(
            "doc_processing",
            {"processing_progress": 15.0},
            config=config,
        )

        if user_doc:
            blob_url = kbm.upload_user_blob(
                file_path=file_path,
                filename=filename,
                doc_id=doc_id,
                user_id=user_id,
                content_type=content_type,
            )
        else:
            blob_url = kbm.upload_extra_kb_blob(
                file_path=file_path,
                filename=filename,
                content_type=content_type,
            )

        # Notify user the doc processing progress
        logger.info(f"Processing file: {request.filename}... {25.0}% complete")
        await adispatch_custom_event(
            "doc_processing",
            {"processing_progress": 25.0},
            config=config,
        )

        if file_ext in supported_llm_image_types:
            logger.info(f"Processing file: {request.filename}... {100.0}% complete")
            if user_doc:
                await adispatch_custom_event(
                    "doc_processing",
                    {
                        "processing_progress": 100.0,
                        "mime_type": content_type,
                        "URL": blob_url,
                        "doc_id": doc_id,
                        "user_id": user_id,
                        "detail": "File successfully uploaded!",
                    },
                    config=config,
                )

                logger.info(f"File {filename} processed successfully. URL: {blob_url}")

                return {
                    "message": {
                        "processing_progress": 100.0,
                        "mime_type": content_type,
                        "URL": blob_url,
                        "doc_id": doc_id,
                        "user_id": user_id,
                        "detail": "File successfully uploaded!",
                    }
                }
            else:
                await adispatch_custom_event(
                    "doc_processing",
                    {
                        "processing_progress": 100.0,
                        "mime_type": content_type,
                        "URL": blob_url,
                        "detail": "File successfully uploaded!",
                    },
                    config=config,
                )

                logger.info(f"File {filename} processed successfully. URL: {blob_url}")

                return {
                    "message": {
                        "processing_progress": 100.0,
                        "mime_type": content_type,
                        "URL": blob_url,
                        "detail": "File successfully uploaded!",
                    }
                }

        elif file_ext == "pdf":
            loader = kbm.process_pdf(
                file_path=file_path,
                partition_strategy=partition_strategy,
            )

        elif file_ext in ["xls", "xlsx"]:
            loader = kbm.process_excel(
                file_path=file_path,
                partition_strategy=partition_strategy,
            )

        elif file_ext in ["ppt", "pptx"]:
            loader = kbm.process_ppt(
                file_path=file_path,
                partition_strategy=partition_strategy,
            )

        elif file_ext in ["doc", "docx"]:
            loader = kbm.process_word(
                file_path=file_path,
                partition_strategy=partition_strategy,
            )

        else:
            raise HTTPException(
                status_code=400,
                detail="Base64 file is not " f"{list(supported_mime_types.values())}",
            )

        # Notify user the doc processing progress
        logger.info(f"Processing file: {request.filename}... {30.0}% complete")
        await adispatch_custom_event(
            "doc_processing",
            {"processing_progress": 30.0},
            config=config,
        )

        # Load file's elements
        docs = await loader.aload()

        # Filter empty docs
        docs = [doc for doc in docs if doc.page_content != ""]

        for doc in docs:
            doc.metadata["filename"] = filename
            doc.metadata["URL"] = blob_url
            if user_doc:
                doc.metadata["doc_id"] = doc_id
                doc.metadata["user_id"] = user_id
            else:
                doc.metadata["public_doc"] = "true"
            doc.metadata["upload_timestamp"] = datetime.now(tzinfo).isoformat()

        async for _progress, _docs in kbm.process_docs(
            docs=docs,
            user_doc=user_doc,
        ):
            if _docs:
                docs = _docs
            else:
                # Notify user the doc processing progress
                await adispatch_custom_event(
                    "doc_processing",
                    {
                        "processing_progress": round(
                            35.0 + (40.0 * (_progress / 100.0)),
                            0,
                        )
                    },
                    config=config,
                )
                continue

        # Notify user the doc processing progress
        logger.info(f"Processing file: {request.filename}... {75.0}% complete")
        await adispatch_custom_event(
            "doc_processing",
            {"processing_progress": 75.0},
            config=config,
        )

        # Clean any vector points that share id
        if user_doc:
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
                        key="metadata.public_doc",
                        match=models.MatchValue(value="true"),
                    ),
                    models.FieldCondition(
                        key="metadata.filename",
                        match=models.MatchValue(value=filename),
                    ),
                ]
            )
        await kbm.aclient.delete(
            collection_name=kbm.collection_name,
            points_selector=points_selector,
        )

        # Notify user the doc processing progress
        logger.info(f"Processing file: {request.filename}... {80.0}% complete")
        await adispatch_custom_event(
            "doc_processing",
            {"processing_progress": 80.0},
            config=config,
        )

        # Add docs to the vector db
        await kbm.vectorstore.aadd_documents(
            docs,
            batch_size=kbm.max_batch_size,
        )

        # Notify user the doc processing progress
        logger.info(f"Processing file: {request.filename}... {100.0}% complete")
        if user_doc:
            await adispatch_custom_event(
                "doc_processing",
                {
                    "processing_progress": 100.0,
                    "mime_type": content_type,
                    "URL": blob_url,
                    "doc_id": doc_id,
                    "user_id": user_id,
                    "detail": "File successfully uploaded!",
                },
                config=config,
            )

            logger.info(f"File {filename} processed successfully. URL: {blob_url}")

            return {
                "message": {
                    "processing_progress": 100.0,
                    "mime_type": content_type,
                    "URL": blob_url,
                    "doc_id": doc_id,
                    "user_id": user_id,
                    "detail": "File successfully uploaded!",
                }
            }
        else:
            await adispatch_custom_event(
                "doc_processing",
                {
                    "processing_progress": 100.0,
                    "mime_type": content_type,
                    "URL": blob_url,
                    "detail": "File successfully uploaded!",
                },
                config=config,
            )

            logger.info(f"File {filename} processed successfully. URL: {blob_url}")

            return {
                "message": {
                    "processing_progress": 100.0,
                    "mime_type": content_type,
                    "URL": blob_url,
                    "detail": "File successfully uploaded!",
                }
            }

    except Exception as error_message:
        # Log the error and raise an exception
        logger.error(f"Error processing file {request.filename}: {error_message}")
        raise HTTPException(
            status_code=400,
            detail=error_message,
        )
    finally:
        # Make sure to remove the temporary file when done
        os.unlink(temp_file.name)
