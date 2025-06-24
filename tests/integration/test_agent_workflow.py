"""
Integration tests for agent workflow.
"""

import pytest
from unittest.mock import patch, Mock


@pytest.mark.integration
class TestAgentWorkflowIntegration:
    """Integration tests for complete agent workflow."""

    @patch('app.vector_db.agent_general.kbm')
    @patch('app.llm_model.azure_llm.AzureOpenAI')
    def test_general_agent_complete_workflow(self, mock_llm, mock_kbm, client):
        """Test complete General Agent workflow from API to response."""
        # Mock knowledge base search
        mock_kbm.similarity_search.return_value = [
            Mock(page_content="Company policy states remote work is allowed", 
                 metadata={"source": "policy.pdf"})
        ]
        
        # Mock LLM response
        mock_llm.invoke.return_value = "Based on the company policy, remote work is indeed allowed."
        
        # Test the complete workflow
        request_data = {
            "input": {
                "query": "Is remote work allowed?",
                "chat_history": [],
                "user_id": "test_user",
                "session_id": "test_session"
            },
            "config": {
                "configurable": {
                    "session_id": "test_session",
                    "user_id": "test_user"
                }
            }
        }
        
        response = client.post(
            "/api/v1/generalagent/generalagent_rag/invoke",
            json=request_data
        )
        
        assert response.status_code == 200
        # Verify the workflow executed properly
        mock_kbm.similarity_search.assert_called()

    @pytest.mark.slow
    @patch('app.vector_db.agent_general.kbm')
    def test_file_processing_workflow(self, mock_kbm, client):
        """Test file processing workflow integration."""
        # Mock successful file processing
        mock_kbm.add_documents.return_value = ["doc_id_1", "doc_id_2"]
        
        request_data = {
            "input": {
                "file_path": "/test/document.pdf",
                "user_id": "test_user",
                "file_name": "document.pdf"
            },
            "config": {
                "configurable": {
                    "user_id": "test_user"
                }
            }
        }
        
        response = client.post(
            "/api/v1/generalagent/generalagent_process_kb_file/invoke",
            json=request_data
        )
        
        # Should process the file successfully
        assert response.status_code == 200

    @pytest.mark.api
    def test_health_check_integration(self, client):
        """Test health check integration."""
        response = client.get("/health")
        
        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}

    @pytest.mark.db
    @patch('app.vector_db.agent_finance.kbm')
    def test_finance_agent_with_vector_db(self, mock_kbm, client):
        """Test Finance Agent integration with vector database."""
        # Mock financial data retrieval
        mock_kbm.similarity_search.return_value = [
            Mock(page_content="Q4 revenue was $1M", metadata={"source": "financial_report.pdf"})
        ]
        
        request_data = {
            "input": {
                "query": "What was the Q4 revenue?",
                "chat_history": [],
                "user_id": "test_user",
                "session_id": "test_session"
            },
            "config": {
                "configurable": {
                    "session_id": "test_session",
                    "user_id": "test_user"
                }
            }
        }
        
        response = client.post(
            "/api/v1/financeagent/financeagent_rag/invoke",
            json=request_data
        )
        
        assert response.status_code == 200
        mock_kbm.similarity_search.assert_called()

    def test_multiple_agent_endpoints(self, client):
        """Test that multiple agent endpoints are available."""
        endpoints = [
            "/api/v1/generalagent/generalagent_rag/invoke",
            "/api/v1/financeagent/financeagent_rag/invoke",
            "/api/v1/engineeringagent/engineeringagent_rag/invoke",
            "/api/v1/hragent/hragent_rag/invoke"
        ]
        
        request_data = {
            "input": {
                "query": "Test query",
                "user_id": "test_user",
                "session_id": "test_session"
            },
            "config": {
                "configurable": {
                    "session_id": "test_session",
                    "user_id": "test_user"
                }
            }
        }
        
        for endpoint in endpoints:
            response = client.post(endpoint, json=request_data)
            # Should at least reach the endpoint (may fail due to mocking, but shouldn't 404)
            assert response.status_code != 404 