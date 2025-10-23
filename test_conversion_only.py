#!/usr/bin/env python3
"""Test only the conversion functionality with debug output"""

from cursor_to_jira_converter import CursorToJiraConverter

def test_conversion():
    converter = CursorToJiraConverter()
    
    print("Testing HTML to Markdown conversion with debug output:")
    print("=" * 60)
    
    # Read the test.html file
    with open('test.html', 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    print(f"HTML content length: {len(html_content)} characters")
    
    # Convert raw HTML directly to Jira using the new method
    jira_content = converter.convert_raw_html(html_content)
    
    print(f"\nFinal Jira content length: {len(jira_content)} characters")
    try:
        print(f"Final Jira content: {repr(jira_content)}")
    except UnicodeEncodeError:
        print(f"Final Jira content: {len(jira_content)} chars (contains Unicode)")

if __name__ == "__main__":
    test_conversion()
