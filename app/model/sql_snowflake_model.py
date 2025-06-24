from typing import List

from pydantic import BaseModel, Field, SecretStr

from langchain_core.messages import BaseMessage


class SnowflakeSQLQueryInput(BaseModel):
    messages: List[BaseMessage] = Field(
        description="List of human queries and analyst responses"
    )

    user: str = Field(None, description="Snowflake User.")

    oauth_token: SecretStr = Field(
        None, description="The Snowflake JWT connection token."
    )
