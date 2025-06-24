from langchain_openai import AzureOpenAIEmbeddings

from ..config import config

EMB_API_MODEL = config.AZURE_OPENAI_EMB_MODEL
EMB_API_BASE = config.AZURE_OPENAI_EMB_ENDPOINT
EMB_API_KEY = config.AZURE_OPENAI_EMB_API_KEY

embeddings_model = AzureOpenAIEmbeddings(
    api_key=EMB_API_KEY, azure_endpoint=EMB_API_BASE, model=EMB_API_MODEL
)
