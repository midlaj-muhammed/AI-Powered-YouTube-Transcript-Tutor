"""
Database utilities for storing processed videos and conversations.
"""

import sqlite3
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Manages SQLite database operations for the chatbot."""
    
    def __init__(self, db_path: str = "data/chatbot.db"):
        """
        Initialize database manager.
        
        Args:
            db_path (str): Path to SQLite database file
        """
        self.db_path = db_path
        self.ensure_db_directory()
        self.init_database()
    
    def ensure_db_directory(self):
        """Ensure database directory exists."""
        db_dir = Path(self.db_path).parent
        db_dir.mkdir(parents=True, exist_ok=True)
    
    def init_database(self):
        """Initialize database tables."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Videos table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS videos (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        video_id TEXT UNIQUE NOT NULL,
                        url TEXT NOT NULL,
                        title TEXT,
                        author TEXT,
                        duration INTEGER,
                        views INTEGER,
                        publish_date TEXT,
                        thumbnail_url TEXT,
                        transcript TEXT,
                        metadata TEXT,
                        processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        language TEXT DEFAULT 'en'
                    )
                ''')
                
                # Conversations table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS conversations (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        conversation_id TEXT NOT NULL,
                        video_id TEXT,
                        question TEXT NOT NULL,
                        answer TEXT NOT NULL,
                        source_documents TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (video_id) REFERENCES videos (video_id)
                    )
                ''')
                
                # Vector stores table (for caching)
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS vector_stores (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        video_id TEXT UNIQUE NOT NULL,
                        vector_data BLOB,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (video_id) REFERENCES videos (video_id)
                    )
                ''')
                
                # User sessions table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS user_sessions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        session_id TEXT UNIQUE NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        metadata TEXT
                    )
                ''')
                
                conn.commit()
                logger.info("Database initialized successfully")
                
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
            raise
    
    def save_video(self, video_data: Dict[str, Any]) -> bool:
        """
        Save video information to database.
        
        Args:
            video_data (Dict[str, Any]): Video data including metadata and transcript
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT OR REPLACE INTO videos 
                    (video_id, url, title, author, duration, views, publish_date, 
                     thumbnail_url, transcript, metadata, language)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    video_data.get('video_id'),
                    video_data.get('url'),
                    video_data.get('title'),
                    video_data.get('author'),
                    video_data.get('duration'),
                    video_data.get('views'),
                    video_data.get('publish_date'),
                    video_data.get('thumbnail_url'),
                    video_data.get('transcript'),
                    json.dumps(video_data.get('metadata', {})),
                    video_data.get('language', 'en')
                ))
                
                conn.commit()
                return True
                
        except Exception as e:
            logger.error(f"Error saving video: {e}")
            return False
    
    def get_video(self, video_id: str) -> Optional[Dict[str, Any]]:
        """
        Get video information from database.
        
        Args:
            video_id (str): Video ID
            
        Returns:
            Optional[Dict[str, Any]]: Video data or None if not found
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT video_id, url, title, author, duration, views, 
                           publish_date, thumbnail_url, transcript, metadata, 
                           processed_at, language
                    FROM videos WHERE video_id = ?
                ''', (video_id,))
                
                row = cursor.fetchone()
                if row:
                    return {
                        'video_id': row[0],
                        'url': row[1],
                        'title': row[2],
                        'author': row[3],
                        'duration': row[4],
                        'views': row[5],
                        'publish_date': row[6],
                        'thumbnail_url': row[7],
                        'transcript': row[8],
                        'metadata': json.loads(row[9]) if row[9] else {},
                        'processed_at': row[10],
                        'language': row[11]
                    }
                
        except Exception as e:
            logger.error(f"Error getting video: {e}")
        
        return None
    
    def save_conversation(self, conversation_data: Dict[str, Any]) -> bool:
        """
        Save conversation entry to database.
        
        Args:
            conversation_data (Dict[str, Any]): Conversation data
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO conversations 
                    (conversation_id, video_id, question, answer, source_documents)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    conversation_data.get('conversation_id'),
                    conversation_data.get('video_id'),
                    conversation_data.get('question'),
                    conversation_data.get('answer'),
                    json.dumps(conversation_data.get('source_documents', []))
                ))
                
                conn.commit()
                return True
                
        except Exception as e:
            logger.error(f"Error saving conversation: {e}")
            return False
    
    def get_conversations(self, video_id: str = None, conversation_id: str = None, 
                         limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get conversations from database.
        
        Args:
            video_id (str): Optional video ID filter
            conversation_id (str): Optional conversation ID filter
            limit (int): Maximum number of results
            
        Returns:
            List[Dict[str, Any]]: List of conversations
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                query = '''
                    SELECT conversation_id, video_id, question, answer, 
                           source_documents, created_at
                    FROM conversations
                '''
                params = []
                
                conditions = []
                if video_id:
                    conditions.append('video_id = ?')
                    params.append(video_id)
                
                if conversation_id:
                    conditions.append('conversation_id = ?')
                    params.append(conversation_id)
                
                if conditions:
                    query += ' WHERE ' + ' AND '.join(conditions)
                
                query += ' ORDER BY created_at DESC LIMIT ?'
                params.append(limit)
                
                cursor.execute(query, params)
                rows = cursor.fetchall()
                
                conversations = []
                for row in rows:
                    conversations.append({
                        'conversation_id': row[0],
                        'video_id': row[1],
                        'question': row[2],
                        'answer': row[3],
                        'source_documents': json.loads(row[4]) if row[4] else [],
                        'created_at': row[5]
                    })
                
                return conversations
                
        except Exception as e:
            logger.error(f"Error getting conversations: {e}")
            return []
    
    def get_processed_videos(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get list of processed videos.
        
        Args:
            limit (int): Maximum number of results
            
        Returns:
            List[Dict[str, Any]]: List of processed videos
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT video_id, title, author, duration, processed_at
                    FROM videos
                    ORDER BY processed_at DESC
                    LIMIT ?
                ''', (limit,))
                
                rows = cursor.fetchall()
                
                videos = []
                for row in rows:
                    videos.append({
                        'video_id': row[0],
                        'title': row[1],
                        'author': row[2],
                        'duration': row[3],
                        'processed_at': row[4]
                    })
                
                return videos
                
        except Exception as e:
            logger.error(f"Error getting processed videos: {e}")
            return []
    
    def delete_video(self, video_id: str) -> bool:
        """
        Delete video and associated conversations.
        
        Args:
            video_id (str): Video ID to delete
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Delete conversations first (foreign key constraint)
                cursor.execute('DELETE FROM conversations WHERE video_id = ?', (video_id,))
                cursor.execute('DELETE FROM vector_stores WHERE video_id = ?', (video_id,))
                cursor.execute('DELETE FROM videos WHERE video_id = ?', (video_id,))
                
                conn.commit()
                return True
                
        except Exception as e:
            logger.error(f"Error deleting video: {e}")
            return False
    
    def get_database_stats(self) -> Dict[str, Any]:
        """
        Get database statistics.
        
        Returns:
            Dict[str, Any]: Database statistics
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Count videos
                cursor.execute('SELECT COUNT(*) FROM videos')
                video_count = cursor.fetchone()[0]
                
                # Count conversations
                cursor.execute('SELECT COUNT(*) FROM conversations')
                conversation_count = cursor.fetchone()[0]
                
                # Get database size
                cursor.execute("SELECT page_count * page_size as size FROM pragma_page_count(), pragma_page_size()")
                db_size = cursor.fetchone()[0]
                
                return {
                    'total_videos': video_count,
                    'total_conversations': conversation_count,
                    'database_size_bytes': db_size,
                    'database_size_mb': round(db_size / (1024 * 1024), 2)
                }
                
        except Exception as e:
            logger.error(f"Error getting database stats: {e}")
            return {}
