"""
Tests for agent API endpoints.
"""

import pytest
from unittest.mock import patch, Mock
from fastapi import status


class TestGeneralAgentEndpoints:
    """Tests for General Agent API endpoints."""

    @patch('app.api.endpoints.agent_general.generalagent_rag_chain')
    def test_general_agent_rag_invoke(self, mock_chain, client, sample_chat_input):
        """Test General Agent RAG invoke endpoint."""
        # Mock the chain response
        mock_chain.invoke.return_value = {
            "answer": "This is a test response from the General Agent",
            "context": ["relevant context"],
            "session_id": "test_session_456"
        }
        
        response = client.post(
            "/api/v1/generalagent/generalagent_rag/invoke",
            json=sample_chat_input
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "answer" in data
        assert data["answer"] == "This is a test response from the General Agent"

    @patch('app.api.endpoints.agent_general.generalagent_rag_chain')
    def test_general_agent_rag_stream(self, mock_chain, client, sample_chat_input):
        """Test General Agent RAG stream endpoint."""
        # Mock the chain streaming response
        mock_chain.stream.return_value = [
            {"answer": "Test"},
            {"answer": " streaming"},
            {"answer": " response"}
        ]
        
        response = client.post(
            "/api/v1/generalagent/generalagent_rag/stream",
            json=sample_chat_input
        )
        
        assert response.status_code == status.HTTP_200_OK
        # For streaming, we expect server-sent events
        assert "text/plain" in response.headers.get("content-type", "")

    def test_general_agent_invalid_input(self, client):
        """Test General Agent with invalid input."""
        invalid_input = {"invalid": "data"}
        
        response = client.post(
            "/api/v1/generalagent/generalagent_rag/invoke",
            json=invalid_input
        )
        
        # Should return validation error
        assert response.status_code in [status.HTTP_422_UNPROCESSABLE_ENTITY, status.HTTP_400_BAD_REQUEST]

    @patch('app.api.endpoints.agent_general.generalagent_process_kb_file_chain')
    def test_general_agent_process_file(self, mock_chain, client, sample_file_input):
        """Test General Agent file processing endpoint."""
        mock_chain.invoke.return_value = {
            "result": "File processed successfully",
            "file_name": "test_document.pdf",
            "chunks_processed": 5
        }
        
        response = client.post(
            "/api/v1/generalagent/generalagent_process_kb_file/invoke",
            json=sample_file_input
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "result" in data
        assert data["result"] == "File processed successfully"


class TestFinanceAgentEndpoints:
    """Tests for Finance Agent API endpoints."""

    @patch('app.api.endpoints.agent_finance.financeagent_rag_chain')
    def test_finance_agent_rag_invoke(self, mock_chain, client, sample_chat_input):
        """Test Finance Agent RAG invoke endpoint."""
        mock_chain.invoke.return_value = {
            "answer": "Financial analysis completed",
            "context": ["financial context"],
            "session_id": "test_session_456"
        }
        
        response = client.post(
            "/api/v1/financeagent/financeagent_rag/invoke",
            json=sample_chat_input
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "answer" in data
        assert "Financial analysis" in data["answer"]

    @patch('app.api.endpoints.agent_finance.financeagent_rag_chain')
    def test_finance_agent_error_handling(self, mock_chain, client, sample_chat_input):
        """Test Finance Agent error handling."""
        # Mock chain to raise an exception
        mock_chain.invoke.side_effect = Exception("Test error")
        
        response = client.post(
            "/api/v1/financeagent/financeagent_rag/invoke",
            json=sample_chat_input
        )
        
        # Should handle error gracefully
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR 