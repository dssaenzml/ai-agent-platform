from typing import List, Optional

from pydantic import BaseModel, Field

from langchain_core.documents import Document


class ConversationInputChat(BaseModel):
    """Input for the chat endpoint."""

    query: str = Field(
        ...,
        description="The human query to the chat system.",
        extra={"widget": {"type": "chat", "input": "query"}},
    )
    username: str = Field(
        "user@example.com",
        description="The human username to the chat system.",
        extra={"widget": {"type": "chat", "input": "username"}},
    )
    oauth_token: str = Field(
        None,
        description="The Azure OAuth connection token.",
    )
    uploaded_image_blob_URL: Optional[List[str]] = Field(
        [],
        description=(
            "The list of Azure Blob URL for the image(s) provided by human "
            "to the chat system."
        ),
        extra={"widget": {"type": "chat", "input": "uploaded_image_blob_URL"}},
    )
    web_search: bool = Field(
        False,  # Default value for web_search
        description="The human request to do web search with the chat system.",
        extra={"widget": {"type": "chat", "input": "web_search"}},
    )


class ConversationOutputChat(BaseModel):
    """Output for the chat endpoint."""

    context: List[Document]
    answer: str
    web_search: bool


class FinanceDetails(BaseModel):
    """
    Details required to reply back about Finance Department details on
    policies and procedures.
    """

    cluster: str = Field(
        description="Business cluster within the group, one of the following: "
        "'Corporate', 'Ports', 'Maritime', 'KEZAD',  'Logistics', 'Digital'"
    )
