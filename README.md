# Cursor AI to Jira Markup Converter

A Python script that converts formatted text from Cursor AI IDE to Jira markup format, preserving formatting when pasting into Jira tickets. The script extracts markdown content from Cursor AI's HTML clipboard data and converts it to proper Jira Wiki Markup syntax.

## Features

- ✅ **Headers** (H1-H6): `# Header` → `h1. Header`
- ✅ **Bold and italic text**: `**bold**` → `*bold*`, `*italic*` → `_italic_`
- ✅ **Inline code**: `` `code` `` → `{{code}}`
- ✅ **Code blocks**: ```` ```js\ncode\n``` ```` → `{code:js}\ncode\n{code}`
- ✅ **Lists**: `- item` → `* item`, `1. item` → `# item`
- ✅ **Tables**: Markdown tables → Jira table format
- ✅ **Links**: `[text](url)` → `[text|url]`
- ✅ **Blockquotes**: `> quote` → `{quote}quote{quote}`
- ✅ **Strikethrough**: `~~text~~` → `-text-`
- ✅ **Horizontal rules**: `---` → `----`
- ✅ **Clipboard integration**: Automatic copy/paste workflow

## Installation

1. Install Python 3.6 or higher
2. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Quick Start
1. Copy formatted text from Cursor AI IDE (Ctrl+C)
2. Run the converter:
   ```bash
   python cursor_to_jira_converter.py
   ```
3. The converted Jira markup is automatically copied to your clipboard
4. Paste directly into Jira (Ctrl+V)

### How It Works
The script:
1. Reads HTML data from your clipboard (format 49356)
2. Extracts markdown content from `data-markdown-raw` attributes
3. Converts markdown to Jira Wiki Markup syntax
4. Copies the result back to your clipboard

## Formatting Conversion Examples

| Cursor AI (Markdown) | Jira Markup | Description |
|---------------------|-------------|-------------|
| `# Header` | `h1. Header` | Headers |
| `## Subheader` | `h2. Subheader` | Subheaders |
| `**bold text**` | `*bold text*` | Bold text |
| `*italic text*` | `_italic text_` | Italic text |
| `` `inline code` `` | `{{inline code}}` | Inline code |
| ```` ```js\ncode\n``` ```` | `{code:js}\ncode\n{code}` | Code blocks |
| `- List item` | `* List item` | Unordered lists |
| `1. Numbered item` | `# Numbered item` | Ordered lists |
| `[Link](url)` | `[Link\|url]` | Links |
| `> Quote` | `{quote}Quote{quote}` | Blockquotes |
| `~~Strikethrough~~` | `-Strikethrough-` | Strikethrough |
| `---` | `----` | Horizontal rules |

## Key Improvements

- **Fixed bold/italic conflicts**: Proper handling of `**bold**` and `*italic*` without interference
- **Direct markdown extraction**: Uses `data-markdown-raw` attributes instead of HTML parsing
- **Proper Jira syntax**: Follows official Jira Wiki Markup formatting rules
- **No escaped periods**: Ordered lists display as `1. Item` instead of `1\. Item`

## Requirements

- Python 3.6+
- Windows (uses `pywin32` for clipboard access)
- Cursor AI IDE with HTML clipboard data

## Troubleshooting

- **"HTML data in clipboard not found"**: Make sure you copied content from Cursor AI IDE, not plain text
- **"Error reading from clipboard"**: Ensure you have proper permissions and pywin32 is installed
- **Formatting issues**: The script works best with content copied directly from Cursor AI IDE

## Contributing

Feel free to submit issues or pull requests to improve the converter's functionality.
