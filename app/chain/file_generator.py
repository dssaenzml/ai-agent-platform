
from langchain_core.prompts import (
    ChatPromptTemplate,
    MessagesPlaceholder
)
from langchain_core.output_parsers import StrOutputParser

from ..llm_model.azure_llm import (
    long_helper_model as llm_model, 
    )

# System Prompt
system_prompt = (
    "You are an HTML writer that generates HTML strings for document "
    "generation based on the user's requirements. You have access to "
    "the chat history and any provided images. Your task is to create "
    "an HTML string that satisfies the user's requirements using the "
    "available information. Ensure that the HTML follows AD Ports Group "
    "(the organization) guidelines and the specific LLM application context.\n\n"
    "The HTML string should include proper formatting details for "
    "document generation, such as titles, subtitles, headings, "
    "subheadings, and body content. Look at the input and try to reason "
    "about the underlying semantic intent/meaning from the user's "
    "requirements for the document. Your HTML output should be detailed, "
    "descriptive, and contextually rich to ensure high-quality results. "
    "You should only provide the HTML string. Your response must follow "
    "the blow example:\n\n"
    "<!DOCTYPE html>\n"
    "<html>\n"
    "...your generated content given the user's requirement goes here...\n"
    "</html>\n\n"
    "Do not reply to the user, or add comments, sidenotes, feedback, or "
    "any other input besides the HTML string.\n\n"
    "Current timestamp: \n\n {timestamp} \n\n"
    "The user's name: \n\n {username} \n\n"
    "Enterprise guidelines and LLM purpose: \n\n {enterprise_context} \n\n"
    "When considering the image context, if an image is provided, ensure "
    "that the content of the image is taken into account when generating "
    "the HTML string."
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
            "Generate an HTML string for the required document.",
        ),
    ]
)

# Chain
html_writer = prompt | llm_model | StrOutputParser()
