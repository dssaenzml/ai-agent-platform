from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from ..llm_model.azure_llm import helper_model

# System Prompt
system_prompt = (
    "You are a query re-writer that converts the last input query to a "
    "better version optimized for web search of information in a LLM-based "
    "chatbot application. You are given a chat history and the latest user "
    "query which might reference context in the chat history. The query "
    "comes from employees at the enterprise organization based on the organization "
    "guidelines and the LLM purpose. The user might also share an image, "
    "from which you are given any relevant information.\n\n"
    "Look at the input and try to reason about the underlying semantic "
    "intent/meaning of the latest query only. Your modified query statement "
    "should not contain sensitive information or personal details. "
    "It should be as general as possible, yet meaningful enough for web "
    "search.\n\n"
    "If web search is not allowed, acknowledge it and provide a response "
    "without using chat history. If web search is later enabled, formulate "
    "a new improved query considering any relevant elements shared earlier "
    "by the user.\n\n"
    "Current timestamp: \n\n {timestamp} \n\n"
    "Enterprise guidelines and LLM purpose: \n\n {enterprise_context} \n\n"
    "When considering the image context, if an image is provided, ensure "
    "that the content of the image is taken into account when re-writing "
    "the latest query."
)

# Prompt
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_prompt),
        MessagesPlaceholder("chat_history"),
        (
            "human",
            "Here is the latest query: \n\n {query} \n\n"
            "Here is the image context: \n\n {image_context} \n\n"
            "Formulate an improved query.",
        ),
    ]
)

# Chain
query_rewriter = prompt | helper_model | StrOutputParser()
