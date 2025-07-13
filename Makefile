# Makefile for YouTube Transcript Chatbot

.PHONY: help install dev-install test lint format clean run validate docker-build docker-run setup

# Default target
help:
	@echo "YouTube Transcript Chatbot - Available Commands:"
	@echo ""
	@echo "Setup and Installation:"
	@echo "  make setup          - Complete setup (install + validate)"
	@echo "  make install        - Install production dependencies"
	@echo "  make dev-install    - Install development dependencies"
	@echo ""
	@echo "Development:"
	@echo "  make run            - Run the Streamlit application"
	@echo "  make test           - Run all tests"
	@echo "  make lint           - Run code linting"
	@echo "  make format         - Format code with black"
	@echo "  make validate       - Validate setup and configuration"
	@echo ""
	@echo "Docker:"
	@echo "  make docker-build   - Build Docker image"
	@echo "  make docker-run     - Run Docker container"
	@echo ""
	@echo "Maintenance:"
	@echo "  make clean          - Clean temporary files and cache"
	@echo "  make clean-all      - Clean everything including data"

# Setup and Installation
setup: install validate
	@echo "✅ Setup complete!"

install:
	@echo "📦 Installing production dependencies..."
	pip install -r requirements.txt

dev-install: install
	@echo "🛠️  Installing development dependencies..."
	pip install -e .[dev]
	pip install pytest pytest-cov black flake8

# Development
run:
	@echo "🚀 Starting Streamlit application..."
	streamlit run app.py

test:
	@echo "🧪 Running tests..."
	python run_tests.py

lint:
	@echo "🔍 Running code linting..."
	flake8 src/ tests/ app.py --max-line-length=88 --ignore=E203,W503

format:
	@echo "🎨 Formatting code..."
	black src/ tests/ app.py --line-length=88

validate:
	@echo "✅ Validating setup..."
	python validate_setup.py

# Docker
docker-build:
	@echo "🐳 Building Docker image..."
	docker build -t youtube-chatbot .

docker-run: docker-build
	@echo "🐳 Running Docker container..."
	docker run -p 8501:8501 --env-file .env youtube-chatbot

# Maintenance
clean:
	@echo "🧹 Cleaning temporary files..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.log" -delete
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	rm -rf .coverage
	rm -f transcript.txt

clean-all: clean
	@echo "🧹 Cleaning all data and cache..."
	rm -rf cache/
	rm -rf data/
	rm -rf logs/
	rm -rf .streamlit/

# Environment setup
env-setup:
	@echo "⚙️  Setting up environment..."
	@if [ ! -f .env ]; then \
		cp .env.template .env; \
		echo "📝 Created .env file from template"; \
		echo "⚠️  Please edit .env and add your OpenAI API key"; \
	else \
		echo "✅ .env file already exists"; \
	fi

# Database setup
db-setup:
	@echo "🗄️  Setting up database..."
	python -c "from src.utils.database import DatabaseManager; DatabaseManager().init_database(); print('Database initialized')"

# Create directories
dirs:
	@echo "📁 Creating directories..."
	mkdir -p cache data logs static/uploads

# Full development setup
dev-setup: env-setup dirs dev-install validate
	@echo "🎉 Development environment ready!"

# Production setup
prod-setup: env-setup dirs install validate
	@echo "🚀 Production environment ready!"

# Testing shortcuts
test-unit:
	@echo "🧪 Running unit tests only..."
	python -m pytest tests/ -v

test-coverage:
	@echo "📊 Running tests with coverage..."
	python -m pytest tests/ --cov=src --cov-report=html --cov-report=term

# Code quality
quality: lint format test
	@echo "✨ Code quality checks complete!"

# Documentation
docs:
	@echo "📚 Generating documentation..."
	@echo "Documentation available in README.md and CONTRIBUTING.md"

# Version info
version:
	@echo "📋 Version Information:"
	@python --version
	@streamlit --version
	@echo "Project version: 1.0.0"

# Health check
health:
	@echo "🏥 Running health checks..."
	python validate_setup.py

# Quick start
quickstart: env-setup install validate run

# Deployment helpers
deploy-check: test lint validate
	@echo "✅ Deployment checks passed!"

# Backup
backup:
	@echo "💾 Creating backup..."
	tar -czf backup_$(shell date +%Y%m%d_%H%M%S).tar.gz \
		--exclude='.git' \
		--exclude='__pycache__' \
		--exclude='cache' \
		--exclude='logs' \
		--exclude='*.pyc' \
		.

# Show project info
info:
	@echo "📋 Project Information:"
	@echo "Name: YouTube Transcript Chatbot"
	@echo "Version: 1.0.0"
	@echo "Python: $(shell python --version)"
	@echo "Directory: $(shell pwd)"
	@echo "Files: $(shell find . -name '*.py' | wc -l) Python files"
	@echo "Tests: $(shell find tests/ -name 'test_*.py' | wc -l) test files"
