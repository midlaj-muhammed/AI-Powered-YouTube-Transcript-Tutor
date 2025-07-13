#!/usr/bin/env python3
"""
Test runner script for YouTube Transcript Chatbot.
This script runs all tests and provides a comprehensive test report.
"""

import os
import sys
import unittest
import subprocess
from pathlib import Path
from typing import List, Dict, Any

class Colors:
    """ANSI color codes for terminal output."""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

class TestRunner:
    """Comprehensive test runner for the YouTube Transcript Chatbot."""
    
    def __init__(self):
        self.test_results = {}
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        self.errors = []
    
    def print_header(self):
        """Print test runner header."""
        print(f"\n{Colors.BOLD}{Colors.BLUE}🧪 YouTube Transcript Chatbot - Test Suite{Colors.END}")
        print("=" * 60)
    
    def discover_tests(self) -> List[str]:
        """Discover all test files."""
        test_dir = Path('tests')
        if not test_dir.exists():
            print(f"{Colors.RED}❌ Tests directory not found{Colors.END}")
            return []
        
        test_files = []
        for test_file in test_dir.glob('test_*.py'):
            test_files.append(str(test_file))
        
        return sorted(test_files)
    
    def run_unit_tests(self) -> bool:
        """Run unit tests using unittest."""
        print(f"\n{Colors.BOLD}📋 Running Unit Tests{Colors.END}")
        print("-" * 30)
        
        # Add src to Python path
        sys.path.insert(0, str(Path.cwd()))
        
        try:
            # Discover and run tests
            loader = unittest.TestLoader()
            start_dir = 'tests'
            suite = loader.discover(start_dir, pattern='test_*.py')
            
            # Run tests with detailed output
            runner = unittest.TextTestRunner(
                verbosity=2,
                stream=sys.stdout,
                buffer=True
            )
            
            result = runner.run(suite)
            
            # Store results
            self.total_tests += result.testsRun
            self.failed_tests += len(result.failures) + len(result.errors)
            self.passed_tests = self.total_tests - self.failed_tests
            
            # Print summary
            if result.wasSuccessful():
                print(f"\n{Colors.GREEN}✓ All unit tests passed ({result.testsRun} tests){Colors.END}")
                return True
            else:
                print(f"\n{Colors.RED}❌ Unit tests failed{Colors.END}")
                print(f"  Tests run: {result.testsRun}")
                print(f"  Failures: {len(result.failures)}")
                print(f"  Errors: {len(result.errors)}")
                
                # Show failures and errors
                if result.failures:
                    print(f"\n{Colors.YELLOW}Failures:{Colors.END}")
                    for test, traceback in result.failures:
                        print(f"  - {test}")
                        print(f"    {traceback.split('AssertionError:')[-1].strip()}")
                
                if result.errors:
                    print(f"\n{Colors.RED}Errors:{Colors.END}")
                    for test, traceback in result.errors:
                        print(f"  - {test}")
                        print(f"    {traceback.split('Exception:')[-1].strip()}")
                
                return False
                
        except Exception as e:
            print(f"{Colors.RED}❌ Error running unit tests: {e}{Colors.END}")
            self.errors.append(f"Unit test error: {e}")
            return False
        finally:
            # Remove from path
            if str(Path.cwd()) in sys.path:
                sys.path.remove(str(Path.cwd()))
    
    def run_linting(self) -> bool:
        """Run code linting with flake8."""
        print(f"\n{Colors.BOLD}🔍 Running Code Linting{Colors.END}")
        print("-" * 30)
        
        try:
            # Check if flake8 is available
            result = subprocess.run(['flake8', '--version'], capture_output=True, text=True)
            if result.returncode != 0:
                print(f"{Colors.YELLOW}⚠️  flake8 not available, skipping linting{Colors.END}")
                return True
            
            # Run flake8 on source code
            files_to_check = ['src/', 'tests/', 'app.py']
            existing_files = [f for f in files_to_check if Path(f).exists()]
            
            if not existing_files:
                print(f"{Colors.YELLOW}⚠️  No files to lint{Colors.END}")
                return True
            
            result = subprocess.run(
                ['flake8'] + existing_files + ['--max-line-length=88', '--ignore=E203,W503'],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                print(f"{Colors.GREEN}✓ Code linting passed{Colors.END}")
                return True
            else:
                print(f"{Colors.RED}❌ Code linting failed{Colors.END}")
                print(result.stdout)
                return False
                
        except FileNotFoundError:
            print(f"{Colors.YELLOW}⚠️  flake8 not installed, skipping linting{Colors.END}")
            return True
        except Exception as e:
            print(f"{Colors.RED}❌ Error running linting: {e}{Colors.END}")
            return False
    
    def run_import_tests(self) -> bool:
        """Test that all modules can be imported."""
        print(f"\n{Colors.BOLD}📦 Testing Module Imports{Colors.END}")
        print("-" * 30)
        
        modules_to_test = [
            'src.utils.youtube_handler',
            'src.utils.text_processor',
            'src.utils.session_manager',
            'src.utils.export_utils',
            'src.utils.database',
            'src.utils.cache_manager',
            'src.utils.logger',
            'config.settings'
        ]
        
        # Add src to path
        sys.path.insert(0, str(Path.cwd()))
        
        import_errors = []
        
        for module in modules_to_test:
            try:
                __import__(module)
                print(f"{Colors.GREEN}✓{Colors.END} {module}")
            except ImportError as e:
                print(f"{Colors.RED}❌{Colors.END} {module}: {e}")
                import_errors.append(f"{module}: {e}")
            except Exception as e:
                print(f"{Colors.YELLOW}⚠️{Colors.END} {module}: {e}")
                import_errors.append(f"{module}: {e}")
        
        # Remove from path
        if str(Path.cwd()) in sys.path:
            sys.path.remove(str(Path.cwd()))
        
        if not import_errors:
            print(f"\n{Colors.GREEN}✓ All modules imported successfully{Colors.END}")
            return True
        else:
            print(f"\n{Colors.RED}❌ Import errors found ({len(import_errors)}){Colors.END}")
            return False
    
    def run_configuration_tests(self) -> bool:
        """Test configuration loading."""
        print(f"\n{Colors.BOLD}⚙️  Testing Configuration{Colors.END}")
        print("-" * 30)
        
        try:
            # Add src to path
            sys.path.insert(0, str(Path.cwd()))
            
            from config.settings import settings
            
            # Test basic configuration access
            app_config = settings.get_app_config()
            ui_config = settings.get_ui_config()
            processing_config = settings.get_processing_config()
            
            if app_config and ui_config and processing_config:
                print(f"{Colors.GREEN}✓ Configuration loaded successfully{Colors.END}")
                print(f"  App title: {app_config.get('title', 'N/A')}")
                print(f"  Supported languages: {len(processing_config.get('supported_languages', []))}")
                return True
            else:
                print(f"{Colors.RED}❌ Configuration loading failed{Colors.END}")
                return False
                
        except Exception as e:
            print(f"{Colors.RED}❌ Configuration test failed: {e}{Colors.END}")
            return False
        finally:
            # Remove from path
            if str(Path.cwd()) in sys.path:
                sys.path.remove(str(Path.cwd()))
    
    def run_basic_functionality_tests(self) -> bool:
        """Run basic functionality tests."""
        print(f"\n{Colors.BOLD}🔧 Testing Basic Functionality{Colors.END}")
        print("-" * 30)
        
        try:
            # Add src to path
            sys.path.insert(0, str(Path.cwd()))
            
            from src.utils.youtube_handler import YouTubeHandler
            
            handler = YouTubeHandler()
            
            # Test URL validation
            test_urls = [
                ("https://www.youtube.com/watch?v=dQw4w9WgXcQ", True),
                ("https://youtu.be/dQw4w9WgXcQ", True),
                ("https://www.google.com", False),
                ("invalid_url", False)
            ]
            
            all_passed = True
            for url, expected in test_urls:
                result = handler.validate_youtube_url(url)
                if result == expected:
                    print(f"{Colors.GREEN}✓{Colors.END} URL validation: {url[:30]}...")
                else:
                    print(f"{Colors.RED}❌{Colors.END} URL validation failed: {url[:30]}...")
                    all_passed = False
            
            if all_passed:
                print(f"\n{Colors.GREEN}✓ Basic functionality tests passed{Colors.END}")
                return True
            else:
                print(f"\n{Colors.RED}❌ Basic functionality tests failed{Colors.END}")
                return False
                
        except Exception as e:
            print(f"{Colors.RED}❌ Basic functionality test error: {e}{Colors.END}")
            return False
        finally:
            # Remove from path
            if str(Path.cwd()) in sys.path:
                sys.path.remove(str(Path.cwd()))
    
    def print_summary(self):
        """Print test summary."""
        print("\n" + "=" * 60)
        print(f"{Colors.BOLD}📊 Test Summary{Colors.END}")
        
        if self.total_tests > 0:
            print(f"Unit Tests: {Colors.GREEN}{self.passed_tests}{Colors.END}/{self.total_tests} passed")
            if self.failed_tests > 0:
                print(f"Failed Tests: {Colors.RED}{self.failed_tests}{Colors.END}")
        
        if self.errors:
            print(f"\n{Colors.RED}{Colors.BOLD}❌ Errors:{Colors.END}")
            for error in self.errors:
                print(f"  - {error}")
        
        success_rate = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        
        if success_rate == 100 and not self.errors:
            print(f"\n{Colors.GREEN}{Colors.BOLD}🎉 All tests passed!{Colors.END}")
        elif success_rate >= 80:
            print(f"\n{Colors.YELLOW}{Colors.BOLD}⚠️  Most tests passed ({success_rate:.1f}%){Colors.END}")
        else:
            print(f"\n{Colors.RED}{Colors.BOLD}❌ Many tests failed ({success_rate:.1f}%){Colors.END}")
    
    def run_all_tests(self) -> bool:
        """Run all tests."""
        self.print_header()
        
        all_passed = True
        
        # Run different test categories
        test_categories = [
            ("Unit Tests", self.run_unit_tests),
            ("Import Tests", self.run_import_tests),
            ("Configuration Tests", self.run_configuration_tests),
            ("Basic Functionality", self.run_basic_functionality_tests),
            ("Code Linting", self.run_linting)
        ]
        
        for category_name, test_func in test_categories:
            try:
                if not test_func():
                    all_passed = False
            except Exception as e:
                print(f"{Colors.RED}❌ Error in {category_name}: {e}{Colors.END}")
                self.errors.append(f"{category_name}: {e}")
                all_passed = False
        
        self.print_summary()
        return all_passed

def main():
    """Main function."""
    runner = TestRunner()
    success = runner.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
