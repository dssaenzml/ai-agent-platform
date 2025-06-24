
from langchain_core.prompts import ChatPromptTemplate

from ..llm_model.azure_llm import (
    grader_model
    )

from ..model.grader_model import (
    GradeDocuments
)

# LLM with function call
structured_grader_model = grader_model.with_structured_output(GradeDocuments)

# System Prompt
system = (
    "You are a grader assessing relevance of a retrieved document or"
    "web search result to a user query.\n"
    "If the document contains keyword(s) or semantic meaning related "
    "to the query, grade it as relevant.\n\n"
    "Additionally, consider the nature of the user query:\n"
    "- If the user asks for general information about the document, "
    "such as its content, summary, details, executive summary, format, etc. "
    "grade it as relevant.\n\n"
    "Give a binary score 'yes' or 'no' score to indicate whether the "
    "document is relevant to the question or not."
    )

# Prompt
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system),
        (
            "human", 
            "Retrieved document / web result: \n\n {document} \n\n "
            "User query: \n\n {query}",
            ),
    ]
)

retrieval_grader = prompt | structured_grader_model