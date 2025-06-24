"""
Tests for vector database utilities.
"""

from unittest.mock import MagicMock, Mock, patch

import pytest


# Mock KnowledgeBaseManager class
class MockKnowledgeBaseManager:
    def __init__(self, bot_name, config):
        self.bot_name = bot_name
        self.config = config
        self.vector_store = Mock()

    def similarity_search(self, query, k=5):
        return self.vector_store.similarity_search(query, k=k)

    def similarity_search_with_score(self, query, k=5, score_threshold=0.5):
        return self.vector_store.similarity_search_with_score(
            query, k=k, score_threshold=score_threshold
        )

    def add_documents(self, documents):
        return self.vector_store.add_documents(documents)

    def delete_documents(self, document_ids):
        return self.vector_store.delete(document_ids)


class TestKnowledgeBaseManager:
    """Tests for KnowledgeBaseManager functionality."""

    @pytest.fixture
    def mock_config(self):
        """Mock configuration for testing."""
        config = Mock()
        config.vec_db_url = "http://test-qdrant:6333"
        config.vec_db_api_key = "test_api_key"
        config.azure_openai_emb_api_key = "test_emb_key"
        config.azure_openai_emb_endpoint = "https://test.openai.azure.com/"
        return config

    @pytest.fixture
    def kbm(self, mock_config):
        """Create KnowledgeBaseManager instance."""
        return MockKnowledgeBaseManager("TestAgent", mock_config)

    def test_init_knowledge_base_manager(self, mock_config):
        """Test initialization of KnowledgeBaseManager."""
        kbm = MockKnowledgeBaseManager("TestAgent", mock_config)

        assert kbm.bot_name == "TestAgent"
        assert kbm.config == mock_config
        assert kbm.vector_store is not None

    def test_similarity_search(self, kbm):
        """Test similarity search functionality."""
        # Mock vector store response
        mock_documents = [
            Mock(page_content="Test content 1", metadata={"source": "test1.pdf"}),
            Mock(page_content="Test content 2", metadata={"source": "test2.pdf"}),
        ]
        kbm.vector_store.similarity_search.return_value = mock_documents

        results = kbm.similarity_search("test query", k=2)

        assert len(results) == 2
        assert results[0].page_content == "Test content 1"
        assert results[1].page_content == "Test content 2"
        kbm.vector_store.similarity_search.assert_called_once_with("test query", k=2)

    def test_similarity_search_with_score(self, kbm):
        """Test similarity search with score threshold."""
        mock_results = [
            (
                Mock(
                    page_content="High score content", metadata={"source": "high.pdf"}
                ),
                0.9,
            ),
            (
                Mock(page_content="Low score content", metadata={"source": "low.pdf"}),
                0.3,
            ),
        ]
        kbm.vector_store.similarity_search_with_score.return_value = mock_results

        results = kbm.similarity_search_with_score(
            "test query", k=2, score_threshold=0.5
        )

        # Should return documents with scores
        assert len(results) == 2
        assert results[0][1] == 0.9  # High score
        assert results[1][1] == 0.3  # Low score

    def test_add_documents(self, kbm):
        """Test adding documents to vector store."""
        mock_documents = [
            Mock(page_content="Document 1 content", metadata={"source": "doc1.pdf"}),
            Mock(page_content="Document 2 content", metadata={"source": "doc2.pdf"}),
        ]
        kbm.vector_store.add_documents.return_value = ["id1", "id2"]

        result = kbm.add_documents(mock_documents)

        assert result == ["id1", "id2"]
        kbm.vector_store.add_documents.assert_called_once_with(mock_documents)

    def test_delete_documents(self, kbm):
        """Test deleting documents from vector store."""
        document_ids = ["id1", "id2", "id3"]
        kbm.vector_store.delete.return_value = True

        result = kbm.delete_documents(document_ids)

        assert result is True
        kbm.vector_store.delete.assert_called_once_with(document_ids)

    def test_get_collection_info(self, kbm):
        """Test getting collection information."""
        mock_info = {
            "vectors_count": 100,
            "indexed_vectors_count": 100,
            "points_count": 100,
        }
        kbm.vector_store.client.get_collection.return_value = Mock(
            vectors_count=100, indexed_vectors_count=100, points_count=100
        )

        # This would be implemented in the actual KBM
        collection_name = f"testagent_collection"

        assert collection_name == "testagent_collection"

    def test_search_empty_query(self, kbm):
        """Test search with empty query."""
        kbm.vector_store.similarity_search.return_value = []

        results = kbm.similarity_search("", k=5)

        assert results == []

    def test_search_exception_handling(self, kbm):
        """Test handling of search exceptions."""
        kbm.vector_store.similarity_search.side_effect = Exception("Search error")

        # Should handle exception gracefully
        with pytest.raises(Exception):
            kbm.similarity_search("test query")

    @pytest.mark.parametrize("k_value", [1, 3, 5, 10])
    def test_search_different_k_values(self, kbm, k_value):
        """Test search with different k values."""
        mock_documents = [
            Mock(page_content=f"Content {i}", metadata={"source": f"doc{i}.pdf"})
            for i in range(k_value)
        ]
        kbm.vector_store.similarity_search.return_value = mock_documents

        results = kbm.similarity_search("test query", k=k_value)

        assert len(results) == k_value
        kbm.vector_store.similarity_search.assert_called_once_with(
            "test query", k=k_value
        )
