"""
Cache management utilities for vector stores and processed data.
"""

import os
import pickle
import hashlib
import logging
from datetime import datetime, timedelta
from typing import Any, Optional, Dict
from pathlib import Path
import shutil

logger = logging.getLogger(__name__)

class CacheManager:
    """Manages caching of vector stores and processed data."""
    
    def __init__(self, cache_dir: str = "cache", max_size_mb: int = 500):
        """
        Initialize cache manager.
        
        Args:
            cache_dir (str): Cache directory path
            max_size_mb (int): Maximum cache size in MB
        """
        self.cache_dir = Path(cache_dir)
        self.max_size_bytes = max_size_mb * 1024 * 1024
        self.ensure_cache_directory()
    
    def ensure_cache_directory(self):
        """Ensure cache directory exists."""
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Create subdirectories
        (self.cache_dir / "vectorstores").mkdir(exist_ok=True)
        (self.cache_dir / "transcripts").mkdir(exist_ok=True)
        (self.cache_dir / "metadata").mkdir(exist_ok=True)
    
    def _get_cache_key(self, data: str) -> str:
        """
        Generate cache key from data.
        
        Args:
            data (str): Data to generate key for
            
        Returns:
            str: Cache key
        """
        return hashlib.md5(data.encode()).hexdigest()
    
    def _get_cache_path(self, cache_type: str, key: str) -> Path:
        """
        Get cache file path.
        
        Args:
            cache_type (str): Type of cache (vectorstores, transcripts, metadata)
            key (str): Cache key
            
        Returns:
            Path: Cache file path
        """
        return self.cache_dir / cache_type / f"{key}.pkl"
    
    def save_vectorstore(self, video_id: str, vectorstore: Any) -> bool:
        """
        Save vector store to cache.
        
        Args:
            video_id (str): Video ID
            vectorstore (Any): Vector store object
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            cache_key = self._get_cache_key(video_id)
            cache_path = self._get_cache_path("vectorstores", cache_key)
            
            # Save vector store using FAISS's built-in save method
            vectorstore.save_local(str(cache_path.with_suffix("")))
            
            # Save metadata
            metadata = {
                'video_id': video_id,
                'created_at': datetime.now().isoformat(),
                'cache_key': cache_key
            }
            
            metadata_path = self._get_cache_path("metadata", cache_key)
            with open(metadata_path, 'wb') as f:
                pickle.dump(metadata, f)
            
            logger.info(f"Vector store cached for video {video_id}")
            self._cleanup_cache()
            return True
            
        except Exception as e:
            logger.error(f"Error caching vector store: {e}")
            return False
    
    def load_vectorstore(self, video_id: str, embeddings: Any) -> Optional[Any]:
        """
        Load vector store from cache.
        
        Args:
            video_id (str): Video ID
            embeddings (Any): Embeddings object for loading
            
        Returns:
            Optional[Any]: Vector store object or None if not found
        """
        try:
            cache_key = self._get_cache_key(video_id)
            cache_path = self._get_cache_path("vectorstores", cache_key)
            
            if not cache_path.with_suffix("").exists():
                return None
            
            # Load vector store using FAISS's built-in load method
            from langchain_community.vectorstores import FAISS
            vectorstore = FAISS.load_local(str(cache_path.with_suffix("")), embeddings)
            
            logger.info(f"Vector store loaded from cache for video {video_id}")
            return vectorstore
            
        except Exception as e:
            logger.error(f"Error loading vector store from cache: {e}")
            return None
    
    def save_transcript(self, video_id: str, transcript_data: Dict[str, Any]) -> bool:
        """
        Save transcript data to cache.
        
        Args:
            video_id (str): Video ID
            transcript_data (Dict[str, Any]): Transcript data
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            cache_key = self._get_cache_key(video_id)
            cache_path = self._get_cache_path("transcripts", cache_key)
            
            cache_data = {
                'video_id': video_id,
                'transcript_data': transcript_data,
                'created_at': datetime.now().isoformat(),
                'cache_key': cache_key
            }
            
            with open(cache_path, 'wb') as f:
                pickle.dump(cache_data, f)
            
            logger.info(f"Transcript cached for video {video_id}")
            self._cleanup_cache()
            return True
            
        except Exception as e:
            logger.error(f"Error caching transcript: {e}")
            return False
    
    def load_transcript(self, video_id: str) -> Optional[Dict[str, Any]]:
        """
        Load transcript data from cache.
        
        Args:
            video_id (str): Video ID
            
        Returns:
            Optional[Dict[str, Any]]: Transcript data or None if not found
        """
        try:
            cache_key = self._get_cache_key(video_id)
            cache_path = self._get_cache_path("transcripts", cache_key)
            
            if not cache_path.exists():
                return None
            
            with open(cache_path, 'rb') as f:
                cache_data = pickle.load(f)
            
            logger.info(f"Transcript loaded from cache for video {video_id}")
            return cache_data['transcript_data']
            
        except Exception as e:
            logger.error(f"Error loading transcript from cache: {e}")
            return None
    
    def is_cached(self, video_id: str, cache_type: str = "vectorstores") -> bool:
        """
        Check if data is cached for video.
        
        Args:
            video_id (str): Video ID
            cache_type (str): Type of cache to check
            
        Returns:
            bool: True if cached, False otherwise
        """
        try:
            cache_key = self._get_cache_key(video_id)
            
            if cache_type == "vectorstores":
                cache_path = self._get_cache_path("vectorstores", cache_key)
                return cache_path.with_suffix("").exists()
            else:
                cache_path = self._get_cache_path(cache_type, cache_key)
                return cache_path.exists()
                
        except Exception as e:
            logger.error(f"Error checking cache: {e}")
            return False
    
    def delete_cache(self, video_id: str) -> bool:
        """
        Delete cached data for video.
        
        Args:
            video_id (str): Video ID
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            cache_key = self._get_cache_key(video_id)
            
            # Delete vector store cache
            vectorstore_path = self._get_cache_path("vectorstores", cache_key)
            if vectorstore_path.with_suffix("").exists():
                shutil.rmtree(vectorstore_path.with_suffix(""))
            
            # Delete transcript cache
            transcript_path = self._get_cache_path("transcripts", cache_key)
            if transcript_path.exists():
                transcript_path.unlink()
            
            # Delete metadata cache
            metadata_path = self._get_cache_path("metadata", cache_key)
            if metadata_path.exists():
                metadata_path.unlink()
            
            logger.info(f"Cache deleted for video {video_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting cache: {e}")
            return False
    
    def get_cache_size(self) -> Dict[str, Any]:
        """
        Get cache size information.
        
        Returns:
            Dict[str, Any]: Cache size information
        """
        try:
            total_size = 0
            file_count = 0
            
            for root, dirs, files in os.walk(self.cache_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    if os.path.exists(file_path):
                        total_size += os.path.getsize(file_path)
                        file_count += 1
            
            return {
                'total_size_bytes': total_size,
                'total_size_mb': round(total_size / (1024 * 1024), 2),
                'file_count': file_count,
                'max_size_mb': self.max_size_bytes / (1024 * 1024),
                'usage_percent': round((total_size / self.max_size_bytes) * 100, 2)
            }
            
        except Exception as e:
            logger.error(f"Error getting cache size: {e}")
            return {}
    
    def _cleanup_cache(self):
        """Clean up cache if it exceeds maximum size."""
        try:
            cache_info = self.get_cache_size()
            
            if cache_info.get('total_size_bytes', 0) > self.max_size_bytes:
                logger.info("Cache size exceeded, cleaning up...")
                
                # Get all cache files with their modification times
                cache_files = []
                for root, dirs, files in os.walk(self.cache_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        if os.path.exists(file_path):
                            mtime = os.path.getmtime(file_path)
                            cache_files.append((file_path, mtime))
                
                # Sort by modification time (oldest first)
                cache_files.sort(key=lambda x: x[1])
                
                # Delete oldest files until under limit
                current_size = cache_info.get('total_size_bytes', 0)
                target_size = self.max_size_bytes * 0.8  # Clean to 80% of max
                
                for file_path, _ in cache_files:
                    if current_size <= target_size:
                        break
                    
                    try:
                        file_size = os.path.getsize(file_path)
                        os.remove(file_path)
                        current_size -= file_size
                        logger.debug(f"Deleted cache file: {file_path}")
                    except Exception as e:
                        logger.error(f"Error deleting cache file {file_path}: {e}")
                
                logger.info("Cache cleanup completed")
                
        except Exception as e:
            logger.error(f"Error during cache cleanup: {e}")
    
    def clear_all_cache(self) -> bool:
        """
        Clear all cached data.
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if self.cache_dir.exists():
                shutil.rmtree(self.cache_dir)
                self.ensure_cache_directory()
            
            logger.info("All cache cleared")
            return True
            
        except Exception as e:
            logger.error(f"Error clearing cache: {e}")
            return False
    
    def get_cached_videos(self) -> List[Dict[str, Any]]:
        """
        Get list of cached videos.
        
        Returns:
            List[Dict[str, Any]]: List of cached video information
        """
        try:
            cached_videos = []
            metadata_dir = self.cache_dir / "metadata"
            
            if not metadata_dir.exists():
                return cached_videos
            
            for metadata_file in metadata_dir.glob("*.pkl"):
                try:
                    with open(metadata_file, 'rb') as f:
                        metadata = pickle.load(f)
                    
                    cached_videos.append({
                        'video_id': metadata.get('video_id'),
                        'cache_key': metadata.get('cache_key'),
                        'created_at': metadata.get('created_at'),
                        'file_size': metadata_file.stat().st_size
                    })
                    
                except Exception as e:
                    logger.error(f"Error reading metadata file {metadata_file}: {e}")
            
            return cached_videos
            
        except Exception as e:
            logger.error(f"Error getting cached videos: {e}")
            return []
