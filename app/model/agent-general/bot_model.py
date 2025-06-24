from typing import List, Optional

from pydantic import BaseModel, Field


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
    doc_ids: List[str] = Field(
        [],  # Default value for doc_ids
        description="The human document to use along with the chat system.",
        extra={"widget": {"type": "chat", "input": "doc_ids"}},
    )


class ConversationOutputChat(BaseModel):
    """Output for the chat endpoint."""

    context: List[dict]
    answer: str
    web_search: bool
    image_blob_url: str
    pdf_blob_url: str
    pdf_filename: str


class AvatarConversationInputChat(BaseModel):
    """Input for the chat endpoint."""

    input: str = Field(
        ...,
        description="The human query to the chat system.",
        extra={"widget": {"type": "chat", "input": "input"}},
    )


class AvatarConversationOutputChat(BaseModel):
    """Output for the chat endpoint."""

    answer: str


class AudioConversationInputChat(BaseModel):
    """Input for the chat endpoint."""

    query: str = Field(
        ...,
        description="The base64 audio of the human query to the chat system.",
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
    doc_ids: List[str] = Field(
        [],  # Default value for doc_ids
        description="The human document to use along with the chat system.",
        extra={"widget": {"type": "chat", "input": "doc_ids"}},
    )


class AudioConversationOutputChat(BaseModel):
    """Output for the chat endpoint."""

    answer: str
