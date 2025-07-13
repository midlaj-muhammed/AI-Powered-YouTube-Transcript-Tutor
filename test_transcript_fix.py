#!/usr/bin/env python3
"""
Test script to verify the YouTube transcript fixes work.
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.utils.youtube_handler import YouTubeHandler
from src.utils.logger import setup_logging

def test_transcript_extraction():
    """Test transcript extraction with various videos."""
    
    # Setup logging
    setup_logging()
    
    # Initialize handler
    handler = YouTubeHandler()
    
    # Test videos - mix of working and potentially problematic ones
    test_videos = [
        {
            "name": "3Blue1Brown - Neural Networks",
            "url": "https://www.youtube.com/watch?v=aircAruvnKk",
            "expected": "should work"
        },
        {
            "name": "Khan Academy - Intro to Programming",
            "url": "https://www.youtube.com/watch?v=WUvTyaaNkzM",
            "expected": "should work"
        },
        {
            "name": "TED-Ed - How does the brain work",
            "url": "https://www.youtube.com/watch?v=kBdfcR-8hEY",
            "expected": "should work"
        },
        {
            "name": "Test video (may fail)",
            "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "expected": "may fail"
        }
    ]
    
    print("🧪 Testing YouTube Transcript Extraction Fixes")
    print("=" * 60)
    
    results = []
    
    for video in test_videos:
        print(f"\n🎬 Testing: {video['name']}")
        print(f"URL: {video['url']}")
        print(f"Expected: {video['expected']}")
        print("-" * 40)
        
        try:
            result = handler.get_youtube_transcript(video['url'])
            
            if result['success']:
                transcript_length = len(result['transcript'])
                used_language = result.get('used_language', 'unknown')
                available_languages = result.get('available_languages', [])
                
                print(f"✅ SUCCESS!")
                print(f"   Transcript length: {transcript_length} characters")
                print(f"   Language used: {used_language}")
                print(f"   Available languages: {len(available_languages)}")
                
                if available_languages:
                    lang_codes = [lang.get('language_code', 'unknown') for lang in available_languages]
                    print(f"   Language codes: {', '.join(lang_codes[:5])}")
                
                # Show first 100 characters of transcript
                preview = result['transcript'][:100] + "..." if len(result['transcript']) > 100 else result['transcript']
                print(f"   Preview: {preview}")
                
                results.append({"video": video['name'], "status": "SUCCESS", "length": transcript_length})
                
            else:
                error = result['error']
                suggestion = result.get('suggestion', 'No suggestion available')
                
                print(f"❌ FAILED: {error}")
                if suggestion:
                    print(f"   Suggestion: {suggestion}")
                
                results.append({"video": video['name'], "status": "FAILED", "error": error})
                
        except Exception as e:
            print(f"💥 EXCEPTION: {str(e)}")
            results.append({"video": video['name'], "status": "EXCEPTION", "error": str(e)})
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 SUMMARY")
    print("=" * 60)
    
    successful = sum(1 for r in results if r['status'] == 'SUCCESS')
    failed = sum(1 for r in results if r['status'] == 'FAILED')
    exceptions = sum(1 for r in results if r['status'] == 'EXCEPTION')
    
    print(f"✅ Successful: {successful}")
    print(f"❌ Failed: {failed}")
    print(f"💥 Exceptions: {exceptions}")
    print(f"📊 Success Rate: {successful}/{len(results)} ({successful/len(results)*100:.1f}%)")
    
    # Detailed results
    print("\n📋 Detailed Results:")
    for result in results:
        status_emoji = "✅" if result['status'] == 'SUCCESS' else "❌" if result['status'] == 'FAILED' else "💥"
        print(f"{status_emoji} {result['video']}: {result['status']}")
        if result['status'] == 'SUCCESS':
            print(f"    Length: {result['length']} characters")
        elif 'error' in result:
            print(f"    Error: {result['error']}")
    
    # Recommendations
    print("\n💡 RECOMMENDATIONS:")
    if successful > 0:
        print("✅ The transcript extraction is working for some videos!")
        print("   - Use educational content (Khan Academy, TED-Ed, 3Blue1Brown)")
        print("   - Look for videos with captions enabled")
        print("   - Try popular educational channels")
    
    if failed > 0 or exceptions > 0:
        print("⚠️  Some videos failed - this is normal due to:")
        print("   - Regional restrictions")
        print("   - Disabled captions")
        print("   - Private/unavailable videos")
        print("   - Network issues")
    
    print("\n🎯 For best results, use videos from:")
    print("   - Educational channels (Khan Academy, Coursera, edX)")
    print("   - Popular science channels (3Blue1Brown, Veritasium)")
    print("   - TED Talks and TED-Ed")
    print("   - University lectures")
    
    return successful > 0

if __name__ == "__main__":
    success = test_transcript_extraction()
    print(f"\n🏁 Test completed. Overall success: {'✅ PASS' if success else '❌ FAIL'}")
    sys.exit(0 if success else 1)
