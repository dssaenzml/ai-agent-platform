
import logging
from typing import Any, Dict, List, Optional, Type

from pydantic import BaseModel, SecretStr

from langchain_core.callbacks import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)
from langchain_core.tools import BaseTool, ToolException

from .tool_wrapper.snowflake_sql_tool_wrapper import SnowflakeSQLQueryWrapper

from ..model.sql_snowflake_model import SnowflakeSQLQueryInput

logger = logging.getLogger(__name__)


class SnowflakeSQLQueryTool(BaseTool):
    """
    Tool for executing SQL queries on Snowflake based on 
    natural language input.

    This tool connects to a Snowflake database using provided 
    connection parameters and translates natural language queries 
    into SQL queries. It then executes these queries and returns 
    the results. The tool supports both synchronous and asynchronous 
    execution of queries.

    Attributes:
        name: The name of the tool.
        description: A brief description of the tool's functionality.
        args_schema: The schema for the input arguments.
        return_direct: Whether the tool should return the result directly.
        tool_wrapper: The wrapper for the Snowflake SQL query tool.
    """
    name: str = "SnowflakeSQLQuery"
    description: str = (
        "useful for when you need to get an SQL query from natural language."
        )
    args_schema: Type[BaseModel] = SnowflakeSQLQueryInput
    return_direct: bool = True
    tool_wrapper: Type[SnowflakeSQLQueryWrapper] = None

    def __init__(
        self, 
        tool_wrapper: Type[SnowflakeSQLQueryWrapper], 
        ):
        super().__init__()
        self.tool_wrapper = tool_wrapper

    def _run(
        self, 
        messages: List[str], 
        user: Optional[str] = None, 
        oauth_token: Optional[SecretStr] = None, 
        run_manager: Optional[CallbackManagerForToolRun] = None, 
        ) -> Dict[str, Any]:
        """
        Runs the SQL query derived from the natural language input 
        and returns the response.

        Args:
            messages: The natural language query to be translated and executed.
            run_manager: Optional callback manager for handling tool run callbacks.

        Returns:
            A dictionary containing the response from the Snowflake database.
        """
        try:
            response = self.tool_wrapper.run(
                messages=messages, 
                user=user, 
                oauth_token=oauth_token, 
                )
            return response
        except ToolException as e:
            logger.error(f"Unable to generate document due to: {e}")
            return {
                "status": "failure", 
                "message": "Generating document failed."
                }
        except Exception as e:
            logger.error(f"Unable to generate document due to: {e}")
            return {
                "status": "failure", 
                "message": "Generating document failed.", 
                }

    async def _arun(
        self,
        messages: List[str], 
        user: Optional[str] = None, 
        oauth_token: Optional[SecretStr] = None, 
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
    ) -> Dict[str, Any]:
        """
        Executes the SQL query derived from the natural language 
        input asynchronously and returns the response.

        Args:
            messages: The natural language query to be translated and executed.
            run_manager: Optional callback manager for handling tool run callbacks.

        Returns:
            A dictionary containing the response from the Snowflake database.
        """
        return self._run(
            messages=messages, 
            user=user, 
            oauth_token=oauth_token, 
            run_manager=run_manager.get_sync(), 
            )
