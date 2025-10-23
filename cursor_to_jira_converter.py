#!/usr/bin/env python3
"""
Cursor AI IDE to Jira Markup Converter

This script converts formatted text from Cursor AI IDE (which typically outputs markdown)
to Jira markup format for easy pasting into Jira tickets.

Usage:
    python cursor_to_jira_converter.py (reads from clipboard)
    python cursor_to_jira_converter.py --debug (shows available clipboard formats)
"""

import re
import win32clipboard
import win32con
from xml.etree import ElementTree as ET
from html.parser import HTMLParser

class CursorToJiraConverter:
    def __init__(self):
        # Jira emoticons that need to be escaped
        # These are converted to emojis if not escaped
        self.jira_emoticons = [
            '(y)',   # thumbs up
            '(n)',   # thumbs down
            '(i)',   # information
            '(!)',   # warning/error
            '(?)',   # question
            '(on)',  # lightbulb on
            '(off)', # lightbulb off
            '(*)',   # star (yellow)
            '(*r)',  # star (red)
            '(*g)',  # star (green)
            '(*b)',  # star (blue)
            '(*y)',  # star (yellow)
            '(flag)', # flag
            '(flagoff)', # flag off
            '(+)',   # plus
            '(-)',   # minus
            '(x)',   # x/cross
            '(/)',   # checkmark
        ]
        
        # Common formatting patterns from Cursor AI
        self.patterns = {
            # Headers (exclude single # which is handled as ordered list)
            'h2': (r'^## (.+)$', r'h2. \1'),
            'h3': (r'^### (.+)$', r'h3. \1'),
            'h4': (r'^#### (.+)$', r'h4. \1'),
            'h5': (r'^##### (.+)$', r'h5. \1'),
            'h6': (r'^###### (.+)$', r'h6. \1'),
            
            # Bold and italic are handled in _convert_line method to avoid conflicts
            'code_inline': (r'`(.+?)`', r'{{\1}}'),
            
            # Lists (exclude already converted Jira syntax like **, #*, #**)
            'unordered_list': (r'^(?!\*\*|#\*|#\*\*)[\s]*[-*+]\s+(.+)$', r'* \1'),
            'ordered_list': (r'^[\s]*\d+\.\s+(.+)$', r'# \1'),
            
            # Code blocks
            'code_block': (r'```(\w+)?\n(.*?)\n```', self._convert_code_block),
            'code_block_no_lang': (r'```\n(.*?)\n```', self._convert_code_block_no_lang),
            
            # Links
            'link': (r'\[([^\]]+)\]\(([^)]+)\)', r'[\1|\2]'),
            
            # Tables (basic support)
            'table_header': (r'^\|(.+)\|$', self._convert_table_header),
            'table_separator': (r'^\|[\s\-\|]+\|$', r''),  # Remove separator lines
            'table_row': (r'^\|(.+)\|$', self._convert_table_row),
            
            # Horizontal rules
            'hr': (r'^---$', r'----'),
            
            # Blockquotes
            'blockquote': (r'^>\s*(.+)$', r'{quote}\1{quote}'),
            
            # Strikethrough
            'strikethrough': (r'~~(.+?)~~', r'-\1-'),
        }
    
    def extract_markdown_from_html(self, html_content: str) -> str:
        """Extract markdown content from data-markdown-raw attributes in HTML, or fallback to text extraction"""
        print(f"[DEBUG] Starting HTML extraction, input length: {len(html_content)}")
        
        try:
            # Extract just the HTML part from clipboard format
            if html_content.startswith('Version:'):
                print("[DEBUG] Detected clipboard format, extracting HTML part")
                # Find the <html> tag
                html_start = html_content.find('<html>')
                if html_start != -1:
                    html_content = html_content[html_start:]
                    print(f"[DEBUG] Extracted HTML part, new length: {len(html_content)}")
            
            # Parse the HTML content
            print("[DEBUG] Parsing HTML with XML parser")
            # First, fix common HTML entities that cause XML parsing issues
            html_content_fixed = html_content.replace('&quot;', '"').replace('&lt;', '<').replace('&gt;', '>').replace('&amp;', '&').replace('&#39;', "'").replace('&apos;', "'")
            print(f"[DEBUG] Fixed HTML entities, new length: {len(html_content_fixed)}")
            root = ET.fromstring(html_content_fixed)
            print(f"[DEBUG] Successfully parsed HTML, root tag: {root.tag}")
            
            # Find all elements with data-markdown-raw attribute
            markdown_sections = []
            data_markdown_count = 0
            for elem in root.iter():
                if 'data-markdown-raw' in elem.attrib:
                    data_markdown_count += 1
                    raw_markdown = elem.attrib['data-markdown-raw']
                    print(f"[DEBUG] Found data-markdown-raw #{data_markdown_count}: {repr(raw_markdown[:100])}...")
                    # Decode HTML entities
                    cleaned = raw_markdown.replace('&quot;', '"').replace('&lt;', '<').replace('&gt;', '>').replace('&amp;', '&').replace('&#10;', '\n')
                    if cleaned.strip():
                        markdown_sections.append(cleaned.strip())
                        print(f"[DEBUG] Added cleaned markdown section: {repr(cleaned.strip())}")
            
            print(f"[DEBUG] Found {data_markdown_count} data-markdown-raw attributes, {len(markdown_sections)} valid sections")
            
            # If no data-markdown-raw attributes found, extract text content and convert to markdown
            if not markdown_sections:
                print("[DEBUG] No data-markdown-raw found, using fallback HTML parsing")
                result = self._extract_text_to_markdown(root)
                print(f"[DEBUG] Fallback result length: {len(result)}")
                return result
            
            # Join all markdown sections with double newlines to preserve structure
            final_result = '\n\n'.join(markdown_sections)
            print(f"[DEBUG] Final markdown result length: {len(final_result)}")
            return final_result
            
        except ET.ParseError as e:
            print(f"[DEBUG] XML parsing failed: {e}, using regex fallback")
            print(f"[DEBUG] Problematic HTML content around error: {repr(html_content_fixed[:500])}")
            # If XML parsing fails, fall back to regex extraction
            return self._extract_markdown_with_regex(html_content)
    
    def _extract_markdown_with_regex(self, html_content: str) -> str:
        """Fallback method to extract markdown using regex if XML parsing fails"""
        print("[DEBUG] Using regex fallback method")
        
        # Find all data-markdown-raw attributes
        pattern = r'data-markdown-raw="([^"]*)"'
        matches = re.findall(pattern, html_content, re.DOTALL)
        print(f"[DEBUG] Found {len(matches)} data-markdown-raw matches with regex")
        
        # Clean up the extracted content
        markdown_sections = []
        for i, match in enumerate(matches):
            print(f"[DEBUG] Processing regex match {i+1}: {repr(match[:100])}...")
            # Decode HTML entities
            cleaned = match.replace('&quot;', '"').replace('&lt;', '<').replace('&gt;', '>').replace('&amp;', '&').replace('&#10;', '\n')
            if cleaned.strip():
                markdown_sections.append(cleaned.strip())
                print(f"[DEBUG] Added cleaned match: {repr(cleaned.strip())}")
        
        result = '\n\n'.join(markdown_sections)
        print(f"[DEBUG] Regex fallback result: {repr(result)}")
        
        # If no data-markdown-raw found, try to extract text from HTML elements
        if not result:
            print("[DEBUG] No data-markdown-raw found, trying to extract text from HTML elements")
            return self._extract_text_from_html_regex(html_content)
        
        return result
    
    def _extract_text_from_html_regex(self, html_content: str) -> str:
        """Extract text from HTML elements using regex when XML parsing fails"""
        print("[DEBUG] Using regex to extract text from HTML elements")
        
        # Extract text from h1-h6 headers
        header_pattern = r'<h([1-6])[^>]*>(.*?)</h[1-6]>'
        headers = re.findall(header_pattern, html_content, re.DOTALL)
        
        markdown_parts = []
        for level, content in headers:
            # Clean up the content - remove HTML tags and decode entities
            clean_content = re.sub(r'<[^>]+>', '', content)
            clean_content = clean_content.replace('&quot;', '"').replace('&lt;', '<').replace('&gt;', '>').replace('&amp;', '&')
            clean_content = clean_content.strip()
            
            if clean_content:
                # Check if content has bold styling
                if 'font-weight: 600' in content or 'markdown-bold-text' in content:
                    markdown_parts.append(f"{'#' * int(level)} **{clean_content}**")
                    try:
                        print(f"[DEBUG] Found h{level} with bold: {repr(clean_content)}")
                    except UnicodeEncodeError:
                        print(f"[DEBUG] Found h{level} with bold: {len(clean_content)} chars")
                else:
                    markdown_parts.append(f"{'#' * int(level)} {clean_content}")
                    try:
                        print(f"[DEBUG] Found h{level}: {repr(clean_content)}")
                    except UnicodeEncodeError:
                        print(f"[DEBUG] Found h{level}: {len(clean_content)} chars")
        
        result = '\n\n'.join(markdown_parts)
        try:
            print(f"[DEBUG] HTML regex extraction result: {repr(result)}")
        except UnicodeEncodeError:
            print(f"[DEBUG] HTML regex extraction result: {len(result)} chars")
        return result
    
    def _extract_text_to_markdown(self, root) -> str:
        """Extract text content from HTML elements and convert to markdown"""
        print("[DEBUG] Starting fallback HTML text extraction")
        markdown_parts = []
        element_count = 0
        
        for elem in root.iter():
            element_count += 1
            # Skip script, style, and other non-content elements
            if elem.tag in ['script', 'style', 'head']:
                continue
                
            # Handle different HTML elements
            if elem.tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                # Convert HTML content to markdown within headers
                header_content = self._convert_html_to_markdown_inline(elem)
                header_level = elem.tag[1]  # Extract number from h1, h2, etc.
                if header_content:
                    markdown_result = f"{'#' * int(header_level)} {header_content}"
                    markdown_parts.append(markdown_result)
                    print(f"[DEBUG] Found {elem.tag}: {repr(header_content)} -> {repr(markdown_result)}")
            elif elem.tag == 'p':
                try:
                    text = ''.join(elem.itertext()).strip()
                    if text:
                        markdown_parts.append(text)
                except UnicodeEncodeError:
                    # Handle Unicode issues by using safe encoding
                    try:
                        text = ''.join(elem.itertext()).encode('ascii', 'ignore').decode('ascii').strip()
                        if text:
                            markdown_parts.append(text)
                    except:
                        pass
            elif elem.tag == 'strong' or elem.tag == 'b':
                try:
                    text = ''.join(elem.itertext()).strip()
                    if text:
                        markdown_parts.append(f"**{text}**")
                except UnicodeEncodeError:
                    try:
                        text = ''.join(elem.itertext()).encode('ascii', 'ignore').decode('ascii').strip()
                        if text:
                            markdown_parts.append(f"**{text}**")
                    except:
                        pass
            elif elem.tag == 'em' or elem.tag == 'i':
                try:
                    text = ''.join(elem.itertext()).strip()
                    if text:
                        markdown_parts.append(f"*{text}*")
                except UnicodeEncodeError:
                    try:
                        text = ''.join(elem.itertext()).encode('ascii', 'ignore').decode('ascii').strip()
                        if text:
                            markdown_parts.append(f"*{text}*")
                    except:
                        pass
            elif elem.tag == 'code':
                try:
                    text = ''.join(elem.itertext()).strip()
                    if text:
                        markdown_parts.append(f"`{text}`")
                except UnicodeEncodeError:
                    try:
                        text = ''.join(elem.itertext()).encode('ascii', 'ignore').decode('ascii').strip()
                        if text:
                            markdown_parts.append(f"`{text}`")
                    except:
                        pass
            elif elem.tag == 'ul':
                for li in elem.findall('.//li'):
                    try:
                        text = ''.join(li.itertext()).strip()
                        if text:
                            markdown_parts.append(f"- {text}")
                    except UnicodeEncodeError:
                        try:
                            text = ''.join(li.itertext()).encode('ascii', 'ignore').decode('ascii').strip()
                            if text:
                                markdown_parts.append(f"- {text}")
                        except:
                            pass
            elif elem.tag == 'ol':
                for i, li in enumerate(elem.findall('.//li'), 1):
                    try:
                        text = ''.join(li.itertext()).strip()
                        if text:
                            markdown_parts.append(f"{i}. {text}")
                    except UnicodeEncodeError:
                        try:
                            text = ''.join(li.itertext()).encode('ascii', 'ignore').decode('ascii').strip()
                            if text:
                                markdown_parts.append(f"{i}. {text}")
                        except:
                            pass
            elif elem.tag == 'blockquote':
                try:
                    text = ''.join(elem.itertext()).strip()
                    if text:
                        markdown_parts.append(f"> {text}")
                except UnicodeEncodeError:
                    try:
                        text = ''.join(elem.itertext()).encode('ascii', 'ignore').decode('ascii').strip()
                        if text:
                            markdown_parts.append(f"> {text}")
                    except:
                        pass
            elif elem.tag == 'a':
                try:
                    text = ''.join(elem.itertext()).strip()
                    href = elem.get('href', '')
                    if text and href:
                        markdown_parts.append(f"[{text}]({href})")
                    elif text:
                        markdown_parts.append(text)
                except UnicodeEncodeError:
                    try:
                        text = ''.join(elem.itertext()).encode('ascii', 'ignore').decode('ascii').strip()
                        href = elem.get('href', '')
                        if text and href:
                            markdown_parts.append(f"[{text}]({href})")
                        elif text:
                            markdown_parts.append(text)
                    except:
                        pass
        
        final_result = '\n\n'.join(markdown_parts)
        print(f"[DEBUG] Fallback extraction complete: processed {element_count} elements, found {len(markdown_parts)} markdown parts")
        print(f"[DEBUG] Final fallback result: {repr(final_result)}")
        return final_result
    
    def _convert_html_to_markdown_inline(self, elem) -> str:
        """Convert HTML elements to markdown inline formatting"""
        try:
            # Get all text content from the element and its children
            all_text = ''.join(elem.itertext()).strip()
            print(f"[DEBUG] Inline conversion - element: {elem.tag}, text: {repr(all_text)}")
            
            if all_text:
                # Check if the element or any child has bold styling
                has_bold = False
                for child in elem.iter():
                    if (child.tag in ['strong', 'b'] or 
                        'bold' in child.get('class', '') or 
                        'font-weight: 600' in child.get('style', '') or
                        'font-weight:600' in child.get('style', '')):
                        has_bold = True
                        print(f"[DEBUG] Found bold styling in child: {child.tag}, class: {child.get('class', '')}, style: {child.get('style', '')[:50]}...")
                        break
                
                if has_bold:
                    result = f"**{all_text}**"
                    print(f"[DEBUG] Applied bold formatting: {repr(result)}")
                    return result
                else:
                    print(f"[DEBUG] No bold formatting applied: {repr(all_text)}")
                    return all_text
            
            return ""
        except UnicodeEncodeError:
            # Handle Unicode encoding issues by using a safe fallback
            try:
                # Try to get text without problematic characters
                safe_text = ''.join(elem.itertext()).encode('ascii', 'ignore').decode('ascii').strip()
                if safe_text:
                    return f"**{safe_text}**" if 'bold' in str(elem.get('class', '')) else safe_text
            except:
                pass
            return ""
    
    def _convert_code_block(self, match) -> str:
        """Convert code block with language specification"""
        lang = match.group(1) or ''
        code = match.group(2)
        if lang:
            return f"{{code:{lang}}}\n{code}\n{{code}}"
        else:
            return f"{{code}}\n{code}\n{{code}}"
    
    def _convert_code_block_no_lang(self, match) -> str:
        """Convert code block without language specification"""
        code = match.group(1)
        return f"{{code}}\n{code}\n{{code}}"
    
    def _convert_table_header(self, match) -> str:
        """Convert table header row"""
        content = match.group(1)
        cells = [cell.strip() for cell in content.split('|')]
        return '||' + '||'.join(cells) + '||'
    
    def _convert_table_row(self, match) -> str:
        """Convert table data row"""
        content = match.group(1)
        cells = [cell.strip() for cell in content.split('|')]
        return '|' + '|'.join(cells) + '|'
    
    def convert_text(self, text: str) -> str:
        """Convert markdown-like text to Jira markup"""
        lines = text.split('\n')
        converted_lines = []
        in_code_block = False
        in_table = False
        
        # First pass: handle lists with proper nesting
        lines = self._convert_lists_with_nesting(lines)
        
        for line in lines:
            # Handle code blocks (multi-line)
            if line.strip().startswith('```'):
                if not in_code_block:
                    # Starting a code block
                    lang = line.strip()[3:].strip()
                    if lang:
                        converted_lines.append(f"{{code:{lang}}}")
                    else:
                        converted_lines.append("{code}")
                    in_code_block = True
                else:
                    # Ending a code block
                    converted_lines.append("{code}")
                    in_code_block = False
                continue
            
            if in_code_block:
                converted_lines.append(line)
                continue
            
            # Handle tables
            if '|' in line and line.strip().startswith('|'):
                if not in_table:
                    in_table = True
                # Convert table line
                if line.strip() == '|' or re.match(r'^\|[\s\-\|]+\|$', line.strip()):
                    continue  # Skip separator lines
                converted_line = self._convert_table_line(line)
                converted_lines.append(converted_line)
                continue
            else:
                if in_table:
                    in_table = False
            
            # Apply other conversions
            converted_line = self._convert_line(line)
            converted_lines.append(converted_line)
        
        # Replace list placeholders with actual Jira syntax
        final_result = '\n'.join(converted_lines)
        final_result = final_result.replace('<<<JIRALIST2>>>', '** ')
        
        return final_result
    
    def convert_raw_html(self, html_content: str) -> str:
        """Convert raw HTML content directly to Jira Wiki Markup"""
        # Extract markdown from HTML
        markdown = self.extract_markdown_from_html(html_content)
        
        # Convert markdown to Jira
        jira_content = self.convert_text(markdown)
        
        return jira_content
    
    def _convert_lists_with_nesting(self, lines: list) -> list:
        """Convert lists with proper nesting to maintain Jira list structure"""
        converted_lines = []
        i = 0
        
        while i < len(lines):
            line = lines[i]
            stripped = line.strip()
            
            # Check if this is an ordered list item (numbered or # format)
            if (stripped.startswith('#') and not stripped.startswith('##')) or re.match(r'^\d+\.\s+', stripped):
                # This is an ordered list item
                if stripped.startswith('#'):
                    # # format
                    content = stripped[1:].strip()
                    converted_lines.append(f"# {content}")
                else:
                    # numbered format (1., 2., etc.)
                    content = re.sub(r'^\d+\.\s+', '', stripped)
                    converted_lines.append(f"# {content}")
                
                # Look ahead for unordered sub-items (indented with -, *, or +)
                j = i + 1
                found_hr_after_list = False
                while j < len(lines):
                    next_line = lines[j]
                    next_stripped = next_line.strip()
                    
                    # Check for horizontal rule (---) after list
                    if next_stripped == '---':
                        # Mark that we found a horizontal rule and should add empty line before it
                        found_hr_after_list = True
                        break
                    
                    # Check if next line is an unordered list item (indented or not)
                    if (next_stripped.startswith('*') or next_stripped.startswith('-') or next_stripped.startswith('+')) or \
                       (next_line.startswith('   ') and (next_stripped.startswith('*') or next_stripped.startswith('-') or next_stripped.startswith('+'))):
                        # Determine indentation level for nesting depth
                        indent_level = len(next_line) - len(next_line.lstrip())
                        
                        # Convert unordered sub-item using Jira's #* syntax for nesting
                        if next_stripped.startswith('*') or next_stripped.startswith('-') or next_stripped.startswith('+'):
                            sub_content = next_stripped[1:].strip()
                        else:
                            # Handle indented items
                            sub_content = next_stripped[1:].strip()
                        
                        # Determine Jira nesting syntax based on indentation
                        # 3-4 spaces (or 1 tab) = #* (level 2)
                        # 6-8 spaces (or 2 tabs) = #** (level 3)
                        if indent_level >= 6:
                            converted_lines.append(f"#** {sub_content}")
                        else:
                            converted_lines.append(f"#* {sub_content}")
                        j += 1
                    elif (next_stripped.startswith('#') and not next_stripped.startswith('##')) or re.match(r'^\d+\.\s+', next_stripped):
                        # Next ordered list item - break to handle it in next iteration
                        break
                    elif next_stripped == '':
                        # Empty line - skip it to maintain list continuity in Jira
                        j += 1
                    else:
                        # Non-list content - break
                        break
                
                # Add empty line before horizontal rule if found
                if found_hr_after_list:
                    converted_lines.append('')
                
                i = j
            elif re.match(r'^[\s]*[-*+]\s+', line) and not stripped.startswith('---'):
                # This is an unordered list item (not part of an ordered list)
                # Pattern requires space after the list marker to avoid matching **bold**
                indent_level = len(line) - len(line.lstrip())
                content = stripped[1:].strip()
                
                # Determine nesting level based on indentation
                # 2+ spaces = nested level (**) 
                if indent_level >= 2:
                    # 2nd level or deeper - use placeholder to prevent bold pattern from matching
                    converted_lines.append(f"<<<JIRALIST2>>>{content}")
                else:
                    # 1st level
                    converted_lines.append(f"* {content}")
                i += 1
            else:
                # Not a list item, keep as is
                converted_lines.append(line)
                i += 1
        
        return converted_lines
    
    def _convert_table_line(self, line: str) -> str:
        """Convert a single table line"""
        content = line.strip()
        if content.startswith('|') and content.endswith('|'):
            content = content[1:-1]  # Remove outer pipes
            cells = [cell.strip() for cell in content.split('|')]
            if line.strip().startswith('||') or '||' in line:
                # Header row
                return '||' + '||'.join(cells) + '||'
            else:
                # Data row
                return '|' + '|'.join(cells) + '|'
        return line
    
    def _escape_jira_emoticons(self, text: str) -> str:
        """Escape Jira emoticons to prevent automatic emoji conversion"""
        # Sort by length (longest first) to handle emoticons like (flagoff) before (flag)
        sorted_emoticons = sorted(self.jira_emoticons, key=len, reverse=True)
        
        for emoticon in sorted_emoticons:
            # Escape only the opening parenthesis
            # (n) becomes \(n)
            escaped = '\\' + emoticon
            text = text.replace(emoticon, escaped)
        
        return text
    
    def _convert_line(self, line: str) -> str:
        """Convert a single line applying all patterns"""
        converted = line
        
        # Escape Jira emoticons FIRST, before any other processing
        # This prevents emoticons from being altered by bold/italic/strikethrough patterns
        emoticon_placeholders = {}
        emoticon_count = 0
        sorted_emoticons = sorted(self.jira_emoticons, key=len, reverse=True)
        for emoticon in sorted_emoticons:
            if emoticon in converted:
                placeholder = f"__EMOTICON_PLACEHOLDER_{emoticon_count}__"
                # Escape only the opening parenthesis
                # (n) becomes \(n)
                escaped = '\\' + emoticon
                emoticon_placeholders[placeholder] = escaped
                converted = converted.replace(emoticon, placeholder)
                emoticon_count += 1
        
        # Handle bold and italic with placeholder technique to avoid conflicts
        # First, replace bold with a placeholder
        bold_placeholders = {}
        bold_count = 0
        for match in re.finditer(r'\*\*(.+?)\*\*', converted):
            placeholder = f"__BOLD_PLACEHOLDER_{bold_count}__"
            bold_placeholders[placeholder] = f"*{match.group(1)}*"
            converted = converted.replace(match.group(0), placeholder, 1)
            bold_count += 1
        
        # Then convert italic (single asterisks)
        converted = re.sub(r'\*([^*\n]+?)\*', r'_\1_', converted)
        
        # Restore bold placeholders
        for placeholder, replacement in bold_placeholders.items():
            converted = converted.replace(placeholder, replacement)
        
        # Apply other patterns
        for pattern_name, (pattern, replacement) in self.patterns.items():
            if pattern_name in ['code_block', 'code_block_no_lang', 'table_header', 'table_row']:
                continue  # These are handled separately or above
            
            if callable(replacement):
                converted = re.sub(pattern, replacement, converted, flags=re.MULTILINE)
            else:
                converted = re.sub(pattern, replacement, converted)
        
        # Restore emoticon placeholders (they are already escaped)
        for placeholder, replacement in emoticon_placeholders.items():
            converted = converted.replace(placeholder, replacement)
        
        # Skip other processing for lines that start with #* (nested list items)
        # But we've already escaped emoticons above
        if line.strip().startswith('#*'):
            return converted
        
        return converted


def debug_clipboard_formats():
    """Debug function to list all available clipboard formats"""
    win32clipboard.OpenClipboard()
    
    try:
        print("[DEBUG] Available clipboard formats:")
        format_id = win32clipboard.EnumClipboardFormats(0)
        while format_id:
            try:
                format_name = win32clipboard.GetClipboardFormatName(format_id)
                print(f"  ID: {format_id}, Name: {format_name}")
            except:
                print(f"  ID: {format_id}, Name: <unknown>")
            format_id = win32clipboard.EnumClipboardFormats(format_id)
    finally:
        win32clipboard.CloseClipboard()

def get_clipboard_html():
    """Get HTML data from clipboard with dynamic format detection"""
    win32clipboard.OpenClipboard()
    
    try:
        # First, try to find HTML format dynamically
        html_format_id = None
        
        # Enumerate all available clipboard formats
        format_id = win32clipboard.EnumClipboardFormats(0)
        while format_id:
            try:
                format_name = win32clipboard.GetClipboardFormatName(format_id)
                if format_name and 'HTML' in format_name.upper():
                    html_format_id = format_id
                    print(f"[DEBUG] Found HTML format: {format_name} (ID: {format_id})")
                    break
            except:
                print(f"[DEBUG] HTML format: {format_name} (ID: {format_id}) not found")
                pass
            format_id = win32clipboard.EnumClipboardFormats(format_id)
        
        # If no HTML format found by name, try common HTML format IDs
        if html_format_id is None:
            common_html_ids = [49356, 49357, 49358, 49359, 49360]  # Common HTML format IDs
            for fmt_id in common_html_ids:
                try:
                    data = win32clipboard.GetClipboardData(fmt_id)
                    if data:
                        html_format_id = fmt_id
                        print(f"[DEBUG] Found HTML format by ID: {fmt_id}")
                        break
                except:
                    continue
        
        if html_format_id is not None:
            data = win32clipboard.GetClipboardData(html_format_id)
            decoded_data = data.decode('utf-8')
            print(f"[DEBUG] Successfully retrieved HTML data, length: {len(decoded_data)}")
            return decoded_data
        else:
            print("[DEBUG] No HTML format found, falling back to plain text")
            # Fallback to plain text
            try:
                data = win32clipboard.GetClipboardData(win32con.CF_UNICODETEXT)
                return data
            except:
                print("[ERROR] No clipboard data available")
                return ""
    
    finally:
        win32clipboard.CloseClipboard()

def main():
    import sys
    
    # Check for debug flag
    if len(sys.argv) > 1 and sys.argv[1] == '--debug':
        print("[DEBUG] Debug mode enabled")
        debug_clipboard_formats()
        print()
    
    # Get data from clipboard (HTML or plain text)
    decoded_data = get_clipboard_html()

    print("=============================== Clipboard Data ================================")
    print(decoded_data)
        
    # Extract markdown and convert to Jira format
    converter = CursorToJiraConverter()
    
    # Check if we have HTML data or plain text
    if decoded_data.strip().startswith('<') or 'data-markdown-raw' in decoded_data:
        print("[DEBUG] Detected HTML format, extracting markdown")
        markdown = converter.extract_markdown_from_html(decoded_data)
    else:
        print("[DEBUG] Detected plain text format, using direct conversion")
        markdown = decoded_data
    
    print("\n=============================== Markdown ================================")
    try:
        print(markdown)
    except UnicodeEncodeError:
        print("Markdown content contains Unicode characters")
        print(f"Content length: {len(markdown)} characters")
    
    jira_content = converter.convert_text(markdown)
    
    print("\n=============================== Jira ================================")
    print(jira_content)
    
        # Copy converted content back to clipboard
    win32clipboard.OpenClipboard()
    win32clipboard.EmptyClipboard()
    win32clipboard.SetClipboardData(win32con.CF_UNICODETEXT, jira_content)
    win32clipboard.CloseClipboard()
        
    print("\nContent converted to Jira markup and copied to clipboard!")
        

if __name__ == "__main__":
    main()
