import os
import certifi

basedir = os.path.abspath(os.path.dirname(__file__))
env_name = os.getenv("AI_AGENT_ENV", "dev")

# App settings
web_search_num_results = 10
max_batch_size = 4
embeddings_size = 1536
child_chunk_size = 700
search_type = (
    "similarity_score_threshold"  # "similarity", "mmr", "similarity_score_threshold"
)
search_kwargs = {"score_threshold": 0.75, "k": 10}  # "k", "score_threshold", "fetch_k"


class Config:
    DEBUG = False
    API_VERSION = "1.0"
    API_PREFIX_STR = "/api/v1"
    PROJECT_NAME = "AI Agent Platform"
    API_DESC = "AI Agent Platform's API server using Langchain's Runnable interfaces"
    TEST: bool = False


class DevelopmentConfig(Config):
    DEBUG = True

    # App settings
    web_search_num_results = web_search_num_results
    max_batch_size = max_batch_size
    embeddings_size = embeddings_size
    child_chunk_size = child_chunk_size
    search_type = search_type
    search_kwargs = search_kwargs

    # AzureOpenAI Access
    AZURE_OPENAI_LLM_DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_LLM_DEPLOYMENT_NAME")
    AZURE_OPENAI_LLM_API_VERSION = os.getenv("AZURE_OPENAI_LLM_API_VERSION")
    AZURE_OPENAI_LLM_ENDPOINT = os.getenv("AZURE_OPENAI_LLM_ENDPOINT")
    AZURE_OPENAI_LLM_API_KEY = os.getenv("AZURE_OPENAI_LLM_API_KEY")

    AZURE_OPENAI_EMB_MODEL = os.getenv("AZURE_OPENAI_EMB_MODEL")
    AZURE_OPENAI_EMB_ENDPOINT = os.getenv("AZURE_OPENAI_EMB_ENDPOINT")
    AZURE_OPENAI_EMB_API_KEY = os.getenv("AZURE_OPENAI_EMB_API_KEY")

    AZURE_OPENAI_IMG_GEN_DEPLOYMENT_NAME = os.getenv(
        "AZURE_OPENAI_IMG_GEN_DEPLOYMENT_NAME"
    )
    AZURE_OPENAI_IMG_GEN_API_VERSION = os.getenv("AZURE_OPENAI_IMG_GEN_API_VERSION")
    AZURE_OPENAI_IMG_GEN_ENDPOINT = os.getenv("AZURE_OPENAI_IMG_GEN_ENDPOINT")
    AZURE_OPENAI_IMG_GEN_API_KEY = os.getenv("AZURE_OPENAI_IMG_GEN_API_KEY")

    AZURE_OPENAI_AUDIO_LLM_DEPLOYMENT_NAME = os.getenv(
        "AZURE_OPENAI_AUDIO_LLM_DEPLOYMENT_NAME"
    )
    AZURE_OPENAI_AUDIO_LLM_API_VERSION = os.getenv("AZURE_OPENAI_AUDIO_LLM_API_VERSION")
    AZURE_OPENAI_AUDIO_LLM_ENDPOINT = os.getenv("AZURE_OPENAI_AUDIO_LLM_ENDPOINT")
    AZURE_OPENAI_AUDIO_LLM_API_KEY = os.getenv("AZURE_OPENAI_AUDIO_LLM_API_KEY")

    # Azure Blob Storage Access
    AZ_TENANT_ID = os.getenv("AZ_TENANT_ID")
    AZ_CLIENT_ID = os.getenv("AZ_CLIENT_ID")
    AZ_SECRET_ID = os.getenv("AZ_SECRET_ID")
    DFS_ACCOUNT_URL = os.getenv("DFS_ACCOUNT_URL")
    BLOB_ACCOUNT_URL = os.getenv("BLOB_ACCOUNT_URL")
    BLOB_CONTAINER_NAME = os.getenv("BLOB_CONTAINER_NAME")

    # Snowflake Access
    SF_MAIN_ACCOUNT = os.getenv("SF_MAIN_ACCOUNT")
    SF_MAIN_USER = os.getenv("SF_MAIN_USER")
    SF_MAIN_PASSWORD = os.getenv("SF_MAIN_PASSWORD")
    SF_MAIN_ROLE = os.getenv("SF_MAIN_ROLE")
    SF_MAIN_WH = os.getenv("SF_MAIN_WH")
    SF_MAIN_DB = os.getenv("SF_MAIN_DB")
    SF_MAIN_SCHEMA = os.getenv("SF_MAIN_SCHEMA")

    SF_KP_ACCOUNT = os.getenv("SF_KP_ACCOUNT")
    SF_KP_USER = os.getenv("SF_KP_USER")
    SF_KP_PASSWORD = os.getenv("SF_KP_PASSWORD")
    SF_KP_ROLE = os.getenv("SF_KP_ROLE")
    SF_KP_WH = os.getenv("SF_KP_WH")
    SF_KP_DB = os.getenv("SF_KP_DB")
    SF_KP_SCHEMA = os.getenv("SF_KP_SCHEMA")
    SF_KP_STAGE = os.getenv("SF_KP_STAGE")
    SF_KP_SM = os.getenv("SF_KP_SM")

    SF_MILAHI_ACCOUNT = os.getenv("SF_MILAHI_ACCOUNT")
    SF_MILAHI_ROLE = os.getenv("SF_MILAHI_ROLE")
    SF_MILAHI_WH = os.getenv("SF_MILAHI_WH")
    SF_MILAHI_DB = os.getenv("SF_MILAHI_DB")
    SF_MILAHI_SCHEMA = os.getenv("SF_MILAHI_SCHEMA")
    SF_MILAHI_STAGE = os.getenv("SF_MILAHI_STAGE")
    SF_MILAHI_SM = os.getenv("SF_MILAHI_SM")

    # Qdrant Access
    VEC_DB_URL = os.getenv("VEC_DB_URL")
    VEC_DB_API_KEY = os.getenv("VEC_DB_API_KEY")

    # Web search service
    BING_SEARCH_URL = os.getenv("BING_SEARCH_URL")
    BING_SUBSCRIPTION_KEY = os.getenv("BING_SUBSCRIPTION_KEY")

    # Email service
    ACS_CONNECTION_STRING = os.getenv("ACS_CONNECTION_STRING")


class TestingConfig(Config):
    DEBUG = True

    # App settings
    web_search_num_results = web_search_num_results
    max_batch_size = max_batch_size
    embeddings_size = embeddings_size
    child_chunk_size = child_chunk_size
    search_type = search_type
    search_kwargs = search_kwargs

    # AzureOpenAI Access
    AZURE_OPENAI_LLM_DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_LLM_DEPLOYMENT_NAME")
    AZURE_OPENAI_LLM_API_VERSION = os.getenv("AZURE_OPENAI_LLM_API_VERSION")
    AZURE_OPENAI_LLM_ENDPOINT = os.getenv("AZURE_OPENAI_LLM_ENDPOINT")
    AZURE_OPENAI_LLM_API_KEY = os.getenv("AZURE_OPENAI_LLM_API_KEY")

    AZURE_OPENAI_EMB_MODEL = os.getenv("AZURE_OPENAI_EMB_MODEL")
    AZURE_OPENAI_EMB_ENDPOINT = os.getenv("AZURE_OPENAI_EMB_ENDPOINT")
    AZURE_OPENAI_EMB_API_KEY = os.getenv("AZURE_OPENAI_EMB_API_KEY")

    AZURE_OPENAI_IMG_GEN_DEPLOYMENT_NAME = os.getenv(
        "AZURE_OPENAI_IMG_GEN_DEPLOYMENT_NAME"
    )
    AZURE_OPENAI_IMG_GEN_API_VERSION = os.getenv("AZURE_OPENAI_IMG_GEN_API_VERSION")
    AZURE_OPENAI_IMG_GEN_ENDPOINT = os.getenv("AZURE_OPENAI_IMG_GEN_ENDPOINT")
    AZURE_OPENAI_IMG_GEN_API_KEY = os.getenv("AZURE_OPENAI_IMG_GEN_API_KEY")

    AZURE_OPENAI_AUDIO_LLM_DEPLOYMENT_NAME = os.getenv(
        "AZURE_OPENAI_AUDIO_LLM_DEPLOYMENT_NAME"
    )
    AZURE_OPENAI_AUDIO_LLM_API_VERSION = os.getenv("AZURE_OPENAI_AUDIO_LLM_API_VERSION")
    AZURE_OPENAI_AUDIO_LLM_ENDPOINT = os.getenv("AZURE_OPENAI_AUDIO_LLM_ENDPOINT")
    AZURE_OPENAI_AUDIO_LLM_API_KEY = os.getenv("AZURE_OPENAI_AUDIO_LLM_API_KEY")

    # Azure Blob Storage Access
    AZ_TENANT_ID = os.getenv("AZ_TENANT_ID")
    AZ_CLIENT_ID = os.getenv("AZ_CLIENT_ID")
    AZ_SECRET_ID = os.getenv("AZ_SECRET_ID")
    DFS_ACCOUNT_URL = os.getenv("DFS_ACCOUNT_URL")
    BLOB_ACCOUNT_URL = os.getenv("BLOB_ACCOUNT_URL")
    BLOB_CONTAINER_NAME = os.getenv("BLOB_CONTAINER_NAME")

    # Snowflake Access
    SF_MAIN_ACCOUNT = os.getenv("SF_MAIN_ACCOUNT")
    SF_MAIN_USER = os.getenv("SF_MAIN_USER")
    SF_MAIN_PASSWORD = os.getenv("SF_MAIN_PASSWORD")
    SF_MAIN_ROLE = os.getenv("SF_MAIN_ROLE")
    SF_MAIN_WH = os.getenv("SF_MAIN_WH")
    SF_MAIN_DB = os.getenv("SF_MAIN_DB")
    SF_MAIN_SCHEMA = os.getenv("SF_MAIN_SCHEMA")

    SF_KP_ACCOUNT = os.getenv("SF_KP_ACCOUNT")
    SF_KP_USER = os.getenv("SF_KP_USER")
    SF_KP_PASSWORD = os.getenv("SF_KP_PASSWORD")
    SF_KP_ROLE = os.getenv("SF_KP_ROLE")
    SF_KP_WH = os.getenv("SF_KP_WH")
    SF_KP_DB = os.getenv("SF_KP_DB")
    SF_KP_SCHEMA = os.getenv("SF_KP_SCHEMA")
    SF_KP_STAGE = os.getenv("SF_KP_STAGE")
    SF_KP_SM = os.getenv("SF_KP_SM")

    SF_MILAHI_ACCOUNT = os.getenv("SF_MILAHI_ACCOUNT")
    SF_MILAHI_ROLE = os.getenv("SF_MILAHI_ROLE")
    SF_MILAHI_WH = os.getenv("SF_MILAHI_WH")
    SF_MILAHI_DB = os.getenv("SF_MILAHI_DB")
    SF_MILAHI_SCHEMA = os.getenv("SF_MILAHI_SCHEMA")
    SF_MILAHI_STAGE = os.getenv("SF_MILAHI_STAGE")
    SF_MILAHI_SM = os.getenv("SF_MILAHI_SM")

    # Qdrant Access
    VEC_DB_URL = os.getenv("VEC_DB_URL")
    VEC_DB_API_KEY = os.getenv("VEC_DB_API_KEY")

    # Web search service
    BING_SEARCH_URL = os.getenv("BING_SEARCH_URL")
    BING_SUBSCRIPTION_KEY = os.getenv("BING_SUBSCRIPTION_KEY")

    # Email service
    ACS_CONNECTION_STRING = os.getenv("ACS_CONNECTION_STRING")


class ProductionConfig(Config):
    DEBUG = False

    # App settings
    web_search_num_results = web_search_num_results
    max_batch_size = max_batch_size
    embeddings_size = embeddings_size
    child_chunk_size = child_chunk_size
    search_type = search_type
    search_kwargs = search_kwargs

    # AzureOpenAI Access
    AZURE_OPENAI_LLM_DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_LLM_DEPLOYMENT_NAME")
    AZURE_OPENAI_LLM_API_VERSION = os.getenv("AZURE_OPENAI_LLM_API_VERSION")
    AZURE_OPENAI_LLM_ENDPOINT = os.getenv("AZURE_OPENAI_LLM_ENDPOINT")
    AZURE_OPENAI_LLM_API_KEY = os.getenv("AZURE_OPENAI_LLM_API_KEY")

    AZURE_OPENAI_EMB_MODEL = os.getenv("AZURE_OPENAI_EMB_MODEL")
    AZURE_OPENAI_EMB_ENDPOINT = os.getenv("AZURE_OPENAI_EMB_ENDPOINT")
    AZURE_OPENAI_EMB_API_KEY = os.getenv("AZURE_OPENAI_EMB_API_KEY")

    AZURE_OPENAI_IMG_GEN_DEPLOYMENT_NAME = os.getenv(
        "AZURE_OPENAI_IMG_GEN_DEPLOYMENT_NAME"
    )
    AZURE_OPENAI_IMG_GEN_API_VERSION = os.getenv("AZURE_OPENAI_IMG_GEN_API_VERSION")
    AZURE_OPENAI_IMG_GEN_ENDPOINT = os.getenv("AZURE_OPENAI_IMG_GEN_ENDPOINT")
    AZURE_OPENAI_IMG_GEN_API_KEY = os.getenv("AZURE_OPENAI_IMG_GEN_API_KEY")

    AZURE_OPENAI_AUDIO_LLM_DEPLOYMENT_NAME = os.getenv(
        "AZURE_OPENAI_AUDIO_LLM_DEPLOYMENT_NAME"
    )
    AZURE_OPENAI_AUDIO_LLM_API_VERSION = os.getenv("AZURE_OPENAI_AUDIO_LLM_API_VERSION")
    AZURE_OPENAI_AUDIO_LLM_ENDPOINT = os.getenv("AZURE_OPENAI_AUDIO_LLM_ENDPOINT")
    AZURE_OPENAI_AUDIO_LLM_API_KEY = os.getenv("AZURE_OPENAI_AUDIO_LLM_API_KEY")

    # Azure Blob Storage Access
    AZ_TENANT_ID = os.getenv("AZ_TENANT_ID")
    AZ_CLIENT_ID = os.getenv("AZ_CLIENT_ID")
    AZ_SECRET_ID = os.getenv("AZ_SECRET_ID")
    DFS_ACCOUNT_URL = os.getenv("DFS_ACCOUNT_URL")
    BLOB_ACCOUNT_URL = os.getenv("BLOB_ACCOUNT_URL")
    BLOB_CONTAINER_NAME = os.getenv("BLOB_CONTAINER_NAME")

    # Snowflake Access
    SF_MAIN_ACCOUNT = os.getenv("SF_MAIN_ACCOUNT")
    SF_MAIN_USER = os.getenv("SF_MAIN_USER")
    SF_MAIN_PASSWORD = os.getenv("SF_MAIN_PASSWORD")
    SF_MAIN_ROLE = os.getenv("SF_MAIN_ROLE")
    SF_MAIN_WH = os.getenv("SF_MAIN_WH")
    SF_MAIN_DB = os.getenv("SF_MAIN_DB")
    SF_MAIN_SCHEMA = os.getenv("SF_MAIN_SCHEMA")

    SF_KP_ACCOUNT = os.getenv("SF_KP_ACCOUNT")
    SF_KP_USER = os.getenv("SF_KP_USER")
    SF_KP_PASSWORD = os.getenv("SF_KP_PASSWORD")
    SF_KP_ROLE = os.getenv("SF_KP_ROLE")
    SF_KP_WH = os.getenv("SF_KP_WH")
    SF_KP_DB = os.getenv("SF_KP_DB")
    SF_KP_SCHEMA = os.getenv("SF_KP_SCHEMA")
    SF_KP_STAGE = os.getenv("SF_KP_STAGE")
    SF_KP_SM = os.getenv("SF_KP_SM")

    SF_MILAHI_ACCOUNT = os.getenv("SF_MILAHI_ACCOUNT")
    SF_MILAHI_ROLE = os.getenv("SF_MILAHI_ROLE")
    SF_MILAHI_WH = os.getenv("SF_MILAHI_WH")
    SF_MILAHI_DB = os.getenv("SF_MILAHI_DB")
    SF_MILAHI_SCHEMA = os.getenv("SF_MILAHI_SCHEMA")
    SF_MILAHI_STAGE = os.getenv("SF_MILAHI_STAGE")
    SF_MILAHI_SM = os.getenv("SF_MILAHI_SM")

    # Qdrant Access
    VEC_DB_URL = os.getenv("VEC_DB_URL")
    VEC_DB_API_KEY = os.getenv("VEC_DB_API_KEY")

    # Web search service
    BING_SEARCH_URL = os.getenv("BING_SEARCH_URL")
    BING_SUBSCRIPTION_KEY = os.getenv("BING_SUBSCRIPTION_KEY")

    # Email service
    ACS_CONNECTION_STRING = os.getenv("ACS_CONNECTION_STRING")


config_by_name = dict(
    dev=DevelopmentConfig,
    test=TestingConfig,
    prod=ProductionConfig,
)
config = config_by_name[env_name]
