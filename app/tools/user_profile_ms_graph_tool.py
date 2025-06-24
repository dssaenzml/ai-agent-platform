import logging

from typing import Any, Dict, Optional, Type

from pydantic import BaseModel, SecretStr

from langchain_core.callbacks import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)
from langchain_core.tools import BaseTool, ToolException

from .tool_wrapper.user_profile_ms_graph_tool_wrapper import (
    UserProfileMSGraphToolWrapper,
)

from ..model.ms_graph_model import UserProfileMSGraphQueryInput

logger = logging.getLogger(__name__)


class UserProfileMSGraphTool(BaseTool):
    """
    Tool for retrieving user company profile information from
    Microsoft Graph API.

    This tool connects to the Microsoft Graph API using provided
    OAuth token and retrieves the user profile information.
    The tool supports both synchronous and asynchronous execution
    of the API call.

    Attributes:
        name: The name of the tool.
        description: A brief description of the tool's functionality.
        args_schema: The schema for the input arguments.
        return_direct: Whether the tool should return the result directly.
    """

    name: str = "MSUserProfileTool"
    description: str = (
        "useful for when you need to retrieve user company profile information"
    )
    args_schema: Type[BaseModel] = UserProfileMSGraphQueryInput
    return_direct: bool = True
    tool_wrapper: Type[UserProfileMSGraphToolWrapper] = None

    def __init__(
        self,
        tool_wrapper: Type[UserProfileMSGraphToolWrapper],
    ):
        super().__init__()
        self.tool_wrapper = tool_wrapper

    def _run(
        self,
        oauth_token: SecretStr,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> Dict[str, Any]:
        """
        Synchronously retrieves the user profile information from
        Microsoft Graph API.

        Args:
            oauth_token: The OAuth token for authenticating with Microsoft Graph API.
            run_manager: Optional callback manager for handling tool run callbacks.

        Returns:
            A dictionary containing the user profile information.
        """
        try:
            response = self.tool_wrapper.run(
                oauth_token=oauth_token,
            )
            return {
                "status": "success",
                "user_profile_details": response,
            }
        except ToolException as e:
            logger.error(f"Unable to retrieve data due to: {e}")
            return {"status": "failure", "message": "Retrieving data failed."}
        except Exception as e:
            logger.error(f"Unable to retrieve data due to: {e}")
            return {"status": "failure", "message": "Retrieving data failed."}

    async def _arun(
        self,
        oauth_token: SecretStr,
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
    ) -> Dict[str, Any]:
        """
        Asynchronously retrieves the user profile information from
        Microsoft Graph API.

        Args:
            oauth_token: The OAuth token for authenticating with Microsoft Graph API.
            run_manager: Optional callback manager for handling tool run callbacks.

        Returns:
            A dictionary containing the user profile information.
        """
        return self._run(
            oauth_token=oauth_token,
            run_manager=run_manager.get_sync(),
        )
