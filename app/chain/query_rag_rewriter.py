from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from ..llm_model.azure_llm import helper_model

# System Prompt
system_prompt = (
    "You are a query re-writer that converts the latest query to a better "
    "version optimized for vectorstore retrieval in an LLM-based chatbot "
    "application. You are given a chat history and the latest user query "
    "which might reference context in the chat history. The query comes "
    "from employees at the enterprise organization based on the organization guidelines "
    "and the LLM purpose. The user might also share an image, "
    "from which you are given any relevant information.\n\n"
    "Look at the input and try to reason about the underlying semantic "
    "intent / meaning.\n\n"
    "Current timestamp: \n\n {timestamp} \n\n"
    "Enterprise guidelines and LLM purpose: \n\n {enterprise_context} \n\n"
    "When considering the image context, if an image is provided, ensure "
    "that the content of the image is taken into account when re-writing "
    "the latest query.\n\n"
    "Important: If the query is general or pertains to personal information "
    "or shared documents, do not add company contextual information unless "
    "it is explicitly relevant to the query. Ensure that general queries "
    "remain general and personal queries are handled with the appropriate "
    "context.\n"
    "Here are a few examples to guide you:\n\n"
    "- If the query is 'How to think about a Gen AI strategy for success', "
    "rewrite it as: 'What are the key components and considerations for "
    "developing a successful Generative AI strategy?' without adding "
    "the organization-specific context.\n\n"
    "- If the query is 'What is the policy for paternal leave?', rewrite it "
    "as: 'What is the policy for paternal leave at the company?' "
    "including the organization-specific context.\n\n"
    "- If the query is 'What are the benefits of AI in logistics?', rewrite "
    "it as: 'What are the benefits of AI in logistics?' without adding "
    "the organization-specific context.\n\n"
    "- If the query is 'How does the organization use AI in its operations?', rewrite it "
    "as: 'How does the organization use AI in its operations?' including "
    "the organization-specific context."
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
