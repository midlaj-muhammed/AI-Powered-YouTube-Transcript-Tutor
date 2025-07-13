"""
AI-Powered YouTube Transcript Tutor - Main Streamlit Application
Enhanced version with modern UI, error handling, and extended functionality.
"""

import os
import sys
import streamlit as st
from datetime import datetime
import time

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import custom modules
from src.utils.youtube_handler import YouTubeHandler
from src.utils.text_processor import TextProcessor
from src.utils.session_manager import SessionManager
from src.utils.export_utils import ExportUtils
from src.utils.logger import setup_logging
from config.settings import settings

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Setup logging
logger = setup_logging(
    log_level=settings.get('logging.level', 'INFO'),
    log_file=settings.get('logging.file')
)

class YouTubeChatbotApp:
    """Main application class for YouTube Transcript Chatbot."""
    
    def __init__(self):
        """Initialize the application."""
        self.setup_page_config()
        self.load_custom_css()
        self.initialize_components()
    
    def setup_page_config(self):
        """Configure Streamlit page settings."""
        app_config = settings.get_app_config()
        st.set_page_config(
            page_title=app_config.get('title', 'YouTube Transcript Tutor'),
            page_icon="🎓",
            layout="wide",
            initial_sidebar_state="expanded"
        )
    
    def load_custom_css(self):
        """Load custom CSS styling with dark theme."""
        try:
            with open('static/style.css', 'r') as f:
                css_content = f.read()
                st.markdown(f'<style>{css_content}</style>', unsafe_allow_html=True)
                logger.info("Custom dark theme CSS loaded successfully")
        except FileNotFoundError:
            logger.warning("Custom CSS file not found, using fallback dark theme")
            # Fallback CSS for dark theme
            fallback_css = """
            <style>
            .stApp {
                background-color: #1a1a1a !important;
                color: #e9ecef !important;
            }
            .stMarkdown, .stText {
                color: #e9ecef !important;
            }
            .stButton > button {
                background-color: #667eea !important;
                color: white !important;
            }
            body, html {
                background-color: #1a1a1a !important;
                color: #e9ecef !important;
            }
            div[data-testid="stSidebar"] {
                background-color: #2d3748 !important;
            }
            </style>
            """
            st.markdown(fallback_css, unsafe_allow_html=True)
    
    def initialize_components(self):
        """Initialize application components."""
        # Check for OpenAI API key
        self.openai_api_key = settings.get_openai_api_key()
        if not self.openai_api_key:
            st.error("⚠️ OpenAI API key not found. Please set OPENAI_API_KEY environment variable.")
            st.stop()
        
        # Initialize components
        self.youtube_handler = YouTubeHandler()
        self.text_processor = TextProcessor(self.openai_api_key)
        self.session_manager = SessionManager()
        self.export_utils = ExportUtils()
    
    def render_header(self):
        """Render application header."""
        app_config = settings.get_app_config()
        
        st.markdown(f"""
        <div class="app-header">
            <h1>🎓 {app_config.get('title', 'AI-Powered YouTube Transcript Tutor')}</h1>
            <p>{app_config.get('description', 'Ask questions from YouTube lecture transcripts using AI')}</p>
        </div>
        """, unsafe_allow_html=True)
    
    def render_sidebar(self):
        """Render sidebar with navigation and controls."""
        with st.sidebar:
            st.markdown("### 📋 Navigation")
            
            # Session statistics
            stats = self.session_manager.get_session_stats()
            st.markdown(f"""
            <div class="sidebar-content">
                <h4>📊 Session Stats</h4>
                <div class="metadata-item">
                    <span class="metadata-label">Questions Asked:</span>
                    <span class="metadata-value">{stats['total_questions']}</span>
                </div>
                <div class="metadata-item">
                    <span class="metadata-label">Videos Processed:</span>
                    <span class="metadata-value">{stats['processed_videos']}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Processed videos
            processed_videos = self.session_manager.get_processed_videos()
            if processed_videos:
                st.markdown("### 📹 Processed Videos")
                for video_id, video_info in processed_videos.items():
                    title = video_info['metadata'].get('title', 'Unknown Title')[:50] + "..."
                    if st.button(f"📺 {title}", key=f"video_{video_id}"):
                        self.session_manager.switch_to_video(video_id)
                        st.rerun()
            
            # Export options
            if st.session_state.chat_history:
                st.markdown("### 📤 Export Options")
                export_format = st.selectbox(
                    "Export Format",
                    ["PDF", "Text", "JSON"],
                    key="export_format"
                )
                
                if st.button("📥 Export Chat History"):
                    self.export_chat_history(export_format.lower())
            
            # Settings
            st.markdown("### ⚙️ Settings")
            
            # Language selection
            processing_config = settings.get_processing_config()
            supported_languages = processing_config.get('supported_languages', ['en'])
            default_language = processing_config.get('default_language', 'en')
            
            selected_language = st.selectbox(
                "Transcript Language",
                supported_languages,
                index=supported_languages.index(default_language) if default_language in supported_languages else 0,
                key="transcript_language"
            )
            
            # Clear history button
            if st.button("🗑️ Clear Chat History", type="secondary"):
                self.session_manager.clear_chat_history()
                st.success("Chat history cleared!")
                st.rerun()

            # Working video examples
            st.markdown("### 🎯 Example Videos")
            st.markdown("Try these videos that usually work:")

            example_videos = {
                "🧮 Neural Networks": "https://www.youtube.com/watch?v=aircAruvnKk",
                "📚 Khan Academy": "https://www.youtube.com/watch?v=WUvTyaaNkzM",
                "🎓 TED-Ed": "https://www.youtube.com/watch?v=kBdfcR-8hEY"
            }

            for title, url in example_videos.items():
                if st.button(title, key=f"example_{title}"):
                    st.session_state.video_url = url
                    st.rerun()

            # Troubleshooting section
            st.markdown("### 🔧 Troubleshooting")
            with st.expander("Common Issues & Solutions"):
                st.markdown("""
                **"Could not retrieve transcript":**
                - Video may be region-restricted
                - Try videos from educational channels
                - Ensure video has captions enabled

                **"No transcript available":**
                - Video doesn't have captions
                - Try auto-generated captions videos
                - Look for educational content

                **"Video unavailable":**
                - Video may be private/deleted
                - Check the URL is correct
                - Try a different video
                """)
    
    def render_video_input_section(self):
        """Render video input and processing section."""
        st.markdown("### 🎬 Video Processing")
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            video_url = st.text_input(
                "Enter YouTube Video URL",
                placeholder="https://www.youtube.com/watch?v=...",
                help="Paste a YouTube video URL to extract and process its transcript"
            )
        
        with col2:
            st.markdown("<br>", unsafe_allow_html=True)  # Add spacing
            process_button = st.button("🚀 Process Video", type="primary")
        
        if process_button and video_url:
            self.process_video(video_url)
        elif process_button and not video_url:
            st.warning("⚠️ Please enter a valid YouTube URL.")
    
    def process_video(self, video_url: str):
        """
        Process YouTube video and create QA chain.
        
        Args:
            video_url (str): YouTube video URL
        """
        # Validate URL
        if not self.youtube_handler.validate_youtube_url(video_url):
            st.error("❌ Invalid YouTube URL format. Please check the URL and try again.")
            return
        
        # Create progress indicators
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            # Step 1: Extract transcript
            status_text.text("🔍 Extracting video transcript...")
            progress_bar.progress(25)
            
            language = st.session_state.get('transcript_language', 'en')
            transcript_result = self.youtube_handler.get_youtube_transcript(video_url, language)
            
            if not transcript_result['success']:
                error_msg = transcript_result['error']
                st.error(f"❌ {error_msg}")

                # Provide specific suggestions based on error type
                if "ip blocked" in error_msg.lower() or "cloud provider" in error_msg.lower():
                    st.warning("🚫 **YouTube has temporarily blocked your IP address**")
                    st.info("💡 **How to fix this:**")
                    st.markdown("""
                    **Immediate solutions:**
                    - ⏰ **Wait 10-15 minutes** before trying again
                    - 🌐 **Try a different network** (mobile hotspot, different WiFi)
                    - 🔄 **Restart your router** to get a new IP address

                    **Why this happens:**
                    - Too many requests to YouTube in a short time
                    - Using cloud services (AWS, Google Cloud, etc.)
                    - YouTube's anti-bot protection

                    **Prevention:**
                    - Wait between video processing attempts
                    - Don't process multiple videos rapidly
                    """)

                    # Show a countdown timer suggestion
                    st.info("⏱️ **Recommended:** Wait 15 minutes, then try one of the example videos below.")

                elif "rate limited" in error_msg.lower() or "too many requests" in error_msg.lower():
                    st.warning("⚡ **Rate Limited: Too many requests**")
                    st.info("💡 **Solution:** Wait 5-10 minutes before trying again.")

                elif "region" in error_msg.lower():
                    st.info("💡 **Suggestions to fix this issue:**")
                    st.markdown("""
                    - Try a different video that's available in your region
                    - Look for videos from creators in your country
                    - Try educational channels like Khan Academy, Coursera, or TED-Ed
                    - Some videos may work better than others depending on regional settings
                    """)
                elif "private" in error_msg.lower():
                    st.info("💡 **This video is private.** Try a public video instead.")
                elif "disabled" in error_msg.lower():
                    st.info("💡 **Captions are disabled for this video.** Try finding a video with captions enabled.")
                elif "unavailable" in error_msg.lower():
                    st.info("💡 **This video is unavailable.** It may have been deleted or made private.")
                else:
                    st.info("💡 **Try these alternatives:**")
                    st.markdown("""
                    - Make sure the video is public and has captions
                    - Try a different YouTube video
                    - Look for educational content which usually has transcripts
                    - Check if the video URL is correct
                    """)

                # Show some example working videos
                st.markdown("### 🎯 **Try these example videos that usually work:**")
                example_videos = [
                    "https://www.youtube.com/watch?v=aircAruvnKk",  # 3Blue1Brown
                    "https://www.youtube.com/watch?v=WUvTyaaNkzM",  # Khan Academy
                    "https://www.youtube.com/watch?v=kBdfcR-8hEY",  # TED-Ed
                ]

                for i, example_url in enumerate(example_videos, 1):
                    if st.button(f"📺 Try Example Video {i}", key=f"example_{i}"):
                        st.session_state.video_url = example_url
                        st.rerun()

                return
            
            # Step 2: Display video metadata
            progress_bar.progress(50)
            status_text.text("📊 Processing video metadata...")
            
            metadata = transcript_result['metadata']
            if metadata:
                self.display_video_metadata(metadata)
            
            # Step 3: Process transcript
            progress_bar.progress(75)
            status_text.text("🧠 Creating AI knowledge base...")
            
            processing_result = self.text_processor.process_transcript(
                transcript_result['transcript'],
                metadata
            )
            
            if not processing_result['success']:
                st.error(f"❌ {processing_result['error']}")
                return
            
            # Step 4: Save to session
            progress_bar.progress(100)
            status_text.text("✅ Video processed successfully!")
            
            video_id = metadata.get('video_id', 'unknown')
            self.session_manager.save_processed_video(
                video_url,
                video_id,
                metadata,
                transcript_result['transcript'],
                processing_result['qa_chain'],
                processing_result['vectorstore']
            )
            
            # Success message
            st.success("🎉 Video processed successfully! You can now ask questions about the content.")
            
            # Show transcript download option
            if st.button("📥 Download Transcript"):
                self.download_transcript(transcript_result['transcript'], metadata)
            
        except Exception as e:
            logger.error(f"Error processing video: {e}")
            st.error(f"❌ An unexpected error occurred: {str(e)}")
        
        finally:
            progress_bar.empty()
            status_text.empty()
    
    def display_video_metadata(self, metadata: dict):
        """
        Display video metadata in a formatted card.
        
        Args:
            metadata (dict): Video metadata
        """
        st.markdown(f"""
        <div class="video-metadata" style="background-color: #2d3748 !important; border: 1px solid #4a5568 !important; color: #e9ecef !important;">
            <h4 style="color: #e9ecef !important;">📹 Video Information</h4>
            <div class="metadata-item">
                <span class="metadata-label" style="color: #a0aec0 !important;">Title:</span>
                <span class="metadata-value" style="color: #e9ecef !important;">{metadata.get('title', 'N/A')}</span>
            </div>
            <div class="metadata-item">
                <span class="metadata-label" style="color: #a0aec0 !important;">Author:</span>
                <span class="metadata-value" style="color: #e9ecef !important;">{metadata.get('author', 'N/A')}</span>
            </div>
            <div class="metadata-item">
                <span class="metadata-label" style="color: #a0aec0 !important;">Duration:</span>
                <span class="metadata-value" style="color: #e9ecef !important;">{self.format_duration(metadata.get('length', 0))}</span>
            </div>
            <div class="metadata-item">
                <span class="metadata-label" style="color: #a0aec0 !important;">Views:</span>
                <span class="metadata-value" style="color: #e9ecef !important;">{metadata.get('views', 'N/A'):,}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    def format_duration(self, seconds: int) -> str:
        """Format duration from seconds to HH:MM:SS."""
        if not seconds:
            return "N/A"
        
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        seconds = seconds % 60
        
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        else:
            return f"{minutes:02d}:{seconds:02d}"
    
    def render_qa_section(self):
        """Render question and answer section."""
        if 'qa_chain' not in st.session_state or st.session_state.qa_chain is None:
            st.info("👆 Please process a YouTube video first to start asking questions.")
            return
        
        st.markdown("### 💬 Ask Questions")
        
        # Question input
        col1, col2 = st.columns([4, 1])
        
        with col1:
            user_question = st.text_input(
                "Your Question",
                placeholder="Ask anything about the video content...",
                key="user_question"
            )
        
        with col2:
            st.markdown("<br>", unsafe_allow_html=True)
            ask_button = st.button("🤔 Ask", type="primary")
        
        if ask_button and user_question:
            self.process_question(user_question)
        elif ask_button and not user_question:
            st.warning("⚠️ Please enter a question.")
    
    def process_question(self, question: str):
        """
        Process user question and generate answer.
        
        Args:
            question (str): User question
        """
        with st.spinner("🤔 Thinking..."):
            try:
                result = self.text_processor.ask_question(st.session_state.qa_chain, question)
                
                if result['success']:
                    # Display answer with dark theme
                    st.markdown("### 💡 Answer")
                    st.markdown(f"""
                    <div class="info-card" style="background: #2d3748 !important; border: 1px solid #4a5568 !important; color: #e9ecef !important;">
                        <p style="color: #e9ecef !important; margin: 0 !important; line-height: 1.6 !important;">{result['answer']}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Add to chat history
                    video_id = st.session_state.get('current_video')
                    self.session_manager.add_to_chat_history(
                        question,
                        result['answer'],
                        video_id,
                        result.get('source_documents', [])
                    )
                    
                    # Show source documents if available
                    if result.get('source_documents'):
                        with st.expander("📚 Source References"):
                            for i, doc in enumerate(result['source_documents'], 1):
                                st.markdown(f"**Reference {i}:**")
                                st.text(doc.page_content[:300] + "..." if len(doc.page_content) > 300 else doc.page_content)
                
                else:
                    st.error(f"❌ {result['error']}")
                    
            except Exception as e:
                logger.error(f"Error processing question: {e}")
                st.error(f"❌ An error occurred while processing your question: {str(e)}")
    
    def render_chat_history(self):
        """Render chat history section."""
        chat_history = self.session_manager.get_chat_history()
        
        if not chat_history:
            return
        
        st.markdown("### 📜 Chat History")
        
        # Limit displayed history
        ui_config = settings.get_ui_config()
        max_display = ui_config.get('max_chat_history_display', 50)
        recent_history = chat_history[-max_display:] if len(chat_history) > max_display else chat_history
        
        for entry in reversed(recent_history):
            with st.expander(f"Q: {entry['question'][:50]}..." if len(entry['question']) > 50 else f"Q: {entry['question']}"):
                st.markdown(f"**Question:** {entry['question']}")
                st.markdown(f"**Answer:** {entry['answer']}")
                st.markdown(f"**Time:** {datetime.fromisoformat(entry['timestamp']).strftime('%Y-%m-%d %H:%M:%S')}")
    
    def export_chat_history(self, format: str):
        """
        Export chat history in specified format.
        
        Args:
            format (str): Export format (pdf, txt, json)
        """
        try:
            chat_history = self.session_manager.get_chat_history()
            video_metadata = st.session_state.get('video_metadata', {})
            
            if format == 'pdf':
                pdf_data = self.export_utils.export_to_pdf(chat_history, video_metadata)
                if pdf_data:
                    st.download_button(
                        label="📥 Download PDF",
                        data=pdf_data,
                        file_name=f"chat_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                        mime="application/pdf"
                    )
            
            elif format == 'txt':
                text_data = self.export_utils.export_to_text(chat_history, video_metadata)
                if text_data:
                    st.download_button(
                        label="📥 Download Text",
                        data=text_data,
                        file_name=f"chat_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                        mime="text/plain"
                    )
            
            elif format == 'json':
                json_data = self.export_utils.export_to_json(chat_history, video_metadata)
                if json_data:
                    st.download_button(
                        label="📥 Download JSON",
                        data=json_data,
                        file_name=f"chat_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                        mime="application/json"
                    )
            
        except Exception as e:
            logger.error(f"Error exporting chat history: {e}")
            st.error(f"❌ Error exporting chat history: {str(e)}")
    
    def download_transcript(self, transcript_text: str, metadata: dict):
        """
        Provide transcript download functionality.
        
        Args:
            transcript_text (str): Transcript text
            metadata (dict): Video metadata
        """
        try:
            transcript_export = self.export_utils.export_transcript(transcript_text, metadata, 'txt')
            
            st.download_button(
                label="📥 Download Transcript",
                data=transcript_export,
                file_name=f"transcript_{metadata.get('video_id', 'unknown')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain"
            )
            
        except Exception as e:
            logger.error(f"Error preparing transcript download: {e}")
            st.error(f"❌ Error preparing transcript download: {str(e)}")
    
    def run(self):
        """Run the main application."""
        try:
            self.render_header()
            self.render_sidebar()
            
            # Main content area
            self.render_video_input_section()
            
            st.markdown("---")
            
            self.render_qa_section()
            
            st.markdown("---")
            
            self.render_chat_history()
            
        except Exception as e:
            logger.error(f"Application error: {e}")
            st.error(f"❌ An application error occurred: {str(e)}")

def main():
    """Main function to run the application."""
    app = YouTubeChatbotApp()
    app.run()

if __name__ == "__main__":
    main()
