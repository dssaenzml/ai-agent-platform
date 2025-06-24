
from langchain_openai import AzureChatOpenAI

from ..config import config

LLM_API_DEPLOYMENT_NAME = config.AZURE_OPENAI_LLM_DEPLOYMENT_NAME
LLM_API_VERSION = config.AZURE_OPENAI_LLM_API_VERSION
LLM_API_BASE = config.AZURE_OPENAI_LLM_ENDPOINT
LLM_API_KEY = config.AZURE_OPENAI_LLM_API_KEY

# Start LLM connections
topic_model = AzureChatOpenAI(
    api_key=LLM_API_KEY,
    azure_endpoint=LLM_API_BASE,
    openai_api_version=LLM_API_VERSION,
    azure_deployment=LLM_API_DEPLOYMENT_NAME,
    verbose=True,
    streaming=True,
    stream_options={"include_usage": True},
    temperature=0.0,
    max_tokens=30,
    timeout=30,
    max_retries=2,
)

retriever_model = AzureChatOpenAI(
    api_key=LLM_API_KEY,
    azure_endpoint=LLM_API_BASE,
    openai_api_version=LLM_API_VERSION,
    azure_deployment=LLM_API_DEPLOYMENT_NAME,
    verbose=True,
    streaming=True,
    stream_options={"include_usage": True},
    temperature=0.0,
    max_tokens=750,
    timeout=30,
    max_retries=2,
)

grader_model = AzureChatOpenAI(
    api_key=LLM_API_KEY,
    azure_endpoint=LLM_API_BASE,
    openai_api_version=LLM_API_VERSION,
    azure_deployment=LLM_API_DEPLOYMENT_NAME,
    verbose=True,
    streaming=True,
    stream_options={"include_usage": True},
    temperature=0.0,
    max_tokens=750,
    timeout=30,
    max_retries=2,
)

helper_model = AzureChatOpenAI(
    api_key=LLM_API_KEY,
    azure_endpoint=LLM_API_BASE,
    openai_api_version=LLM_API_VERSION,
    azure_deployment=LLM_API_DEPLOYMENT_NAME,
    verbose=True,
    streaming=True,
    stream_options={"include_usage": True},
    temperature=0.0,
    max_tokens=2000,
    timeout=30,
    max_retries=2,
)

long_helper_model = AzureChatOpenAI(
    api_key=LLM_API_KEY,
    azure_endpoint=LLM_API_BASE,
    openai_api_version=LLM_API_VERSION,
    azure_deployment=LLM_API_DEPLOYMENT_NAME,
    verbose=True,
    streaming=True,
    stream_options={"include_usage": True},
    temperature=0.0,
    max_tokens=4096,
    timeout=30,
    max_retries=2,
)

chat_model = AzureChatOpenAI(
    api_key=LLM_API_KEY,
    azure_endpoint=LLM_API_BASE,
    openai_api_version=LLM_API_VERSION,
    azure_deployment=LLM_API_DEPLOYMENT_NAME,
    verbose=True,
    streaming=True,
    stream_options={"include_usage": True},
    temperature=0.15,
    max_tokens=2000,
    timeout=30,
    max_retries=2,
)

document_generator_model = AzureChatOpenAI(
    api_key=LLM_API_KEY,
    azure_endpoint=LLM_API_BASE,
    openai_api_version=LLM_API_VERSION,
    azure_deployment=LLM_API_DEPLOYMENT_NAME,
    verbose=True,
    streaming=True,
    stream_options={"include_usage": True},
    temperature=0.1,
    max_tokens=10000,
    timeout=30,
    max_retries=2,
)

rpa_model = AzureChatOpenAI(
    api_key=LLM_API_KEY,
    azure_endpoint=LLM_API_BASE,
    openai_api_version=LLM_API_VERSION,
    azure_deployment=LLM_API_DEPLOYMENT_NAME,
    verbose=True,
    streaming=True,
    stream_options={"include_usage": True},
    temperature=0.1,
    max_tokens=2000,
    timeout=30,
    max_retries=2,
)

# Audio enabled deployment
AUDIO_LLM_API_DEPLOYMENT_NAME = config.AZURE_OPENAI_AUDIO_LLM_DEPLOYMENT_NAME
AUDIO_LLM_API_VERSION = config.AZURE_OPENAI_AUDIO_LLM_API_VERSION
AUDIO_LLM_API_BASE = config.AZURE_OPENAI_AUDIO_LLM_ENDPOINT
AUDIO_LLM_API_KEY = config.AZURE_OPENAI_AUDIO_LLM_API_KEY

# audio_chat_model = AzureChatOpenAI(
#     api_key=AUDIO_LLM_API_KEY,
#     azure_endpoint=AUDIO_LLM_API_BASE,
#     openai_api_version=AUDIO_LLM_API_VERSION,
#     azure_deployment=AUDIO_LLM_API_DEPLOYMENT_NAME,
#     verbose=True,
#     streaming=True,
#     stream_options={"include_usage": True},
#     temperature=0.15,
#     max_tokens=2000,
#     timeout=30,
#     max_retries=2,
#     model_kwargs={
#         "modalities": [
#             "text", 
#             "audio", 
#             ],  # We’re telling the model to handle both text and audio
#         "audio": {
#             "voice": "alloy", 
#             "format": "wav", 
#             },  # Configure voice and output format
#     },
# )