#!/usr/bin/env python3
"""
Test script for content validation functionality.
Run this to verify the validation rules work correctly.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from main import validate_content

def test_validation():
    """Test various content validation scenarios."""
    
    test_cases = [
        # (content, should_pass, description)
        ("This is a normal post about technology", True, "Valid normal post"),
        ("", False, "Empty content"),
        ("   ", False, "Whitespace only"),
        ("short", False, "Too short"),
        ("A" * 300, False, "Exceeds character limit"),
        ("Hello world! This is a test post.", True, "Valid with punctuation"),
        ("Check this out! Amazing! Wow! Cool!", False, "Excessive exclamation marks"),
        ("What? What? What? What? What?", False, "Excessive question marks"),
        ("This is a test test test test test", False, "Repetitive content"),
        ("Lorem ipsum dolor sit amet", False, "Contains placeholder text"),
        ("TODO: Write actual content here", False, "Contains TODO placeholder"),
        ("HELLO EVERYONE THIS IS ALL CAPS", False, "All caps content"),
        ("Short ALL CAPS", True, "Short all caps is OK"),
        ("Check out http://example.com and http://test.com and http://spam.com", False, "Too many URLs"),
        ("Visit my site at https://example.com", True, "One URL is fine"),
        ("The quick brown fox jumps over the lazy dog multiple times", True, "Valid longer post"),
        ("Sample text for testing purposes", False, "Contains 'sample text' placeholder"),
        ("This is an example post to demonstrate", False, "Contains 'example post' placeholder"),
        ("Generated text goes here", False, "Contains 'generated text' placeholder"),
        ("Just a regular tweet about my day!", True, "Valid casual post"),
        ("!!!!!!", False, "Only punctuation"),
        ("This is fine... but this... pattern... repeats... too much...", False, "Excessive ellipsis"),
    ]
    
    print("🧪 Running Content Validation Tests\n")
    print("=" * 70)
    
    passed = 0
    failed = 0
    
    for content, should_pass, description in test_cases:
        is_valid, error_msg = validate_content(content, char_limit=280)
        
        # Truncate long content for display
        display_content = content[:50] + "..." if len(content) > 50 else content
        
        if is_valid == should_pass:
            status = "✅ PASS"
            passed += 1
        else:
            status = "❌ FAIL"
            failed += 1
        
        print(f"\n{status}: {description}")
        print(f"   Content: \"{display_content}\"")
        print(f"   Expected: {'Valid' if should_pass else 'Invalid'}, Got: {'Valid' if is_valid else 'Invalid'}")
        if error_msg:
            print(f"   Error: {error_msg}")
    
    print("\n" + "=" * 70)
    print(f"\n📊 Test Results: {passed} passed, {failed} failed out of {len(test_cases)} tests")
    
    if failed == 0:
        print("🎉 All tests passed!\n")
        return 0
    else:
        print(f"⚠️  {failed} test(s) failed.\n")
        return 1

if __name__ == "__main__":
    exit(test_validation())
