import logging
from typing import Any, Dict, Optional, Type

from langchain_core.callbacks import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)
from langchain_core.tools import BaseTool, ToolException
from pydantic import BaseModel

from ..model.file_gen_model import PDFDocumentGeneratorInput
from ..vector_db.utils import KnowledgeBaseManager
from .tool_wrapper.pdf_gen_tool_wrapper import PDFGeneratorToolWrapper

logger = logging.getLogger(__name__)


class PDFGeneratorTool(BaseTool):
    """
    Tool for generating PDFs based on a given input.

    This tool uses an HTML input to create PDFs based on provided input.
    The generated PDF is returned as a base64 encoded string.

    Attributes:
        name: The name of the tool.
        description: A brief description of the tool's functionality.
        args_schema: The schema for the input arguments.
        return_direct: Whether the tool should return the result directly.
        tool_wrapper: The wrapper for the PDF generation tool.
        kbm: The knowledge base manager for handling blob storage.
    """

    name: str = "GeneratePDFQuery"
    description: str = (
        "useful for when you need to create a PDF using an HTML input " "generator"
    )
    args_schema: Type[BaseModel] = PDFDocumentGeneratorInput
    return_direct: bool = True
    tool_wrapper: Type[PDFGeneratorToolWrapper] = None
    kbm: Type[KnowledgeBaseManager] = None

    def __init__(
        self,
        tool_wrapper: Type[PDFGeneratorToolWrapper],
        kbm: Type[KnowledgeBaseManager],
    ):
        super().__init__()
        self.tool_wrapper = tool_wrapper
        self.kbm = kbm

    def generate_pdf(
        self,
        html_input: str,
        user_id: str,
        session_id: str,
    ) -> Optional[str]:
        """
        Generate a PDF based on the provided input.

        Args:
            html_input: A string containing the HTML content.
            user_id: The ID of the user generating the PDF.
            session_id: The session ID for the PDF generation.

        Returns:
            A URL to the generated PDF.
        """
        try:
            generated_pdf_base64 = self.tool_wrapper.run(html_input=html_input)

            generated_pdf_blob_url = self.kbm.upload_user_generated_blob(
                base64_data=generated_pdf_base64,
                user_id=user_id,
                session_id=session_id,
            )

            logger.info("PDF successfully generated.")
            return generated_pdf_blob_url
        except Exception as e:
            logger.error(f"Unable to generate PDF due to: {e}")
            raise ToolException(e)

    def _run(
        self,
        html_input: str,
        user_id: str,
        session_id: str,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> Dict[str, Any]:
        """
        Synchronously generate a PDF.

        Args:
            html_input: A string containing the HTML content.
            user_id: The ID of the user generating the PDF.
            session_id: The session ID for the PDF generation.
            run_manager: Optional callback manager for handling tool run callbacks.

        Returns:
            A dictionary containing the base64 string of the generated PDF.
        """
        try:
            generated_pdf_blob_url = self.generate_pdf(
                html_input=html_input,
                user_id=user_id,
                session_id=session_id,
            )
            return {
                "status": "success",
                "generated_pdf_blob_url": generated_pdf_blob_url,
            }
        except ToolException as e:
            logger.error(f"Unable to generate PDF due to: {e}")
            return {"status": "failure", "message": "Generating PDF failed."}
        except Exception as e:
            logger.error(f"Unable to generate PDF due to: {e}")
            return {"status": "failure", "message": "Generating PDF failed."}

    async def _arun(
        self,
        html_input: str,
        user_id: str,
        session_id: str,
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
    ) -> str:
        """
        Asynchronously generate a PDF.

        Args:
            html_input: A string containing the HTML content.
            user_id: The ID of the user generating the PDF.
            session_id: The session ID for the PDF generation.
            run_manager: Optional callback manager for handling tool run callbacks.

        Returns:
            A dictionary containing the base64 string of the generated PDF.
        """
        return self._run(
            html_input=html_input,
            user_id=user_id,
            session_id=session_id,
            run_manager=run_manager.get_sync(),
        )
