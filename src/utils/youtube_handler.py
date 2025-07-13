"""
YouTube video handling utilities for transcript extraction and metadata retrieval.
"""

import os
import re
import logging
from typing import Optional, Dict, Any, List
from pytube import YouTube
from youtube_transcript_api import (
    YouTubeTranscriptApi,
    TranscriptsDisabled, 
    NoTranscriptFound,
    VideoUnavailable,
    CouldNotRetrieveTranscript
)

logger = logging.getLogger(__name__)

class YouTubeHandler:
    """Handles YouTube video operations including transcript extraction and metadata retrieval."""
    
    def __init__(self):
        self.supported_languages = ['en', 'es', 'fr', 'de', 'it', 'pt', 'ru', 'ja', 'ko', 'zh']
    
    def validate_youtube_url(self, url: str) -> bool:
        """
        Validate if the provided URL is a valid YouTube URL.
        
        Args:
            url (str): YouTube URL to validate
            
        Returns:
            bool: True if valid, False otherwise
        """
        youtube_regex = re.compile(
            r'(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/'
            r'(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})'
        )
        return bool(youtube_regex.match(url))
    
    def extract_video_id(self, url: str) -> Optional[str]:
        """
        Extract video ID from YouTube URL.
        
        Args:
            url (str): YouTube URL
            
        Returns:
            Optional[str]: Video ID if found, None otherwise
        """
        try:
            yt = YouTube(url)
            return yt.video_id
        except Exception as e:
            logger.error(f"Error extracting video ID: {e}")
            return None
    
    def get_video_metadata(self, url: str) -> Dict[str, Any]:
        """
        Get video metadata including title, description, duration, etc.
        
        Args:
            url (str): YouTube URL
            
        Returns:
            Dict[str, Any]: Video metadata
        """
        try:
            yt = YouTube(url)
            metadata = {
                'title': yt.title,
                'description': yt.description,
                'length': yt.length,
                'views': yt.views,
                'rating': getattr(yt, 'rating', None),
                'author': yt.author,
                'publish_date': yt.publish_date,
                'thumbnail_url': yt.thumbnail_url,
                'video_id': yt.video_id
            }
            return metadata
        except Exception as e:
            logger.error(f"Error getting video metadata: {e}")
            return {}
    
    def get_available_transcripts(self, video_id: str) -> List[Dict[str, str]]:
        """
        Get list of available transcript languages for a video.
        
        Args:
            video_id (str): YouTube video ID
            
        Returns:
            List[Dict[str, str]]: List of available transcripts with language info
        """
        try:
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            available = []
            
            for transcript in transcript_list:
                available.append({
                    'language': transcript.language,
                    'language_code': transcript.language_code,
                    'is_generated': transcript.is_generated,
                    'is_translatable': transcript.is_translatable
                })
            
            return available
        except Exception as e:
            logger.error(f"Error getting available transcripts: {e}")
            return []
    
    def get_youtube_transcript(self, url: str, language: str = 'en') -> Dict[str, Any]:
        """
        Extract transcript from YouTube video with comprehensive error handling.
        
        Args:
            url (str): YouTube video URL
            language (str): Preferred language code (default: 'en')
            
        Returns:
            Dict[str, Any]: Dictionary containing transcript text and metadata
        """
        result = {
            'success': False,
            'transcript': '',
            'error': None,
            'metadata': {},
            'available_languages': []
        }
        
        try:
            if not self.validate_youtube_url(url):
                result['error'] = "Invalid YouTube URL format"
                return result
            
            video_id = self.extract_video_id(url)
            if not video_id:
                result['error'] = "Could not extract video ID from URL"
                return result
            
            # Get video metadata
            result['metadata'] = self.get_video_metadata(url)
            
            # Get available transcripts
            result['available_languages'] = self.get_available_transcripts(video_id)
            
            # Try to get transcript
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            
            # Try preferred language first, then fallback to English, then any available
            languages_to_try = [language] if language != 'en' else []
            languages_to_try.extend(['en'])
            languages_to_try.extend([lang['language_code'] for lang in result['available_languages'] 
                                   if lang['language_code'] not in languages_to_try])
            
            transcript_data = None
            used_language = None
            
            for lang in languages_to_try:
                try:
                    transcript = transcript_list.find_transcript([lang])
                    transcript_data = transcript.fetch()
                    used_language = lang
                    break
                except (NoTranscriptFound, TranscriptsDisabled):
                    continue
            
            if transcript_data:
                # Format transcript text - handle both dict and object formats
                text_parts = []
                formatted_transcript_data = []

                for item in transcript_data:
                    if hasattr(item, 'text'):
                        # New format: object with attributes
                        text_parts.append(item.text)
                        formatted_transcript_data.append({
                            'text': item.text,
                            'start': getattr(item, 'start', 0),
                            'duration': getattr(item, 'duration', 0)
                        })
                    elif isinstance(item, dict) and 'text' in item:
                        # Old format: dictionary
                        text_parts.append(item['text'])
                        formatted_transcript_data.append(item)
                    else:
                        # Fallback: convert to string
                        text_parts.append(str(item))
                        formatted_transcript_data.append({'text': str(item), 'start': 0, 'duration': 0})

                text = " ".join(text_parts)
                result['transcript'] = text
                result['success'] = True
                result['used_language'] = used_language
                result['transcript_data'] = formatted_transcript_data  # Raw transcript with timestamps
            else:
                result['error'] = "No transcript available in any supported language"
                
        except TranscriptsDisabled:
            result['error'] = "Transcripts are disabled for this video"
        except NoTranscriptFound:
            result['error'] = "No transcript found for this video"
        except VideoUnavailable:
            result['error'] = "This video is unavailable"
        except CouldNotRetrieveTranscript:
            result['error'] = "Could not retrieve transcript. It may not be available in your region"
        except Exception as e:
            result['error'] = f"Unexpected error: {str(e)}"
            logger.error(f"Unexpected error getting transcript: {e}")
        
        return result
    
    def save_transcript_to_file(self, transcript_text: str, filename: str = "transcript.txt") -> bool:
        """
        Save transcript text to a file.
        
        Args:
            transcript_text (str): Transcript text to save
            filename (str): Output filename
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            os.makedirs(os.path.dirname(filename) if os.path.dirname(filename) else '.', exist_ok=True)
            with open(filename, "w", encoding="utf-8") as f:
                f.write(transcript_text)
            return True
        except Exception as e:
            logger.error(f"Error saving transcript to file: {e}")
            return False
