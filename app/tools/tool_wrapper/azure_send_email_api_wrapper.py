import logging
from typing import Any, Dict, Optional

from azure.communication.email import EmailClient
from pydantic import BaseModel, Field, SecretStr, model_validator
from typing_extensions import Self

logger = logging.getLogger(__name__)


class AzureCommunicationServiceSendEmailAPIWrapper(BaseModel):
    """
    Wrapper for Azure Communication Service email management.

    This class provides methods to send emails and check their status
    using Azure Communication Services.

    Usage instructions:
    1. `pip install azure.communication.email`
    2. Use your Azure Communication Services (ACS) connection string.
    """

    client: Any = None  #: :meta private:
    acs_connection_string: Optional[SecretStr] = Field(
        alias="connection_string",
    )

    @model_validator(mode="after")
    def validate_environment(self) -> Self:
        """
        Validate that the ACS connection string exists in the environment.

        :raises ValueError: If the ACS connection string is not provided.
        :return: The instance of the class.
        """
        if not self.acs_connection_string:
            raise ValueError(
                "Azure Communication Services connection string is missing. "
                "Please provide it via the `connection_string` parameter."
            )
        return self

    def initialize_client(self) -> None:
        """Initialize the Azure Communication Services Email Client.

        This method sets up the EmailClient using the provided ACS
        connection string.
        """
        if not self.client:
            self.client = EmailClient.from_connection_string(
                self.acs_connection_string.get_secret_value()
            )

    def send_email(
        self,
        message: Dict[str, Any],
    ) -> str:
        """Send an email using Azure Communication Services.

        :param message: The email message content.
        :param attachments: Optional list of attachments.
        :return: The message ID of the sent email.
        """
        self.initialize_client()

        poller = self.client.begin_send(message)
        result = poller.result()
        return result.message_id

    def check_email_status(self, message_id: str) -> None:
        """Check the status of the sent email.

        :param message_id: The ID of the sent email message.
        :return: The status of the email.
        """
        try:
            status_response = self.client.get_send_status(message_id)
            return status_response.status
        except Exception as e:
            print(f"Failed to get email status: {e}")

    def run(
        self,
        message: Dict[str, Any],
    ) -> str:
        """Run the process to send an email and check its status.

        :param message: The email message content.
        :param attachments: Optional list of attachments.
        :return: The status of the sent email.
        """
        try:
            message_id = self.send_email(
                message=message,
            )
            message_status = self.check_email_status(message_id)
            return message_status
        except Exception as e:
            raise e
