#!/usr/bin/env python3
"""
Quick script to check if YouTube access is working and if IP is blocked.
"""

import sys
import os
import time

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.utils.youtube_handler import YouTubeHandler
from src.utils.logger import setup_logging

def check_youtube_access():
    """Check if YouTube access is working."""
    
    print("🔍 Checking YouTube Access Status")
    print("=" * 50)
    
    # Setup logging
    setup_logging()
    
    # Initialize handler
    handler = YouTubeHandler()
    
    # Test with a simple, reliable video
    test_url = "https://www.youtube.com/watch?v=aircAruvnKk"  # 3Blue1Brown
    
    print(f"🎬 Testing with: {test_url}")
    print("📡 Making request to YouTube...")
    
    start_time = time.time()
    result = handler.get_youtube_transcript(test_url)
    end_time = time.time()
    
    print(f"⏱️  Request took: {end_time - start_time:.2f} seconds")
    print("-" * 50)
    
    if result['success']:
        print("✅ SUCCESS: YouTube access is working!")
        print(f"   Transcript length: {len(result['transcript'])} characters")
        print(f"   Language used: {result.get('used_language', 'unknown')}")
        print(f"   Available languages: {len(result.get('available_languages', []))}")
        
        # Show first 100 characters
        preview = result['transcript'][:100] + "..." if len(result['transcript']) > 100 else result['transcript']
        print(f"   Preview: {preview}")
        
        print("\n🎉 Your IP is NOT blocked. You can use the application normally!")
        return True
        
    else:
        error = result['error']
        print(f"❌ FAILED: {error}")
        
        # Check if it's an IP blocking issue
        error_lower = error.lower()
        if "ip blocked" in error_lower or "cloud provider" in error_lower:
            print("\n🚫 IP BLOCKING DETECTED")
            print("=" * 30)
            print("Your IP address has been blocked by YouTube.")
            print("\n💡 SOLUTIONS:")
            print("1. ⏰ Wait 15-30 minutes before trying again")
            print("2. 🌐 Try a different network (mobile hotspot, different WiFi)")
            print("3. 🔄 Restart your router to get a new IP address")
            print("4. 🏠 Try from a home network instead of cloud/office network")
            
            print("\n⚠️  PREVENTION:")
            print("- Don't make too many requests in a short time")
            print("- Wait at least 3-5 seconds between video processing")
            print("- Avoid processing multiple videos rapidly")
            
        elif "rate limited" in error_lower or "too many requests" in error_lower:
            print("\n⚡ RATE LIMITING DETECTED")
            print("=" * 30)
            print("You're making requests too quickly.")
            print("\n💡 SOLUTION:")
            print("- Wait 5-10 minutes before trying again")
            print("- The app now includes automatic rate limiting")
            
        else:
            print(f"\n🤔 OTHER ISSUE: {error}")
            if 'suggestion' in result:
                print(f"💡 Suggestion: {result['suggestion']}")
            if 'details' in result:
                print(f"📝 Details: {result['details']}")
        
        return False

def main():
    """Main function."""
    print("🎓 YouTube Transcript Tutor - Access Check")
    print("This tool checks if your IP is blocked by YouTube\n")
    
    success = check_youtube_access()
    
    print("\n" + "=" * 50)
    if success:
        print("🎊 RESULT: YouTube access is working normally!")
        print("You can use the application without issues.")
    else:
        print("⚠️  RESULT: YouTube access is currently blocked or limited.")
        print("Follow the suggestions above to resolve the issue.")
    
    print("\n📚 For more help, check the troubleshooting section in the app sidebar.")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
