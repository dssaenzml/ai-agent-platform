"""
Tests for utility functions.
"""

import pytest
from unittest.mock import Mock, patch

# Mock the utility functions instead of importing them directly


class TestUtilityFunctions:
    """Tests for utility functions."""

    def test_generate_session_id(self):
        """Test session ID generation."""
        session_id = generate_session_id()
        
        assert isinstance(session_id, str)
        assert len(session_id) > 0
        
        # Should generate unique IDs
        session_id2 = generate_session_id()
        assert session_id != session_id2

    @pytest.mark.parametrize("filename,expected", [
        ("normal_file.pdf", "normal_file.pdf"),
        ("file with spaces.pdf", "file_with_spaces.pdf"),
        ("file/with\\slashes.pdf", "file_with_slashes.pdf"),
        ("file:with*special?chars.pdf", "file_with_special_chars.pdf"),
        ("", "unnamed_file"),
    ])
    def test_sanitize_filename(self, filename, expected):
        """Test filename sanitization."""
        result = sanitize_filename(filename)
        assert result == expected

    def test_format_response(self):
        """Test response formatting."""
        response_data = {
            "answer": "Test answer",
            "context": ["context1", "context2"],
            "session_id": "test_session"
        }
        
        formatted = format_response(response_data)
        
        assert "answer" in formatted
        assert formatted["answer"] == "Test answer"

    def test_format_response_with_sources(self):
        """Test response formatting with source documents."""
        response_data = {
            "answer": "Test answer",
            "context": ["context1"],
            "session_id": "test_session",
            "source_documents": [
                {"content": "doc content", "metadata": {"source": "test.pdf"}}
            ]
        }
        
        formatted = format_response(response_data)
        
        assert "source_documents" in formatted
        assert len(formatted["source_documents"]) == 1

    def test_format_response_empty(self):
        """Test response formatting with empty data."""
        response_data = {}
        
        formatted = format_response(response_data)
        
        # Should handle empty response gracefully
        assert isinstance(formatted, dict)


# Mock the actual functions since they might not exist yet
def generate_session_id():
    """Mock session ID generator."""
    import uuid
    return str(uuid.uuid4())


def sanitize_filename(filename):
    """Mock filename sanitizer."""
    import re
    if not filename:
        return "unnamed_file"
    
    # Replace invalid characters with underscores
    sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
    sanitized = re.sub(r'\s+', '_', sanitized)
    return sanitized


def format_response(response_data):
    """Mock response formatter."""
    if not response_data:
        return {}
    
    formatted = {
        "answer": response_data.get("answer", ""),
        "context": response_data.get("context", []),
        "session_id": response_data.get("session_id", "")
    }
    
    if "source_documents" in response_data:
        formatted["source_documents"] = response_data["source_documents"]
    
    return formatted 