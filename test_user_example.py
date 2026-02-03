#!/usr/bin/env python3
"""Test the exact user example"""

from cursor_to_jira_converter import CursorToJiraConverter

def test_user_example():
    converter = CursorToJiraConverter()
    
    # User's exact example
    input_text = """When `resetStateForRetry()` is called:

1. **Channels:** All message channels are released and cleared
2. **Counters:** All request/response counters reset to 0
3. **Collections:** Failed hosts list cleared, channels map/list cleared
4. **Files:** Partial result files rolled back/deleted
5. **Profile Counters:** Written profiles count reset to 0 (prevents accumulation across retries)
6. **Worker State:** Collision cache cleared, output params reset

## Configuration

The maximum retry attempts can be adjusted by modifying `m_maxRetryAttempts` (default: 3).
Future enhancement: Make this configurable via system configuration or task parameters."""
    
    result = converter.convert_text(input_text)
    
    print("=" * 70)
    print("INPUT (Markdown):")
    print("=" * 70)
    print(input_text)
    print()
    print("=" * 70)
    print("OUTPUT (Jira):")
    print("=" * 70)
    print(result)
    print()
    
    # Check for blank line before h2
    lines = result.split('\n')
    for i, line in enumerate(lines):
        if line.startswith('h2.'):
            if i > 0 and lines[i-1] == '':
                print("✓ Blank line before header found (correct!)")
            else:
                print("✗ No blank line before header (incorrect!)")
            break

if __name__ == "__main__":
    test_user_example()
