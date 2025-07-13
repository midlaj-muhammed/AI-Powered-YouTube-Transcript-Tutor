"""
YouTube video handling utilities for transcript extraction and metadata retrieval.
"""

import os
import re
import logging
import time
import random
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
        # Rate limiting to prevent IP blocking
        self.last_request_time = 0
        self.min_request_interval = 3.0  # Minimum 3 seconds between requests
        self.max_retries = 3
        self.base_delay = 2.0

    def _rate_limit(self):
        """Implement rate limiting to prevent IP blocking."""
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time

        if time_since_last_request < self.min_request_interval:
            sleep_time = self.min_request_interval - time_since_last_request
            logger.info(f"Rate limiting: sleeping for {sleep_time:.2f} seconds")
            time.sleep(sleep_time)

        self.last_request_time = time.time()

    def _exponential_backoff(self, attempt: int):
        """Implement exponential backoff for retries."""
        delay = self.base_delay * (2 ** attempt) + random.uniform(0, 1)
        logger.info(f"Exponential backoff: attempt {attempt + 1}, sleeping for {delay:.2f} seconds")
        time.sleep(delay)

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
        Extract transcript from YouTube video with comprehensive error handling and rate limiting.

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

            # Apply rate limiting before making requests
            self._rate_limit()

            # Get video metadata
            result['metadata'] = self.get_video_metadata(url)

            # Apply rate limiting before transcript requests
            self._rate_limit()

            # Get available transcripts
            result['available_languages'] = self.get_available_transcripts(video_id)
            
            # Try to get transcript with multiple strategies and retries
            transcript_data = None
            used_language = None

            # Strategy 1: Try the standard approach with retries
            for attempt in range(self.max_retries):
                try:
                    if attempt > 0:
                        self._exponential_backoff(attempt - 1)

                    self._rate_limit()
                    transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)

                    # Try preferred language first, then fallback to English, then any available
                    languages_to_try = [language] if language != 'en' else []
                    languages_to_try.extend(['en'])
                    languages_to_try.extend([lang['language_code'] for lang in result['available_languages']
                                           if lang['language_code'] not in languages_to_try])

                    for lang in languages_to_try:
                        try:
                            transcript = transcript_list.find_transcript([lang])
                            transcript_data = transcript.fetch()
                            used_language = lang
                            logger.info(f"Successfully got transcript in {lang} on attempt {attempt + 1}")
                            break
                        except (NoTranscriptFound, TranscriptsDisabled):
                            continue

                    if transcript_data:
                        break

                except Exception as e:
                    logger.warning(f"Standard transcript method failed on attempt {attempt + 1}: {e}")
                    if attempt == self.max_retries - 1:
                        logger.error(f"All {self.max_retries} attempts failed for standard method")

            # Strategy 2: Try alternative approach if first failed
            if not transcript_data:
                for attempt in range(self.max_retries):
                    try:
                        if attempt > 0:
                            self._exponential_backoff(attempt - 1)

                        self._rate_limit()
                        # Try to get any available transcript without language preference
                        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
                        available_transcripts = list(transcript_list)

                        if available_transcripts:
                            # Try manual transcripts first
                            manual_transcripts = [t for t in available_transcripts if not t.is_generated]
                            if manual_transcripts:
                                transcript = manual_transcripts[0]
                            else:
                                transcript = available_transcripts[0]

                            transcript_data = transcript.fetch()
                            used_language = transcript.language_code
                            logger.info(f"Got transcript using alternative method in {used_language} on attempt {attempt + 1}")
                            break

                    except Exception as e:
                        logger.warning(f"Alternative transcript method failed on attempt {attempt + 1}: {e}")
                        if attempt == self.max_retries - 1:
                            logger.error(f"All {self.max_retries} attempts failed for alternative method")

            # Strategy 3: Try basic method as last resort
            if not transcript_data:
                for attempt in range(self.max_retries):
                    try:
                        if attempt > 0:
                            self._exponential_backoff(attempt - 1)

                        self._rate_limit()
                        # This is a last resort - try with minimal parameters
                        transcript_data = YouTubeTranscriptApi.get_transcript(video_id)
                        used_language = 'auto-detected'
                        logger.info(f"Got transcript using basic method on attempt {attempt + 1}")
                        break
                    except Exception as e:
                        logger.warning(f"Basic transcript method failed on attempt {attempt + 1}: {e}")
                        if attempt == self.max_retries - 1:
                            logger.error(f"All {self.max_retries} attempts failed for basic method")
            
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
        except CouldNotRetrieveTranscript as e:
            error_msg = str(e).lower()
            if "ip" in error_msg and "block" in error_msg:
                result['error'] = "IP blocked by YouTube: Too many requests from your IP address"
                result['suggestion'] = "Wait 10-15 minutes before trying again, or try a different network"
                result['details'] = "YouTube has temporarily blocked your IP due to too many requests. This is common when testing or using cloud services."
            elif "region" in error_msg or "country" in error_msg:
                result['error'] = "Regional restriction: This video's transcripts are not available in your region"
                result['suggestion'] = "Try using a VPN or try a different video"
            elif "private" in error_msg:
                result['error'] = "This video is private and transcripts cannot be accessed"
            elif "disabled" in error_msg:
                result['error'] = "Transcripts are disabled for this video"
            elif "cloud provider" in error_msg:
                result['error'] = "Cloud provider IP blocked: YouTube blocks most cloud service IPs"
                result['suggestion'] = "Try from a different network or wait before retrying"
                result['details'] = "YouTube automatically blocks IPs from cloud providers like AWS, Google Cloud, etc."
            else:
                result['error'] = f"Could not retrieve transcript: {str(e)}"
            logger.warning(f"Could not retrieve transcript for video: {e}")
        except Exception as e:
            error_msg = str(e).lower()
            if "ip" in error_msg and ("block" in error_msg or "ban" in error_msg):
                result['error'] = "IP blocked by YouTube: Too many requests from your IP address"
                result['suggestion'] = "Wait 10-15 minutes before trying again, or try a different network"
                result['details'] = "YouTube has temporarily blocked your IP due to too many requests. This is common when testing or using cloud services."
            elif "cloud provider" in error_msg or "aws" in error_msg or "google cloud" in error_msg or "azure" in error_msg:
                result['error'] = "Cloud provider IP blocked: YouTube blocks most cloud service IPs"
                result['suggestion'] = "Try from a different network or wait before retrying"
                result['details'] = "YouTube automatically blocks IPs from cloud providers like AWS, Google Cloud, etc."
            elif "region" in error_msg or "country" in error_msg:
                result['error'] = "Regional restriction: This video's transcripts are not available in your region"
                result['suggestion'] = "Try using a VPN or try a different video"
            elif "private" in error_msg:
                result['error'] = "This video is private and transcripts cannot be accessed"
            elif "unavailable" in error_msg:
                result['error'] = "This video is unavailable or has been removed"
            elif "disabled" in error_msg:
                result['error'] = "Transcripts are disabled for this video"
            elif "too many requests" in error_msg:
                result['error'] = "Rate limited: Too many requests to YouTube"
                result['suggestion'] = "Wait a few minutes before trying again"
                result['details'] = "You've made too many requests to YouTube. Please wait before trying again."
            else:
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
