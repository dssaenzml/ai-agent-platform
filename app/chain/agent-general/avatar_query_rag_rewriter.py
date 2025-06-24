
from langchain_core.prompts import (
    ChatPromptTemplate,
    MessagesPlaceholder
)
from langchain_core.output_parsers import StrOutputParser

from ...llm_model.azure_llm import (
    helper_model, 
    )

# System Prompt
system_prompt = (
    "You a query re-writer that converts the lastest query to a better "
    "version that is optimized for vectorstore retrieval in an LLM-based "
    "chatbot application. You are given a chat history and "
    "the latest user query which might reference context in the chat "
    "history. The query comes from visitors of and employees at Abu Dhabi "
    "Ports Group (the organization) based on the organization guidelines and the LLM purpose.\n\n"
    "Look at the input and try to reason about the underlying semantic "
    "intent / meaning.\n\n"
    "Current timestamp: \n\n {timestamp} \n\n"
    "Enterprise guidelines and LLM purpose: \n\n {enterprise_context} \n\n"
)

# Prompt
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_prompt),
        MessagesPlaceholder("chat_history"),
        (
            "human",
            "Here is the latest query: \n\n {query} \n\n"
            "Formulate an improved query.",
        ),
    ]
)

# Chain
query_rewriter = prompt | helper_model | StrOutputParser()
