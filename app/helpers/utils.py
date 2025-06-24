import json
import logging
import sys
import time
from datetime import datetime
from typing import Any, Dict
from zoneinfo import ZoneInfo

from fastapi import HTTPException, Request
from snowflake.connector import connect
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from ..config import config

logger = logging.getLogger(__name__)

# get timezone for standard timestamps
tzinfo = ZoneInfo("Asia/Dubai")

connection_parameters = {
    "account": config.SF_MAIN_ACCOUNT,
    "user": config.SF_MAIN_USER,
    "password": config.SF_MAIN_PASSWORD,
    "role": config.SF_MAIN_ROLE,
    "warehouse": config.SF_MAIN_WH,
    "database": config.SF_MAIN_DB,
    "schema": config.SF_MAIN_SCHEMA,
}


async def _per_request_config_modifier(
    config: Dict[str, Any], request: Request
) -> Dict[str, Any]:
    """Update the config"""
    message_timereceived = datetime.now(tzinfo).strftime("%Y-%m-%d %H:%M:%S.%f %Z")
    config = config.copy()
    configurable = config.get("configurable", {})

    try:
        # Parse the request body as a JSON object
        request_data = await request.json()

        # Get the "username" value from the input data
        user_id = request_data.get("input", {}).get("username", None)

        if user_id is None:
            error_message = "No username found. Please set "
            "a value in 'username'."
            logger.error(error_message)
            raise HTTPException(
                status_code=400,
                detail=error_message,
            )

        configurable["user_id"] = user_id
        configurable["message_timereceived"] = message_timereceived
        configurable["recursion_limit"] = 50
        config["configurable"] = configurable
        return config

    except Exception as error_message:
        logger.error(error_message)
        raise HTTPException(
            status_code=500,
            detail=f"Error processing request: {str(error_message)}",
        )


def _per_avatar_request_config_modifier(
    config: Dict[str, Any], request: Request
) -> Dict[str, Any]:
    """Update the config"""
    message_timereceived = datetime.now(tzinfo)
    message_timereceived = message_timereceived.strftime("%Y-%m-%d %H:%M:%S.%f %Z")
    config = config.copy()
    configurable = config.get("configurable", {})

    try:
        configurable["user_id"] = "avatar.rag@example.com"
        configurable["message_timereceived"] = message_timereceived
        config["configurable"] = configurable

        return config

    except Exception as error_message:
        logger.error(error_message)
        raise HTTPException(
            status_code=500,
            detail=f"Error processing request: {str(error_message)}",
        )


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app,
        snowflake_logging_table_name: str = "AI_AGENT_API_REQUESTS",
        snowflake_connect_timeout: int = 30,
        snowflake_connect_retries: int = 2,
    ):
        super().__init__(app)
        self.snowflake_logging_table_name = snowflake_logging_table_name
        self.connection_parameters = connection_parameters
        self.snowflake_connect_timeout = snowflake_connect_timeout
        self.snowflake_connect_retries = snowflake_connect_retries

    async def log(self, request_json: str, message_timereceived: str):
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
                            f"{self.snowflake_logging_table_name} ( "
                            "REQUEST_DETAILS VARIANT, "
                            "MESSAGE_TIMERECEIVED TIMESTAMP, "
                            "LOGGING_TIMERECEIVED TIMESTAMP "
                            ");"
                        )
                        cursor.execute(
                            "INSERT INTO "
                            f"{self.connection_parameters['database']}."
                            f"{self.connection_parameters['schema']}."
                            f"{self.snowflake_logging_table_name} ( "
                            "REQUEST_DETAILS, "
                            "MESSAGE_TIMERECEIVED, "
                            "LOGGING_TIMERECEIVED "
                            ") SELECT "
                            f"PARSE_JSON( $${request_json}$$ ), "
                            f"'{message_timereceived}', "
                            "CURRENT_TIMESTAMP"
                            ";"
                        )
                break

            except Exception as error:
                logger.error(error)
                attempt += 1
                time.sleep(2)

    async def dispatch(self, request: Request, call_next):
        message_timereceived = datetime.now(tzinfo).strftime("%Y-%m-%d %H:%M:%S.%f %Z")

        # Log the POST request details
        if request.method == "POST":
            request_data = {
                "method": request.method,
                "url": str(request.url),
                "headers": dict(request.headers),
                "client": request.client.host,
            }

            try:
                body = await request.json()
                request_data["body"] = body
                body_size = sys.getsizeof(body)
                if body_size > 16 * 1024 * 1024:  # 16MB
                    error_message = {
                        "Message Processing Exception": (
                            f"Body too large to log ({body_size} bytes)"
                        )
                    }
                    request_data["body"] = error_message
                else:
                    request_data["body"] = body
            except Exception as e:
                error_message = {"Message Processing Exception": str(e)}
                request_data["body"] = error_message
                logger.error(json.dumps(request_data, indent=2))

            logger.info(json.dumps(request_data, indent=2))
            await self.log(
                json.dumps(request_data),
                message_timereceived,
            )

        try:
            # Process the request
            response = await call_next(request)
            return response
        except Exception as e:
            error_message = {"API Endpoint Exception": str(e)}
            request_data["error"] = error_message
            logger.error(json.dumps(request_data, indent=2))
            await self.log(
                json.dumps(request_data),
                message_timereceived,
            )
            raise HTTPException(
                status_code=500,
                detail=(
                    "An internal server error occurred. " "Please try again later."
                ),
            )
