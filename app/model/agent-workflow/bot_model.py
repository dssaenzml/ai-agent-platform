
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
    snowflake_oauth_token: str = Field(
        ..., 
        description="The Snowflake OAuth connection token.",
        extra={"widget": {"type": "chat", "input": "oauth_token"}},
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
    sql_search: bool
    web_search: bool