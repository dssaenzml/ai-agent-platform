from langchain_core.prompts import (
    ChatPromptTemplate,
    MessagesPlaceholder,
)

from ...llm_model.azure_llm import (
    helper_model,
    long_helper_model,
)

from ...model.agent_procurement.bot_model import (
    SoWType,
    ConsultancyServicesSoWDetails,
)

## SoW type gatherer
# Add tools to llm
llm_with_tool = helper_model.bind_tools([SoWType])

# System Prompt
system_prompt = (
    "You are an advanced AI assistant responsible for managing SoW data "
    "gathering requests. You are given a chat history and the latest user "
    "query which might reference context in the chat history. The query "
    "comes from employees at the enterprise organization based on the organization "
    "guidelines and the LLM purpose. The user might also share an image, "
    "from which you are given any relevant information. Your task is to "
    "get the scope of work type that a user would like to fill in.\n\n"
    "You should get the following information from them:\n\n"
    "\t-What is the scope of work type of interest in the conversation "
    "(select one of the following choices): 'Consultancy Services', "
    "'General Services', 'Manpower Supply'.\n\n"
    "If you are not able to discern this info, ask them to clarify! "
    "Do not attempt to wildly guess.\n\n"
    "After you are able to discern all the information, fill in the SoW "
    "type accordingly.\n\n"
    "You are given contextual information about the company and the LLM "
    "chatbot system you are part of and its purpose.\n\n"
    "Enterprise guidelines and LLM purpose: \n\n {enterprise_context} \n\n"
    "Current timestamp: \n\n {timestamp} \n\n"
    "When considering the image context, if an image is provided, ensure "
    "that the content of the image is taken into account when gathering "
    "the necessary information.\n\n"
    "Please ensure the conversation is relevant, detailed, and "
    "considers the unique geography, politics, economics, environment, "
    "culture, and international relations of the GCC region."
)

# Prompt
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_prompt),
        MessagesPlaceholder("chat_history"),
        (
            "human",
            "Here is the latest human query: \n\n {query} \n\n"
            "Here is the image context: \n\n {image_context} \n\n"
            "Gather the necessary details.",
        ),
    ]
)

# Chain
sow_type_gatherer = prompt | llm_with_tool

## Consultancy Services Information gatherer
# Add tools to llm
llm_with_tool = long_helper_model.bind_tools([ConsultancyServicesSoWDetails])

# System Prompt
system_prompt = (
    "You are an advanced AI assistant responsible for managing SoW data "
    "gathering requests. You are given a chat history and the latest user "
    "query which might reference context in the chat history. The query "
    "comes from employees at the enterprise organization based on the organization "
    "guidelines and the LLM purpose. The user might also share an image, "
    "from which you are given any relevant information. Your task is to "
    "get information from a user about the details "
    "needed to fill in an SOW template.\n\n"
    "You should get the following information from them:\n\n"
    "\t-Preamble: A brief high-level introduction about the project such "
    "as location, objectives, and parties involved in execution.\n"
    "\t-General SoW: An overview of the general scope of services to be "
    "performed.\n"
    "\t-Description of Services: A detailed description of the actual "
    "services to be performed.\n"
    "\t-Codes and Standards: Details around codes and standards to ensure "
    "compliance with the project requirements.\n"
    "\t-Drawings and Specifications: Detailed drawings and specifications "
    "to ensure compliance with the project requirements.\n"
    "\t-Review Meetings and Reporting: Procedural requirements regarding "
    "review and approval processes, meetings, and reporting requirements.\n"
    "\t-Training Requirements: Any training that is required to be provided "
    "under the contract.\n"
    "\t-Interface Requirements: Description of any and all interfaces that "
    "the contractor is required to manage in the execution of the services, "
    "including site access and interference with other contractors.\n"
    "\t-Deliverables: An exhaustive list of deliverables that the contractor "
    "may be required to provide during the course of execution of the "
    "services and upon completion.\n"
    "\t-Exclusions: Items that are excluded from the scope but could be "
    "misconstrued as being part of the scope, such as scope executed by "
    "others, items free issued by the Employer, and charges or expenses "
    "to be borne by the Employer.\n"
    "\t-Optional Scope: Optional scope items, which may be instructed "
    "later at Employer's discretion.\n"
    "\t-Facilities by Employer: An exhaustive list and description of the "
    "facilities and support services to be provided by the Employer, such "
    "as specific data or information to be provided at a later date, office "
    "space and related facilities, and any other item of general "
    "assistance.\n\n"
    "If you are not able to discern this info, ask them to clarify! "
    "Do not attempt to wildly guess.\n\n"
    "After you are able to discern all the information, fill in the SOW "
    "template accordingly.\n\n"
    "You are given contextual information about the company and the LLM "
    "chatbot system you are part of and its purpose.\n\n"
    "Enterprise guidelines and LLM purpose: \n\n {enterprise_context} \n\n"
    "Current timestamp: \n\n {timestamp} \n\n"
    "When considering the image context, if an image is provided, ensure "
    "that the content of the image is taken into account when gathering "
    "the necessary information.\n\n"
    "Please ensure the conversation is relevant, detailed, and "
    "considers the unique geography, politics, economics, environment, "
    "culture, and international relations of the GCC region."
)

# Prompt
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_prompt),
        MessagesPlaceholder("chat_history"),
        (
            "human",
            "Here is the latest human query: \n\n {query} \n\n"
            "Here is the image context: \n\n {image_context} \n\n"
            "Gather the necessary details.",
        ),
    ]
)

# Chain
consultancy_services_sow_details_gatherer = prompt | llm_with_tool


# query = """Hello!

# Thank you for offering to assist with the SOW. Here are the details you requested:

# 1. Main Objectives and Expected Outcomes:
#    - The primary objective of the project is to enhance our logistics management system to improve efficiency and reduce operational costs.
#    - Expected outcomes include a 20% reduction in delivery times, improved tracking capabilities, and enhanced customer satisfaction.

# 2. Specific Requirements and Deliverables:
#    - The project requires the development of a new software module for real-time tracking of shipments.
#    - Deliverables include a fully functional software module, user training sessions, and comprehensive documentation.
#    - Additionally, the project should integrate seamlessly with our existing systems and comply with industry standards.

# 3. Budget:
#    - The allocated budget for this project is $500,000, which includes development, implementation, and training costs.

# Please let me know if you need any further information or clarification.

# Best regards,

# Diego Saenz"""
# # query = "hi"
# response = gatherer.invoke({
#         "query": query,
#         "timestamp": "16th Jan 2025 15:29PM",
#         "chat_history": [],
#         "enterprise_context": enterprise_context,
#         "image_context": image_context,
#         })


# if isinstance(response, AIMessage) and response.tool_calls:
#     print('information gathered')
# else:
#     print('request for info')

# response.tool_calls[0]["args"]
