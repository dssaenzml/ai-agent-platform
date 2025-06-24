
from ..tool_wrapper.snowflake_sql_tool_wrapper import SnowflakeSQLQueryWrapper

from ..snowflake_sql_tool import SnowflakeSQLQueryTool

from ...config import config

connection_parameters = {
    "account": config.SF_MILAHI_ACCOUNT, 
    "host": f"{config.SF_MILAHI_ACCOUNT}.snowflakecomputing.com",  
    "role": config.SF_MILAHI_ROLE, 
    "warehouse": config.SF_MILAHI_WH, 
    "database": config.SF_MILAHI_DB, 
    "schema": config.SF_MILAHI_SCHEMA, 
    "stage": config.SF_MILAHI_STAGE, 
    "semantic_model_file": config.SF_MILAHI_SM, 
}

# Instantiate the SnowflakeSQLQueryTool
tool_wrapper = SnowflakeSQLQueryWrapper(
    connection_parameters=connection_parameters
    )

# Instantiate the SnowflakeSQLQueryTool
tool = SnowflakeSQLQueryTool(tool_wrapper=tool_wrapper)

# from langchain_core.messages import HumanMessage
# from pydantic import SecretStr

# from dotenv import load_dotenv
# load_dotenv('.dev_env')

# query="what is the total volume by business unit?"
# query="distinct business unit"
# oauth_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsIng1dCI6IllUY2VPNUlKeXlxUjZqekRTNWlBYnBlNDJKdyIsImtpZCI6IllUY2VPNUlKeXlxUjZqekRTNWlBYnBlNDJKdyJ9.eyJhdWQiOiJhcGk6Ly85MDhmMTk2OC1mYTI1LTRiODMtODNiNi04ODg0YmI5ZGMzOTMiLCJpc3MiOiJodHRwczovL3N0cy53aW5kb3dzLm5ldC8zYjYxODQ2My05MzUyLTRmYTQtYTY3Yy0xMTJkYTI4MzdjMjkvIiwiaWF0IjoxNzM3Njk5MzAzLCJuYmYiOjE3Mzc2OTkzMDMsImV4cCI6MTczNzcwMzU1MywiYWNyIjoiMSIsImFpbyI6IkFWUUFxLzhaQUFBQW43aDVNWk1KNERFYWhhdWFPVUg1RlFUQ0pKclcrUDBXREtvekpZb0hHb0dxeXhJVXV6THJoZDBqbHVBdkNxK1Y1M1c3bmtKTFBTL0F3dExod3NBSDc0aGZVK1VLQU1GSkNEQkVzQlRFazNrPSIsImFtciI6WyJwd2QiLCJtZmEiXSwiYXBwaWQiOiJlYzRjYWI3NS1jNWNiLTQ4NTYtYjAyZC1hYTBlNjI5MzM4NDEiLCJhcHBpZGFjciI6IjAiLCJmYW1pbHlfbmFtZSI6IlNhZW56IiwiZ2l2ZW5fbmFtZSI6IkRpZWdvIiwiaXBhZGRyIjoiMTk1LjIyOS4yNTQuNDEiLCJuYW1lIjoiRGllZ28gU2FlbnoiLCJvaWQiOiI4MjExNWUwMC1mMjgyLTRiZWEtOGM4Mi1hMDUwYjNlNWUzMDMiLCJvbnByZW1fc2lkIjoiUy0xLTUtMjEtMzMyNTk0NDY2My0zMzE4ODg2MDkwLTE0NzQ2OTg5OTgtNTg2ODciLCJyaCI6IjEuQVY4QVk0UmhPMUtUcEUtbWZCRXRvb044S1dnWmo1QWwtb05MZzdhSWhMdWR3NU5mQUVaZkFBLiIsInNjcCI6InNlc3Npb246cm9sZS1hbnkiLCJzaWQiOiJiZjRlNTcwOC05ZDcxLTRiYjItYmEzZS0zNzg5OGY2OWIwZTYiLCJzdWIiOiJYRmxrS045MVVYOEtUZHRiazRFX21KbEtnRm1pUGU2UlJDV0M1T080RXNJIiwidGlkIjoiM2I2MTg0NjMtOTM1Mi00ZmE0LWE2N2MtMTEyZGEyODM3YzI5IiwidW5pcXVlX25hbWUiOiJkaWVnby5zYWVuekBtYXF0YS5jb20iLCJ1cG4iOiJkaWVnby5zYWVuekBtYXF0YS5jb20iLCJ1dGkiOiJTSXBKUTZPZHpFU0FMRXg4MG5FWEFBIiwidmVyIjoiMS4wIn0.FMr9_8LvGVjsC77iboPwBJYDZgJ2RWdF2qduzEuquA5cBOoe-H6focaXWJHGB5bvLfDtK82CUGhS1IqhlethMVoOVH6YCxC4Os1sZ37cn0nwy9V5Te2hBNoDv7Ci55Fbh96V3tYbS7lT20DCEEK5yw6s6k5hyrRMRbPN64jDTSdS70zjolQCumXy24bHicDUKJYqWjflzx_knLx6Fk0Yxp_f7wsfZjPizmuj_ou6toSy4YHts9USGqTRDvYFKayyBF8gV5phXA5FdWxGFVXeYfNUm-rY1enc3k1nCxPZQHnpNrcW6rEqRm9Yqly0jr7H-2V5J96coHATe3W9CcDqfA"
# oauth_token = SecretStr(oauth_token)

# response = tool_wrapper.run(
#     messages=[HumanMessage(content=query)], 
#     user = "diego.saenz@maqta.com", 
#     oauth_token = oauth_token, 
# )
