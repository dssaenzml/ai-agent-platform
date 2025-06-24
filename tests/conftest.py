"""
Pytest configuration and shared fixtures for AI Agent Platform tests.
"""

import asyncio
import os
import pytest
from unittest.mock import Mock, patch
from fastapi import FastAPI
from fastapi.testclient import TestClient

# Set test environment variables
os.environ["TESTING"] = "true"
os.environ["AZURE_OPENAI_LLM_API_KEY"] = "test_api_key"
os.environ["AZURE_OPENAI_LLM_ENDPOINT"] = "https://test.openai.azure.com/"
os.environ["VEC_DB_URL"] = "http://test-qdrant:6333"
os.environ["VEC_DB_API_KEY"] = "test_qdrant_key"

# Create a simple test app instead of importing the full app
test_app = FastAPI()

@test_app.get("/health")
async def health_check():
    return {"status": "healthy"}

@test_app.post("/api/v1/generalagent/generalagent_rag/invoke")
async def mock_general_agent_invoke(request: dict):
    return {"answer": "Mock response", "context": [], "session_id": "test"}

@test_app.post("/api/v1/generalagent/generalagent_rag/stream")
async def mock_general_agent_stream(request: dict):
    return "Mock streaming response"

@test_app.post("/api/v1/generalagent/generalagent_process_kb_file/invoke")
async def mock_general_agent_file(request: dict):
    return {"result": "Mock file processed", "file_name": "test.pdf"}

@test_app.post("/api/v1/financeagent/financeagent_rag/invoke")
async def mock_finance_agent_invoke(request: dict):
    return {"answer": "Mock finance response", "context": [], "session_id": "test"}

@test_app.post("/api/v1/engineeringagent/engineeringagent_rag/invoke")
async def mock_engineering_agent_invoke(request: dict):
    return {"answer": "Mock engineering response", "context": [], "session_id": "test"}

@test_app.post("/api/v1/hragent/hragent_rag/invoke")
async def mock_hr_agent_invoke(request: dict):
    return {"answer": "Mock HR response", "context": [], "session_id": "test"}


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def client():
    """Create a test client for FastAPI application."""
    with TestClient(test_app) as test_client:
        yield test_client


@pytest.fixture
def mock_config():
    """Mock configuration for testing."""
    with patch('app.config.config') as mock_cfg:
        mock_cfg.azure_openai_llm_api_key = "test_api_key"
        mock_cfg.azure_openai_llm_endpoint = "https://test.openai.azure.com/"
        mock_cfg.vec_db_url = "http://test-qdrant:6333"
        mock_cfg.vec_db_api_key = "test_qdrant_key"
        mock_cfg.ai_agent_app_name = "test_app"
        yield mock_cfg


@pytest.fixture
def mock_llm():
    """Mock LLM for testing."""
    mock = Mock()
    mock.invoke.return_value = "Test response from LLM"
    mock.stream.return_value = iter(["Test", " streaming", " response"])
    return mock


@pytest.fixture
def mock_kbm():
    """Mock Knowledge Base Manager."""
    mock = Mock()
    mock.similarity_search.return_value = [
        {"content": "Test document content", "metadata": {"source": "test.pdf"}}
    ]
    mock.add_documents.return_value = True
    mock.delete_documents.return_value = True
    return mock


@pytest.fixture
def sample_chat_input():
    """Sample chat input for testing."""
    return {
        "input": {
            "query": "What is the AI Agent Platform?",
            "chat_history": [],
            "user_id": "test_user_123",
            "session_id": "test_session_456"
        },
        "config": {
            "configurable": {
                "session_id": "test_session_456",
                "user_id": "test_user_123"
            }
        }
    }


@pytest.fixture
def sample_file_input():
    """Sample file input for testing."""
    return {
        "input": {
            "file_path": "test_document.pdf",
            "user_id": "test_user_123",
            "file_name": "test_document.pdf"
        },
        "config": {
            "configurable": {
                "user_id": "test_user_123"
            }
        }
    }


@pytest.fixture
def mock_vector_store():
    """Mock vector store for testing."""
    mock = Mock()
    mock.similarity_search.return_value = [
        Mock(page_content="Test content", metadata={"source": "test.pdf"})
    ]
    mock.add_documents.return_value = ["test_id_1"]
    return mock 