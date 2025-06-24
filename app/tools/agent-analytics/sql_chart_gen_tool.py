from ...vector_db.agent_analytics import kbm
from ..sql_chart_gen_tool import SQLChartGeneratorTool
from ..tool_wrapper.sql_chart_gen_tool_wrapper import SQLChartGeneratorToolWrapper

# Instantiate the SQLChartGeneratorTool
tool_wrapper = SQLChartGeneratorToolWrapper()

tool = SQLChartGeneratorTool(
    tool_wrapper=tool_wrapper,
    kbm=kbm,
)
