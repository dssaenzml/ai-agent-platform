
import logging

from pydantic import BaseModel, SecretStr

import requests

logger = logging.getLogger(__name__)


class UserProfileMSGraphToolWrapper(BaseModel):
    """
    Wrapper for retrieving user profile information from Microsoft Graph API.

    This class provides a method to retrieve user profile information 
    using an OAuth token.

    Usage instructions:
    1. Ensure you have the `requests` library installed.
    2. Use the `get_user_profile` method to retrieve the user profile information.
    """

    def get_user_profile(self, oauth_token: SecretStr) -> dict:
        """
        Retrieves the user profile information from Microsoft Graph API.

        Args:
            oauth_token: The OAuth token for authenticating with Microsoft Graph API.

        Returns:
            A dictionary containing the user profile information.
        """
        graph_api_url = 'https://graph.microsoft.com/v1.0/me'
        headers = {
            'Authorization': 'Bearer ' + oauth_token.get_secret_value(),
        }
        response = requests.get(graph_api_url, headers=headers)
        response.raise_for_status()
        return response.json()

    def run(self, oauth_token: SecretStr) -> dict:
        """
        Run the process to retrieve user profile information.

        Args:
            oauth_token: The OAuth token for authenticating with Microsoft Graph API.

        Returns:
            A dictionary containing the user profile information.
        """
        try:
            return self.get_user_profile(oauth_token)
        except Exception as e:
            logger.error(f"Error in run method: {e}")
            raise e
