"""
Tests for session manager functionality.
"""

import unittest
from unittest.mock import patch, MagicMock
import sys
import os
from datetime import datetime

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Mock streamlit before importing session_manager
sys.modules['streamlit'] = MagicMock()

from src.utils.session_manager import SessionManager

class TestSessionManager(unittest.TestCase):
    """Test cases for SessionManager class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Mock streamlit session_state
        self.mock_st = MagicMock()
        self.mock_st.session_state = {}
        
        with patch('src.utils.session_manager.st', self.mock_st):
            self.session_manager = SessionManager()
    
    def test_initialization(self):
        """Test SessionManager initialization."""
        with patch('src.utils.session_manager.st', self.mock_st):
            manager = SessionManager()
            
            # Check that session state variables are initialized
            expected_keys = [
                'chat_history', 'processed_videos', 'current_video',
                'qa_chain', 'vectorstore', 'video_metadata', 'conversation_id'
            ]
            
            for key in expected_keys:
                self.assertIn(key, self.mock_st.session_state)
    
    def test_generate_conversation_id(self):
        """Test conversation ID generation."""
        conv_id = self.session_manager.generate_conversation_id()
        
        self.assertIsInstance(conv_id, str)
        self.assertTrue(conv_id.startswith('conv_'))
        self.assertEqual(len(conv_id), 19)  # conv_ + YYYYMMDD_HHMMSS
    
    def test_add_to_chat_history(self):
        """Test adding entries to chat history."""
        with patch('src.utils.session_manager.st', self.mock_st):
            self.mock_st.session_state = {
                'chat_history': [],
                'conversation_id': 'test_conv_123'
            }
            
            manager = SessionManager()
            
            question = "What is this about?"
            answer = "This is a test answer."
            video_id = "test_video_123"
            
            manager.add_to_chat_history(question, answer, video_id)
            
            self.assertEqual(len(self.mock_st.session_state['chat_history']), 1)
            
            entry = self.mock_st.session_state['chat_history'][0]
            self.assertEqual(entry['question'], question)
            self.assertEqual(entry['answer'], answer)
            self.assertEqual(entry['video_id'], video_id)
            self.assertEqual(entry['conversation_id'], 'test_conv_123')
            self.assertIn('timestamp', entry)
    
    def test_get_chat_history_all(self):
        """Test getting all chat history."""
        with patch('src.utils.session_manager.st', self.mock_st):
            test_history = [
                {'question': 'Q1', 'answer': 'A1', 'video_id': 'vid1'},
                {'question': 'Q2', 'answer': 'A2', 'video_id': 'vid2'}
            ]
            self.mock_st.session_state = {'chat_history': test_history}
            
            manager = SessionManager()
            history = manager.get_chat_history()
            
            self.assertEqual(history, test_history)
    
    def test_get_chat_history_filtered(self):
        """Test getting filtered chat history by video ID."""
        with patch('src.utils.session_manager.st', self.mock_st):
            test_history = [
                {'question': 'Q1', 'answer': 'A1', 'video_id': 'vid1'},
                {'question': 'Q2', 'answer': 'A2', 'video_id': 'vid2'},
                {'question': 'Q3', 'answer': 'A3', 'video_id': 'vid1'}
            ]
            self.mock_st.session_state = {'chat_history': test_history}
            
            manager = SessionManager()
            history = manager.get_chat_history('vid1')
            
            self.assertEqual(len(history), 2)
            self.assertEqual(history[0]['video_id'], 'vid1')
            self.assertEqual(history[1]['video_id'], 'vid1')
    
    def test_clear_chat_history_all(self):
        """Test clearing all chat history."""
        with patch('src.utils.session_manager.st', self.mock_st):
            test_history = [
                {'question': 'Q1', 'answer': 'A1', 'video_id': 'vid1'},
                {'question': 'Q2', 'answer': 'A2', 'video_id': 'vid2'}
            ]
            self.mock_st.session_state = {'chat_history': test_history}
            
            manager = SessionManager()
            manager.clear_chat_history()
            
            self.assertEqual(self.mock_st.session_state['chat_history'], [])
    
    def test_clear_chat_history_filtered(self):
        """Test clearing chat history for specific video."""
        with patch('src.utils.session_manager.st', self.mock_st):
            test_history = [
                {'question': 'Q1', 'answer': 'A1', 'video_id': 'vid1'},
                {'question': 'Q2', 'answer': 'A2', 'video_id': 'vid2'},
                {'question': 'Q3', 'answer': 'A3', 'video_id': 'vid1'}
            ]
            self.mock_st.session_state = {'chat_history': test_history}
            
            manager = SessionManager()
            manager.clear_chat_history('vid1')
            
            remaining_history = self.mock_st.session_state['chat_history']
            self.assertEqual(len(remaining_history), 1)
            self.assertEqual(remaining_history[0]['video_id'], 'vid2')
    
    def test_save_processed_video(self):
        """Test saving processed video information."""
        with patch('src.utils.session_manager.st', self.mock_st):
            self.mock_st.session_state = {
                'processed_videos': {},
                'conversation_id': 'test_conv_123'
            }
            
            manager = SessionManager()
            
            video_url = "https://youtube.com/watch?v=test123"
            video_id = "test123"
            metadata = {"title": "Test Video", "author": "Test Author"}
            transcript = "This is a test transcript."
            qa_chain = MagicMock()
            vectorstore = MagicMock()
            
            manager.save_processed_video(
                video_url, video_id, metadata, transcript, qa_chain, vectorstore
            )
            
            # Check processed_videos
            self.assertIn(video_id, self.mock_st.session_state['processed_videos'])
            saved_video = self.mock_st.session_state['processed_videos'][video_id]
            
            self.assertEqual(saved_video['url'], video_url)
            self.assertEqual(saved_video['metadata'], metadata)
            self.assertEqual(saved_video['transcript'], transcript)
            self.assertEqual(saved_video['conversation_id'], 'test_conv_123')
            self.assertIn('processed_at', saved_video)
            
            # Check current session state
            self.assertEqual(self.mock_st.session_state['current_video'], video_id)
            self.assertEqual(self.mock_st.session_state['qa_chain'], qa_chain)
            self.assertEqual(self.mock_st.session_state['vectorstore'], vectorstore)
            self.assertEqual(self.mock_st.session_state['video_metadata'], metadata)
    
    def test_get_processed_videos(self):
        """Test getting processed videos."""
        with patch('src.utils.session_manager.st', self.mock_st):
            test_videos = {
                'vid1': {'title': 'Video 1'},
                'vid2': {'title': 'Video 2'}
            }
            self.mock_st.session_state = {'processed_videos': test_videos}
            
            manager = SessionManager()
            videos = manager.get_processed_videos()
            
            self.assertEqual(videos, test_videos)
    
    def test_switch_to_video_success(self):
        """Test successful video switching."""
        with patch('src.utils.session_manager.st', self.mock_st):
            test_videos = {
                'vid1': {'title': 'Video 1'},
                'vid2': {'title': 'Video 2'}
            }
            self.mock_st.session_state = {'processed_videos': test_videos}
            
            manager = SessionManager()
            result = manager.switch_to_video('vid1')
            
            self.assertTrue(result)
            self.assertEqual(self.mock_st.session_state['current_video'], 'vid1')
    
    def test_switch_to_video_failure(self):
        """Test video switching failure."""
        with patch('src.utils.session_manager.st', self.mock_st):
            self.mock_st.session_state = {'processed_videos': {}}
            
            manager = SessionManager()
            result = manager.switch_to_video('nonexistent_vid')
            
            self.assertFalse(result)
    
    def test_export_chat_history_json(self):
        """Test exporting chat history as JSON."""
        with patch('src.utils.session_manager.st', self.mock_st):
            test_history = [
                {'question': 'Q1', 'answer': 'A1', 'timestamp': '2024-01-01T12:00:00'}
            ]
            self.mock_st.session_state = {'chat_history': test_history}
            
            manager = SessionManager()
            result = manager.export_chat_history('json')
            
            self.assertIsInstance(result, str)
            self.assertIn('Q1', result)
            self.assertIn('A1', result)
    
    def test_export_chat_history_txt(self):
        """Test exporting chat history as text."""
        with patch('src.utils.session_manager.st', self.mock_st):
            test_history = [
                {'question': 'Q1', 'answer': 'A1', 'timestamp': '2024-01-01T12:00:00'}
            ]
            self.mock_st.session_state = {'chat_history': test_history}
            
            manager = SessionManager()
            result = manager.export_chat_history('txt')
            
            self.assertIsInstance(result, str)
            self.assertIn('Question: Q1', result)
            self.assertIn('Answer: A1', result)
    
    def test_get_session_stats(self):
        """Test getting session statistics."""
        with patch('src.utils.session_manager.st', self.mock_st):
            test_history = [
                {'question': 'Q1', 'timestamp': '2024-01-01T12:00:00'},
                {'question': 'Q2', 'timestamp': '2024-01-01T13:00:00'}
            ]
            test_videos = {'vid1': {}, 'vid2': {}}
            
            self.mock_st.session_state = {
                'chat_history': test_history,
                'processed_videos': test_videos,
                'current_video': 'vid1',
                'conversation_id': 'test_conv_123'
            }
            
            manager = SessionManager()
            stats = manager.get_session_stats()
            
            self.assertEqual(stats['total_questions'], 2)
            self.assertEqual(stats['processed_videos'], 2)
            self.assertEqual(stats['current_video'], 'vid1')
            self.assertEqual(stats['conversation_id'], 'test_conv_123')
            self.assertIn('session_start', stats)

if __name__ == '__main__':
    unittest.main()
