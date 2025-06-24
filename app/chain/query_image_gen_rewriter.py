from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser

from ..llm_model.azure_llm import (
    helper_model,
)

# System Prompt
system_prompt = (
    "You are a query re-writer that converts the last input query "
    "to a better version that is optimized for generating images "
    "using an LLM-based application. You are given a chat history "
    "and the latest user query which might reference context "
    "in the chat history. The query comes from employees at Abu "
    "Dhabi Ports Group (the organization) based on the organization guidelines and the LLM "
    "purpose. The user might also share an image, from which you are "
    "given any relevant information.\n\n"
    "Look at the input and try to reason about the underlying semantic "
    "intent / meaning. Your modified query statement should be detailed, "
    "descriptive, and contextually rich to ensure high-quality image "
    "generation. Avoid sensitive information or personal details. It "
    "should be as general as possible, yet meaningful enough for the "
    "image generator model.\n\n"
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
