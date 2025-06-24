
from pydantic import BaseModel, SecretStr, Field


class UserProfileMSGraphQueryInput(BaseModel):
    oauth_token: SecretStr = Field(
        description="The Azure OAuth connection token."
        )
