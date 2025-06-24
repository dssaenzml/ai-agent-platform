from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from ..llm_model.azure_llm import grader_model
from ..model.grader_model import (
    SimpleRAGWebGradeQuery,
    SimpleRAGWebImgGradeQuery,
    SimpleRAGWebImgPDFGradeQuery,
)
from ..prompt.query_classifier import (
    simple_rag_web_img_pdf_system_prompt,
    simple_rag_web_img_system_prompt,
    simple_rag_web_system_prompt,
)

## Simple vs RAG vs Web query classifier
# LLM with function call
structured_grader_model = grader_model.with_structured_output(
    SimpleRAGWebGradeQuery,
)

answer_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", simple_rag_web_system_prompt),
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

simple_rag_web_query_classifier = answer_prompt | structured_grader_model

## Simple vs RAG vs Web vs Image generation query classifier
# LLM with function call
structured_grader_model = grader_model.with_structured_output(
    SimpleRAGWebImgGradeQuery,
)

answer_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", simple_rag_web_img_system_prompt),
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

simple_rag_web_img_query_classifier = answer_prompt | structured_grader_model

## Simple vs RAG vs Web vs Image vs PDF generation query classifier
# LLM with function call
structured_grader_model = grader_model.with_structured_output(
    SimpleRAGWebImgPDFGradeQuery,
)

answer_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", simple_rag_web_img_pdf_system_prompt),
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

simple_rag_web_img_pdf_query_classifier = answer_prompt | structured_grader_model
