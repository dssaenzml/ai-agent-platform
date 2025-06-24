from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from ..llm_model.azure_llm import grader_model

from ..model.grader_model import GradeAnswer

# LLM with function call
structured_grader_model = grader_model.with_structured_output(GradeAnswer)

# System Prompt
system = (
    "You are a grader assessing whether an LLM generation addresses "
    "or resolves a question. You are given the current timestamp, the the organization "
    "guidelines and LLM purpose, a set of retrieved facts under "
    "'Set of facts', the given chat history, the latest user "
    "query which might reference context in the chat history, and, if "
    "provided, the context extracted from the user-shared image. The LLM "
    "generation addresses employees' queries working at the company "
    "Group (the organization).\n\n"
    "Give a binary score 'yes' or 'no'. 'Yes' means that the "
    "answer resolves the question and is relevant to the query, "
    "while 'No' means it does not.\n\n"
    "For simple conversational exchanges such as greetings or "
    "polite expressions (e.g., 'hi', 'hello', 'thank "
    "you'), consider the response appropriate if it matches the "
    "context, even if it doesn't provide new information.\n\n"
    "For answers based on contextual documentation, "
    "consider the response appropiate if it achieves the query's "
    "task given the contextual documentation. Also, make sure that "
    "citations to any source are provided in the following formats only:\n\n"
    "\tRAG Document citation, i.e. Document.metadata['context_type'] == "
    "'rag_result', should have this format: (<em>Document.metadata['title'], "
    "p. Document.metadata['page_number']</em>)\n\n"
    "\tWebsite Document citation, i.e. Document.metadata['context_type'] == "
    "'web_search_result', should have this format and you have to ensure "
    "all elements like the href, title, and target given correctly: <a "
    "href=Document.metadata['URL'] "
    "title=Document.metadata['title'] target='_blank'>[1]</a> ... <a "
    "href=Document.metadata['URL'] "
    "title=Document.metadata['title'] target='_blank'>[5]</a>\n\n"
    "If the Document is an SQL result, i.e. Document.metadata["
    "'context_type'] == 'sql_search', then it does not need to be cited.\n\n"
    "Current timestamp: \n\n {timestamp} \n\n"
    "Enterprise guidelines and LLM purpose: \n\n {enterprise_context} \n\n"
    "Contextual Documentation: \n\n {context}"
)

# Prompt
prompt = ChatPromptTemplate.from_messages(
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
answer_grader = prompt | structured_grader_model
