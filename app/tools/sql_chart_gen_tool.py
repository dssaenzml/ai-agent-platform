import logging
from typing import Any, Dict, Optional, Type

from langchain_core.callbacks import (AsyncCallbackManagerForToolRun,
                                      CallbackManagerForToolRun)
from langchain_core.tools import BaseTool, ToolException
from pydantic import BaseModel

from ..model.file_gen_model import SQLChartGenerationInput
from ..vector_db.utils import KnowledgeBaseManager
from .tool_wrapper.sql_chart_gen_tool_wrapper import \
    SQLChartGeneratorToolWrapper

logger = logging.getLogger(__name__)


class SQLChartGeneratorTool(BaseTool):
    """
    Tool for generating charts based on a given SQL result.

    This tool uses the SQLChartGeneratorToolWrapper to generate charts
    based on provided SQL results. The generated chart is provided
    through a URL.

    Attributes:
        name: The name of the tool.
        description: A brief description of the tool's functionality.
        args_schema: The schema for the input arguments.
        return_direct: Tool should return the result directly.
    """

    name: str = "SQLChartGenerator"
    description: str = "Useful for generating charts based on a given SQL result."
    args_schema: Type[BaseModel] = SQLChartGenerationInput
    return_direct: bool = True
    tool_wrapper: Type[SQLChartGeneratorToolWrapper] = None
    kbm: Type[KnowledgeBaseManager] = None

    def __init__(
        self,
        tool_wrapper: Type[SQLChartGeneratorToolWrapper],
        kbm: Type[KnowledgeBaseManager],
    ):
        super().__init__()
        self.tool_wrapper = tool_wrapper
        self.kbm = kbm

    def generate_chart(
        self,
        sql_result: str,
        chart_type: str,
        user_id: str,
        session_id: str,
    ) -> Optional[str]:
        """
        Synchronously generates a chart.

        Args:
            sql_result: A JSON string containing the SQL result.
            chart_type: The type of chart to generate ('bar', 'line', or 'pie').
            user_id: The ID of the user requesting the chart.
            session_id: The session ID for the current operation.
            run_manager: Optional callback manager for handling tool run callbacks.

        Returns:
            A dictionary containing the URL pointing to the generated chart.
        """
        try:
            chart_base64 = self.tool_wrapper.run(
                sql_result=sql_result,
                chart_type=chart_type,
            )

            chart_blob_url = self.kbm.upload_user_image_blob(
                base64_data=chart_base64,
                user_id=user_id,
                session_id=session_id,
            )

            logger.info("Chart generated successfully.")
            return chart_blob_url
        except Exception as e:
            logger.error(f"Unable to generate chart due to: {e}")
            raise ToolException(e)

    def _run(
        self,
        sql_result: str,
        chart_type: str,
        user_id: str,
        session_id: str,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> Dict[str, Any]:
        """
        Asynchronously generates a chart.

        Args:
            sql_result: A JSON string containing the SQL result.
            chart_type: The type of chart to generate ('bar', 'line', or 'pie').
            user_id: The ID of the user requesting the chart.
            session_id: The session ID for the current operation.
            run_manager: Optional callback manager for handling tool run callbacks.

        Returns:
            A dictionary containing the URL pointing to the generated chart.
        """
        try:
            chart_blob_url = self.generate_chart(
                sql_result=sql_result,
                chart_type=chart_type,
                user_id=user_id,
                session_id=session_id,
            )
            return {
                "status": "success",
                "chart_blob_url": chart_blob_url,
            }
        except ToolException as e:
            logger.error(f"Unable to generate chart due to: {e}")
            return {
                "status": "failure",
                "message": "Chart generation failed.",
            }
        except Exception as e:
            logger.error(f"Unable to generate chart due to: {e}")
            return {
                "status": "failure",
                "message": "Chart generation failed.",
            }

    async def _arun(
        self,
        sql_result: str,
        chart_type: str,
        user_id: str,
        session_id: str,
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
    ) -> Dict[str, Any]:
        """
        Asynchronously generates a chart.

        Args:
            sql_result: A JSON string containing the SQL result.
            chart_type: The type of chart to generate ('bar', 'line', or 'pie').
            user_id: The ID of the user requesting the chart.
            session_id: The session ID for the current operation.
            run_manager: Optional callback manager for handling tool run callbacks.

        Returns:
            A dictionary containing the base64 string of the generated chart.
        """
        return self._run(
            sql_result=sql_result,
            chart_type=chart_type,
            user_id=user_id,
            session_id=session_id,
            run_manager=run_manager.get_sync() if run_manager else None,
        )
