
from langchain_core.prompts import (
    ChatPromptTemplate,
    MessagesPlaceholder
)

from ...llm_model.azure_llm import (
    grader_model, 
    )

from ...model.grader_model import (
    SimpleRAGWebSQLGradeQuery, 
)

from ...prompt.query_classifier import (
    simple_milahi_sql_system_prompt, 
)

## Simple vs RAG vs Web vs SQL query classifier
# LLM with function call
structured_grader_model = grader_model.with_structured_output(
    SimpleRAGWebSQLGradeQuery, 
    )

answer_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", simple_milahi_sql_system_prompt),
        MessagesPlaceholder("chat_history"),
        (
            "human", 
            "Here is the latest query: \n\n {query} \n\n"
            "Here is the summary of the user's uploaded documents: "
            "\n\n {summary_docs} \n\n"
            "Here is the image context: \n\n {image_context}",
        ),
    ]
)

classifier = answer_prompt | structured_grader_model