
from langchain_core.prompts import (
    ChatPromptTemplate,
    MessagesPlaceholder
)
from langchain_core.output_parsers import StrOutputParser

from ..llm_model.azure_llm import (
    helper_model as llm_model, 
    )

# System Prompt
system_prompt = (
    "You are an AI assistant that generates filenames from HTML strings. "
    "The HTML string describes the content of the file, and your task is "
    "to create a concise and meaningful filename based on the content "
    "provided in the HTML. The filename should be in lowercase, use hyphens "
    "instead of spaces, and do not provide any file extension. Do not "
    "answer any question, or comment that filename, or provide any extra "
    "output besides the filename. You are given the current timestamp and "
    "additional information of the guidelines and purpose of the application "
    "you are part of.\n\n"
    "Current timestamp: \n\n {timestamp} \n\n"
    "Enterprise guidelines and LLM purpose: \n\n {enterprise_context} \n\n"
    "For example:\n"
    "HTML: <html><head><title>Monthly Report</title></head><body><h1>Report "
    "for January</h1></body></html>\n"
    "Filename: monthly-report-january\n\n"
    "HTML: <html><head><title>Project Plan</title></head><body><h1>Plan for "
    "Project X</h1></body></html>\n"
    "Filename: project-plan-project-x\n\n"
    "Please generate a filename based on the following HTML input:"
)

# Prompt
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_prompt),
        (
            "human",
            "{html_input}",
        ),
    ]
)

# HTML file Chain
html_filename_generator = prompt | llm_model | StrOutputParser()

# System Prompt
system_prompt = (
    "You are an AI assistant that generates filenames based on the user's "
    "request. The user has requested a file to be generated and we need to "
    "create a concise and meaningful filename based on the content provided "
    "during the chat history and the latest inputs from the user. The "
    "filename should be in lowercase, use hyphens "
    "instead of spaces, and do not provide any file extension. Do not "
    "answer any question, or comment that filename, or provide any extra "
    "output besides the filename. You are given the current timestamp and "
    "additional information of the guidelines and purpose of the application "
    "you are part of.\n\n"
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
            "Here is the image context: \n\n {image_context} \n\n"
            "Generate a filename given the provided context.",
        ),
    ]
)

# Chain
filename_generator = prompt | llm_model | StrOutputParser()
