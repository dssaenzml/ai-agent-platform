
import logging

import io
import base64
from weasyprint import HTML

from pydantic import BaseModel

logger = logging.getLogger(__name__)


class PDFGeneratorToolWrapper(BaseModel):
    """
    Wrapper for generating PDFs and returning them as base64 
    encoded strings.

    This class provides methods to generate a PDF based on 
    provided HTML content and return the PDF as a base64 encoded string.

    Usage instructions:
    1. `pip install weasyprint`
    2. Use the `generate_pdf` method to create and retrieve the PDF.
    """

    def generate_pdf(
        self, 
        html_input: str, 
    ) -> str:
        """
        Create a PDF using the provided HTML input, and return it as a 
        base64 encoded string.

        :param html_input: A string containing the HTML content.
        :return: The base64 encoded string of the generated PDF.
        """
        # Convert the HTML string to a PDF
        pdf = HTML(string=html_input).write_pdf()

        # Save the PDF to an in-memory file-like object
        with io.BytesIO() as tmp_file:
            tmp_file.write(pdf)
            tmp_file.seek(0)
            encoded_string = base64.b64encode(tmp_file.read()).decode('utf-8')

        return encoded_string

    def run(
        self, 
        html_input: str, 
    ) -> str:
        """
        Run the process to generate a PDF and return it as a base64 
        encoded string.

        :param html_input: A string containing the HTML content.
        :return: The base64 encoded string of the generated PDF.
        """
        try:
            return self.generate_pdf(html_input)
        except Exception as e:
            raise e
