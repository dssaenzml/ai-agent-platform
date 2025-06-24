
from ..tool_wrapper.user_profile_ms_graph_tool_wrapper import (
    UserProfileMSGraphToolWrapper
    )

from ..user_profile_ms_graph_tool import UserProfileMSGraphTool

# Instantiate the UserProfileMSGraphTool
tool_wrapper = UserProfileMSGraphToolWrapper()

tool = UserProfileMSGraphTool(
    tool_wrapper=tool_wrapper, 
    )
