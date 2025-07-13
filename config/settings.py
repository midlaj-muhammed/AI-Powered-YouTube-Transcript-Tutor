"""
Configuration settings management.
"""

import os
import yaml
from typing import Dict, Any, Optional
from pathlib import Path

class Settings:
    """Application settings manager."""
    
    def __init__(self, config_file: str = "config/config.yaml"):
        """
        Initialize settings from config file and environment variables.
        
        Args:
            config_file (str): Path to configuration file
        """
        self.config_file = config_file
        self.config = self._load_config()
        self._override_with_env()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        try:
            config_path = Path(self.config_file)
            if config_path.exists():
                with open(config_path, 'r', encoding='utf-8') as f:
                    return yaml.safe_load(f) or {}
            else:
                return self._get_default_config()
        except Exception as e:
            print(f"Error loading config file: {e}")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration."""
        return {
            'app': {
                'title': 'AI-Powered YouTube Transcript Tutor',
                'description': 'Ask questions from YouTube lecture transcripts using AI',
                'version': '1.0.0'
            },
            'ui': {
                'theme': 'light',
                'sidebar_width': 300,
                'max_chat_history_display': 50,
                'enable_animations': True
            },
            'processing': {
                'default_chunk_size': 1000,
                'chunk_overlap': 200,
                'max_transcript_length': 1000000,
                'supported_languages': ['en', 'es', 'fr', 'de', 'it', 'pt', 'ru', 'ja', 'ko', 'zh'],
                'default_language': 'en'
            },
            'ai': {
                'model_temperature': 0.7,
                'max_tokens': 2000,
                'retrieval_k': 4,
                'chain_type': 'stuff'
            },
            'export': {
                'formats': ['pdf', 'txt', 'json'],
                'max_export_entries': 1000,
                'pdf_page_size': 'A4'
            },
            'cache': {
                'enable_vectorstore_cache': True,
                'cache_directory': 'cache',
                'max_cache_size_mb': 500
            },
            'logging': {
                'level': 'INFO',
                'file': 'logs/app.log',
                'max_file_size_mb': 10,
                'backup_count': 5
            },
            'security': {
                'max_url_length': 2048,
                'allowed_domains': ['youtube.com', 'youtu.be', 'm.youtube.com'],
                'rate_limit_requests': 100,
                'rate_limit_window_minutes': 60
            }
        }
    
    def _override_with_env(self):
        """Override configuration with environment variables."""
        # OpenAI API Key
        openai_key = os.getenv('OPENAI_API_KEY')
        if openai_key:
            if 'ai' not in self.config:
                self.config['ai'] = {}
            self.config['ai']['openai_api_key'] = openai_key
        
        # Log level
        log_level = os.getenv('LOG_LEVEL')
        if log_level:
            self.config['logging']['level'] = log_level.upper()
        
        # Cache directory
        cache_dir = os.getenv('CACHE_DIRECTORY')
        if cache_dir:
            self.config['cache']['cache_directory'] = cache_dir
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value using dot notation.
        
        Args:
            key (str): Configuration key (e.g., 'app.title')
            default (Any): Default value if key not found
            
        Returns:
            Any: Configuration value
        """
        keys = key.split('.')
        value = self.config
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key: str, value: Any):
        """
        Set configuration value using dot notation.
        
        Args:
            key (str): Configuration key (e.g., 'app.title')
            value (Any): Value to set
        """
        keys = key.split('.')
        config = self.config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
    
    def get_openai_api_key(self) -> Optional[str]:
        """Get OpenAI API key from config or environment."""
        return self.get('ai.openai_api_key') or os.getenv('OPENAI_API_KEY')
    
    def get_app_config(self) -> Dict[str, Any]:
        """Get application configuration."""
        return self.get('app', {})
    
    def get_ui_config(self) -> Dict[str, Any]:
        """Get UI configuration."""
        return self.get('ui', {})
    
    def get_processing_config(self) -> Dict[str, Any]:
        """Get processing configuration."""
        return self.get('processing', {})
    
    def get_ai_config(self) -> Dict[str, Any]:
        """Get AI configuration."""
        return self.get('ai', {})
    
    def get_export_config(self) -> Dict[str, Any]:
        """Get export configuration."""
        return self.get('export', {})
    
    def get_cache_config(self) -> Dict[str, Any]:
        """Get cache configuration."""
        return self.get('cache', {})
    
    def get_logging_config(self) -> Dict[str, Any]:
        """Get logging configuration."""
        return self.get('logging', {})
    
    def get_security_config(self) -> Dict[str, Any]:
        """Get security configuration."""
        return self.get('security', {})

# Global settings instance
settings = Settings()
