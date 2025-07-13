"""
Session management utilities for handling chat history and application state.
"""

import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
import streamlit as st

logger = logging.getLogger(__name__)

class SessionManager:
    """Manages session state, chat history, and conversation persistence."""
    
    def __init__(self):
        self.initialize_session_state()
    
    def initialize_session_state(self):
        """Initialize Streamlit session state variables."""
        if 'chat_history' not in st.session_state:
            st.session_state.chat_history = []
        
        if 'processed_videos' not in st.session_state:
            st.session_state.processed_videos = {}
        
        if 'current_video' not in st.session_state:
            st.session_state.current_video = None
        
        if 'qa_chain' not in st.session_state:
            st.session_state.qa_chain = None
        
        if 'vectorstore' not in st.session_state:
            st.session_state.vectorstore = None
        
        if 'video_metadata' not in st.session_state:
            st.session_state.video_metadata = {}
        
        if 'conversation_id' not in st.session_state:
            st.session_state.conversation_id = self.generate_conversation_id()
    
    def generate_conversation_id(self) -> str:
        """Generate a unique conversation ID."""
        return f"conv_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    def add_to_chat_history(self, question: str, answer: str, video_id: str = None, 
                           source_docs: List[Any] = None):
        """
        Add a Q&A pair to chat history.
        
        Args:
            question (str): User question
            answer (str): AI answer
            video_id (str): Associated video ID
            source_docs (List[Any]): Source documents used for answer
        """
        chat_entry = {
            'timestamp': datetime.now().isoformat(),
            'question': question,
            'answer': answer,
            'video_id': video_id,
            'source_docs': [doc.page_content[:200] + "..." if len(doc.page_content) > 200 
                           else doc.page_content for doc in (source_docs or [])],
            'conversation_id': st.session_state.conversation_id
        }
        
        st.session_state.chat_history.append(chat_entry)
    
    def get_chat_history(self, video_id: str = None) -> List[Dict[str, Any]]:
        """
        Get chat history, optionally filtered by video ID.
        
        Args:
            video_id (str): Optional video ID to filter by
            
        Returns:
            List[Dict[str, Any]]: Chat history entries
        """
        if video_id:
            return [entry for entry in st.session_state.chat_history 
                   if entry.get('video_id') == video_id]
        return st.session_state.chat_history
    
    def clear_chat_history(self, video_id: str = None):
        """
        Clear chat history, optionally for a specific video.
        
        Args:
            video_id (str): Optional video ID to clear history for
        """
        if video_id:
            st.session_state.chat_history = [
                entry for entry in st.session_state.chat_history 
                if entry.get('video_id') != video_id
            ]
        else:
            st.session_state.chat_history = []
    
    def save_processed_video(self, video_url: str, video_id: str, metadata: Dict[str, Any], 
                           transcript: str, qa_chain: Any, vectorstore: Any):
        """
        Save processed video information to session state.
        
        Args:
            video_url (str): Video URL
            video_id (str): Video ID
            metadata (Dict[str, Any]): Video metadata
            transcript (str): Video transcript
            qa_chain (Any): QA chain object
            vectorstore (Any): Vector store object
        """
        st.session_state.processed_videos[video_id] = {
            'url': video_url,
            'metadata': metadata,
            'transcript': transcript,
            'processed_at': datetime.now().isoformat(),
            'conversation_id': st.session_state.conversation_id
        }
        
        st.session_state.current_video = video_id
        st.session_state.qa_chain = qa_chain
        st.session_state.vectorstore = vectorstore
        st.session_state.video_metadata = metadata
    
    def get_processed_videos(self) -> Dict[str, Dict[str, Any]]:
        """Get all processed videos."""
        return st.session_state.processed_videos
    
    def switch_to_video(self, video_id: str) -> bool:
        """
        Switch to a previously processed video.
        
        Args:
            video_id (str): Video ID to switch to
            
        Returns:
            bool: True if successful, False if video not found
        """
        if video_id in st.session_state.processed_videos:
            st.session_state.current_video = video_id
            # Note: QA chain and vectorstore would need to be recreated
            # This is a simplified version - in a full implementation,
            # you'd want to persist and reload these objects
            return True
        return False
    
    def export_chat_history(self, format: str = 'json') -> str:
        """
        Export chat history in specified format.
        
        Args:
            format (str): Export format ('json', 'txt')
            
        Returns:
            str: Exported chat history
        """
        if format == 'json':
            return json.dumps(st.session_state.chat_history, indent=2)
        
        elif format == 'txt':
            output = []
            for entry in st.session_state.chat_history:
                output.append(f"Timestamp: {entry['timestamp']}")
                output.append(f"Question: {entry['question']}")
                output.append(f"Answer: {entry['answer']}")
                if entry.get('video_id'):
                    output.append(f"Video ID: {entry['video_id']}")
                output.append("-" * 50)
            return "\n".join(output)
        
        return ""
    
    def get_session_stats(self) -> Dict[str, Any]:
        """Get session statistics."""
        return {
            'total_questions': len(st.session_state.chat_history),
            'processed_videos': len(st.session_state.processed_videos),
            'current_video': st.session_state.current_video,
            'conversation_id': st.session_state.conversation_id,
            'session_start': min([entry['timestamp'] for entry in st.session_state.chat_history], 
                               default=datetime.now().isoformat())
        }
