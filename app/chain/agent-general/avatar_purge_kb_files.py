import logging
from functools import partial

from langchain_core.runnables import RunnableLambda

from ...model.vectordb_file_model import KBFilePurgingOutput as FilePurgingOutput
from ...model.vectordb_file_model import KBFilePurgingRequest as FilePurgingRequest
from ...vector_db.agent_general import avatar_kbm as kbm
from ..purge_files import _purge_files

logger = logging.getLogger(__name__)

purge_files = RunnableLambda(partial(_purge_files, kbm=kbm)).with_types(
    input_type=FilePurgingRequest, output_type=FilePurgingOutput
)
