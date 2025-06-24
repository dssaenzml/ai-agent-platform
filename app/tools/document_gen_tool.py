
import logging

from typing import Any, Dict, Optional, Type

from pydantic import BaseModel

from langchain_core.callbacks import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)
from langchain_core.tools import BaseTool, ToolException

from .tool_wrapper.document_gen_tool_wrapper import (
    DocumentGeneratorToolWrapper
)

from ..model.file_gen_model import WordDocumentGeneratorInput

from ..vector_db.utils import KnowledgeBaseManager

logger = logging.getLogger(__name__)


class DocumentGeneratorTool(BaseTool):
    """
    Tool for generating documents based on a given input.

    This tool uses a document generation template to create documents based 
    on provided input. The generated document is returned as a base64 
    encoded string.

    Attributes:
        name: The name of the tool.
        description: A brief description of the tool's functionality.
        args_schema: The schema for the input arguments.
        return_direct: Whether the tool should return the result directly.
        tool_wrapper: The wrapper for the document generation tool.
    """
    name: str = "GenerateDocumentQuery"
    description: str = (
        "useful for when you need to create a document using a document "
        "generator"
        )
    args_schema: Type[BaseModel] = WordDocumentGeneratorInput
    return_direct: bool = True
    tool_wrapper: Type[DocumentGeneratorToolWrapper] = None
    kbm: Type[KnowledgeBaseManager] = None

    def __init__(
        self, 
        tool_wrapper: Type[DocumentGeneratorToolWrapper], 
        kbm: Type[KnowledgeBaseManager], 
        ):
        super().__init__()
        self.tool_wrapper = tool_wrapper
        self.kbm = kbm

    def generate_document(
        self, 
        document_input: Dict[str, Any], 
        user_id: str, 
        session_id: str, 
        ) -> Optional[str]:
        """
        Generate a document based on the provided input.

        Args:
            document_input: A dictionary containing the document content.

        Returns:
            A base64 encoded string of the generated document.
        """
        try:
            generated_document_base64 = self.tool_wrapper.run(
                document_input=document_input
            )
            
            generated_document_blob_url = self.kbm.upload_user_generated_blob(
                base64_data=generated_document_base64, 
                user_id=user_id, 
                session_id=session_id, 
                )

            logger.info("Document successfully generated.")
            return generated_document_blob_url
        except Exception as e:
            logger.error(f"Unable to generate document due to: {e}")
            raise ToolException(e)
    
    def _run(
        self, 
        document_input: Dict[str, Any], 
        user_id: str, 
        session_id: str, 
        run_manager: Optional[CallbackManagerForToolRun] = None
        ) -> Dict[str, Any]:
        """
        Synchronously generate a document.

        Args:
            document_input: A dictionary containing the document content.
            run_manager: Optional callback manager for handling tool run callbacks.

        Returns:
            A dictionary containing the base64 string of the generated document.
        """
        try:
            generated_document_blob_url = self.generate_document(
                document_input=document_input, 
                user_id=user_id, 
                session_id=session_id, 
            )
            return {
                "status": "success", 
                "generated_document_blob_url": generated_document_blob_url, 
            }
        except ToolException as e:
            logger.error(f"Unable to generate document due to: {e}")
            return {
                "status": "failure", 
                "message": "Generating document failed.", 
            }
        except Exception as e:
            logger.error(f"Unable to generate document due to: {e}")
            return {
                "status": "failure", 
                "message": "Generating document failed.", 
            }

    async def _arun(
        self, 
        document_input: Dict[str, Any], 
        user_id: str, 
        session_id: str, 
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
    ) -> str:
        """
        Asynchronously generate a document.

        Args:
            document_input: A dictionary containing the document content.
            run_manager: Optional callback manager for handling tool run callbacks.

        Returns:
            A dictionary containing the base64 string of the generated document.
        """
        return self._run(
            document_input=document_input, 
            user_id=user_id, 
            session_id=session_id, 
            run_manager=run_manager.get_sync(), 
            )
