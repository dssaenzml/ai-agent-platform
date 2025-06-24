import logging
import re
from typing import Callable

from fastapi import HTTPException
from langchain_core.chat_history import BaseChatMessageHistory

from ..config import config
from .chat_history_snowflake import SnowflakeChatMessageHistory

logger = logging.getLogger(__name__)

connection_parameters = {
    "account": config.SF_MAIN_ACCOUNT,
    "user": config.SF_MAIN_USER,
    "password": config.SF_MAIN_PASSWORD,
    "role": config.SF_MAIN_ROLE,
    "warehouse": config.SF_MAIN_WH,
    "database": config.SF_MAIN_DB,
    "schema": config.SF_MAIN_SCHEMA,
}


def _is_valid_user_id(value: str) -> bool:
    """Check if the given string is a valid email address."""
    # Regular expression pattern for a valid email address
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    # Use re.match to check if the email matches the pattern
    return bool(re.match(pattern, value))


def _is_valid_session_id(value: str) -> bool:
    """Check if the session ID is in a valid format."""
    # Use a regular expression to match the allowed characters
    valid_characters = re.compile(r"^[a-zA-Z0-9-_]+$")
    return bool(valid_characters.match(value))


def create_session_factory(
    table_name: str,
    max_len_history: int = 15,
) -> Callable[[str, str, str], BaseChatMessageHistory]:
    """Create a factory that can retrieve chat histories.

    The chat histories are keyed by user ID and session ID.

    Args:
        table_name: Table name in database storing the chat histories.

    Returns:
        A factory that can retrieve chat histories keyed by user ID and session ID.
    """

    def get_session_history(
        user_id: str,
        session_id: str,
        message_timereceived: str,
    ) -> SnowflakeChatMessageHistory:
        """Get a chat history from a user id and conversation id."""
        if not _is_valid_user_id(user_id):
            error_message = (
                f"User ID {user_id} is not in a valid format. "
                "User ID must only contain alphanumeric characters, "
                "hyphens, and underscores."
                "Please include a valid cookie in the request headers "
                "called 'user-id'."
            )
            logger.error(error_message)
            raise HTTPException(
                status_code=400,
                detail=error_message,
            )
        if not _is_valid_session_id(session_id):
            error_message = (
                f"Conversation session ID `{session_id}` is not in a valid format. "
                "Session ID must only contain alphanumeric characters, "
                "hyphens, and underscores."
            )
            logger.error(error_message)
            raise HTTPException(
                status_code=400,
                detail=error_message,
            )

        # Get any chat history
        history_langchain_format = SnowflakeChatMessageHistory(
            user_id=user_id,
            session_id=session_id,
            message_timereceived=message_timereceived,
            connection_parameters=connection_parameters,
            table_name=table_name,
            max_len_history=max_len_history,
        )
        return history_langchain_format

    return get_session_history
