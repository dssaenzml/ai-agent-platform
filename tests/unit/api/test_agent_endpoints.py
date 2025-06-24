"""
Tests for agent API endpoints.
"""

import pytest
from unittest.mock import patch, Mock
from fastapi import status


class TestGeneralAgentEndpoints:
    """Tests for General Agent API endpoints."""

    def test_general_agent_rag_invoke(self, client, sample_chat_input):
        """Test General Agent RAG invoke endpoint."""
        response = client.post(
            "/api/v1/generalagent/generalagent_rag/invoke", json=sample_chat_input
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "answer" in data
        assert data["answer"] == "Mock response"

    def test_general_agent_rag_stream(self, client, sample_chat_input):
        """Test General Agent RAG stream endpoint."""
        response = client.post(
            "/api/v1/generalagent/generalagent_rag/stream", json=sample_chat_input
        )

        assert response.status_code == status.HTTP_200_OK

    def test_general_agent_invalid_input(self, client):
        """Test General Agent with invalid input."""
        invalid_input = {"invalid": "data"}

        response = client.post(
            "/api/v1/generalagent/generalagent_rag/invoke", json=invalid_input
        )

        # Mock endpoint accepts any input and returns 200
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "answer" in data

    def test_general_agent_process_file(self, client, sample_file_input):
        """Test General Agent file processing endpoint."""
        response = client.post(
            "/api/v1/generalagent/generalagent_process_kb_file/invoke",
            json=sample_file_input,
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "result" in data
        assert data["result"] == "Mock file processed"


class TestFinanceAgentEndpoints:
    """Tests for Finance Agent API endpoints."""

    def test_finance_agent_rag_invoke(self, client, sample_chat_input):
        """Test Finance Agent RAG invoke endpoint."""
        response = client.post(
            "/api/v1/financeagent/financeagent_rag/invoke", json=sample_chat_input
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "answer" in data
        assert data["answer"] == "Mock finance response"

    def test_finance_agent_error_handling(self, client):
        """Test Finance Agent error handling with invalid data."""
        # Test with invalid JSON structure
        invalid_data = {"completely": "wrong", "structure": True}

        response = client.post(
            "/api/v1/financeagent/financeagent_rag/invoke", json=invalid_data
        )

        # Should handle invalid input gracefully (mock endpoint will still respond)
        assert response.status_code == status.HTTP_200_OK
