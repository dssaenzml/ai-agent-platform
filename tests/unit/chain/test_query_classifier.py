"""
Tests for query classification chain.
"""

import pytest
from unittest.mock import Mock, patch
from app.chain.query_classifier import QueryClassifier


class TestQueryClassifier:
    """Tests for QueryClassifier functionality."""

    @pytest.fixture
    def classifier(self, mock_llm):
        """Create QueryClassifier instance with mocked LLM."""
        return QueryClassifier(mock_llm)

    def test_classify_rag_query(self, classifier):
        """Test classification of RAG queries."""
        # Mock LLM response for RAG query
        classifier.llm.invoke.return_value = "rag_query"
        
        result = classifier.classify("What is the company policy on remote work?")
        
        assert result == "rag_query"
        classifier.llm.invoke.assert_called_once()

    def test_classify_web_search_query(self, classifier):
        """Test classification of web search queries."""
        classifier.llm.invoke.return_value = "web_search"
        
        result = classifier.classify("What is the current weather in New York?")
        
        assert result == "web_search"

    def test_classify_image_generation_query(self, classifier):
        """Test classification of image generation queries."""
        classifier.llm.invoke.return_value = "image_generation"
        
        result = classifier.classify("Generate an image of a sunset over mountains")
        
        assert result == "image_generation"

    def test_classify_file_generation_query(self, classifier):
        """Test classification of file generation queries."""
        classifier.llm.invoke.return_value = "file_generation"
        
        result = classifier.classify("Create a PowerPoint presentation about AI")
        
        assert result == "file_generation"

    def test_classify_empty_query(self, classifier):
        """Test classification of empty query."""
        classifier.llm.invoke.return_value = "rag_query"
        
        result = classifier.classify("")
        
        assert result == "rag_query"

    def test_classify_invalid_llm_response(self, classifier):
        """Test handling of invalid LLM response."""
        classifier.llm.invoke.return_value = "invalid_category"
        
        # Should default to rag_query for unknown categories
        result = classifier.classify("Some query")
        
        assert result == "rag_query"

    def test_classify_llm_exception(self, classifier):
        """Test handling of LLM exceptions."""
        classifier.llm.invoke.side_effect = Exception("LLM Error")
        
        # Should handle exception gracefully and default to rag_query
        result = classifier.classify("Some query")
        
        assert result == "rag_query"

    @pytest.mark.parametrize("query,expected", [
        ("What is the company revenue?", "rag_query"),
        ("Search for latest AI news", "web_search"),
        ("Create a chart showing sales data", "image_generation"),
        ("Generate a report document", "file_generation"),
    ])
    def test_classify_multiple_queries(self, classifier, query, expected):
        """Test classification of multiple query types."""
        classifier.llm.invoke.return_value = expected
        
        result = classifier.classify(query)
        
        assert result == expected 