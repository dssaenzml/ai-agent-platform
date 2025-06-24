from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from ..llm_model.azure_llm import (
    helper_model,
)

# System Prompt
system_prompt = (
    "You are a document summarizer assistant. You are provided extracts "
    "from user's uploaded documents and your task is to create a concise "
    "and very detailed summary of all the shared documents by the user. This "
    "summary is going to be used to route the user's queries in an LLM "
    "application, so the summary has to concentrate on the content of "
    "the documents in order to have a perfect routing for the queries."
)

# Prompt
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_prompt),
        (
            "human",
            "Here are the documents' extracts: \n\n {documents} \n\n"
            "Produce a concise summary of them.",
        ),
    ]
)

# Chain
summarizer = prompt | helper_model | StrOutputParser()
