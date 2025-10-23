#!/usr/bin/env python3
"""Detailed test showing actual content"""

from cursor_to_jira_converter import CursorToJiraConverter

def test_detailed():
    converter = CursorToJiraConverter()
    
    print("Detailed test with test.html file:")
    print("=" * 50)
    
    try:
        # Read the test.html file
        with open('test.html', 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        print(f"HTML content length: {len(html_content)} characters")
        
        # Convert raw HTML directly to Jira
        jira_content = converter.convert_raw_html(html_content)
        print(f"Jira content length: {len(jira_content)} characters")
        
        # Show Jira content
        print(f"Jira content: {repr(jira_content)}")
        
        # Test clipboard functionality
        print("\nTesting clipboard functionality:")
        try:
            import win32clipboard
            import win32con
            
            win32clipboard.OpenClipboard()
            win32clipboard.EmptyClipboard()
            win32clipboard.SetClipboardData(win32con.CF_UNICODETEXT, jira_content)
            win32clipboard.CloseClipboard()
            print("SUCCESS: Content copied to clipboard")
            
            # Verify clipboard content
            win32clipboard.OpenClipboard()
            clipboard_data = win32clipboard.GetClipboardData(win32con.CF_UNICODETEXT)
            win32clipboard.CloseClipboard()
            print(f"Clipboard verification: {len(clipboard_data)} characters")
            print(f"Clipboard content: {repr(clipboard_data)}")
            
        except Exception as e:
            print(f"FAILED: Clipboard error - {e}")
        
    except FileNotFoundError:
        print("ERROR: test.html file not found")
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_detailed()
