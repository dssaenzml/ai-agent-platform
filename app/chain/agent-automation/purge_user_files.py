import logging

from functools import partial

from langchain_core.runnables import RunnableLambda

from ..purge_files import _purge_files

from ...model.vectordb_file_model import (
    UserFilePurgingRequest as FilePurgingRequest,
    UserFilePurgingOutput as FilePurgingOutput,
)

from ...vector_db.agent_automation import kbm

logger = logging.getLogger(__name__)

purge_files = RunnableLambda(partial(_purge_files, kbm=kbm, user_doc=True)).with_types(
    input_type=FilePurgingRequest, output_type=FilePurgingOutput
)
