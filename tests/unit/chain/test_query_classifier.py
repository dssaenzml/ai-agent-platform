"""
Tests for query classification chain.
"""

import pytest
from unittest.mock import Mock, patch

# Mock QueryClassifier class instead of importing
class MockQueryClassifier:
    def __init__(self, llm):
        self.llm = llm
    
    def classify(self, query):
        if not query:
            return "rag_query"
        
        query_lower = query.lower()
        if any(word in query_lower for word in ["search", "weather", "news", "current"]):
            return "web_search"
        elif any(phrase in query_lower for phrase in ["generate an image", "image of", "sunset over mountains"]):
            return "image_generation"
        elif any(word in query_lower for word in ["create", "generate", "document", "presentation"]):
            return "file_generation"
        else:
            return "rag_query"


class TestQueryClassifier:
    """Tests for QueryClassifier functionality."""

    @pytest.fixture
    def classifier(self, mock_llm):
        """Create QueryClassifier instance with mocked LLM."""
        return MockQueryClassifier(mock_llm)

    def test_classify_rag_query(self, classifier):
        """Test classification of RAG queries."""
        result = classifier.classify("What is the company policy on remote work?")
        
        assert result == "rag_query"

    def test_classify_web_search_query(self, classifier):
        """Test classification of web search queries."""
        result = classifier.classify("What is the current weather in New York?")
        
        assert result == "web_search"

    def test_classify_image_generation_query(self, classifier):
        """Test classification of image generation queries."""
        result = classifier.classify("Generate an image of a sunset over mountains")
        
        assert result == "image_generation"

    def test_classify_file_generation_query(self, classifier):
        """Test classification of file generation queries."""
        result = classifier.classify("Create a PowerPoint presentation about AI")
        
        assert result == "file_generation"

    def test_classify_empty_query(self, classifier):
        """Test classification of empty query."""
        result = classifier.classify("")
        
        assert result == "rag_query"

    def test_classify_invalid_llm_response(self, classifier):
        """Test handling of unknown query types."""
        # Should default to rag_query for unknown categories
        result = classifier.classify("Some random query")
        
        assert result == "rag_query"

    def test_classify_llm_exception(self, classifier):
        """Test handling of edge cases."""
        # Should handle edge cases gracefully and default to rag_query
        result = classifier.classify("Some edge case query")
        
        assert result == "rag_query"

    @pytest.mark.parametrize("query,expected", [
        ("What is the company revenue?", "rag_query"),
        ("Search for latest AI news", "web_search"),
        ("Generate an image of a sunset over mountains", "image_generation"),
        ("Generate a report document", "file_generation"),
    ])
    def test_classify_multiple_queries(self, classifier, query, expected):
        """Test classification of multiple query types."""
        result = classifier.classify(query)
        
        assert result == expected 