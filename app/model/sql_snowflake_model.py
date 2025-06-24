from typing import List

from langchain_core.messages import BaseMessage
from pydantic import BaseModel, Field, SecretStr


class SnowflakeSQLQueryInput(BaseModel):
    messages: List[BaseMessage] = Field(
        description="List of human queries and analyst responses"
    )

    user: str = Field(None, description="Snowflake User.")

    oauth_token: SecretStr = Field(
        None, description="The Snowflake JWT connection token."
    )
