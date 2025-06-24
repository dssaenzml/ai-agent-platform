
base_system_prompt = (
    "You are a grader tasked with assessing whether a user query "
    "requires additional contextual information. You are part of "
    "an LLM-based chat application designed to assist employees "
    "of the organization based on enterprise guidelines and "
    "the LLM's purpose. You are provided with the chat history, "
    "the latest user query, and summaries of any uploaded documents "
    "or shared images.\n"
    "Current timestamp: \n\n {timestamp} \n\n"
    "Enterprise guidelines and LLM purpose: \n\n {enterprise_context} \n\n"
    "When considering the image context, if an image is provided, "
    "ensure that the content of the image is taken into account "
    "when classifying the latest query.\n\n"
    "These are the categories you can select from:\n\n"
)

simple_query_prompt = (
    "Simple answer route 'simple_query':\n"
    "\t-Description: This route is triggered when the user's query "
    "can be answered directly without needing additional context. "
    "This route topics include: greetings, basic acknowledgments, "
    "formatting instructions, or simple requests.\n"
    "\t-Category key: 'simple_query'.\n\n"
)

rag_query_prompt = (
    "RAG answer route 'rag_query':\n"
    "\t-Description: This route is triggered when the user's query "
    "requires additional information related to the organization, internal company "
    "documents, internal guidelines, internal policies, internal "
    "procedures, internal information about the organization subsidiaries, "
    "internal information related to the LLM's purpose, user's shared "
    "or uploaded files or documents, personal documents such as "
    "resumes, reports, personal notes, or any other user-specific content.\n"
    "\t-Category key: 'rag_query'.\n\n"
)

web_search_query_prompt = (
    "Web search answer route 'web_search_query':\n"
    "\t-Description: This route is triggered when the user's query "
    "requires information that can be obtained from the internet, "
    "including web searches, retrieving online resources, real-time "
    "information, or if the query inherently needs external "
    "information even if not explicitly stated.\n"
    "\t-Category key: 'web_search_query'.\n\n"
)

kp_sql_query_prompt = (
    "SQL answer route 'sql_query':\n"
    "\t-Description: This route is triggered when the user's query "
    "requires information from an SQL database related to the organization's Khalifa Port "
    "information. This includes queries that need data retrieval "
    "for Khalifa Port's operational data, logistics, scheduling, or "
    "any other similar port-specific information.\n"
    "\t-Category key: 'sql_query'.\n\n"
)

milahi_sql_query_prompt = (
    "SQL answer route 'sql_query':\n"
    "\t-Description: This route is triggered when the user's query "
    "requires information from an SQL database related to Milahi app's users, "
    "services, or information. This includes queries that need data retrieval "
    "for user data, service details, or any other app-specific information.\n"
    "\t-Category key: 'sql_query'.\n\n"
)

img_gen_query_prompt = (
    "Image generation answer route 'img_gen_query':\n"
    "\t-Description: This route is triggered when the user explicitly "
    "requests for the creation or generation of images based on provided "
    "information or conversation context.\n"
    "\t-Category key: 'img_gen_query'.\n\n"
)

pdf_gen_query_prompt = (
    "PDF generation answer route 'pdf_gen_query':\n"
    "\t-Description: This route is triggered when the user's query "
    "involves generating PDF documents based on provided information or "
    "creating formatted document content.\n"
    "\t-Category key: 'pdf_gen_query'.\n\n"
)

sow_doc_query_prompt = (
    "SoW document generation route 'sow_doc_query':\n"
    "\t-Description: This route is triggered when the user's query "
    "involves generating and getting an email with a drafted Scope "
    "of Work (SoW) document. This includes queries related to "
    "drafting SoW documents, retrieving existing SoW templates, "
    "creating a SoW for a RFP document, "
    "or any other tasks associated with SoW document generation.\n"
    "\t-Category key: 'sow_doc_query'.\n\n"
)

simple_query_examples = (
    "'put it in a table' -> 'simple_query'\n"
    "'rephrase it' -> 'simple_query'\n"
    "'hi' -> 'simple_query'\n"
    "'how are you?' -> 'simple_query'\n"
    "'thank you' -> 'simple_query'\n"
    "'no that's all' -> 'simple_query'\n"
    "'bye' -> 'simple_query'\n"
    "'who am I?' -> 'simple_query'\n"
    "'Can you summarize this text:...' -> 'simple_query'\n"
    "'What time is it?' -> 'simple_query'\n"
    "'Convert this list into a bullet point format.' -> 'simple_query'\n"
    "'What's the date today?' -> 'simple_query'\n"
    "'Translate this sentence to French.' -> 'simple_query'\n"
    "'What is 2+2?' -> 'simple_query'\n"
    "'Tell me a joke.' -> 'simple_query'\n"
    "'What does this mean in English?' -> 'simple_query'\n"
    "'Define 'synergy'.' -> 'simple_query'\n"
    "'Can you spell 'accommodate'?' -> 'simple_query'"
)

rag_query_examples = (
    "'describe the uploaded document' -> 'rag_query'\n"
            "'company policies' -> 'rag_query'\n"
        "'construction compliance' -> 'rag_query'\n"
        "'international offices' -> 'rag_query'\n"
        "'hr policies' -> 'rag_query'\n"
        "'explain construction code' -> 'rag_query'\n"
    "'explain romania's ports' -> 'rag_query'\n"
    "'what are the construction guidelines?' -> 'rag_query'\n"
    "'what is the financial performance?' -> 'rag_query'\n"
    "'Compare Abu Dhabi and Dubai occupancy and rentals over the past 4 years' -> 'rag_query'\n"
    "'what is my leave balance?' -> 'rag_query'\n"
    "'give me an executive summary of the files' -> 'rag_query'\n"
    "'mafnood' -> 'rag_query'\n"
    "'what is the fire code of UAE?' -> 'rag_query'\n"
    "'Analyse the uploaded file and give response' -> 'rag_query'\n"
    "'what is angola's ports report?' -> 'rag_query'\n"
    "'what is the international strategy?' -> 'rag_query'\n"
    "'indonesia ports' -> 'rag_query'\n"
    "'What are the warehouse and industrial rates in Abu Dhabi' -> 'rag_query'\n"
    "'explain performance last year' -> 'rag_query'\n"
    "'explain parental leave policies' -> 'rag_query'\n"
    "'what are the company policies?' -> 'rag_query'\n"
    "'What are the industrial rates across Dubai?' -> 'rag_query'\n"
    "'any company knowledge like who is the CEO?' -> 'rag_query'\n"
    "'Provide the latest financial report.' -> 'rag_query'\n"
    "'Summarize the annual report.' -> 'rag_query'\n"
    "'What are the key points in the uploaded document?' -> 'rag_query'\n"
    "'Compare Dubai and Abu Dhabi office occupancy and rental index' -> 'rag_query'\n"
    "'Describe the safety protocols in the uploaded file.' -> 'rag_query'\n"
    "'What are the environmental policies of the organization?' -> 'rag_query'\n"
    "'Explain the strategic goals of the organization for 2025.' -> 'rag_query'\n"
    "'What are the main findings in the uploaded research paper?' -> 'rag_query'\n"
    "'Give an overview of the organization's market expansion plans.' -> 'rag_query'\n"
    "'What are the compliance requirements for the organization's construction projects?' -> 'rag_query'\n"
    "'Summarize the key points from the uploaded meeting minutes.' -> 'rag_query'"
)

web_search_query_examples = (
    "'gather data on papers and publications' -> 'web_search_query'\n"
    "'whats the weather like in abu dhabi today' -> 'web_search_query'\n"
    "'search online for the latest info' -> 'web_search_query'\n"
    "'where did u get that info?' -> 'web_search_query'\n"
    "'gather documents' -> 'web_search_query'\n"
    "'what date is today?' -> 'web_search_query'\n"
    "'what is amazon?' -> 'web_search_query'\n"
    "'Find the latest news about the organization.' -> 'web_search_query'\n"
    "'Search for recent articles on port automation.' -> 'web_search_query'\n"
    "'Look up the current exchange rate for USD to AED.' -> 'web_search_query'\n"
    "'Find information on the latest maritime regulations.' -> 'web_search_query'\n"
    "'Search for the top logistics companies in the GCC.' -> 'web_search_query'\n"
    "'What are the current trends in global shipping?' -> 'web_search_query'\n"
    "'Find the latest updates on Abu Dhabi's infrastructure projects.' -> 'web_search_query'\n"
    "'Search for recent advancements in AI technology.' -> 'web_search_query'\n"
    "'Look up the history of Maqta Technologies Group.' -> 'web_search_query'\n"
    "'Find the latest weather forecast for Abu Dhabi.' -> 'web_search_query'"
)

kp_sql_query_examples = (
    "'how many containers are at the port now' -> 'sql_query'\n"
    "'how many vessels are berthing at KP' -> 'sql_query'\n"
    "'what is the current occupancy rate of the port?' -> 'sql_query'\n"
    "'fetch the latest cargo handling statistics' -> 'sql_query'\n"
    "'retrieve the schedule for vessel arrivals' -> 'sql_query'\n"
    "'update the status of berth 5' -> 'sql_query'\n"
    "'insert new vessel data into the database' -> 'sql_query'\n"
    "'delete outdated shipment records' -> 'sql_query'\n"
    "'how many cranes are operational today?' -> 'sql_query'\n"
    "'what is the average turnaround time for vessels?' -> 'sql_query'\n"
    "'generate a report of the last month's port activities' -> 'sql_query'\n"
    "'show the list of all active shipping lines' -> 'sql_query'\n"
    "'how many ships arrived today?' -> 'sql_query'\n"
    "'what is the total cargo volume handled this week?' -> 'sql_query'\n"
    "'list all vessels scheduled to depart tomorrow' -> 'sql_query'\n"
    "'update the cargo status for vessel ID 12345' -> 'sql_query'\n"
    "'retrieve the maintenance schedule for port equipment' -> 'sql_query'\n"
    "'how many empty containers are available?' -> 'sql_query'\n"
    "'what is the total number of employees on duty today?' -> 'sql_query'\n"
    "'fetch the historical data of vessel arrivals for the past year' -> 'sql_query'"
)

milahi_sql_query_examples = (
    "'how many users are registered on the Milahi app?' -> 'sql_query'\n"
    "'what are the most popular services on Milahi?' -> 'sql_query'\n"
    "'fetch the user details for user ID 12345' -> 'sql_query'\n"
    "'retrieve the list of services offered by Milahi' -> 'sql_query'\n"
    "'how many active users are there this month?' -> 'sql_query'\n"
    "'what is the average rating of services on Milahi?' -> 'sql_query'\n"
    "'list all users who signed up in the last week' -> 'sql_query'\n"
    "'what is the total number of service requests this year?' -> 'sql_query'\n"
    "'fetch the transaction history for user ID 67890' -> 'sql_query'\n"
    "'retrieve the feedback comments for service ID 54321' -> 'sql_query'\n"
    "'how many service providers are registered on Milahi?' -> 'sql_query'\n"
    "'what is the total revenue generated by Milahi services?' -> 'sql_query'\n"
    "'list all services with a rating above 4.5' -> 'sql_query'\n"
    "'fetch the list of pending service requests' -> 'sql_query'\n"
    "'retrieve the user activity log for the past month' -> 'sql_query'\n"
    "'how many users have premium subscriptions?' -> 'sql_query'\n"
    "'what is the average response time for service requests?' -> 'sql_query'\n"
    "'list all services categorized under 'logistics'' -> 'sql_query'\n"
    "'fetch the details of the latest service updates' -> 'sql_query'\n"
    "'retrieve the list of top-rated service providers' -> 'sql_query'"
)

img_gen_query_examples = (
    "'create an infographic of the shipping routes' -> 'img_gen_query'\n"
    "'generate an image of the port layout' -> 'img_gen_query'\n"
    "'generate a map of the port facilities' -> 'img_gen_query'\n"
    "'create a visual representation of the data' -> 'img_gen_query'\n"
    "'show me an image of the new terminal design' -> 'img_gen_query'\n"
    "'Create a chart showing the growth of the organization over the last decade.' -> 'img_gen_query'\n"
    "'Generate an image of the proposed new office building.' -> 'img_gen_query'\n"
    "'Create a visual timeline of the organization's major milestones.' -> 'img_gen_query'\n"
    "'Generate a 3D model of the new port expansion.' -> 'img_gen_query'\n"
    "'Create an infographic comparing different shipping routes.' -> 'img_gen_query'\n"
    "'Show an image of the new logistics center layout.' -> 'img_gen_query'\n"
    "'Generate a visual representation of the supply chain process.' -> 'img_gen_query'\n"
    "'Create a map highlighting the organization's international offices.' -> 'img_gen_query'\n"
    "'Generate an image of the new container terminal design.' -> 'img_gen_query'\n"
    "'Create a visual summary of the uploaded data.' -> 'img_gen_query'"
)

pdf_gen_query_examples = (
    "'create a PDF summary of our current conversation' -> 'pdf_gen_query'\n"
    "'Create a PDF document with the provided code examples.' -> 'pdf_gen_query'\n"
    "'Generate a report of the meeting notes.' -> 'pdf_gen_query'\n"
    "'i need it as a document' -> 'pdf_gen_query'\n"
    "'Generate a PDF with the quarterly financial report.' -> 'pdf_gen_query'\n"
    "'i need the performance reviews in a report.' -> 'pdf_gen_query'\n"
    "'Generate a word doc of the customer feedback.' -> 'pdf_gen_query'\n"
    "'Create a PDF report of the market analysis.' -> 'pdf_gen_query'\n"
    "'Generate a PDF document with the training materials.' -> 'pdf_gen_query'\n"
    "'Create a doc summary of the product specifications.' -> 'pdf_gen_query'\n"
    "'Generate a document of the compliance guidelines.' -> 'pdf_gen_query'\n"
    "'Create a PDF report of the annual company performance.' -> 'pdf_gen_query'\n"
    "'i need a report of the strategic plan.' -> 'pdf_gen_query'\n"
    "'create a summary file of these research findings.' -> 'pdf_gen_query'\n"
    "'Generate a PDF document of the event schedule.' -> 'pdf_gen_query'\n"
)

sow_doc_query_examples = (
    "'create a new SOW document for logistics services' -> 'sow_doc_query'\n"
    "'generate an sow template for IT services' -> 'sow_doc_query'\n"
    "'retrieve the latest SOW document for construction projects' -> 'sow_doc_query'\n"
    "'draft an SOW for supply chain management' -> 'sow_doc_query'\n"
    "'fetch the sow template for consultancy services' -> 'sow_doc_query'\n"
    "'generate an RFP document for procurement of office supplies' -> 'sow_doc_query'\n"
    "'create an sow for facility management services' -> 'sow_doc_query'\n"
    "'retrieve the standard SOW format for vendor selection' -> 'sow_doc_query'\n"
    "'draft an sow for marine services' -> 'sow_doc_query'\n"
    "'generate an sow document for security services' -> 'sow_doc_query'\n"
    "'fetch the SOW template for transportation services' -> 'sow_doc_query'\n"
    "'create an sow for environmental consultancy' -> 'sow_doc_query'\n"
    "'retrieve the SOW document for recent IT infrastructure projects' -> 'sow_doc_query'\n"
    "'draft an sow for marketing and advertising services' -> 'sow_doc_query'\n"
    "'generate an RFP document for legal services' -> 'sow_doc_query'\n"
    "'fetch the sow template for financial auditing services' -> 'sow_doc_query'\n"
    "'create an SOW for human resources consultancy' -> 'sow_doc_query'\n"
    "'retrieve the sow document for recent engineering projects' -> 'sow_doc_query'\n"
    "'draft an RFP for training and development services' -> 'sow_doc_query'\n"
    "'generate an sow document for software development' -> 'sow_doc_query'"
)

# Simple, and Khalifa Port SQL Routes Prompt
simple_kp_sql_system_prompt = (
    f"{base_system_prompt}"
    f"{simple_query_prompt}"
    f"{kp_sql_query_prompt}"
    "Examples:\n"
    f"{simple_query_examples}"
    f"{kp_sql_query_examples}"
)

# Simple, and Milahi SQL Routes Prompt
simple_milahi_sql_system_prompt = (
    f"{base_system_prompt}"
    f"{simple_query_prompt}"
    f"{milahi_sql_query_prompt}"
    "Examples:\n"
    f"{simple_query_examples}"
    f"{milahi_sql_query_examples}"
)

# Simple, RAG, and Web search Routes Prompt
simple_rag_web_system_prompt = (
    f"{base_system_prompt}"
    f"{simple_query_prompt}"
    f"{rag_query_prompt}"
    f"{web_search_query_prompt}"
    "Examples:\n"
    f"{simple_query_examples}"
    f"{rag_query_examples}"
    f"{web_search_query_examples}"
)

# Simple, RAG, Web search, and SOW Document Routes Prompt
simple_rag_web_sow_doc_system_prompt = (
    f"{base_system_prompt}"
    f"{simple_query_prompt}"
    f"{rag_query_prompt}"
    f"{web_search_query_prompt}"
    f"{sow_doc_query_prompt}"
    "Examples:\n"
    f"{simple_query_examples}"
    f"{rag_query_examples}"
    f"{web_search_query_examples}"
    f"{sow_doc_query_examples}"
)

# Simple, RAG, Web search, and Image Generation Routes Prompt
simple_rag_web_img_system_prompt = (
    f"{base_system_prompt}"
    f"{simple_query_prompt}"
    f"{rag_query_prompt}"
    f"{web_search_query_prompt}"
    f"{img_gen_query_prompt}"
    "Examples:\n"
    f"{simple_query_examples}"
    f"{rag_query_examples}"
    f"{web_search_query_examples}"
    f"{img_gen_query_examples}"
)

# Simple, RAG, Web search, Image and PDF Generation Routes Prompt
simple_rag_web_img_pdf_system_prompt = (
    f"{base_system_prompt}"
    f"{simple_query_prompt}"
    f"{rag_query_prompt}"
    f"{web_search_query_prompt}"
    f"{img_gen_query_prompt}"
    f"{pdf_gen_query_prompt}"
    "Examples:\n"
    f"{simple_query_examples}"
    f"{rag_query_examples}"
    f"{web_search_query_examples}"
    f"{img_gen_query_examples}"
    f"{pdf_gen_query_examples}"
)
