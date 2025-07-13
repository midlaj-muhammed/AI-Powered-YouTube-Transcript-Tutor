"""
Tests for text processor functionality.
"""

import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.utils.text_processor import TextProcessor

class TestTextProcessor(unittest.TestCase):
    """Test cases for TextProcessor class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.api_key = "test_api_key"
        self.processor = TextProcessor(self.api_key)
    
    def test_initialization(self):
        """Test TextProcessor initialization."""
        self.assertEqual(self.processor.openai_api_key, self.api_key)
        self.assertIsNotNone(self.processor.embeddings)
        self.assertIsNotNone(self.processor.llm)
    
    def test_create_documents_from_text(self):
        """Test document creation from text."""
        text = "This is a test transcript. It has multiple sentences."
        metadata = {"video_id": "test123", "title": "Test Video"}
        
        documents = self.processor.create_documents_from_text(text, metadata)
        
        self.assertIsInstance(documents, list)
        self.assertGreater(len(documents), 0)
        
        # Check first document
        first_doc = documents[0]
        self.assertIn("test transcript", first_doc.page_content.lower())
        self.assertEqual(first_doc.metadata["video_id"], "test123")
        self.assertEqual(first_doc.metadata["title"], "Test Video")
    
    def test_create_documents_from_text_no_metadata(self):
        """Test document creation without metadata."""
        text = "Simple test text."
        
        documents = self.processor.create_documents_from_text(text)
        
        self.assertIsInstance(documents, list)
        self.assertGreater(len(documents), 0)
        self.assertEqual(documents[0].metadata, {})
    
    @patch('src.utils.text_processor.FAISS')
    def test_create_vector_store_success(self, mock_faiss):
        """Test successful vector store creation."""
        mock_vectorstore = MagicMock()
        mock_faiss.from_documents.return_value = mock_vectorstore
        
        documents = [MagicMock()]
        result = self.processor.create_vector_store(documents)
        
        self.assertEqual(result, mock_vectorstore)
        mock_faiss.from_documents.assert_called_once_with(documents, self.processor.embeddings)
    
    def test_create_vector_store_empty_documents(self):
        """Test vector store creation with empty documents."""
        result = self.processor.create_vector_store([])
        self.assertIsNone(result)
    
    @patch('src.utils.text_processor.FAISS')
    def test_create_vector_store_failure(self, mock_faiss):
        """Test vector store creation failure."""
        mock_faiss.from_documents.side_effect = Exception("Test error")
        
        documents = [MagicMock()]
        result = self.processor.create_vector_store(documents)
        
        self.assertIsNone(result)
    
    @patch('src.utils.text_processor.RetrievalQA')
    def test_create_qa_chain_success(self, mock_retrieval_qa):
        """Test successful QA chain creation."""
        mock_qa_chain = MagicMock()
        mock_retrieval_qa.from_chain_type.return_value = mock_qa_chain
        
        mock_vectorstore = MagicMock()
        mock_retriever = MagicMock()
        mock_vectorstore.as_retriever.return_value = mock_retriever
        
        result = self.processor.create_qa_chain(mock_vectorstore)
        
        self.assertEqual(result, mock_qa_chain)
        mock_vectorstore.as_retriever.assert_called_once()
        mock_retrieval_qa.from_chain_type.assert_called_once()
    
    @patch('src.utils.text_processor.RetrievalQA')
    def test_create_qa_chain_failure(self, mock_retrieval_qa):
        """Test QA chain creation failure."""
        mock_retrieval_qa.from_chain_type.side_effect = Exception("Test error")
        
        mock_vectorstore = MagicMock()
        result = self.processor.create_qa_chain(mock_vectorstore)
        
        self.assertIsNone(result)
    
    def test_ask_question_success(self):
        """Test successful question asking."""
        mock_qa_chain = MagicMock()
        mock_qa_chain.return_value = {
            'result': 'Test answer',
            'source_documents': [MagicMock()]
        }
        
        question = "What is this about?"
        result = self.processor.ask_question(mock_qa_chain, question)
        
        self.assertTrue(result['success'])
        self.assertEqual(result['answer'], 'Test answer')
        self.assertIsNotNone(result['source_documents'])
        self.assertIsNone(result['error'])
        
        mock_qa_chain.assert_called_once_with({"query": question})
    
    def test_ask_question_failure(self):
        """Test question asking failure."""
        mock_qa_chain = MagicMock()
        mock_qa_chain.side_effect = Exception("Test error")
        
        question = "What is this about?"
        result = self.processor.ask_question(mock_qa_chain, question)
        
        self.assertFalse(result['success'])
        self.assertIsNone(result['answer'])
        self.assertEqual(result['source_documents'], [])
        self.assertIsNotNone(result['error'])
    
    @patch.object(TextProcessor, 'create_qa_chain')
    @patch.object(TextProcessor, 'create_vector_store')
    @patch.object(TextProcessor, 'create_documents_from_text')
    def test_process_transcript_success(self, mock_create_docs, mock_create_vs, mock_create_qa):
        """Test successful transcript processing."""
        # Setup mocks
        mock_documents = [MagicMock()]
        mock_vectorstore = MagicMock()
        mock_qa_chain = MagicMock()
        
        mock_create_docs.return_value = mock_documents
        mock_create_vs.return_value = mock_vectorstore
        mock_create_qa.return_value = mock_qa_chain
        
        transcript_text = "Test transcript text"
        metadata = {"video_id": "test123"}
        
        result = self.processor.process_transcript(transcript_text, metadata)
        
        self.assertTrue(result['success'])
        self.assertEqual(result['qa_chain'], mock_qa_chain)
        self.assertEqual(result['vectorstore'], mock_vectorstore)
        self.assertEqual(result['documents'], mock_documents)
        self.assertIsNone(result['error'])
        
        mock_create_docs.assert_called_once_with(transcript_text, metadata)
        mock_create_vs.assert_called_once_with(mock_documents)
        mock_create_qa.assert_called_once_with(mock_vectorstore)
    
    @patch.object(TextProcessor, 'create_documents_from_text')
    def test_process_transcript_document_creation_failure(self, mock_create_docs):
        """Test transcript processing with document creation failure."""
        mock_create_docs.return_value = []
        
        transcript_text = "Test transcript text"
        result = self.processor.process_transcript(transcript_text)
        
        self.assertFalse(result['success'])
        self.assertIsNone(result['qa_chain'])
        self.assertIsNone(result['vectorstore'])
        self.assertIsNone(result['documents'])
        self.assertEqual(result['error'], "Failed to create documents from transcript")
    
    @patch.object(TextProcessor, 'create_vector_store')
    @patch.object(TextProcessor, 'create_documents_from_text')
    def test_process_transcript_vectorstore_creation_failure(self, mock_create_docs, mock_create_vs):
        """Test transcript processing with vector store creation failure."""
        mock_create_docs.return_value = [MagicMock()]
        mock_create_vs.return_value = None
        
        transcript_text = "Test transcript text"
        result = self.processor.process_transcript(transcript_text)
        
        self.assertFalse(result['success'])
        self.assertIsNone(result['qa_chain'])
        self.assertIsNone(result['vectorstore'])
        self.assertIsNotNone(result['documents'])
        self.assertEqual(result['error'], "Failed to create vector store")
    
    @patch.object(TextProcessor, 'create_qa_chain')
    @patch.object(TextProcessor, 'create_vector_store')
    @patch.object(TextProcessor, 'create_documents_from_text')
    def test_process_transcript_qa_chain_creation_failure(self, mock_create_docs, mock_create_vs, mock_create_qa):
        """Test transcript processing with QA chain creation failure."""
        mock_create_docs.return_value = [MagicMock()]
        mock_create_vs.return_value = MagicMock()
        mock_create_qa.return_value = None
        
        transcript_text = "Test transcript text"
        result = self.processor.process_transcript(transcript_text)
        
        self.assertFalse(result['success'])
        self.assertIsNone(result['qa_chain'])
        self.assertIsNotNone(result['vectorstore'])
        self.assertIsNotNone(result['documents'])
        self.assertEqual(result['error'], "Failed to create QA chain")

if __name__ == '__main__':
    unittest.main()
