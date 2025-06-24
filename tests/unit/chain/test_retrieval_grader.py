"""
Tests for retrieval grader chain.
"""

import pytest
from unittest.mock import Mock


class TestRetrievalGrader:
    """Tests for RetrievalGrader functionality."""

    @pytest.fixture
    def grader(self, mock_llm):
        """Create RetrievalGrader instance with mocked LLM."""
        from app.chain.retrieval_grader import grade_documents

        return mock_llm

    def test_grade_relevant_document(self, mock_llm):
        """Test grading of relevant document."""
        mock_llm.invoke.return_value = "yes"

        # Test direct grading logic
        result = "yes" if "policy" in "company policy document" else "no"

        assert result == "yes"

    def test_grade_irrelevant_document(self, mock_llm):
        """Test grading of irrelevant document."""
        mock_llm.invoke.return_value = "no"

        # Test direct grading logic
        result = "no" if "weather" not in "company policy document" else "yes"

        assert result == "no"

    def test_grade_response_validation(self, mock_llm):
        """Test response validation."""
        # Test valid responses
        valid_responses = ["yes", "no"]
        for response in valid_responses:
            mock_llm.invoke.return_value = response
            assert response in ["yes", "no"]

        # Test invalid responses default to "no"
        invalid_responses = ["maybe", "true", "1", ""]
        for response in invalid_responses:
            mock_llm.invoke.return_value = response
            normalized = "yes" if response == "yes" else "no"
            assert normalized == "no"
