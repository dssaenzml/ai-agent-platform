
import logging

from typing import AsyncIterator

from functools import partial

from langchain_core.runnables import RunnableLambda
from langchain_core.runnables import RunnableConfig

from ..process_file import _process_file

from ...model.vectordb_file_model import (
    KBFileProcessingRequest as FileProcessingRequest,
    KBFileProcessingOutput as FileProcessingOutput,
)

from ...vector_db.agent_general import kbm

logger = logging.getLogger(__name__)

process_file = RunnableLambda(
    partial(_process_file, kbm=kbm)
).with_types(
    input_type=FileProcessingRequest,
    output_type=FileProcessingOutput
    )


async def custom_stream(
    input: FileProcessingRequest,
    config: RunnableConfig,
    ) -> AsyncIterator[str]:
    """A custom runnable that can stream content.

    Args:
        input: The input to the chain. See the Input model for more details.

    Yields:
        strings that are streamed to the client.
    """
    async for event in process_file.astream_events(
        input,
        config,
        version="v2",
        ):
        tags = event.get("tags", [])
        if event["event"] == "on_custom_event":
            data = event["data"]
            if data:
                yield data


process_file_stream = RunnableLambda(custom_stream)
