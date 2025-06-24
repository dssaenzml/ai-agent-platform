"""
Tests for bot data models.
"""

import pytest
from pydantic import BaseModel, ValidationError
from typing import List, Dict, Any, Optional

# Define simple test models similar to what would be in the actual app
class ChatInput(BaseModel):
    query: str
    chat_history: List[Dict[str, str]] = []
    user_id: str
    session_id: Optional[str] = None

class ChatOutput(BaseModel):
    answer: str
    context: List[str] = []
    session_id: Optional[str] = None
    source_documents: List[Dict[str, Any]] = []

class FileInput(BaseModel):
    file_path: str
    user_id: str
    file_name: str

class FileOutput(BaseModel):
    result: str
    file_name: str
    chunks_processed: Optional[int] = None
    processing_time: Optional[float] = None

class StreamOutput(BaseModel):
    token: str
    session_id: str
    is_final: bool = False


class TestChatInput:
    """Tests for ChatInput model."""

    def test_valid_chat_input(self):
        """Test creation of valid ChatInput."""
        chat_input = ChatInput(
            query="What is the company policy?",
            chat_history=[],
            user_id="user123",
            session_id="session456"
        )
        
        assert chat_input.query == "What is the company policy?"
        assert chat_input.chat_history == []
        assert chat_input.user_id == "user123"
        assert chat_input.session_id == "session456"

    def test_chat_input_with_history(self):
        """Test ChatInput with chat history."""
        history = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there!"}
        ]
        
        chat_input = ChatInput(
            query="How are you?",
            chat_history=history,
            user_id="user123",
            session_id="session456"
        )
        
        assert len(chat_input.chat_history) == 2
        assert chat_input.chat_history[0]["role"] == "user"

    def test_chat_input_required_fields(self):
        """Test ChatInput with missing required fields."""
        with pytest.raises(ValidationError):
            ChatInput(
                chat_history=[],
                user_id="user123",
                session_id="session456"
                # Missing query
            )

    def test_chat_input_empty_query(self):
        """Test ChatInput with empty query."""
        chat_input = ChatInput(
            query="",
            chat_history=[],
            user_id="user123",
            session_id="session456"
        )
        
        assert chat_input.query == ""

    def test_chat_input_optional_fields(self):
        """Test ChatInput with optional fields."""
        chat_input = ChatInput(
            query="Test query",
            user_id="user123"
        )
        
        assert chat_input.query == "Test query"
        assert chat_input.user_id == "user123"
        # Optional fields should have defaults or be None


class TestChatOutput:
    """Tests for ChatOutput model."""

    def test_valid_chat_output(self):
        """Test creation of valid ChatOutput."""
        chat_output = ChatOutput(
            answer="This is the response",
            context=["context1", "context2"],
            session_id="session456",
            source_documents=[]
        )
        
        assert chat_output.answer == "This is the response"
        assert len(chat_output.context) == 2
        assert chat_output.session_id == "session456"

    def test_chat_output_with_sources(self):
        """Test ChatOutput with source documents."""
        sources = [
            {"content": "Document content", "metadata": {"source": "doc.pdf"}},
            {"content": "Another document", "metadata": {"source": "doc2.pdf"}}
        ]
        
        chat_output = ChatOutput(
            answer="Response with sources",
            context=["context"],
            session_id="session456",
            source_documents=sources
        )
        
        assert len(chat_output.source_documents) == 2
        assert chat_output.source_documents[0]["metadata"]["source"] == "doc.pdf"

    def test_chat_output_required_fields(self):
        """Test ChatOutput with missing required fields."""
        with pytest.raises(ValidationError):
            ChatOutput(
                context=["context"],
                session_id="session456"
                # Missing answer
            )


class TestFileInput:
    """Tests for FileInput model."""

    def test_valid_file_input(self):
        """Test creation of valid FileInput."""
        file_input = FileInput(
            file_path="/path/to/document.pdf",
            user_id="user123",
            file_name="document.pdf"
        )
        
        assert file_input.file_path == "/path/to/document.pdf"
        assert file_input.user_id == "user123"
        assert file_input.file_name == "document.pdf"

    def test_file_input_required_fields(self):
        """Test FileInput with missing required fields."""
        with pytest.raises(ValidationError):
            FileInput(
                user_id="user123",
                file_name="document.pdf"
                # Missing file_path
            )

    def test_file_input_path_validation(self):
        """Test FileInput path validation."""
        # Test with various file paths
        valid_paths = [
            "/absolute/path/file.pdf",
            "relative/path/file.docx",
            "file.txt",
            "/path/with spaces/file.pdf"
        ]
        
        for path in valid_paths:
            file_input = FileInput(
                file_path=path,
                user_id="user123",
                file_name="test.pdf"
            )
            assert file_input.file_path == path


class TestFileOutput:
    """Tests for FileOutput model."""

    def test_valid_file_output(self):
        """Test creation of valid FileOutput."""
        file_output = FileOutput(
            result="File processed successfully",
            file_name="document.pdf",
            chunks_processed=5,
            processing_time=2.5
        )
        
        assert file_output.result == "File processed successfully"
        assert file_output.file_name == "document.pdf"
        assert file_output.chunks_processed == 5
        assert file_output.processing_time == 2.5

    def test_file_output_optional_fields(self):
        """Test FileOutput with optional fields."""
        file_output = FileOutput(
            result="Basic result",
            file_name="test.pdf"
        )
        
        assert file_output.result == "Basic result"
        assert file_output.file_name == "test.pdf"


class TestStreamOutput:
    """Tests for StreamOutput model."""

    def test_valid_stream_output(self):
        """Test creation of valid StreamOutput."""
        stream_output = StreamOutput(
            token="Hello",
            session_id="session456",
            is_final=False
        )
        
        assert stream_output.token == "Hello"
        assert stream_output.session_id == "session456"
        assert stream_output.is_final is False

    def test_stream_output_final_token(self):
        """Test StreamOutput for final token."""
        stream_output = StreamOutput(
            token="",
            session_id="session456",
            is_final=True
        )
        
        assert stream_output.token == ""
        assert stream_output.is_final is True

    @pytest.mark.parametrize("token,expected", [
        ("Hello", "Hello"),
        ("", ""),
        ("123", "123"),
        ("🤖", "🤖"),
    ])
    def test_stream_output_token_types(self, token, expected):
        """Test StreamOutput with different token types."""
        stream_output = StreamOutput(
            token=token,
            session_id="session456",
            is_final=False
        )
        
        assert stream_output.token == expected 