from ...config import config
from ..azure_send_email_tool import \
    AzureCommunicationServiceSendEmailTool as SendEmailTool
from ..tool_wrapper.azure_send_email_api_wrapper import \
    AzureCommunicationServiceSendEmailAPIWrapper as SendEmailAPIWrapper

ACS_CONNECTION_STRING = config.ACS_CONNECTION_STRING

api_wrapper = SendEmailAPIWrapper(
    connection_string=ACS_CONNECTION_STRING,
)

tool = SendEmailTool(api_wrapper=api_wrapper)


# # Example usage
# document_input = {
#     "project_objectives": "To enhance the port's operational efficiency.",
#     "project_requirements": "Automated cargo handling system.",
#     "project_budget": "USD 5 million"
# }

# result = tool_wrapper.run(document_input)
# output = tool.invoke({"document_input": document_input})
# output.keys()
# def send_email_with_attachment(recipient_email, file_path):
#     """
#     Send an email with an attachment using Azure Communication Services.

#     :param recipient_email: The email address to send the document to.
#     :param file_path: The path to the file to attach.
#     """
#     # Initialize the Email Client
#     connection_string = "your_acs_connection_string"  # Replace with your ACS connection string
#     email_client = EmailClient.from_connection_string(connection_string)

#     # Prepare the Email Message
#     with open(file_path, 'rb') as attachment:
#         attachment_content = attachment.read()

#     message = {
#         "content": {
#             "subject": "Request for Proposal (RFP) Document",
#             "plainText": "Please find attached the RFP document.",
#             "html": "<html><h1>Please find attached the RFP document.</h1></html>"
#         },
#         "recipients": {
#             "to": [
#                 {
#                     "address": recipient_email,
#                     "displayName": "Recipient Name"
#                 }
#             ]
#         },
#         "attachments": [
#             {
#                 "name": os.path.basename(file_path),
#                 "attachmentType": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
#                 "contentBytesBase64": attachment_content.encode('base64')
#             }
#         ],
#         "senderAddress": "sender@contoso.com"
#     }

#     # Send the email
#     poller = email_client.begin_send(message)
#     result = poller.result()
