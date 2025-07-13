# Contributing to YouTube Transcript Chatbot

Thank you for your interest in contributing to the YouTube Transcript Chatbot! This document provides guidelines and information for contributors.

## 🤝 How to Contribute

### Reporting Issues

1. **Search existing issues** first to avoid duplicates
2. **Use issue templates** when available
3. **Provide detailed information** including:
   - Steps to reproduce the issue
   - Expected vs actual behavior
   - Environment details (OS, Python version, etc.)
   - Error messages and logs
   - Screenshots if applicable

### Suggesting Features

1. **Check the roadmap** in README.md or issues
2. **Open a feature request** with:
   - Clear description of the feature
   - Use cases and benefits
   - Possible implementation approach
   - Any relevant examples or mockups

### Code Contributions

1. **Fork the repository**
2. **Create a feature branch** from `main`
3. **Make your changes** following our coding standards
4. **Add tests** for new functionality
5. **Update documentation** as needed
6. **Submit a pull request**

## 🛠️ Development Setup

### Prerequisites
- Python 3.8+
- Git
- OpenAI API key for testing

### Setup Steps

1. **Clone your fork**
   ```bash
   git clone https://github.com/yourusername/youtube-transcript-chatbot.git
   cd youtube-transcript-chatbot
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   pip install -e .[dev]  # Install development dependencies
   ```

4. **Set up environment**
   ```bash
   cp .env.template .env
   # Add your OpenAI API key to .env
   ```

5. **Run tests**
   ```bash
   pytest
   ```

## 📝 Coding Standards

### Python Style Guide
- Follow [PEP 8](https://pep8.org/) style guide
- Use [Black](https://black.readthedocs.io/) for code formatting
- Use [flake8](https://flake8.pycqa.org/) for linting
- Maximum line length: 88 characters (Black default)

### Code Formatting
```bash
# Format code
black src/ tests/ app.py

# Check linting
flake8 src/ tests/ app.py

# Run both
make format  # If Makefile is available
```

### Documentation
- Use docstrings for all functions, classes, and modules
- Follow [Google docstring format](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings)
- Update README.md for user-facing changes
- Add inline comments for complex logic

### Example Docstring
```python
def process_transcript(self, transcript_text: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Process transcript text and create QA chain.
    
    Args:
        transcript_text (str): Transcript text to process
        metadata (Dict[str, Any], optional): Video metadata. Defaults to None.
        
    Returns:
        Dict[str, Any]: Processing result containing QA chain and vector store
        
    Raises:
        ValueError: If transcript_text is empty
        ProcessingError: If vector store creation fails
    """
```

## 🧪 Testing Guidelines

### Test Structure
- Place tests in the `tests/` directory
- Mirror the source structure: `tests/test_module.py` for `src/module.py`
- Use descriptive test names: `test_validate_youtube_url_with_valid_input`

### Writing Tests
```python
import unittest
from unittest.mock import patch, MagicMock
from src.utils.youtube_handler import YouTubeHandler

class TestYouTubeHandler(unittest.TestCase):
    def setUp(self):
        self.handler = YouTubeHandler()
    
    def test_validate_youtube_url_valid(self):
        """Test URL validation with valid YouTube URLs."""
        valid_urls = [
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "https://youtu.be/dQw4w9WgXcQ"
        ]
        
        for url in valid_urls:
            with self.subTest(url=url):
                self.assertTrue(self.handler.validate_youtube_url(url))
```

### Running Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src

# Run specific test file
pytest tests/test_youtube_handler.py

# Run specific test method
pytest tests/test_youtube_handler.py::TestYouTubeHandler::test_validate_youtube_url_valid
```

## 📁 Project Structure

### Directory Organization
```
src/
├── utils/              # Utility modules
│   ├── youtube_handler.py    # YouTube operations
│   ├── text_processor.py     # AI and text processing
│   ├── session_manager.py    # Session management
│   ├── export_utils.py       # Export functionality
│   ├── database.py           # Database operations
│   ├── cache_manager.py      # Caching system
│   └── logger.py             # Logging configuration
config/                 # Configuration files
static/                 # Static assets (CSS, images)
tests/                  # Test files
```

### Adding New Modules
1. Create the module in appropriate directory
2. Add corresponding test file
3. Update imports in `__init__.py` files
4. Add documentation
5. Update configuration if needed

## 🔄 Pull Request Process

### Before Submitting
- [ ] Code follows style guidelines
- [ ] Tests pass locally
- [ ] New tests added for new functionality
- [ ] Documentation updated
- [ ] No merge conflicts with main branch

### PR Description Template
```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Tests pass
- [ ] New tests added
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No breaking changes (or documented)
```

### Review Process
1. **Automated checks** must pass (tests, linting)
2. **Code review** by maintainers
3. **Testing** in development environment
4. **Approval** and merge

## 🏷️ Versioning

We use [Semantic Versioning](https://semver.org/):
- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

## 📋 Issue Labels

- `bug`: Something isn't working
- `enhancement`: New feature or request
- `documentation`: Documentation improvements
- `good first issue`: Good for newcomers
- `help wanted`: Extra attention needed
- `question`: Further information requested
- `wontfix`: This will not be worked on

## 🎯 Areas for Contribution

### High Priority
- Bug fixes and stability improvements
- Performance optimizations
- Test coverage improvements
- Documentation enhancements

### Medium Priority
- New export formats
- UI/UX improvements
- Additional language support
- Integration with other platforms

### Low Priority
- Advanced features
- Experimental functionality
- Developer tools
- Automation improvements

## 💬 Communication

- **GitHub Issues**: Bug reports and feature requests
- **Pull Requests**: Code contributions and discussions
- **Discussions**: General questions and ideas

## 📄 License

By contributing, you agree that your contributions will be licensed under the same license as the project (MIT License).

## 🙏 Recognition

Contributors will be recognized in:
- README.md contributors section
- CHANGELOG.md for significant contributions
- GitHub contributors page

Thank you for contributing to YouTube Transcript Chatbot! 🎉
