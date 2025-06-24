from typing import Any, Dict

from pydantic import BaseModel, Field


class SendEmailInput(BaseModel):
    message: Dict[str, Any] = Field(
        description="A detailed message of the email to be sent."
    )
