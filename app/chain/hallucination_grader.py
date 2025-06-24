
from langchain_core.prompts import (
    ChatPromptTemplate,
    MessagesPlaceholder
)

from ..llm_model.azure_llm import (
    grader_model
    )

from ..model.grader_model import (
    GradeHallucinations
)

# LLM with function call
structured_grader_model = grader_model.with_structured_output(
    GradeHallucinations, 
    )

# System Prompt
system = (
    "You are a grader assessing whether an LLM generation "
    "is grounded in or supported by the current timestamp, the the organization "
    "guidelines and LLM purpose, a set of retrieved facts under "
    "'Set of facts', the given chat history, the latest user "
    "query which might reference context in the chat history, and, if "
    "provided, the context extracted from the user-shared image.\n\n"
    "Give a binary score 'yes' or 'no'. 'Yes' means that the "
    "answer is grounded in or supported by the mentioned data points. "
    "Additionally, consider the context of the query: if the "
    "response is appropriate and relevant to the query, even "
    "if it is not purely informational, it should be scored as 'yes'.\n\n"
    "Current timestamp: \n\n {timestamp} \n\n"
    "Enterprise guidelines and LLM purpose: \n\n {enterprise_context} \n\n"
    "Set of facts: \n\n {context}"
    )

# Prompt
hallucination_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system),
        MessagesPlaceholder("chat_history"),
        (
            "human", 
            "Here is the latest query: \n\n {query} \n\n"
            "Here is the image context: \n\n {image_context} \n\n"
            "LLM generation: \n\n {generation}",
        ),
    ]
)

# Chain
hallucination_grader = hallucination_prompt | structured_grader_model
