# 🎓 AI-Powered YouTube Transcript Tutor

A sophisticated Streamlit application that transforms YouTube videos into interactive learning experiences using AI. Ask questions about video content and get intelligent answers based on the transcript.

![Python](https://img.shields.io/badge/python-v3.8+-blue.svg)
![Streamlit](https://img.shields.io/badge/streamlit-v1.28+-red.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## 🚀 Live Demo

**Try the app now:** [https://ai-powered-youtube-transcript-tutor.streamlit.app/](https://ai-powered-youtube-transcript-tutor.streamlit.app/)

Experience the full functionality without any setup required!

## 🌟 Features

### Core Functionality
- **YouTube Transcript Extraction**: Automatically extracts transcripts from YouTube videos
- **AI-Powered Q&A**: Ask questions about video content and get intelligent responses
- **Multi-language Support**: Supports transcripts in multiple languages
- **Video Metadata Display**: Shows video information including title, author, duration, and views

### Enhanced UI/UX
- **Modern Dark Theme**: Clean, professional interface with dark theme
- **Responsive Layout**: Works seamlessly on desktop and mobile devices
- **Loading Indicators**: Visual feedback during processing
- **Sidebar Navigation**: Easy access to processed videos and settings
- **Progress Bars**: Real-time processing status updates

### Advanced Features
- **Multiple Video Processing**: Handle multiple videos in a single session
- **Chat History**: Persistent conversation history with export options
- **Export Functionality**: Export Q&A sessions as PDF, text, or JSON
- **Transcript Download**: Download video transcripts for offline use
- **Fallback System**: Works even when OpenAI API quota is exceeded
- **Session Management**: Advanced session state management

## 🚀 Quick Start

> **💡 Want to try it first?** Check out the [live demo](https://ai-powered-youtube-transcript-tutor.streamlit.app/) - no installation required!

### Prerequisites
- Python 3.8 or higher
- OpenAI API key

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/midlaj-muhammed/AI-Powered-YouTube-Transcript-Tutor.git
   cd AI-Powered-YouTube-Transcript-Tutor
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   # Create .env file
   echo "OPENAI_API_KEY=your_openai_api_key_here" > .env
   ```

5. **Run the application**
   ```bash
   streamlit run app.py
   ```

## 🔧 Configuration

### Environment Variables
- `OPENAI_API_KEY`: Your OpenAI API key for AI-powered responses

### Streamlit Configuration
The app includes custom Streamlit configuration in `.streamlit/config.toml` for optimal performance.

## 📱 Usage

1. **Enter YouTube URL**: Paste any YouTube video URL in the input field
2. **Process Video**: Click "🚀 Process Video" to extract and analyze the transcript
3. **Ask Questions**: Use the Q&A interface to ask about the video content
4. **Export Results**: Export conversations in multiple formats
5. **Manage Sessions**: Use sidebar to navigate between processed videos

## 🏗️ Project Structure

```
AI-Powered-YouTube-Transcript-Tutor/
├── app.py                      # Main Streamlit application
├── requirements.txt            # Python dependencies
├── README.md                   # Project documentation
├── .env.example               # Environment variables template
├── .streamlit/
│   └── config.toml            # Streamlit configuration
├── static/
│   └── style.css              # Custom CSS styling
├── src/
│   ├── __init__.py
│   └── utils/
│       ├── __init__.py
│       ├── youtube_handler.py  # YouTube processing
│       ├── text_processor.py   # AI text processing
│       ├── session_manager.py  # Session management
│       ├── export_utils.py     # Export functionality
│       └── logger.py          # Logging utilities
├── config/
│   ├── __init__.py
│   └── settings.py            # Application settings
└── logs/                      # Application logs
```

## 🌐 Deployment

### Hugging Face Spaces
This application is optimized for deployment on Hugging Face Spaces:

1. Create a new Space on [Hugging Face](https://huggingface.co/spaces)
2. Choose Streamlit SDK
3. Upload all project files
4. Set `OPENAI_API_KEY` in Repository secrets
5. Your app will be live in minutes!

### Local Development
```bash
streamlit run app.py --server.port 8501
```

## 🔒 Privacy & Security

- **No Data Storage**: Conversations are only stored in your browser session
- **Secure Processing**: All API calls are made securely
- **Privacy First**: No personal data is collected or stored

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Streamlit](https://streamlit.io/) for the amazing web app framework
- [OpenAI](https://openai.com/) for the powerful AI capabilities
- [YouTube Transcript API](https://github.com/jdepoix/youtube-transcript-api) for transcript extraction

## 📞 Support

If you encounter any issues or have questions, please [open an issue](https://github.com/midlaj-muhammed/AI-Powered-YouTube-Transcript-Tutor/issues).

---

**Made with ❤️ using Streamlit and OpenAI**

## ✨ Features

### Core Functionality
- **YouTube Transcript Extraction**: Automatically extracts transcripts from YouTube videos
- **AI-Powered Q&A**: Ask questions about video content and get intelligent responses
- **Multi-language Support**: Supports transcripts in multiple languages
- **Video Metadata Display**: Shows video information including title, author, duration, and views

### Enhanced UI/UX
- **Modern Design**: Clean, professional interface with custom CSS styling
- **Responsive Layout**: Works seamlessly on desktop and mobile devices
- **Loading Indicators**: Visual feedback during processing
- **Sidebar Navigation**: Easy access to processed videos and settings
- **Progress Bars**: Real-time processing status updates

### Advanced Features
- **Multiple Video Processing**: Handle multiple videos in a single session
- **Chat History**: Persistent conversation history with export options
- **Export Functionality**: Export Q&A sessions as PDF, text, or JSON
- **Transcript Download**: Download video transcripts for offline use
- **Caching System**: Intelligent caching for improved performance
- **Database Integration**: SQLite database for storing processed videos and conversations

### Technical Improvements
- **Error Handling**: Comprehensive error handling and user feedback
- **Input Validation**: Robust YouTube URL validation
- **Session Management**: Advanced session state management
- **Logging System**: Detailed logging for debugging and monitoring
- **Configuration Management**: Flexible configuration via YAML and environment variables

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- OpenAI API key
- Git (for cloning the repository)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/youtube-transcript-chatbot.git
   cd youtube-transcript-chatbot
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.template .env
   # Edit .env file and add your OpenAI API key
   ```

5. **Run the application**
   ```bash
   streamlit run app.py
   ```

6. **Open your browser**
   Navigate to `http://localhost:8501`

## 🔧 Configuration

### Environment Variables

Create a `.env` file based on `.env.template`:

```env
# Required
OPENAI_API_KEY=your_openai_api_key_here

# Optional
LOG_LEVEL=INFO
CACHE_DIRECTORY=cache
DATABASE_PATH=data/chatbot.db
MAX_CACHE_SIZE_MB=500
```

### Configuration File

Modify `config/config.yaml` to customize application behavior:

```yaml
app:
  title: "AI-Powered YouTube Transcript Tutor"
  description: "Ask questions from YouTube lecture transcripts using AI"

processing:
  default_chunk_size: 1000
  chunk_overlap: 200
  supported_languages: ["en", "es", "fr", "de", "it", "pt", "ru", "ja", "ko", "zh"]

ai:
  model_temperature: 0.7
  max_tokens: 2000
  retrieval_k: 4
```

## 📖 Usage Guide

### Processing a Video

1. **Enter YouTube URL**: Paste a YouTube video URL in the input field
2. **Click Process Video**: The application will:
   - Extract the video transcript
   - Display video metadata
   - Create an AI knowledge base
   - Enable Q&A functionality

### Asking Questions

1. **Enter your question** in the text input field
2. **Click Ask** to get an AI-generated answer
3. **View source references** to see which parts of the transcript were used

### Managing Sessions

- **View processed videos** in the sidebar
- **Switch between videos** by clicking on video titles
- **Export chat history** in PDF, text, or JSON format
- **Clear chat history** using the sidebar button

### Advanced Features

- **Language Selection**: Choose transcript language in settings
- **Export Options**: Download transcripts and chat histories
- **Cache Management**: Automatic caching for improved performance
- **Database Storage**: Persistent storage of processed videos and conversations

## 🐳 Docker Deployment

### Using Docker Compose (Recommended)

1. **Create environment file**
   ```bash
   cp .env.template .env
   # Add your OpenAI API key to .env
   ```

2. **Build and run**
   ```bash
   docker-compose up -d
   ```

3. **Access the application**
   Open `http://localhost:8501`

### Using Docker

1. **Build the image**
   ```bash
   docker build -t youtube-chatbot .
   ```

2. **Run the container**
   ```bash
   docker run -p 8501:8501 -e OPENAI_API_KEY=your_key_here youtube-chatbot
   ```

## 🧪 Testing

Run the test suite:

```bash
# Install development dependencies
pip install -e .[dev]

# Run tests
pytest

# Run tests with coverage
pytest --cov=src

# Run specific test file
pytest tests/test_youtube_handler.py
```

## 📁 Project Structure

```
youtube-transcript-chatbot/
├── app.py                      # Main Streamlit application
├── src/                        # Source code
│   ├── utils/                  # Utility modules
│   │   ├── youtube_handler.py  # YouTube operations
│   │   ├── text_processor.py   # Text processing and AI
│   │   ├── session_manager.py  # Session management
│   │   ├── export_utils.py     # Export functionality
│   │   ├── database.py         # Database operations
│   │   ├── cache_manager.py    # Caching system
│   │   └── logger.py           # Logging configuration
├── config/                     # Configuration files
│   ├── config.yaml            # Application configuration
│   └── settings.py            # Settings management
├── static/                     # Static assets
│   └── style.css              # Custom CSS styles
├── tests/                      # Test files
├── requirements.txt           # Python dependencies
├── .env.template             # Environment template
├── Dockerfile                # Docker configuration
├── docker-compose.yml        # Docker Compose configuration
└── README.md                 # This file
```

## 🔍 Troubleshooting

### Common Issues

1. **OpenAI API Key Error**
   - Ensure your API key is correctly set in the `.env` file
   - Check that you have sufficient API credits

2. **YouTube Video Not Found**
   - Verify the URL is correct and the video is public
   - Some videos may have transcripts disabled

3. **Transcript Not Available**
   - Try selecting a different language in settings
   - Some videos may not have auto-generated transcripts

4. **Performance Issues**
   - Clear cache using the sidebar option
   - Reduce chunk size in configuration
   - Check available disk space

### Getting Help

- Check the logs in the `logs/` directory
- Enable debug mode by setting `LOG_LEVEL=DEBUG` in `.env`
- Review the application configuration in `config/config.yaml`

## 🚀 Deployment Options

### Local Development
- Use `streamlit run app.py` for development
- Enable debug mode for detailed logging

### Production Deployment

#### Streamlit Cloud
1. Push code to GitHub repository
2. Connect to Streamlit Cloud
3. Add secrets for environment variables

#### Heroku
1. Create `Procfile`: `web: streamlit run app.py --server.port=$PORT`
2. Set environment variables in Heroku dashboard
3. Deploy using Git or GitHub integration

#### AWS/GCP/Azure
- Use Docker container deployment
- Set up load balancer for high availability
- Configure environment variables in cloud console

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Streamlit](https://streamlit.io/) for the amazing web framework
- [LangChain](https://langchain.com/) for AI/ML capabilities
- [OpenAI](https://openai.com/) for the language models
- [YouTube Transcript API](https://github.com/jdepoix/youtube-transcript-api) for transcript extraction

## 📊 Performance Tips

### Optimization Recommendations
- **Use caching**: Enable vectorstore caching for frequently accessed videos
- **Adjust chunk size**: Smaller chunks (500-800) for better precision, larger (1200-1500) for broader context
- **Monitor memory**: Clear cache periodically for long-running sessions
- **Database maintenance**: Regularly clean up old conversations and videos

### Scaling Considerations
- **Horizontal scaling**: Use multiple instances behind a load balancer
- **Database optimization**: Consider PostgreSQL for high-volume deployments
- **Caching layer**: Implement Redis for distributed caching
- **API rate limiting**: Monitor OpenAI API usage and implement rate limiting

## 📞 Support

For support, please open an issue on GitHub or contact the development team.

---

Made with ❤️ by the YouTube Transcript Chatbot Team
