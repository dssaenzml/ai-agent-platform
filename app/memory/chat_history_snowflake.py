import os

import json
import time

import logging
from typing import List

from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages import (
    BaseMessage,
    message_to_dict,
    messages_from_dict,
)
from snowflake.connector import connect

logger = logging.getLogger(__name__)

DEFAULT_TABLENAME = os.getenv(
    "SNOWFLAKE_CHAT_HISTORY_TABLENAME",
    "MESSAGES_STORE",
)


class SnowflakeChatMessageHistory(BaseChatMessageHistory):
    """Chat message history that stores history in Snowflake.

    Args:
        connection_parameters: connection string to connect to Snowflake
        user_id: arbitrary key that is used to store the messages
            of a single chat session.
        session_id: arbitrary key that is used to store the messages
            of a single chat session.
        database_name: name of the database to use
        schema_name: name of the schema to use
    """

    def __init__(
        self,
        connection_parameters: dict,
        user_id: str,
        session_id: str,
        message_timereceived: str,
        table_name: str = DEFAULT_TABLENAME,
        max_len_history: int = 15,
        snowflake_connect_timeout: int = 30,
        snowflake_connect_retries: int = 2,
    ):
        self.connection_parameters = connection_parameters
        self.user_id = user_id
        self.session_id = session_id
        self.message_timereceived = message_timereceived
        self.table_name = table_name
        self.max_len_history = max_len_history
        self.snowflake_connect_timeout = snowflake_connect_timeout
        self.snowflake_connect_retries = snowflake_connect_retries

    @property
    def messages(self) -> List[BaseMessage]:  # type: ignore
        """Retrieve the messages from Snowflake"""
        attempt = 0
        while attempt < self.snowflake_connect_retries:
            try:
                with connect(
                    **self.connection_parameters,
                    timeout=self.snowflake_connect_timeout,
                ) as connection:
                    with connection.cursor() as cursor:
                        cursor.execute(
                            "CREATE TABLE IF NOT EXISTS "
                            f"{self.connection_parameters['database']}."
                            f"{self.connection_parameters['schema']}."
                            f"{self.table_name} ( "
                            "HISTORY_ID INT IDENTITY, "
                            "USER_ID STRING, "
                            "SESSION_ID STRING, "
                            "HISTORY VARIANT, "
                            "MESSAGE_TIMERECEIVED TIMESTAMP, "
                            "LOGGING_TIMERECEIVED TIMESTAMP "
                            ");"
                        )
                        cursor.execute(
                            "SELECT HISTORY "
                            "FROM ( SELECT * FROM "
                            f"{self.connection_parameters['database']}."
                            f"{self.connection_parameters['schema']}."
                            f"{self.table_name} "
                            f"WHERE SESSION_ID = '{self.session_id}' "
                            f"AND USER_ID = '{self.user_id}'"
                            "ORDER BY MESSAGE_TIMERECEIVED DESC, "
                            "LOGGING_TIMERECEIVED DESC "
                            f"LIMIT {int(self.max_len_history * 2)} "
                            ") AS subquery "
                            "ORDER BY MESSAGE_TIMERECEIVED ASC, "
                            "LOGGING_TIMERECEIVED ASC"
                            ";"
                        )
                        # Commit the transaction
                        response = cursor.fetchall()

                if response:
                    items = [json.loads(document[0]) for document in response]
                else:
                    items = []

                messages = messages_from_dict(items)
                return messages

            except Exception as error:
                logger.error(error)
                attempt += 1
                time.sleep(2)

    def add_message(self, message: BaseMessage) -> None:
        """Append the message to the record in Snowflake"""
        attempt = 0
        while attempt < self.snowflake_connect_retries:
            try:
                with connect(
                    **self.connection_parameters,
                    timeout=self.snowflake_connect_timeout,
                ) as connection:
                    with connection.cursor() as cursor:
                        cursor.execute(
                            "CREATE TABLE IF NOT EXISTS "
                            f"{self.connection_parameters['database']}."
                            f"{self.connection_parameters['schema']}."
                            f"{self.table_name} ( "
                            "HISTORY_ID INT IDENTITY, "
                            "USER_ID STRING, "
                            "SESSION_ID STRING, "
                            "HISTORY VARIANT, "
                            "MESSAGE_TIMERECEIVED TIMESTAMP, "
                            "LOGGING_TIMERECEIVED TIMESTAMP "
                            ");"
                        )
                        cursor.execute(
                            "INSERT INTO "
                            f"{self.connection_parameters['database']}."
                            f"{self.connection_parameters['schema']}."
                            f"{self.table_name} ( "
                            "SESSION_ID, "
                            "HISTORY, "
                            "USER_ID, "
                            "MESSAGE_TIMERECEIVED, "
                            "LOGGING_TIMERECEIVED "
                            ") SELECT "
                            f"'{self.session_id}', "
                            f"PARSE_JSON( $${json.dumps(message_to_dict(message))}$$ ), "
                            f"'{self.user_id}', "
                            f"'{self.message_timereceived}', "
                            "CURRENT_TIMESTAMP"
                            ";"
                        )
                break
            except Exception as err:
                logger.error(err)
                attempt += 1
                time.sleep(2)

    def clear(self) -> None:
        """Clear session memory from Snowflake"""
        attempt = 0
        while attempt < self.snowflake_connect_retries:
            try:
                with connect(
                    **self.connection_parameters,
                    timeout=self.snowflake_connect_timeout,
                ) as connection:
                    with connection.cursor() as cursor:
                        cursor.execute(
                            "CREATE TABLE IF NOT EXISTS "
                            f"{self.connection_parameters['database']}."
                            f"{self.connection_parameters['schema']}."
                            f"{self.table_name} ( "
                            "HISTORY_ID INT IDENTITY, "
                            "USER_ID STRING, "
                            "SESSION_ID STRING, "
                            "HISTORY VARIANT, "
                            "MESSAGE_TIMERECEIVED TIMESTAMP, "
                            "LOGGING_TIMERECEIVED TIMESTAMP "
                            ");"
                        )
                        cursor.execute(
                            "DELETE FROM "
                            f"{self.connection_parameters['database']}."
                            f"{self.connection_parameters['schema']}."
                            f"{self.table_name} "
                            f"WHERE SESSION_ID = '{self.session_id}' "
                            f"AND USER_ID = '{self.user_id}'"
                            ";"
                        )
                break
            except Exception as err:
                logger.error(err)
                attempt += 1
                time.sleep(2)
