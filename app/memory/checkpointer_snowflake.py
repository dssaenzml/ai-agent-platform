
import logging

from typing import Any, Dict

import os

import json
import time

from snowflake.connector import connect

logger = logging.getLogger(__name__)

DEFAULT_TABLENAME = os.getenv(
    "SNOWFLAKE_CHECKPOINTER_TABLENAME", 
    "SAVER",
    )


class SnowflakeSaver:
    """Class for storing and managing graph checkpoint objects in Snowflake.

    Args:
        connection_parameters (dict): Connection parameters for Snowflake.
        user_id (str): Unique identifier for the user.
        session_id (str): Unique identifier for the session.
        table_name (str, optional): Name of the table to store checkpoints. Defaults to DEFAULT_TABLENAME.
        snowflake_connect_timeout (int, optional): Timeout for Snowflake connection. Defaults to 30 seconds.
        snowflake_connect_retries (int, optional): Number of retries for Snowflake connection. Defaults to 2.
    """

    def __init__(
        self,
        connection_parameters: dict,
        user_id: str,
        session_id: str,
        table_name: str = DEFAULT_TABLENAME,
        snowflake_connect_timeout: int = 30, 
        snowflake_connect_retries: int = 2, 
    ):
        self.connection_parameters = connection_parameters
        self.user_id = user_id
        self.session_id = session_id
        self.table_name = table_name
        self.snowflake_connect_timeout = snowflake_connect_timeout
        self.snowflake_connect_retries = snowflake_connect_retries
    
    @property
    def _load_checkpoint(self) -> Dict[str, Any]:
        """Retrieve the latest checkpoint from Snowflake.

        Returns:
            Dict[str, Any]: The latest checkpoint data.
        """
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
                            "CHECKPOINT_ID INT IDENTITY, "
                            "USER_ID STRING, "
                            "SESSION_ID STRING, "
                            "CHECKPOINT VARIANT, "
                            "LOGGING_TIMERECEIVED TIMESTAMP "
                            ");"
                            )
                        cursor.execute(
                            "SELECT CHECKPOINT FROM "
                            f"{self.connection_parameters['database']}."
                            f"{self.connection_parameters['schema']}."
                            f"{self.table_name} "
                            f"WHERE SESSION_ID = '{self.session_id}' "
                            f"AND USER_ID = '{self.user_id}'"
                            "ORDER BY LOGGING_TIMERECEIVED DESC "
                            "LIMIT 1;"
                        )
                        # Commit the transaction
                        response = cursor.fetchall()

                if response:
                    items = json.loads(response[0][0])
                else:
                    items = {}

                return items
            
            except Exception as error:
                logger.error(error)
                attempt += 1
                time.sleep(2)

    def add_checkpoint(self, checkpoint: Dict[str, Any]) -> None:
        """Append a new checkpoint to the record in Snowflake.

        Args:
            checkpoint (Dict[str, Any]): The checkpoint data to be added.
        """
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
                            "CHECKPOINT_ID INT IDENTITY, "
                            "USER_ID STRING, "
                            "SESSION_ID STRING, "
                            "CHECKPOINT VARIANT, "
                            "LOGGING_TIMERECEIVED TIMESTAMP "
                            ");"
                            )
                        cursor.execute(
                            "INSERT INTO "
                            f"{self.connection_parameters['database']}."
                            f"{self.connection_parameters['schema']}."
                            f"{self.table_name} ( "
                            "SESSION_ID, "
                            "CHECKPOINT, "
                            "USER_ID, "
                            "LOGGING_TIMERECEIVED "
                            ") SELECT "
                            f"'{self.session_id}', "
                            f"PARSE_JSON( $${json.dumps(checkpoint)}$$ ), "
                            f"'{self.user_id}', "
                            "CURRENT_TIMESTAMP"
                            ";"
                        )
                break
            except Exception as err:
                logger.error(err)
                attempt += 1
                time.sleep(2)

    def clear(self) -> None:
        """Clear all checkpoints for the current session from Snowflake."""
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
                            "CHECKPOINT_ID INT IDENTITY, "
                            "USER_ID STRING, "
                            "SESSION_ID STRING, "
                            "CHECKPOINT VARIANT, "
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
