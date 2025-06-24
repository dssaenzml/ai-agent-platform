
from ..tool_wrapper.sql_chart_gen_tool_wrapper import (
    SQLChartGeneratorToolWrapper
)

from ..sql_chart_gen_tool import (
    SQLChartGeneratorTool
    )

from ...vector_db.agent_analytics import kbm

# Instantiate the SQLChartGeneratorTool
tool_wrapper = SQLChartGeneratorToolWrapper()

tool = SQLChartGeneratorTool(
    tool_wrapper=tool_wrapper, 
    kbm=kbm, 
    )