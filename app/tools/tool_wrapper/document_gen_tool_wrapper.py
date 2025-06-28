import base64
import io
import logging
from typing import TYPE_CHECKING, Any, Callable, Dict, Optional

from docx import Document
from pydantic import BaseModel, model_validator
from typing_extensions import Self

if TYPE_CHECKING:
    from docx.document import Document as DocxDocument
else:
    DocxDocument = object  # fallback for runtime

logger = logging.getLogger(__name__)


class DocumentGeneratorToolWrapper(BaseModel):
    """
    Wrapper for generating documents and returning them as base64
    encoded strings.

    This class provides methods to generate a document based on
    provided content and return the document as a base64 encoded string.

    Usage instructions:
    1. `pip install python-docx`
    2. Use the `generate_document` method to create and retrieve the document.
    """

    document_template: Optional[Callable[["DocxDocument", Dict[str, Any]], None]] = None

    @model_validator(mode="after")
    def validate_environment(self) -> Self:
        """
        Validate that the document template is provided.

        :raises ValueError: If the document template is not provided.
        :return: The instance of the class.
        """
        if not self.document_template:
            raise ValueError(
                "Document template is missing. "
                "Please provide it via the `document_template` parameter."
            )
        return self

    def generate_document(
        self,
        document_input: Dict[str, Any],
    ) -> str:
        """
        Create a document using the provided template and input, and return it as a base64 encoded string.

        :param document_input: A dictionary containing the document content.
        :return: The base64 encoded string of the generated document.
        """
        # Create a Document object
        document = Document()

        # Apply the template logic to the document
        self.document_template(document, document_input)

        # Save the document to an in-memory file-like object
        with io.BytesIO() as tmp_file:
            document.save(tmp_file)
            tmp_file.seek(0)
            encoded_string = base64.b64encode(tmp_file.read()).decode("utf-8")

        return encoded_string

    def run(
        self,
        document_input: Dict[str, Any],
    ) -> str:
        """
        Run the process to generate a document and return it as a base64
        encoded string.

        :param document_input: A dictionary containing the document content.
        :return: The base64 encoded string of the generated document.
        """
        try:
            return self.generate_document(document_input)
        except Exception as e:
            raise e
