#!/usr/bin/env python3
"""
Comprehensive test suite for Cursor to Jira converter
Tests all conversion scenarios including list nesting with empty lines
"""

from cursor_to_jira_converter import CursorToJiraConverter

class TestResult:
    def __init__(self, name):
        self.name = name
        self.passed = 0
        self.failed = 0
        self.tests = []
    
    def add_test(self, test_name, passed, expected=None, actual=None):
        self.tests.append({
            'name': test_name,
            'passed': passed,
            'expected': expected,
            'actual': actual
        })
        if passed:
            self.passed += 1
        else:
            self.failed += 1
    
    def print_summary(self):
        print(f"\n{'='*70}")
        print(f"{self.name}")
        print(f"{'='*70}")
        for test in self.tests:
            status = "[PASS]" if test['passed'] else "[FAIL]"
            print(f"{status}: {test['name']}")
            if not test['passed'] and test['expected'] and test['actual']:
                print(f"  Expected: {repr(test['expected'])}")
                print(f"  Actual:   {repr(test['actual'])}")
        print(f"\nTotal: {self.passed} passed, {self.failed} failed")
        return self.failed == 0


def test_basic_formatting():
    """Test basic markdown to Jira formatting"""
    result = TestResult("Basic Formatting Tests")
    converter = CursorToJiraConverter()
    
    # Test headers
    test_cases = [
        ("## Header 2", "h2. Header 2", "Header conversion"),
        ("### Header 3", "h3. Header 3", "Header 3 conversion"),
        ("**bold text**", "*bold text*", "Bold text"),
        ("*italic text*", "_italic text_", "Italic text"),
        ("`code`", "{{code}}", "Inline code"),
        ("[link text](http://example.com)", "[link text|http://example.com]", "Links"),
        ("~~strikethrough~~", "-strikethrough-", "Strikethrough"),
    ]
    
    for input_text, expected, description in test_cases:
        actual = converter.convert_text(input_text).strip()
        result.add_test(description, actual == expected, expected, actual)
    
    return result


def test_simple_lists():
    """Test simple list conversions"""
    result = TestResult("Simple List Tests")
    converter = CursorToJiraConverter()
    
    # Unordered list
    input_text = """* item 1
* item 2
* item 3"""
    expected = """* item 1
* item 2
* item 3"""
    actual = converter.convert_text(input_text)
    result.add_test("Unordered list", actual == expected, expected, actual)
    
    # Ordered list (numbered)
    input_text = """1. first item
2. second item
3. third item"""
    expected = """# first item
# second item
# third item"""
    actual = converter.convert_text(input_text)
    result.add_test("Ordered list (numbered)", actual == expected, expected, actual)
    
    # Ordered list (# format)
    input_text = """# first item
# second item
# third item"""
    expected = """# first item
# second item
# third item"""
    actual = converter.convert_text(input_text)
    result.add_test("Ordered list (# format)", actual == expected, expected, actual)
    
    return result


def test_nested_lists_basic():
    """Test basic nested list conversions"""
    result = TestResult("Basic Nested List Tests")
    converter = CursorToJiraConverter()
    
    # Numbered list with unordered sub-items
    input_text = """1. First item
   - sub item 1.1
   - sub item 1.2
2. Second item
   - sub item 2.1"""
    
    expected = """# First item
#* sub item 1.1
#* sub item 1.2
# Second item
#* sub item 2.1"""
    
    actual = converter.convert_text(input_text)
    result.add_test("Numbered list with indented dashes", actual == expected, expected, actual)
    
    # Hash format list with asterisk sub-items
    input_text = """# First item
* sub item 1.1
* sub item 1.2
# Second item
* sub item 2.1"""
    
    expected = """# First item
#* sub item 1.1
#* sub item 1.2
# Second item
#* sub item 2.1"""
    
    actual = converter.convert_text(input_text)
    result.add_test("Hash list with asterisk sub-items", actual == expected, expected, actual)
    
    return result


def test_nested_lists_with_empty_lines():
    """Test nested lists with empty lines (should be removed)"""
    result = TestResult("Nested Lists with Empty Lines")
    converter = CursorToJiraConverter()
    
    # Test case 1: Empty lines between ordered items
    input_text = """1. First item
   - sub 1.1
   - sub 1.2

2. Second item
   - sub 2.1

3. Third item
   - sub 3.1"""
    
    expected = """# First item
#* sub 1.1
#* sub 1.2
# Second item
#* sub 2.1
# Third item
#* sub 3.1"""
    
    actual = converter.convert_text(input_text)
    result.add_test("Empty lines between ordered items (removed)", actual == expected, expected, actual)
    
    # Test case 2: Empty lines within sub-items (should be removed)
    input_text = """1. First item
   - sub 1.1

   - sub 1.2
2. Second item
   - sub 2.1"""
    
    expected = """# First item
#* sub 1.1
#* sub 1.2
# Second item
#* sub 2.1"""
    
    actual = converter.convert_text(input_text)
    result.add_test("Empty lines within sub-items (removed)", actual == expected, expected, actual)
    
    # Test case 3: User's original example
    input_text = """# *Campaign Template Versioning*
   * System shall support multiple versions of a campaign template for a single running campaign

# *Business Rule "Final" Flag*
   * Business Rules shall support a "Final" flag configuration"""
    
    # Note: The input already has markdown formatting, so we need to handle it properly
    expected_lines = [
        '# _Campaign Template Versioning_',
        '#* System shall support multiple versions of a campaign template for a single running campaign',
        '# _Business Rule "Final" Flag_',
        '#* Business Rules shall support a "Final" flag configuration'
    ]
    expected = '\n'.join(expected_lines)
    
    actual = converter.convert_text(input_text)
    # Check that no empty lines exist between # items
    has_empty_between = '\n\n#' in actual
    result.add_test("User example - no empty lines between # items", not has_empty_between, "No \\n\\n# pattern", actual)
    
    # Test case 4: Multiple empty lines
    input_text = """1. First item
   - sub 1.1


2. Second item
   - sub 2.1"""
    
    expected = """# First item
#* sub 1.1
# Second item
#* sub 2.1"""
    
    actual = converter.convert_text(input_text)
    result.add_test("Multiple empty lines (all removed)", actual == expected, expected, actual)
    
    return result


def test_nested_lists_with_bold():
    """Test nested lists with bold formatting"""
    result = TestResult("Nested Lists with Bold Formatting")
    converter = CursorToJiraConverter()
    
    input_text = """1. **Campaign Template Versioning**
   - System shall support multiple versions of a campaign template for a single running campaign
   - Campaign page shall display a template version selector to control which version is active

2. **Business Rule "Final" Flag**
   - Business Rules shall support a "Final" flag configuration
   - The flag shall prevent modifications when set to true"""
    
    expected = """# *Campaign Template Versioning*
#* System shall support multiple versions of a campaign template for a single running campaign
#* Campaign page shall display a template version selector to control which version is active
# *Business Rule "Final" Flag*
#* Business Rules shall support a "Final" flag configuration
#* The flag shall prevent modifications when set to true"""
    
    actual = converter.convert_text(input_text)
    result.add_test("Bold ordered items with nested lists", actual == expected, expected, actual)
    
    return result


def test_mixed_content():
    """Test lists mixed with other content"""
    result = TestResult("Mixed Content Tests")
    converter = CursorToJiraConverter()
    
    input_text = """## Acceptance Criteria

1. **First Requirement**
   - sub requirement 1.1
   - sub requirement 1.2

2. **Second Requirement**
   - sub requirement 2.1

Some paragraph text here.

3. **Third Requirement**
   - sub requirement 3.1"""
    
    expected = """h2. Acceptance Criteria

# *First Requirement*
#* sub requirement 1.1
#* sub requirement 1.2
# *Second Requirement*
#* sub requirement 2.1
Some paragraph text here.

# *Third Requirement*
#* sub requirement 3.1"""
    
    actual = converter.convert_text(input_text)
    result.add_test("Lists mixed with headers and paragraphs", actual == expected, expected, actual)
    
    return result


def test_edge_cases():
    """Test edge cases and special scenarios"""
    result = TestResult("Edge Case Tests")
    converter = CursorToJiraConverter()
    
    # Test case 1: List item with no sub-items
    input_text = """1. First item
2. Second item
3. Third item"""
    
    expected = """# First item
# Second item
# Third item"""
    
    actual = converter.convert_text(input_text)
    result.add_test("Ordered list with no sub-items", actual == expected, expected, actual)
    
    # Test case 2: Single list item with sub-items
    input_text = """1. Only item
   - sub 1.1
   - sub 1.2"""
    
    expected = """# Only item
#* sub 1.1
#* sub 1.2"""
    
    actual = converter.convert_text(input_text)
    result.add_test("Single item with sub-items", actual == expected, expected, actual)
    
    # Test case 3: Different bullet markers
    input_text = """1. First item
   * asterisk sub-item
   - dash sub-item
   + plus sub-item"""
    
    expected = """# First item
#* asterisk sub-item
#* dash sub-item
#* plus sub-item"""
    
    actual = converter.convert_text(input_text)
    result.add_test("Different bullet markers (*, -, +)", actual == expected, expected, actual)
    
    # Test case 4: Headers should not be treated as lists
    input_text = """## This is a header
# This is an ordered list item
### Another header"""
    
    actual = converter.convert_text(input_text)
    has_h2 = 'h2.' in actual
    has_h3 = 'h3.' in actual
    has_list = actual.count('# This is an ordered list item') == 1
    result.add_test("Headers vs ordered lists distinction", has_h2 and has_h3 and has_list, 
                   "Should have h2, h3, and one # list item", actual)
    
    return result


def test_code_blocks():
    """Test code blocks are preserved"""
    result = TestResult("Code Block Tests")
    converter = CursorToJiraConverter()
    
    input_text = """Some text

```python
def hello():
    print("world")
```

More text"""
    
    expected = """Some text

{code:python}
def hello():
    print("world")
{code}

More text"""
    
    actual = converter.convert_text(input_text)
    result.add_test("Code block with language", actual == expected, expected, actual)
    
    return result


def test_nested_unordered_lists():
    """Test nested unordered lists (not under ordered lists)"""
    result = TestResult("Nested Unordered List Tests")
    converter = CursorToJiraConverter()
    
    # Test 2-level nested unordered list
    input_text = """- Item 1
- Item 2 with sub-items:
  - Sub-item 2.1
  - Sub-item 2.2
- Item 3"""
    
    expected = """* Item 1
* Item 2 with sub-items:
** Sub-item 2.1
** Sub-item 2.2
* Item 3"""
    
    actual = converter.convert_text(input_text)
    result.add_test("2-level unordered list", actual == expected, expected, actual)
    
    # Test user's AC example
    input_text = """### **1. Message Pattern Variable Configuration**
- **AC1.1:** User can define variables
- **AC1.2:** System supports three variable source types:
  - **SPD (Stat Parameter)** - only common SPDs
  - **Cube values** - generic cubes"""
    
    actual = converter.convert_text(input_text)
    # Check that nested items use **
    has_double_star = '** *SPD' in actual and '** *Cube' in actual
    result.add_test("User AC example with nested items",
                   has_double_star,
                   "Nested items use ** syntax",
                   f"Has **: {has_double_star}")
    
    return result


def test_horizontal_rules():
    """Test horizontal rule conversion"""
    result = TestResult("Horizontal Rule Tests")
    converter = CursorToJiraConverter()
    
    # Test basic horizontal rule
    input_text = """Some text

---

More text"""
    
    expected = """Some text

----

More text"""
    
    actual = converter.convert_text(input_text)
    result.add_test("Basic horizontal rule", actual == expected, expected, actual)
    
    # Test horizontal rule after list
    input_text = """1. Item one
   - sub item

---"""
    
    expected = """# Item one
#* sub item

----"""
    
    actual = converter.convert_text(input_text)
    result.add_test("Horizontal rule after list with empty line", actual == expected, expected, actual)
    
    # Test horizontal rule between lists
    input_text = """1. First list

---

2. Second list"""
    
    expected = """# First list

----

# Second list"""
    
    actual = converter.convert_text(input_text)
    result.add_test("Horizontal rule between lists", actual == expected, expected, actual)
    
    # Test the user's example
    input_text = """10. **Non-Functional Requirements**
    - Solution must work for already running campaigns
    - Performance shall not impact real-time processing
    - Template version selector UI shall be intuitive

---"""
    
    actual = converter.convert_text(input_text)
    # Check that there's an empty line before ----
    lines = actual.split('\n')
    hr_index = -1
    for i, line in enumerate(lines):
        if line.strip() == '----':
            hr_index = i
            break
    
    has_empty_before_hr = hr_index > 0 and lines[hr_index - 1].strip() == ''
    result.add_test("User example - empty line before horizontal rule", 
                   has_empty_before_hr,
                   "Empty line before ----",
                   f"HR at line {hr_index}, previous line: {repr(lines[hr_index-1] if hr_index > 0 else 'N/A')}")
    
    return result


def test_jira_emoticon_escaping():
    """Test that Jira emoticons are properly escaped"""
    result = TestResult("Jira Emoticon Escaping Tests")
    converter = CursorToJiraConverter()
    
    # Test common emoticons
    test_cases = [
        ("This is (n) not good", "This is \\(n) not good", "Escape (n) thumbs down"),
        ("This is (y) good", "This is \\(y) good", "Escape (y) thumbs up"),
        ("Important (i) information", "Important \\(i) information", "Escape (i) information"),
        ("Warning (!)", "Warning \\(!)", "Escape (!) warning"),
        ("Question (?)", "Question \\(?)", "Escape (?) question"),
        ("Light (on) or (off)", "Light \\(on) or \\(off)", "Escape (on) and (off)"),
        ("Star (*) rating", "Star \\(*) rating", "Escape (*) star"),
        ("Plus (+) and minus (-)", "Plus \\(+) and minus \\(-)", "Escape (+) and (-)"),
        ("Cross (x) mark", "Cross \\(x) mark", "Escape (x) cross"),
        ("Check (/) mark", "Check \\(/) mark", "Escape (/) checkmark"),
    ]
    
    for input_text, expected, description in test_cases:
        actual = converter.convert_text(input_text).strip()
        result.add_test(description, actual == expected, expected, actual)
    
    # Test emoticon in list context
    input_text = """1. Item with (n) in text
   - Sub item with (y)"""
    
    actual = converter.convert_text(input_text)
    has_escaped_n = '\\(n)' in actual
    has_escaped_y = '\\(y)' in actual
    result.add_test("Emoticons in nested lists", has_escaped_n and has_escaped_y, 
                   "Both emoticons escaped", f"(n) escaped: {has_escaped_n}, (y) escaped: {has_escaped_y}")
    
    # Test multiple emoticons in same line
    input_text = "Status: (y) approved but (n) rejected with (i) info"
    actual = converter.convert_text(input_text)
    escaped_count = actual.count('\\(')
    result.add_test("Multiple emoticons in one line", escaped_count == 3,
                   "3 emoticons escaped", f"{escaped_count} emoticons escaped")
    
    return result


def test_html_conversion():
    """Test HTML file conversion if test.html exists"""
    result = TestResult("HTML Conversion Tests")
    converter = CursorToJiraConverter()
    
    try:
        with open('test.html', 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        jira_content = converter.convert_raw_html(html_content)
        
        result.add_test("HTML file conversion", 
                       len(jira_content) > 0,
                       "Non-empty output",
                       f"{len(jira_content)} characters")
        
        result.add_test("HTML contains Jira markup",
                       any(marker in jira_content for marker in ['h1.', 'h2.', '#', '*']),
                       "Contains Jira markers",
                       "Found Jira markup" if any(marker in jira_content for marker in ['h1.', 'h2.', '#', '*']) else "No markup found")
        
    except FileNotFoundError:
        result.add_test("HTML file test", True, "test.html not found (skipped)", "skipped")
    except Exception as e:
        result.add_test("HTML file test", False, "No errors", f"Error: {e}")
    
    return result


def main():
    """Run all tests and print summary"""
    print("\n" + "="*70)
    print("CURSOR TO JIRA CONVERTER - COMPREHENSIVE TEST SUITE")
    print("="*70)
    
    test_functions = [
        test_basic_formatting,
        test_simple_lists,
        test_nested_lists_basic,
        test_nested_lists_with_empty_lines,
        test_nested_lists_with_bold,
        test_mixed_content,
        test_edge_cases,
        test_code_blocks,
        test_nested_unordered_lists,
        test_horizontal_rules,
        test_jira_emoticon_escaping,
        test_html_conversion,
    ]
    
    all_passed = True
    total_passed = 0
    total_failed = 0
    
    for test_func in test_functions:
        result = test_func()
        passed = result.print_summary()
        all_passed = all_passed and passed
        total_passed += result.passed
        total_failed += result.failed
    
    print("\n" + "="*70)
    print("OVERALL SUMMARY")
    print("="*70)
    print(f"Total Tests: {total_passed + total_failed}")
    print(f"Passed: {total_passed}")
    print(f"Failed: {total_failed}")
    print(f"Status: {'ALL TESTS PASSED' if all_passed else 'SOME TESTS FAILED'}")
    print("="*70)
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    exit(main())

