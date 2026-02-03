#!/usr/bin/env python3
"""Test the specific user issue with inline code"""

from cursor_to_jira_converter import CursorToJiraConverter

def test_user_issue():
    converter = CursorToJiraConverter()
    
    # Test 1: Simple unordered list with inline code
    print("Test 1: No indentation")
    input_text = "- Calls parent `ToFileAggregatorDFTaskWorker::resetForRetry()`"
    result = converter.convert_text(input_text)
    print(f"Input:  {repr(input_text)}")
    print(f"Output: {repr(result)}")
    print(f"Visual: {result}")
    print()
    
    # Test 2: With 2 spaces indentation (nested list)
    print("Test 2: With 2 spaces indentation")
    input_text = "  - Calls parent `ToFileAggregatorDFTaskWorker::resetForRetry()`"
    result = converter.convert_text(input_text)
    print(f"Input:  {repr(input_text)}")
    print(f"Output: {repr(result)}")
    print(f"Visual: {result}")
    print()
    
    # Test 3: After a numbered list item
    print("Test 3: After a numbered list item")
    input_text = """1. First item
- Calls parent `ToFileAggregatorDFTaskWorker::resetForRetry()`"""
    result = converter.convert_text(input_text)
    print(f"Input:  {repr(input_text)}")
    print(f"Output: {repr(result)}")
    print(f"Visual:\n{result}")
    print()
    
    # Test 4: Multiple list items
    print("Test 4: Multiple list items")
    input_text = """- First item
- Calls parent `ToFileAggregatorDFTaskWorker::resetForRetry()`
- Third item"""
    result = converter.convert_text(input_text)
    print(f"Input:  {repr(input_text)}")
    print(f"Output: {repr(result)}")
    print(f"Visual:\n{result}")

if __name__ == "__main__":
    test_user_issue()
