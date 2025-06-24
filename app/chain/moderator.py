from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from ..llm_model.azure_llm import grader_model
from ..model.grader_model import GradeModeration

# LLM with function call
structured_grader_model = grader_model.with_structured_output(GradeModeration)

# System Prompt
system_prompt = (
    "You are a grader assessing whether a query needs to be "
    "moderated. You are part of an LLM-based chat application. You "
    "are given a chat history and the latest user query, "
    "which might reference context in the chat history. The query comes "
    "from employees of the enterprise organization based on the organization guidelines "
    "and the LLM purpose. The user might also share an image, from which "
    "you are given any relevant contextual information.\n\n"
    "Current timestamp: {timestamp}\n"
    "Enterprise guidelines and LLM purpose: \n\n {enterprise_context}\n\n"
    "Criteria for Moderation:\n"
    "- A query is considered proper if it adheres to the organization guidelines, "
    "maintains professionalism, and follows basic social etiquette.\n"
    "- A query is considered proper if it is related to productivity "
    "activities such as image generation, web searching, document analysis, "
    "database information retrieval, document information retrieval, "
    "and so forth.\n"
    "- A query is considered not proper if it violates the organization guidelines, "
    "contains inappropriate language, is disrespectful, or does not follow "
    "basic social etiquette.\n\n"
    "Instructions:\n"
    "- If the query is proper, respond with 'yes'.\n"
    "- If the query is not proper, respond with 'no'.\n\n"
    "When considering the image context, if an image is provided, ensure "
    "that the content of the image adheres to the organization guidelines and is "
    "appropriate.\n\n"
    "For image generation prompts, allow queries that request the creation "
    "of images relevant to the organization operations or business lines, such as "
    "'generate an image of the organization' or 'create an image of shipping vessels'.\n\n"
    "Examples:\n"
    "- Proper query: 'Can you help me with the latest project report?'\n"
    "- Proper query: 'Hi!'\n"
    "- Proper query: 'Generate an image of the organization headquarters.'\n"
    "- Proper query: 'summarize this file'\n"
    "- Not proper query: 'This project is stupid, who came up with this?'\n"
    "- Not proper query: 'Generate an inappropriate image.'\n\n"
)

# Prompt
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_prompt),
        MessagesPlaceholder("chat_history"),
        (
            "human",
            "Here is the latest query: \n\n {query} \n\n"
            "Here is the image context: \n\n {image_context}",
        ),
    ]
)

# Chain
query_grader = prompt | structured_grader_model
