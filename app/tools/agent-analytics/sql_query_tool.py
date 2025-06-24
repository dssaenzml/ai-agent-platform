from ...config import config
from ..snowflake_sql_tool import SnowflakeSQLQueryTool
from ..tool_wrapper.snowflake_sql_tool_wrapper import SnowflakeSQLQueryWrapper

connection_parameters = {
    "account": config.SF_KP_ACCOUNT,
    "host": f"{config.SF_KP_ACCOUNT}.snowflakecomputing.com",
    "user": config.SF_KP_USER,
    "password": config.SF_KP_PASSWORD,
    "role": config.SF_KP_ROLE,
    "warehouse": config.SF_KP_WH,
    "database": config.SF_KP_DB,
    "schema": config.SF_KP_SCHEMA,
    "stage": config.SF_KP_STAGE,
    "semantic_model_file": config.SF_KP_SM,
}

# Instantiate the SnowflakeSQLQueryTool
tool_wrapper = SnowflakeSQLQueryWrapper(connection_parameters=connection_parameters)

# Instantiate the SnowflakeSQLQueryTool
tool = SnowflakeSQLQueryTool(tool_wrapper=tool_wrapper)
