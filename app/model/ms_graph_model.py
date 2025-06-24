from pydantic import BaseModel, Field, SecretStr


class UserProfileMSGraphQueryInput(BaseModel):
    oauth_token: SecretStr = Field(description="The Azure OAuth connection token.")
