from importlib import metadata

import logging
from fastapi import APIRouter, Request, Response, HTTPException
from langserve import APIHandler

from sse_starlette import EventSourceResponse

from openai import BadRequestError

from ...chain.topic_summarizer import topic_summary_chain

from ...chain.agent_hr.qa_bot import (
    conversational_chain,
    conversational_chain_stream,
)

from ...chain.agent_hr.process_kb_file import (
    process_file as process_kb_file,
    process_file_stream as process_kb_file_stream,
)

from ...chain.agent_hr.purge_kb_files import purge_files as purge_kb_files

from ...chain.agent_hr.process_user_file import (
    process_file as process_user_file,
    process_file_stream as process_user_file_stream,
)

from ...chain.agent_hr.purge_user_files import purge_files as purge_user_files

from ...helpers.utils import (
    _per_request_config_modifier,
)

logger = logging.getLogger(__name__)

# Set AI Agent's bot name
BOT_NAME = "HRAgent"

PYDANTIC_VERSION = metadata.version("pydantic")
_PYDANTIC_MAJOR_VERSION: int = int(PYDANTIC_VERSION.split(".")[0])

router = APIRouter(prefix=f"/{BOT_NAME.lower()}", tags=[f"{BOT_NAME} Bot"])

# Additional Knowledge Base files
process_kb_file_api_handler = APIHandler(
    process_kb_file,
    path=f"/{BOT_NAME.lower()}_process_kb_file",
    config_keys=["configurable"],
)

process_kb_file_api_stream_handler = APIHandler(
    process_kb_file_stream,
    path=f"/{BOT_NAME.lower()}_process_kb_file",
    config_keys=["configurable"],
)

# Delete Additional Knowledge Base Files
purge_kb_files_api_handler = APIHandler(
    purge_kb_files,
    path=f"/{BOT_NAME.lower()}_purge_kb_files",
    config_keys=["configurable"],
)

# User files
process_user_file_api_handler = APIHandler(
    process_user_file,
    path=f"/{BOT_NAME.lower()}_process_file",
    config_keys=["configurable"],
)

process_user_file_api_stream_handler = APIHandler(
    process_user_file_stream,
    path=f"/{BOT_NAME.lower()}_process_file",
    config_keys=["configurable"],
)

# Delete User Files
purge_user_files_api_handler = APIHandler(
    purge_user_files,
    path=f"/{BOT_NAME.lower()}_purge_files",
    config_keys=["configurable"],
)

# Langchain bots
topic_api_handler = APIHandler(
    topic_summary_chain,
    path=f"/{BOT_NAME.lower()}_ts",
)

rag_api_handler = APIHandler(
    conversational_chain,
    path=f"/{BOT_NAME.lower()}_rag",
    per_req_config_modifier=_per_request_config_modifier,
)

rag_api_stream_handler = APIHandler(
    conversational_chain_stream,
    path=f"/{BOT_NAME.lower()}_rag",
    per_req_config_modifier=_per_request_config_modifier,
)


## First register the endpoints without documentation
# Process additional KB File
@router.post(
    f"/{BOT_NAME.lower()}_process_kb_file/invoke",
    tags=["File Processing"],
    include_in_schema=False,
)
async def process_kb_file_invoke(
    request: Request,
) -> Response:
    """Handle invoke request."""
    try:
        return await process_kb_file_api_handler.invoke(request)
    except BadRequestError as e:
        logger.error(
            f"Error processing KB file invoke request: {e}",
            exc_info=True,
        )
        openai_bad_request_message = (
            "Your request was blocked due to triggering our content "
            "management policy. Unfortunately, this conversation cannot "
            "continue. Please modify your prompt and try again."
        )
        raise HTTPException(
            status_code=500,
            detail=openai_bad_request_message,
        )
    except Exception as e:
        logger.error(
            f"Error processing KB file invoke request: {e}",
            exc_info=True,
        )
        raise HTTPException(
            status_code=500,
            detail="An internal server error occurred. Please try again later.",
        )


@router.post(
    f"/{BOT_NAME.lower()}_process_kb_file/batch",
    tags=["File Processing"],
    include_in_schema=False,
)
async def process_kb_file_batch(
    request: Request,
) -> Response:
    """Handle batch request."""
    try:
        return await process_kb_file_api_handler.batch(request)
    except BadRequestError as e:
        logger.error(
            f"Error processing KB file invoke request: {e}",
            exc_info=True,
        )
        openai_bad_request_message = (
            "Your request was blocked due to triggering our content "
            "management policy. Unfortunately, this conversation cannot "
            "continue. Please modify your prompt and try again."
        )
        raise HTTPException(
            status_code=500,
            detail=openai_bad_request_message,
        )
    except Exception as e:
        logger.error(
            f"Error processing KB file batch request: {e}",
            exc_info=True,
        )
        raise HTTPException(
            status_code=500,
            detail="An internal server error occurred. Please try again later.",
        )


@router.post(
    f"/{BOT_NAME.lower()}_process_kb_file/stream",
    tags=["File Processing"],
    include_in_schema=False,
)
async def process_kb_file_stream(
    request: Request,
) -> EventSourceResponse:
    """Handle stream request."""
    try:
        return await process_kb_file_api_stream_handler.stream(request)
    except BadRequestError as e:
        logger.error(
            f"Error processing KB file invoke request: {e}",
            exc_info=True,
        )
        openai_bad_request_message = (
            "Your request was blocked due to triggering our content "
            "management policy. Unfortunately, this conversation cannot "
            "continue. Please modify your prompt and try again."
        )
        raise HTTPException(
            status_code=500,
            detail=openai_bad_request_message,
        )
    except Exception as e:
        logger.error(
            f"Error processing KB file stream request: {e}",
            exc_info=True,
        )
        raise HTTPException(
            status_code=500,
            detail="An internal server error occurred. Please try again later.",
        )


# Delete additional KB File
@router.post(
    f"/{BOT_NAME.lower()}_purge_kb_files/invoke",
    tags=["File Processing"],
    include_in_schema=False,
)
async def purge_kb_files_invoke(
    request: Request,
) -> Response:
    """Handle invoke request."""
    try:
        return await purge_kb_files_api_handler.invoke(request)
    except BadRequestError as e:
        logger.error(
            f"Error processing KB file invoke request: {e}",
            exc_info=True,
        )
        openai_bad_request_message = (
            "Your request was blocked due to triggering our content "
            "management policy. Unfortunately, this conversation cannot "
            "continue. Please modify your prompt and try again."
        )
        raise HTTPException(
            status_code=500,
            detail=openai_bad_request_message,
        )
    except Exception as e:
        logger.error(
            f"Error purging KB file invoke request: {e}",
            exc_info=True,
        )
        raise HTTPException(
            status_code=500,
            detail="An internal server error occurred. Please try again later.",
        )


# Process User File
@router.post(
    f"/{BOT_NAME.lower()}_process_file/invoke",
    tags=["File Processing"],
    include_in_schema=False,
)
async def process_user_file_invoke(
    request: Request,
) -> Response:
    """Handle invoke request."""
    try:
        return await process_user_file_api_handler.invoke(request)
    except BadRequestError as e:
        logger.error(
            f"Error processing KB file invoke request: {e}",
            exc_info=True,
        )
        openai_bad_request_message = (
            "Your request was blocked due to triggering our content "
            "management policy. Unfortunately, this conversation cannot "
            "continue. Please modify your prompt and try again."
        )
        raise HTTPException(
            status_code=500,
            detail=openai_bad_request_message,
        )
    except Exception as e:
        logger.error(
            f"Error processing User file invoke request: {e}",
            exc_info=True,
        )
        raise HTTPException(
            status_code=500,
            detail="An internal server error occurred. Please try again later.",
        )


@router.post(
    f"/{BOT_NAME.lower()}_process_file/batch",
    tags=["File Processing"],
    include_in_schema=False,
)
async def process_user_file_batch(
    request: Request,
) -> Response:
    """Handle batch request."""
    try:
        return await process_user_file_api_handler.batch(request)
    except BadRequestError as e:
        logger.error(
            f"Error processing KB file invoke request: {e}",
            exc_info=True,
        )
        openai_bad_request_message = (
            "Your request was blocked due to triggering our content "
            "management policy. Unfortunately, this conversation cannot "
            "continue. Please modify your prompt and try again."
        )
        raise HTTPException(
            status_code=500,
            detail=openai_bad_request_message,
        )
    except Exception as e:
        logger.error(
            f"Error processing User file batch request: {e}",
            exc_info=True,
        )
        raise HTTPException(
            status_code=500,
            detail="An internal server error occurred. Please try again later.",
        )


@router.post(
    f"/{BOT_NAME.lower()}_process_file/stream",
    tags=["File Processing"],
    include_in_schema=False,
)
async def process_user_file_stream(
    request: Request,
) -> EventSourceResponse:
    """Handle stream request."""
    try:
        return await process_user_file_api_stream_handler.stream(request)
    except BadRequestError as e:
        logger.error(
            f"Error processing KB file invoke request: {e}",
            exc_info=True,
        )
        openai_bad_request_message = (
            "Your request was blocked due to triggering our content "
            "management policy. Unfortunately, this conversation cannot "
            "continue. Please modify your prompt and try again."
        )
        raise HTTPException(
            status_code=500,
            detail=openai_bad_request_message,
        )
    except Exception as e:
        logger.error(
            f"Error processing User file stream request: {e}",
            exc_info=True,
        )
        raise HTTPException(
            status_code=500,
            detail="An internal server error occurred. Please try again later.",
        )


# Delete User Files
@router.post(
    f"/{BOT_NAME.lower()}_purge_files/invoke",
    tags=["File Processing"],
    include_in_schema=False,
)
async def purge_user_files_invoke(
    request: Request,
) -> Response:
    """Handle invoke request."""
    try:
        return await purge_user_files_api_handler.invoke(request)
    except BadRequestError as e:
        logger.error(
            f"Error processing KB file invoke request: {e}",
            exc_info=True,
        )
        openai_bad_request_message = (
            "Your request was blocked due to triggering our content "
            "management policy. Unfortunately, this conversation cannot "
            "continue. Please modify your prompt and try again."
        )
        raise HTTPException(
            status_code=500,
            detail=openai_bad_request_message,
        )
    except Exception as e:
        logger.error(
            f"Error purging User file invoke request: {e}",
            exc_info=True,
        )
        raise HTTPException(
            status_code=500,
            detail="An internal server error occurred. Please try again later.",
        )


# Topic Summary
@router.post(
    f"/{BOT_NAME.lower()}_ts/invoke",
    tags=["Topic Summary"],
    include_in_schema=False,
)
async def bot_ts_invoke(
    request: Request,
) -> Response:
    """Handle invoke request."""
    try:
        return await topic_api_handler.invoke(request)
    except BadRequestError as e:
        logger.error(
            f"Error processing KB file invoke request: {e}",
            exc_info=True,
        )
        openai_bad_request_message = (
            "Your request was blocked due to triggering our content "
            "management policy. Unfortunately, this conversation cannot "
            "continue. Please modify your prompt and try again."
        )
        raise HTTPException(
            status_code=500,
            detail=openai_bad_request_message,
        )
    except Exception as e:
        logger.error(
            f"Error processing Topic summary invoke request: {e}",
            exc_info=True,
        )
        raise HTTPException(
            status_code=500,
            detail="An internal server error occurred. Please try again later.",
        )


@router.post(
    f"/{BOT_NAME.lower()}_ts/batch",
    tags=["Topic Summary"],
    include_in_schema=False,
)
async def bot_ts_batch(
    request: Request,
) -> Response:
    """Handle batch request."""
    try:
        return await topic_api_handler.batch(request)
    except BadRequestError as e:
        logger.error(
            f"Error processing KB file invoke request: {e}",
            exc_info=True,
        )
        openai_bad_request_message = (
            "Your request was blocked due to triggering our content "
            "management policy. Unfortunately, this conversation cannot "
            "continue. Please modify your prompt and try again."
        )
        raise HTTPException(
            status_code=500,
            detail=openai_bad_request_message,
        )
    except Exception as e:
        logger.error(
            f"Error processing Topic summary batch request: {e}",
            exc_info=True,
        )
        raise HTTPException(
            status_code=500,
            detail="An internal server error occurred. Please try again later.",
        )


@router.post(
    f"/{BOT_NAME.lower()}_ts/stream",
    tags=["Topic Summary"],
    include_in_schema=False,
)
async def bot_ts_stream(
    request: Request,
) -> EventSourceResponse:
    """Handle stream request."""
    try:
        return await topic_api_handler.stream(request)
    except BadRequestError as e:
        logger.error(
            f"Error processing KB file invoke request: {e}",
            exc_info=True,
        )
        openai_bad_request_message = (
            "Your request was blocked due to triggering our content "
            "management policy. Unfortunately, this conversation cannot "
            "continue. Please modify your prompt and try again."
        )
        raise HTTPException(
            status_code=500,
            detail=openai_bad_request_message,
        )
    except Exception as e:
        logger.error(
            f"Error processing Topic summary stream request: {e}",
            exc_info=True,
        )
        raise HTTPException(
            status_code=500,
            detail="An internal server error occurred. Please try again later.",
        )


# Conversational RAG
@router.post(
    f"/{BOT_NAME.lower()}_rag/invoke",
    tags=["Conversational RAG"],
    include_in_schema=False,
)
async def bot_rag_invoke(
    request: Request,
) -> Response:
    """Handle invoke request."""
    try:
        return await rag_api_handler.invoke(request)
    except BadRequestError as e:
        logger.error(
            f"Error processing KB file invoke request: {e}",
            exc_info=True,
        )
        openai_bad_request_message = (
            "Your request was blocked due to triggering our content "
            "management policy. Unfortunately, this conversation cannot "
            "continue. Please modify your prompt and try again."
        )
        raise HTTPException(
            status_code=500,
            detail=openai_bad_request_message,
        )
    except Exception as e:
        logger.error(
            f"Error processing Conversational invoke request: {e}",
            exc_info=True,
        )
        raise HTTPException(
            status_code=500,
            detail="An internal server error occurred. Please try again later.",
        )


@router.post(
    f"/{BOT_NAME.lower()}_rag/batch",
    tags=["Conversational RAG"],
    include_in_schema=False,
)
async def bot_rag_batch(
    request: Request,
) -> Response:
    """Handle batch request."""
    try:
        return await rag_api_handler.batch(request)
    except BadRequestError as e:
        logger.error(
            f"Error processing KB file invoke request: {e}",
            exc_info=True,
        )
        openai_bad_request_message = (
            "Your request was blocked due to triggering our content "
            "management policy. Unfortunately, this conversation cannot "
            "continue. Please modify your prompt and try again."
        )
        raise HTTPException(
            status_code=500,
            detail=openai_bad_request_message,
        )
    except Exception as e:
        logger.error(
            f"Error processing Conversational batch request: {e}",
            exc_info=True,
        )
        raise HTTPException(
            status_code=500,
            detail="An internal server error occurred. Please try again later.",
        )


@router.post(
    f"/{BOT_NAME.lower()}_rag/stream",
    tags=["Conversational RAG"],
    include_in_schema=False,
)
async def bot_rag_stream(
    request: Request,
) -> EventSourceResponse:
    """Handle stream request."""
    try:
        return await rag_api_stream_handler.stream(request)
    except BadRequestError as e:
        logger.error(
            f"Error processing KB file invoke request: {e}",
            exc_info=True,
        )
        openai_bad_request_message = (
            "Your request was blocked due to triggering our content "
            "management policy. Unfortunately, this conversation cannot "
            "continue. Please modify your prompt and try again."
        )
        raise HTTPException(
            status_code=500,
            detail=openai_bad_request_message,
        )
    except Exception as e:
        logger.error(
            f"Error processing Conversational stream request: {e}",
            exc_info=True,
        )
        raise HTTPException(
            status_code=500,
            detail="An internal server error occurred. Please try again later.",
        )


# Here, we show how to populate the documentation for the endpoint.
# Please note that this is done separately from the actual endpoint.
# This happens due to:
# 1. Configurable Runnables have a *dynamic* schema, which means that
#    the shape of the input depends on the config.
#    In this case, the openapi schema is a best effort showing the documentation
#    that will work for the default config (and any non-conflicting configs).
if _PYDANTIC_MAJOR_VERSION == 2:
    # Process additional KB file
    @router.post(
        f"/{BOT_NAME.lower()}_process_kb_file/invoke",
        tags=["File Processing"],
    )
    async def process_kb_file_invoke(
        # Included for documentation purposes
        request: process_kb_file_api_handler.InvokeRequest,
    ) -> process_kb_file_api_handler.InvokeResponse:
        """
        API endpoint used only for single static response from the chain.
        """
        raise NotImplementedError(
            "This endpoint is only used for documentation purposes"
        )

    @router.post(
        f"/{BOT_NAME.lower()}_process_kb_file/batch",
        tags=["File Processing"],
    )
    async def process_kb_file_batch(
        # Included for documentation purposes
        request: process_kb_file_api_handler.BatchRequest,
    ) -> process_kb_file_api_handler.BatchResponse:
        """
        API endpoint used only for batch static response from the chain.
        """
        raise NotImplementedError(
            "This endpoint is only used for documentation purposes"
        )

    @router.post(
        f"/{BOT_NAME.lower()}_process_kb_file/stream",
        tags=["File Processing"],
    )
    async def process_kb_file_stream(
        # Included for documentation purposes
        request: process_kb_file_api_stream_handler.StreamRequest,
    ) -> EventSourceResponse:
        """
        API endpoint used only for single streaming response from the chain.
        """
        raise NotImplementedError(
            "This endpoint is only used for documentation purposes"
        )

    # Delete additional KB File
    @router.post(
        f"/{BOT_NAME.lower()}_purge_kb_files/invoke",
        tags=["File Processing"],
    )
    async def purge_kb_files_invoke(
        # Included for documentation purposes
        request: purge_kb_files_api_handler.InvokeRequest,
    ) -> purge_kb_files_api_handler.InvokeResponse:
        """
        API endpoint used only for single static response from the chain.
        """
        raise NotImplementedError(
            "This endpoint is only used for documentation purposes"
        )

    # Process User File
    @router.post(
        f"/{BOT_NAME.lower()}_process_file/invoke",
        tags=["File Processing"],
    )
    async def process_user_file_invoke(
        # Included for documentation purposes
        request: process_user_file_api_handler.InvokeRequest,
    ) -> process_user_file_api_handler.InvokeResponse:
        """
        API endpoint used only for single static response from the chain.
        """
        raise NotImplementedError(
            "This endpoint is only used for documentation purposes"
        )

    @router.post(
        f"/{BOT_NAME.lower()}_process_file/batch",
        tags=["File Processing"],
    )
    async def process_user_file_batch(
        # Included for documentation purposes
        request: process_user_file_api_handler.BatchRequest,
    ) -> process_user_file_api_handler.BatchResponse:
        """
        API endpoint used only for batch static response from the chain.
        """
        raise NotImplementedError(
            "This endpoint is only used for documentation purposes"
        )

    @router.post(
        f"/{BOT_NAME.lower()}_process_file/stream",
        tags=["File Processing"],
    )
    async def process_user_file_stream(
        # Included for documentation purposes
        request: process_user_file_api_stream_handler.StreamRequest,
    ) -> EventSourceResponse:
        """
        API endpoint used only for single streaming response from the chain.
        """
        raise NotImplementedError(
            "This endpoint is only used for documentation purposes"
        )

    # Delete User Files
    @router.post(
        f"/{BOT_NAME.lower()}_purge_files/invoke",
        tags=["File Processing"],
    )
    async def purge_user_files_invoke(
        # Included for documentation purposes
        request: purge_user_files_api_handler.InvokeRequest,
    ) -> purge_user_files_api_handler.InvokeResponse:
        """
        API endpoint used only for single static response from the chain.
        """
        raise NotImplementedError(
            "This endpoint is only used for documentation purposes"
        )

    # Topic Summary
    @router.post(
        f"/{BOT_NAME.lower()}_ts/invoke",
        tags=["Topic Summary"],
    )
    async def bot_ts_invoke(
        # Included for documentation purposes
        request: topic_api_handler.InvokeRequest,
    ) -> topic_api_handler.InvokeResponse:
        """
        API endpoint used only for single static response from the bot.
        """
        raise NotImplementedError(
            "This endpoint is only used for documentation purposes"
        )

    @router.post(
        f"/{BOT_NAME.lower()}_ts/batch",
        tags=["Topic Summary"],
    )
    async def bot_ts_batch(
        # Included for documentation purposes
        request: topic_api_handler.BatchRequest,
    ) -> topic_api_handler.BatchResponse:
        """
        API endpoint used only for batch static response from the bot.
        """
        raise NotImplementedError(
            "This endpoint is only used for documentation purposes"
        )

    @router.post(
        f"/{BOT_NAME.lower()}_ts/stream",
        tags=["Topic Summary"],
    )
    async def bot_ts_stream(
        # Included for documentation purposes
        request: topic_api_handler.StreamRequest,
    ) -> EventSourceResponse:
        """
        API endpoint used only for single streaming response from the bot.
        """
        raise NotImplementedError(
            "This endpoint is only used for documentation purposes"
        )

    # Conversational RAG
    @router.post(
        f"/{BOT_NAME.lower()}_rag/invoke",
        tags=["Conversational RAG"],
    )
    async def bot_rag_invoke(
        # Included for documentation purposes
        request: rag_api_handler.InvokeRequest,
    ) -> rag_api_handler.InvokeResponse:
        """
        API endpoint used only for single static response from the bot.
        """
        raise NotImplementedError(
            "This endpoint is only used for documentation purposes"
        )

    @router.post(
        f"/{BOT_NAME.lower()}_rag/batch",
        tags=["Conversational RAG"],
    )
    async def bot_rag_batch(
        # Included for documentation purposes
        request: rag_api_handler.BatchRequest,
    ) -> rag_api_handler.BatchResponse:
        """
        API endpoint used only for batch static response from the bot.
        """
        raise NotImplementedError(
            "This endpoint is only used for documentation purposes"
        )

    @router.post(
        f"/{BOT_NAME.lower()}_rag/stream",
        tags=["Conversational RAG"],
    )
    async def bot_rag_stream(
        # Included for documentation purposes
        request: rag_api_stream_handler.StreamRequest,
    ) -> EventSourceResponse:
        """
        API endpoint used only for single streaming response from the bot.
        """
        raise NotImplementedError(
            "This endpoint is only used for documentation purposes"
        )
