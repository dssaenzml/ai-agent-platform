import logging

from functools import partial

from langchain_core.runnables import RunnableLambda

from ..purge_files import _purge_files

from ...model.vectordb_file_model import (
    KBFilePurgingRequest as FilePurgingRequest,
    KBFilePurgingOutput as FilePurgingOutput,
)

from ...vector_db.agent_realestate import kbm

logger = logging.getLogger(__name__)

purge_files = RunnableLambda(partial(_purge_files, kbm=kbm)).with_types(
    input_type=FilePurgingRequest, output_type=FilePurgingOutput
)
