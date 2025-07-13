"""
Tests for YouTube handler functionality.
"""

import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.utils.youtube_handler import YouTubeHandler

class TestYouTubeHandler(unittest.TestCase):
    """Test cases for YouTubeHandler class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.handler = YouTubeHandler()
    
    def test_validate_youtube_url_valid(self):
        """Test URL validation with valid URLs."""
        valid_urls = [
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "https://youtu.be/dQw4w9WgXcQ",
            "http://youtube.com/watch?v=dQw4w9WgXcQ",
            "https://m.youtube.com/watch?v=dQw4w9WgXcQ"
        ]
        
        for url in valid_urls:
            with self.subTest(url=url):
                self.assertTrue(self.handler.validate_youtube_url(url))
    
    def test_validate_youtube_url_invalid(self):
        """Test URL validation with invalid URLs."""
        invalid_urls = [
            "https://www.google.com",
            "not_a_url",
            "https://vimeo.com/123456",
            "",
            None
        ]
        
        for url in invalid_urls:
            with self.subTest(url=url):
                if url is not None:
                    self.assertFalse(self.handler.validate_youtube_url(url))
    
    @patch('src.utils.youtube_handler.YouTube')
    def test_extract_video_id_success(self, mock_youtube):
        """Test successful video ID extraction."""
        mock_yt = MagicMock()
        mock_yt.video_id = "dQw4w9WgXcQ"
        mock_youtube.return_value = mock_yt
        
        video_id = self.handler.extract_video_id("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
        self.assertEqual(video_id, "dQw4w9WgXcQ")
    
    @patch('src.utils.youtube_handler.YouTube')
    def test_extract_video_id_failure(self, mock_youtube):
        """Test video ID extraction failure."""
        mock_youtube.side_effect = Exception("Invalid URL")
        
        video_id = self.handler.extract_video_id("invalid_url")
        self.assertIsNone(video_id)
    
    @patch('src.utils.youtube_handler.YouTube')
    def test_get_video_metadata_success(self, mock_youtube):
        """Test successful video metadata retrieval."""
        mock_yt = MagicMock()
        mock_yt.title = "Test Video"
        mock_yt.author = "Test Author"
        mock_yt.length = 300
        mock_yt.views = 1000
        mock_yt.video_id = "dQw4w9WgXcQ"
        mock_youtube.return_value = mock_yt
        
        metadata = self.handler.get_video_metadata("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
        
        self.assertEqual(metadata['title'], "Test Video")
        self.assertEqual(metadata['author'], "Test Author")
        self.assertEqual(metadata['length'], 300)
        self.assertEqual(metadata['views'], 1000)
        self.assertEqual(metadata['video_id'], "dQw4w9WgXcQ")
    
    @patch('src.utils.youtube_handler.YouTube')
    def test_get_video_metadata_failure(self, mock_youtube):
        """Test video metadata retrieval failure."""
        mock_youtube.side_effect = Exception("Network error")
        
        metadata = self.handler.get_video_metadata("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
        self.assertEqual(metadata, {})
    
    def test_save_transcript_to_file(self):
        """Test transcript file saving."""
        test_text = "This is a test transcript."
        test_file = "test_transcript.txt"
        
        try:
            result = self.handler.save_transcript_to_file(test_text, test_file)
            self.assertTrue(result)
            
            # Verify file was created and contains correct content
            with open(test_file, 'r', encoding='utf-8') as f:
                content = f.read()
            self.assertEqual(content, test_text)
            
        finally:
            # Clean up
            if os.path.exists(test_file):
                os.remove(test_file)

if __name__ == '__main__':
    unittest.main()
