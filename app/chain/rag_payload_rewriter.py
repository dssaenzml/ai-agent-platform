
from langchain_core.prompts import (
    ChatPromptTemplate, 
)
from langchain_core.output_parsers import StrOutputParser

from ..llm_model.azure_llm import (
    helper_model, 
    )

# Prompt
prompt = ChatPromptTemplate.from_messages(
    [(
        "human",
        "Context information is below.\n\n"
        "---------------------\n"
        "{doc_context}\n"
        "---------------------\n\n"
        "Given the context information and not prior knowledge, "
        "generate only a five-sentences summary and questions based "
        "on the below query.\n\n"
        "You are a Teacher/Professor. Your task is to create a maximum of "
        "{num_questions_per_chunk} questions and one meaningful summary "
        "of the content for an upcoming quiz/examination. The questions "
        "should be diverse in nature and should cover different aspects "
        "of the content. Ensure that the questions are directly related "
        "to the content within the context information provided, "
        "and avoid referencing the document itself. Do not include any "
        "subtitles or section headers like 'Summary' or 'Questions'. "
        "Ensure that the summary and questions are presented "
        "without excessive whitespace between them.",
        )]
)

# Chain
rag_payload_rewriter = prompt | helper_model | StrOutputParser()
