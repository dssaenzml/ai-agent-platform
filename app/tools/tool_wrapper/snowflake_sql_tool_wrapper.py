
import logging

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, SecretStr

import json
import time

from datetime import date
from decimal import Decimal

import requests
from snowflake.connector import connect

from langchain_core.messages import message_to_dict

logger = logging.getLogger(__name__)


class CustomJSONEncoder(json.JSONEncoder):
    """
    Custom JSON Encoder to handle date and Decimal objects.
    """
    def default(self, obj):
        if isinstance(obj, date):
            return obj.isoformat()
        elif isinstance(obj, Decimal):
            return str(obj)
        return super().default(obj)


class SnowflakeSQLQueryWrapper(BaseModel):
    """
    Wrapper for executing SQL queries on Snowflake.

    This class provides methods to connect to Snowflake, send messages,
    and process SQL queries.
    """
    connection_parameters: Dict[str, Any]
    snowflake_connect_timeout: int = 30
    snowflake_connect_retries: int = 2

    def get_snowflake_connect(
        self, 
        user: Optional[str] = None, 
        oauth_token: Optional[SecretStr] = None, 
    ):
        """
        Establishes a connection to Snowflake.

        Args:
            user: Optional user for the Snowflake connection.
            oauth_token: Optional OAuth access token for the Snowflake connection.

        Returns:
            A Snowflake connection object.

        Raises:
            ValueError: If only one of 'user' or 'oauth_token' is provided.
        """
        if (user and not oauth_token) or (not user and oauth_token):
            raise ValueError(
                "Please provide both 'user' and 'oauth_token'."
                )

        if user and oauth_token:
            snowflake_connect = connect(
                user=user,
                authenticator="oauth",
                token=oauth_token.get_secret_value(),
                account=self.connection_parameters['account'],
                host=self.connection_parameters['host'],
                port=443,
                warehouse=self.connection_parameters['warehouse'],
                role=self.connection_parameters['role'], 
                timeout=self.snowflake_connect_timeout
            )
        else:
            snowflake_connect = connect(
                user=self.connection_parameters['user'],
                password=self.connection_parameters['password'],
                account=self.connection_parameters['account'],
                host=self.connection_parameters['host'],
                port=443,
                warehouse=self.connection_parameters['warehouse'],
                role=self.connection_parameters['role'], 
                timeout=self.snowflake_connect_timeout
            )
        return snowflake_connect

    def get_connection_parameters(
        self, 
        user: Optional[str] = None, 
        oauth_token: Optional[SecretStr] = None, 
    ) -> Dict[str, Any]:
        """
        Retrieves the connection parameters for Snowflake.

        Args:
            user: Optional user for the Snowflake connection.
            oauth_token: Optional JWT access token for the Snowflake connection.

        Returns:
            A dictionary containing the connection parameters.

        Raises:
            ValueError: If only one of 'user' or 'oauth_token' is provided.
        """
        if (user and not oauth_token) or (not user and oauth_token):
            raise ValueError(
                "Please provide both 'user' and 'oauth_token'."
                )

        if user and oauth_token:
            connection_parameters = {
                "account": self.connection_parameters['account'], 
                "host": self.connection_parameters['host'], 
                "user": user, 
                "authenticator": "oauth", 
                "token": oauth_token.get_secret_value(), 
                "role": self.connection_parameters['role'], 
                "warehouse": self.connection_parameters['warehouse'], 
                "database": self.connection_parameters['database'], 
                "schema": self.connection_parameters['schema'], 
                "stage": self.connection_parameters['stage'], 
                "semantic_model_file": self.connection_parameters['semantic_model_file']
            }
        else:
            connection_parameters = self.connection_parameters
        return connection_parameters

    def send_message(
        self, 
        messages: List[str], 
        user: Optional[str] = None, 
        oauth_token: Optional[SecretStr] = None, 
        ) -> Dict[str, Any]:
        """
        Executes the SQL query derived from the natural language input 
        and returns the response.

        Args:
            messages: The natural language query to be translated and executed.
            user: Optional user for the Snowflake connection.
            oauth_token: Optional OAuth access token for the Snowflake connection.

        Returns:
            A dictionary containing the response from the Snowflake database.

        Raises:
            Exception: If the request to Snowflake fails.
        """
        snowflake_connect = self.get_snowflake_connect(
            user=user, 
            oauth_token=oauth_token, 
        )
        
        messages = [message_to_dict(m) for m in messages]
        messages = [{
            **m, 'data': {
                **m['data'], 
                'content': json.loads(m['data']['content'])
                }} if m['type'] != 'human' else m
            for m in messages
        ]
        messages = [{
            "role": "user", 
            "content": [{
                "type": "text", 
                "text": m['data']['content']
                }]
            } 
         if m['type'] == 'human' else {
            "role": "analyst", 
            "content": [{
                "type": "text", 
                "text": m['data']['content']['text']
                }, {
                    "type": "sql",
                    "statement": m['data']['content']['sql']
                }]
            } 
         for m in messages]
        
        request_body = {
            "messages": messages,
            "semantic_model_file": (
                f"@{self.connection_parameters['database']}."
                f"{self.connection_parameters['schema']}."
                f"{self.connection_parameters['stage']}/"
                f"{self.connection_parameters['semantic_model_file']}"
                ),
        }
        resp = requests.post(
            url=(
                f"https://{self.connection_parameters['host']}/"
                "api/v2/cortex/analyst/message"
                ),
            json=request_body,
            headers={
                "Authorization": (
                    'Snowflake Token='
                    f'"{snowflake_connect.rest.token}"'
                    ),
                "Content-Type": "application/json",
            },
        )
        request_id = resp.headers.get("X-Snowflake-Request-Id")
        if resp.status_code < 400:
            return {
                **resp.json(), 
                "request_id": request_id, 
                }  # type: ignore[arg-type]
        else:
            raise Exception(
                f"Failed request (id: {request_id}) with status "
                f"{resp.status_code}: {resp.text}"
            )
    
    def process_sql_query(
        self, 
        sql_query: str, 
        request_id: str, 
        user: Optional[str] = None, 
        oauth_token: Optional[SecretStr] = None, 
        ) -> Dict[str, Any]:
        """
        Executes the SQL query on Snowflake and retrieves the result.

        Args:
            sql_query: The SQL query to be executed.
            request_id: The request ID for tracking the query.
            user: Optional user for the Snowflake connection.
            oauth_token: Optional OAuth access token for the Snowflake connection.

        Returns:
            A dictionary containing the results of the SQL query.

        Raises:
            Exception: If the SQL query execution fails.
        """
        connection_parameters = self.get_connection_parameters(
            user=user, 
            oauth_token=oauth_token, 
        )
        attempt = 0
        while attempt < self.snowflake_connect_retries:
            try:
                with connect(
                        **connection_parameters, 
                        timeout=self.snowflake_connect_timeout, 
                        ) as connection:
                    with connection.cursor() as cursor:
                        cursor.execute(sql_query)
                        # Commit the transaction
                        response = cursor.fetchall()
                
                if response:
                    # Convert the response to a list of dictionaries
                    columns = [desc[0] for desc in cursor.description]
                    data = [dict(zip(columns, row)) for row in response]
                else:
                    data = []
                return json.dumps(data, cls=CustomJSONEncoder)
            
            except Exception as error:
                logger.error(
                    f"Failed Snowflake query (id: {request_id}) with error "
                    f"'{error}'"
                    )
                attempt += 1
                time.sleep(2)
        else:
            raise Exception(
                f"Failed Snowflake query (id: {request_id}) with error "
                f"'{error}'"
            )

    def run(
        self, 
        messages: List[str], 
        user: Optional[str] = None, 
        oauth_token: Optional[SecretStr] = None, 
    ) -> str:
        """
        Run the process to generate a document and return it as a base64 
        encoded string.

        Args:
            messages: A list of messages containing the document content.
            user: Optional user for the Snowflake connection.
            oauth_token: Optional OAuth access token for the Snowflake connection.

        Returns:
            A dictionary containing the request ID, human query, SQL query, and SQL result.

        Raises:
            Exception: If any step in the process fails.
        """
        try:
            response = self.send_message(
                messages=messages, 
                user=user, 
                oauth_token=oauth_token, 
                )
            
            request_id = response["request_id"]
            content = response["message"]["content"]
            human_query = [c for c in content if c["type"] == "text"]
            sql_query = [c for c in content if c["type"] == "sql"]
            if len(sql_query) > 0:
                human_query = human_query[0]["text"]
                sql_query = sql_query[0]["statement"]
                sql_result = self.process_sql_query(
                    sql_query=sql_query, 
                    request_id=request_id, 
                    user=user, 
                    oauth_token=oauth_token, 
                )
            else:
                human_query = "We could not interpret your question."
                sql_query = "SELECT * FROM table"
                sql_result = "[]"
            return {
                "request_id": request_id, 
                "human_query": human_query, 
                "sql_query": sql_query, 
                "sql_result": sql_result, 
            }
        except Exception as e:
            logger.error(f"Error in run method: {e}")
            raise e
