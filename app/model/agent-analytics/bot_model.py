from typing import List, Optional, Dict, Any

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


class ConversationOutputChat(BaseModel):
    """Output for the chat endpoint."""

    context: List[dict]
    answer: str
    sql_search: bool
    sql_charts: Dict[str, Any]
