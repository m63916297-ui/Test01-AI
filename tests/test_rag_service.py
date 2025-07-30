import pytest
from unittest.mock import Mock, patch
from app.services.rag_service import RAGService


class TestRAGService:
    
    @pytest.fixture
    def rag_service(self):
        with patch('app.services.rag_service.SentenceTransformer'):
            with patch('app.services.rag_service.chromadb'):
                return RAGService()
    
    def test_retrieve_documents_empty_collection(self, rag_service):
        """Test retrieving documents from empty collection"""
        # Mock empty collection
        mock_collection = Mock()
        mock_collection.query.return_value = {
            'documents': [[]],
            'metadatas': [[]],
            'distances': [[]]
        }
        
        rag_service.client.get_collection.return_value = mock_collection
        
        documents = rag_service.retrieve_documents("test question", "test_chat_id")
        
        assert documents == []
    
    def test_retrieve_documents_with_results(self, rag_service):
        """Test retrieving documents with results"""
        # Mock collection with results
        mock_collection = Mock()
        mock_collection.query.return_value = {
            'documents': [['Document 1', 'Document 2']],
            'metadatas': [[{'source_url': 'http://test.com'}, {'source_url': 'http://test2.com'}]],
            'distances': [[0.1, 0.3]]
        }
        
        rag_service.client.get_collection.return_value = mock_collection
        
        documents = rag_service.retrieve_documents("test question", "test_chat_id")
        
        assert len(documents) == 2
        assert documents[0]['content'] == 'Document 1'
        assert documents[0]['similarity_score'] == 0.9  # 1 - 0.1
        assert documents[1]['content'] == 'Document 2'
        assert documents[1]['similarity_score'] == 0.7  # 1 - 0.3
    
    def test_format_context_empty_documents(self, rag_service):
        """Test formatting context with empty documents"""
        context = rag_service.format_context([])
        assert context == "No se encontró información relevante en la documentación."
    
    def test_format_context_with_documents(self, rag_service):
        """Test formatting context with documents"""
        documents = [
            {
                'content': 'Test content 1',
                'metadata': {'source_url': 'http://test.com'}
            },
            {
                'content': 'Test content 2',
                'metadata': {'source_url': 'http://test2.com'}
            }
        ]
        
        context = rag_service.format_context(documents)
        
        assert 'Documento 1' in context
        assert 'Documento 2' in context
        assert 'Test content 1' in context
        assert 'Test content 2' in context
        assert 'http://test.com' in context
        assert 'http://test2.com' in context 