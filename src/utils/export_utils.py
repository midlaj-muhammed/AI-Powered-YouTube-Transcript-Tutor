"""
Export utilities for generating PDF, text, and other format exports.
"""

import io
import json
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor

logger = logging.getLogger(__name__)

class ExportUtils:
    """Utilities for exporting chat history and transcripts in various formats."""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.setup_custom_styles()
    
    def setup_custom_styles(self):
        """Setup custom styles for PDF generation."""
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=16,
            spaceAfter=30,
            textColor=HexColor('#2E86AB')
        ))
        
        self.styles.add(ParagraphStyle(
            name='QuestionStyle',
            parent=self.styles['Normal'],
            fontSize=12,
            spaceAfter=10,
            textColor=HexColor('#A23B72'),
            leftIndent=20
        ))
        
        self.styles.add(ParagraphStyle(
            name='AnswerStyle',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceAfter=20,
            leftIndent=40
        ))
    
    def export_to_pdf(self, chat_history: List[Dict[str, Any]], 
                     video_metadata: Dict[str, Any] = None) -> bytes:
        """
        Export chat history to PDF format.
        
        Args:
            chat_history (List[Dict[str, Any]]): Chat history entries
            video_metadata (Dict[str, Any]): Video metadata
            
        Returns:
            bytes: PDF content as bytes
        """
        try:
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=A4)
            story = []
            
            # Title
            title = "YouTube Transcript Q&A Session"
            story.append(Paragraph(title, self.styles['CustomTitle']))
            story.append(Spacer(1, 12))
            
            # Video information
            if video_metadata:
                story.append(Paragraph("Video Information", self.styles['Heading2']))
                story.append(Paragraph(f"<b>Title:</b> {video_metadata.get('title', 'N/A')}", 
                                     self.styles['Normal']))
                story.append(Paragraph(f"<b>Author:</b> {video_metadata.get('author', 'N/A')}", 
                                     self.styles['Normal']))
                story.append(Paragraph(f"<b>Duration:</b> {self._format_duration(video_metadata.get('length', 0))}", 
                                     self.styles['Normal']))
                story.append(Spacer(1, 20))
            
            # Export information
            story.append(Paragraph(f"<b>Exported on:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", 
                                 self.styles['Normal']))
            story.append(Paragraph(f"<b>Total Questions:</b> {len(chat_history)}", 
                                 self.styles['Normal']))
            story.append(Spacer(1, 20))
            
            # Chat history
            story.append(Paragraph("Questions and Answers", self.styles['Heading2']))
            story.append(Spacer(1, 12))
            
            for i, entry in enumerate(chat_history, 1):
                # Question
                story.append(Paragraph(f"<b>Q{i}:</b> {entry['question']}", 
                                     self.styles['QuestionStyle']))
                
                # Answer
                story.append(Paragraph(f"<b>A{i}:</b> {entry['answer']}", 
                                     self.styles['AnswerStyle']))
                
                # Timestamp
                timestamp = datetime.fromisoformat(entry['timestamp']).strftime('%Y-%m-%d %H:%M:%S')
                story.append(Paragraph(f"<i>Asked on: {timestamp}</i>", 
                                     self.styles['Normal']))
                story.append(Spacer(1, 15))
            
            doc.build(story)
            buffer.seek(0)
            return buffer.getvalue()
            
        except Exception as e:
            logger.error(f"Error generating PDF: {e}")
            return b""
    
    def export_to_text(self, chat_history: List[Dict[str, Any]], 
                      video_metadata: Dict[str, Any] = None) -> str:
        """
        Export chat history to plain text format.
        
        Args:
            chat_history (List[Dict[str, Any]]): Chat history entries
            video_metadata (Dict[str, Any]): Video metadata
            
        Returns:
            str: Text content
        """
        try:
            lines = []
            lines.append("YouTube Transcript Q&A Session")
            lines.append("=" * 50)
            lines.append("")
            
            # Video information
            if video_metadata:
                lines.append("Video Information:")
                lines.append(f"Title: {video_metadata.get('title', 'N/A')}")
                lines.append(f"Author: {video_metadata.get('author', 'N/A')}")
                lines.append(f"Duration: {self._format_duration(video_metadata.get('length', 0))}")
                lines.append("")
            
            # Export information
            lines.append(f"Exported on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            lines.append(f"Total Questions: {len(chat_history)}")
            lines.append("")
            lines.append("Questions and Answers:")
            lines.append("-" * 30)
            lines.append("")
            
            # Chat history
            for i, entry in enumerate(chat_history, 1):
                timestamp = datetime.fromisoformat(entry['timestamp']).strftime('%Y-%m-%d %H:%M:%S')
                lines.append(f"Q{i}: {entry['question']}")
                lines.append(f"A{i}: {entry['answer']}")
                lines.append(f"Asked on: {timestamp}")
                lines.append("")
                lines.append("-" * 30)
                lines.append("")
            
            return "\n".join(lines)
            
        except Exception as e:
            logger.error(f"Error generating text export: {e}")
            return ""
    
    def export_to_json(self, chat_history: List[Dict[str, Any]], 
                      video_metadata: Dict[str, Any] = None) -> str:
        """
        Export chat history to JSON format.
        
        Args:
            chat_history (List[Dict[str, Any]]): Chat history entries
            video_metadata (Dict[str, Any]): Video metadata
            
        Returns:
            str: JSON content
        """
        try:
            export_data = {
                'export_info': {
                    'exported_at': datetime.now().isoformat(),
                    'total_questions': len(chat_history),
                    'format_version': '1.0'
                },
                'video_metadata': video_metadata or {},
                'chat_history': chat_history
            }
            
            return json.dumps(export_data, indent=2, ensure_ascii=False)
            
        except Exception as e:
            logger.error(f"Error generating JSON export: {e}")
            return ""
    
    def export_transcript(self, transcript_text: str, video_metadata: Dict[str, Any] = None, 
                         format: str = 'txt') -> str:
        """
        Export transcript in specified format.
        
        Args:
            transcript_text (str): Transcript text
            video_metadata (Dict[str, Any]): Video metadata
            format (str): Export format ('txt', 'json')
            
        Returns:
            str: Exported transcript
        """
        try:
            if format == 'txt':
                lines = []
                lines.append("YouTube Video Transcript")
                lines.append("=" * 30)
                lines.append("")
                
                if video_metadata:
                    lines.append(f"Title: {video_metadata.get('title', 'N/A')}")
                    lines.append(f"Author: {video_metadata.get('author', 'N/A')}")
                    lines.append(f"Duration: {self._format_duration(video_metadata.get('length', 0))}")
                    lines.append("")
                
                lines.append(f"Exported on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                lines.append("")
                lines.append("Transcript:")
                lines.append("-" * 20)
                lines.append("")
                lines.append(transcript_text)
                
                return "\n".join(lines)
            
            elif format == 'json':
                export_data = {
                    'export_info': {
                        'exported_at': datetime.now().isoformat(),
                        'format_version': '1.0'
                    },
                    'video_metadata': video_metadata or {},
                    'transcript': transcript_text
                }
                return json.dumps(export_data, indent=2, ensure_ascii=False)
            
            return transcript_text
            
        except Exception as e:
            logger.error(f"Error exporting transcript: {e}")
            return ""
    
    def _format_duration(self, seconds: int) -> str:
        """Format duration from seconds to HH:MM:SS format."""
        if not seconds:
            return "N/A"
        
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        seconds = seconds % 60
        
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        else:
            return f"{minutes:02d}:{seconds:02d}"
