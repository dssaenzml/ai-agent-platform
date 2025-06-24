
import logging

from typing import Any, Dict, Optional, Type

from pydantic import BaseModel

from langchain_core.callbacks import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)
from langchain_core.tools import BaseTool, ToolException

from .tool_wrapper.azure_send_email_api_wrapper import (
    AzureCommunicationServiceSendEmailAPIWrapper
)

from ..model.send_email_model import SendEmailInput

logger = logging.getLogger(__name__)


class AzureCommunicationServiceSendEmailTool(BaseTool):
    """
    Tool for sending emails using Azure Communication Services.

    This tool uses the Azure Communication Services API to send emails 
    with or without attachments. The status of the sent email is returned.

    Attributes:
        name: The name of the tool.
        description: A brief description of the tool's functionality.
        args_schema: The schema for the input arguments.
        return_direct: Whether the tool should return the result directly.
        api_wrapper: The API wrapper for Azure Communication Services.
    """
    name: str = "SendEmailQuery"
    description: str = (
        "useful for when you need to send an email with or "
        "without attachments"
        )
    args_schema: Type[BaseModel] = SendEmailInput
    return_direct: bool = True
    api_wrapper: Type[AzureCommunicationServiceSendEmailAPIWrapper] = None

    def __init__(
        self, 
        api_wrapper: Type[AzureCommunicationServiceSendEmailAPIWrapper], 
        ):
        super().__init__()
        self.api_wrapper = api_wrapper

    def send_email(
        self, 
        message: Dict[str, Any], 
        ) -> Optional[str]:
        """
        Send an email using Azure Communication Services.

        Args:
            message: The email message content.
            attachments: Optional list of attachments to include in the email.

        Returns:
            The status of the sent email.
        """
        try:
            status_response = self.api_wrapper.run(
                message=message, 
                )

            logger.info("Email successfully sent.")
            return status_response
        except Exception as e:
            logger.error(f"Unable to send email due to: {e}")
            raise ToolException(e)
    
    def _run(
        self, 
        message: Dict[str, Any], 
        run_manager: Optional[CallbackManagerForToolRun] = None
        ) -> Dict[str, Any]:
        """
        Synchronously send an email.

        Args:
            message: The email message content.
            attachments: Optional list of attachments to include in the email.
            run_manager: Optional callback manager for handling tool run callbacks.

        Returns:
            A dictionary containing the status of the sent email.
        """
        try:
            status_response = self.send_email(
                message=message, 
                )
            return {
                "status": "success", 
                "status_response": status_response, 
                }
        except ToolException as e:
            logger.error(f"Unable to send email due to: {e}")
            return {
                "status": "failure", 
                "message": "Sending email failed.", 
                }
        except Exception as e:
            logger.error(f"Unable to send email due to: {e}")
            return {
                "status": "failure", 
                "message": "Sending email failed.", 
                }

    async def _arun(
        self, 
        message: Dict[str, Any], 
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
    ) -> str:
        """
        Asynchronously send an email.

        Args:
            message: The email message content.
            attachments: Optional list of attachments to include in the email.
            run_manager: Optional callback manager for handling tool run callbacks.

        Returns:
            A dictionary containing the status of the sent email.
        """
        return self._run(
            message=message, 
            run_manager=run_manager.get_sync(), 
            )
