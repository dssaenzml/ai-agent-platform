from typing import Dict

from pydantic import BaseModel, Field


class ImageGenerationInput(BaseModel):
    query: str = Field(
        description="A detailed description of the image to be generated."
    )
    user_id: str = Field(
        "user@example.com",
        description="The user email address of whom requested the service.",
    )
    session_id: str = Field(
        "test", description="The session id of whom requested the service."
    )


class SQLChartGenerationInput(BaseModel):
    sql_result: str = Field(description="A string with the SQL result data.")
    chart_type: str = Field(
        description=("The desired chart type. Options: " "['bar', 'line', 'pie']"),
        examples=["bar", "line", "pie"],
    )
    user_id: str = Field(
        "user@example.com",
        description="The user email address of whom requested the service.",
    )
    session_id: str = Field(
        "test", description="The session id of whom requested the service."
    )


class WordDocumentGeneratorInput(BaseModel):
    document_input: Dict = Field(
        description="A detailed dictionary of inputs to be passed to a document "
        "generator."
    )


class PDFDocumentGeneratorInput(BaseModel):
    html_input: str = Field(
        description="A detailed string containing the HTML content for the PDF document."
    )
    user_id: str = Field(
        "user@example.com",
        description="The user email address of whom requested the service.",
    )
    session_id: str = Field(
        "test", description="The session id of whom requested the service."
    )
