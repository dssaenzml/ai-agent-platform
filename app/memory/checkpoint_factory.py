import re

import logging
from typing import Callable

from fastapi import HTTPException

from .checkpointer_snowflake import SnowflakeSaver

from ..config import config

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


def create_checkpoint_factory(
    table_name: str,
) -> Callable[[str, str], SnowflakeSaver]:
    """Create a factory that can retrieve checkpoints.

    The checkpoints are keyed by user ID and session ID.

    Args:
        table_name: Table name in database storing the checkpoints.

    Returns:
        A factory that can retrieve checkpoints keyed by user ID and session ID.
    """

    def get_checkpoint(
        user_id: str,
        session_id: str,
    ) -> SnowflakeSaver:
        """Get a checkpoint from a user id and conversation id."""
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

        # Get any checkpoint
        checkpoint_langgraph_format = SnowflakeSaver(
            user_id=user_id,
            session_id=session_id,
            connection_parameters=connection_parameters,
            table_name=table_name,
        )
        return checkpoint_langgraph_format

    return get_checkpoint
