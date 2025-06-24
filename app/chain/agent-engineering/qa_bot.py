import logging
import re
from operator import itemgetter
from typing import AsyncIterator

from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import (ConfigurableFieldSpec, RunnableConfig,
                                      RunnableLambda)
from langchain_core.runnables.history import RunnableWithMessageHistory

from ...graph.agent_engineering.graph_bot import app as chat_agent
from ...memory.session_factory import create_session_factory
from ...model.agent_engineering.bot_model import (ConversationInputChat,
                                                  ConversationOutputChat)
from ..utils import (format_username, get_current_timestamp,
                     get_image_type_data, itemgetter_with_default)

logger = logging.getLogger(__name__)

BOT_NAME = "EngineeringAgent"

conversational_chain = (
    (
        {
            "query": itemgetter("query"),
            "username": itemgetter("username", "oauth_token")
            | RunnableLambda(format_username),
            "timestamp": RunnableLambda(get_current_timestamp),
            "image_type_data": itemgetter("uploaded_image_blob_url")
            | RunnableLambda(get_image_type_data),
            "web_search": itemgetter("web_search"),
        }
        | RunnableWithMessageHistory(
            chat_agent,
            create_session_factory(
                table_name=f"{re.sub('-', '_', BOT_NAME).upper()}_MESSAGES_STORE",
                max_len_history=10,
            ),
            input_messages_key="query",
            history_messages_key="chat_history",
            output_messages_key="answer",
            history_factory_config=[
                ConfigurableFieldSpec(
                    id="user_id",
                    annotation=str,
                    name="User ID",
                    description="Unique identifier for the user.",
                    default="",
                    is_shared=True,
                ),
                ConfigurableFieldSpec(
                    id="session_id",
                    annotation=str,
                    name="Session ID",
                    description="Unique identifier for the conversation session.",
                    default="test",
                    is_shared=True,
                ),
                ConfigurableFieldSpec(
                    id="message_timereceived",
                    annotation=str,
                    name="Message Timereceived",
                    description="Timestamp when user message was received.",
                    default="",
                    is_shared=True,
                ),
            ],
        )
        | {
            "context": itemgetter("context"),
            "answer": itemgetter("answer") | StrOutputParser(),
            "web_search": itemgetter_with_default("web_search", False),
        }
    )
    .with_types(
        input_type=ConversationInputChat,
        output_type=ConversationOutputChat,
    )
    .with_config(configurable={"recursion_limit": 50})
)

### DUPLICATE THE ABOVE CHAIN SINCE POST-PROCESSING
### ITEMS DOESNT WORK WITH STREAMING
streaming_conversational_chain = (
    (
        {
            "query": itemgetter("query"),
            "username": itemgetter("username", "oauth_token")
            | RunnableLambda(format_username),
            "timestamp": RunnableLambda(get_current_timestamp),
            "image_type_data": itemgetter("uploaded_image_blob_url")
            | RunnableLambda(get_image_type_data),
            "web_search": itemgetter("web_search"),
        }
        | RunnableWithMessageHistory(
            chat_agent,
            create_session_factory(
                table_name=f"{re.sub('-', '_', BOT_NAME).upper()}_MESSAGES_STORE",
                max_len_history=10,
            ),
            input_messages_key="query",
            history_messages_key="chat_history",
            output_messages_key="answer",
            history_factory_config=[
                ConfigurableFieldSpec(
                    id="user_id",
                    annotation=str,
                    name="User ID",
                    description="Unique identifier for the user.",
                    default="",
                    is_shared=True,
                ),
                ConfigurableFieldSpec(
                    id="session_id",
                    annotation=str,
                    name="Session ID",
                    description="Unique identifier for the conversation session.",
                    default="test",
                    is_shared=True,
                ),
                ConfigurableFieldSpec(
                    id="message_timereceived",
                    annotation=str,
                    name="Message Timereceived",
                    description="Timestamp when user message was received.",
                    default="",
                    is_shared=True,
                ),
            ],
        )
    )
    .with_types(
        input_type=ConversationInputChat,
        output_type=ConversationOutputChat,
    )
    .with_config(configurable={"recursion_limit": 50})
)


async def custom_stream(
    input: ConversationInputChat,
    config: RunnableConfig,
) -> AsyncIterator[str]:
    """A custom runnable that can stream content.

    Args:
        input: The input to the graph. See the Input model for more details.

    Yields:
        strings that are streamed to the client.
    """
    async for event in streaming_conversational_chain.astream_events(
        input,
        config,
        version="v2",
    ):
        tags = event.get("tags", [])
        if event["event"] == "on_custom_event":
            data = event["data"]
            if data:
                yield data


conversational_chain_stream = RunnableLambda(custom_stream)
