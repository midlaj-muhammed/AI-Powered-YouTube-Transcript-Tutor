#!/usr/bin/env python3
"""
Setup validation script for YouTube Transcript Chatbot.
This script validates the installation and configuration.
"""

import os
import sys
import importlib
import subprocess
from pathlib import Path
from typing import List, Tuple, Dict, Any

class Colors:
    """ANSI color codes for terminal output."""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

class SetupValidator:
    """Validates the setup and configuration of the YouTube Transcript Chatbot."""
    
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.success_count = 0
        self.total_checks = 0
    
    def print_header(self):
        """Print validation header."""
        print(f"\n{Colors.BOLD}{Colors.BLUE}🔍 YouTube Transcript Chatbot - Setup Validation{Colors.END}")
        print("=" * 60)
    
    def print_result(self, check_name: str, success: bool, message: str = ""):
        """Print check result."""
        self.total_checks += 1
        if success:
            self.success_count += 1
            status = f"{Colors.GREEN}✓{Colors.END}"
        else:
            status = f"{Colors.RED}✗{Colors.END}"
        
        print(f"{status} {check_name}")
        if message:
            print(f"  {message}")
    
    def check_python_version(self) -> bool:
        """Check Python version compatibility."""
        version = sys.version_info
        required_major, required_minor = 3, 8
        
        if version.major >= required_major and version.minor >= required_minor:
            self.print_result(
                "Python Version", 
                True, 
                f"Python {version.major}.{version.minor}.{version.micro}"
            )
            return True
        else:
            self.print_result(
                "Python Version", 
                False, 
                f"Python {version.major}.{version.minor}.{version.micro} (requires >= {required_major}.{required_minor})"
            )
            self.errors.append(f"Python version {required_major}.{required_minor}+ required")
            return False
    
    def check_required_packages(self) -> bool:
        """Check if required packages are installed."""
        required_packages = [
            'streamlit',
            'langchain',
            'langchain_community',
            'openai',
            'pytube',
            'youtube_transcript_api',
            'faiss',
            'dotenv',
            'yaml',
            'reportlab'
        ]
        
        all_installed = True
        missing_packages = []
        
        for package in required_packages:
            try:
                if package == 'faiss':
                    importlib.import_module('faiss')
                elif package == 'dotenv':
                    importlib.import_module('dotenv')
                elif package == 'yaml':
                    importlib.import_module('yaml')
                else:
                    importlib.import_module(package)
                
            except ImportError:
                all_installed = False
                missing_packages.append(package)
        
        if all_installed:
            self.print_result("Required Packages", True, "All packages installed")
        else:
            self.print_result(
                "Required Packages", 
                False, 
                f"Missing: {', '.join(missing_packages)}"
            )
            self.errors.append(f"Install missing packages: pip install {' '.join(missing_packages)}")
        
        return all_installed
    
    def check_project_structure(self) -> bool:
        """Check if project structure is correct."""
        required_files = [
            'app.py',
            'requirements.txt',
            '.env.template',
            'README.md',
            'src/__init__.py',
            'src/utils/__init__.py',
            'src/utils/youtube_handler.py',
            'src/utils/text_processor.py',
            'src/utils/session_manager.py',
            'config/config.yaml',
            'config/settings.py',
            'static/style.css'
        ]
        
        required_dirs = [
            'src',
            'src/utils',
            'config',
            'static',
            'tests'
        ]
        
        missing_files = []
        missing_dirs = []
        
        # Check directories
        for dir_path in required_dirs:
            if not Path(dir_path).exists():
                missing_dirs.append(dir_path)
        
        # Check files
        for file_path in required_files:
            if not Path(file_path).exists():
                missing_files.append(file_path)
        
        if not missing_files and not missing_dirs:
            self.print_result("Project Structure", True, "All required files and directories present")
            return True
        else:
            missing_items = missing_dirs + missing_files
            self.print_result(
                "Project Structure", 
                False, 
                f"Missing: {', '.join(missing_items[:5])}{'...' if len(missing_items) > 5 else ''}"
            )
            self.errors.append("Project structure incomplete")
            return False
    
    def check_environment_config(self) -> bool:
        """Check environment configuration."""
        env_file = Path('.env')
        env_template = Path('.env.template')
        
        if not env_template.exists():
            self.print_result("Environment Template", False, ".env.template not found")
            self.errors.append("Create .env.template file")
            return False
        
        if not env_file.exists():
            self.print_result(
                "Environment File", 
                False, 
                ".env file not found (copy from .env.template)"
            )
            self.warnings.append("Create .env file from template and add your OpenAI API key")
            return False
        
        # Check for OpenAI API key
        try:
            from dotenv import load_dotenv
            load_dotenv()
            
            api_key = os.getenv('OPENAI_API_KEY')
            if api_key and api_key != 'your_openai_api_key_here':
                self.print_result("OpenAI API Key", True, "API key configured")
                return True
            else:
                self.print_result("OpenAI API Key", False, "API key not set or using template value")
                self.errors.append("Set OPENAI_API_KEY in .env file")
                return False
                
        except Exception as e:
            self.print_result("Environment Configuration", False, f"Error loading .env: {e}")
            self.errors.append("Fix .env file configuration")
            return False
    
    def check_imports(self) -> bool:
        """Check if custom modules can be imported."""
        modules_to_check = [
            'src.utils.youtube_handler',
            'src.utils.text_processor',
            'src.utils.session_manager',
            'config.settings'
        ]
        
        import_errors = []
        
        # Add src to path temporarily
        sys.path.insert(0, str(Path.cwd()))
        
        for module in modules_to_check:
            try:
                importlib.import_module(module)
            except ImportError as e:
                import_errors.append(f"{module}: {e}")
        
        # Remove from path
        sys.path.pop(0)
        
        if not import_errors:
            self.print_result("Module Imports", True, "All custom modules importable")
            return True
        else:
            self.print_result(
                "Module Imports", 
                False, 
                f"Import errors: {len(import_errors)}"
            )
            for error in import_errors[:3]:  # Show first 3 errors
                print(f"    {error}")
            self.errors.append("Fix module import errors")
            return False
    
    def check_streamlit_config(self) -> bool:
        """Check Streamlit configuration."""
        try:
            result = subprocess.run(
                ['streamlit', '--version'], 
                capture_output=True, 
                text=True, 
                timeout=10
            )
            
            if result.returncode == 0:
                version = result.stdout.strip()
                self.print_result("Streamlit Installation", True, version)
                return True
            else:
                self.print_result("Streamlit Installation", False, "Streamlit command failed")
                self.errors.append("Streamlit not properly installed")
                return False
                
        except (subprocess.TimeoutExpired, FileNotFoundError):
            self.print_result("Streamlit Installation", False, "Streamlit command not found")
            self.errors.append("Install Streamlit: pip install streamlit")
            return False
    
    def check_directory_permissions(self) -> bool:
        """Check directory permissions for cache, data, and logs."""
        directories = ['cache', 'data', 'logs']
        permission_issues = []
        
        for dir_name in directories:
            dir_path = Path(dir_name)
            
            try:
                # Create directory if it doesn't exist
                dir_path.mkdir(exist_ok=True)
                
                # Test write permission
                test_file = dir_path / 'test_write.tmp'
                test_file.write_text('test')
                test_file.unlink()
                
            except PermissionError:
                permission_issues.append(dir_name)
            except Exception as e:
                permission_issues.append(f"{dir_name} ({e})")
        
        if not permission_issues:
            self.print_result("Directory Permissions", True, "All directories writable")
            return True
        else:
            self.print_result(
                "Directory Permissions", 
                False, 
                f"Issues with: {', '.join(permission_issues)}"
            )
            self.errors.append("Fix directory permissions")
            return False
    
    def run_basic_functionality_test(self) -> bool:
        """Run basic functionality test."""
        try:
            # Add src to path
            sys.path.insert(0, str(Path.cwd()))
            
            from src.utils.youtube_handler import YouTubeHandler
            
            handler = YouTubeHandler()
            
            # Test URL validation
            valid_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
            if handler.validate_youtube_url(valid_url):
                self.print_result("Basic Functionality", True, "URL validation working")
                return True
            else:
                self.print_result("Basic Functionality", False, "URL validation failed")
                self.errors.append("Basic functionality test failed")
                return False
                
        except Exception as e:
            self.print_result("Basic Functionality", False, f"Error: {e}")
            self.errors.append("Basic functionality test failed")
            return False
        finally:
            # Remove from path
            if str(Path.cwd()) in sys.path:
                sys.path.remove(str(Path.cwd()))
    
    def print_summary(self):
        """Print validation summary."""
        print("\n" + "=" * 60)
        print(f"{Colors.BOLD}📊 Validation Summary{Colors.END}")
        print(f"Checks passed: {Colors.GREEN}{self.success_count}{Colors.END}/{self.total_checks}")
        
        if self.errors:
            print(f"\n{Colors.RED}{Colors.BOLD}❌ Errors ({len(self.errors)}):{Colors.END}")
            for i, error in enumerate(self.errors, 1):
                print(f"  {i}. {error}")
        
        if self.warnings:
            print(f"\n{Colors.YELLOW}{Colors.BOLD}⚠️  Warnings ({len(self.warnings)}):{Colors.END}")
            for i, warning in enumerate(self.warnings, 1):
                print(f"  {i}. {warning}")
        
        if not self.errors and not self.warnings:
            print(f"\n{Colors.GREEN}{Colors.BOLD}🎉 All checks passed! Your setup is ready.{Colors.END}")
            print(f"\nTo start the application, run:")
            print(f"{Colors.BLUE}streamlit run app.py{Colors.END}")
        elif not self.errors:
            print(f"\n{Colors.YELLOW}{Colors.BOLD}⚠️  Setup mostly complete with warnings.{Colors.END}")
            print(f"You can start the application, but consider addressing the warnings.")
        else:
            print(f"\n{Colors.RED}{Colors.BOLD}❌ Setup incomplete. Please fix the errors above.{Colors.END}")
    
    def validate(self):
        """Run all validation checks."""
        self.print_header()
        
        # Run all checks
        self.check_python_version()
        self.check_required_packages()
        self.check_project_structure()
        self.check_environment_config()
        self.check_imports()
        self.check_streamlit_config()
        self.check_directory_permissions()
        self.run_basic_functionality_test()
        
        self.print_summary()
        
        # Return True if no errors
        return len(self.errors) == 0

def main():
    """Main function."""
    validator = SetupValidator()
    success = validator.validate()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
