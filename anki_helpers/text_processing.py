"""
Text Processing Module
Functions for processing text, LaTeX conversion, and HTML formatting
"""

import re

# =============================================================================
# TEXT PROCESSING AND LATEX CONVERSION
# =============================================================================

def process_latex_to_markdown(text: str) -> str:
    """
    Convert LaTeX expressions to markdown while preserving LaTeX math blocks.
    
    Args:
        text: Text containing LaTeX expressions
        
    Returns:
        Processed text with LaTeX blocks preserved
    """
    try:
        import mistune
    except ImportError:
        print("Warning: mistune not available. Returning text unchanged.")
        return text
    
    # Identify LaTeX blocks
    block_latex_pattern = re.compile(r"\\\[(.*?)\\\]", re.DOTALL)
    inline_latex_pattern = re.compile(r"\\\((.*?)\\\)")

    # Store placeholders for replacement later
    block_latex_map = {}
    inline_latex_map = {}

    def block_replacer(match):
        placeholder = f"{{BLOCK_LATEX_{len(block_latex_map)}}}"
        block_latex_map[placeholder] = match.group(0)
        return placeholder

    def inline_replacer(match):
        placeholder = f"{{INLINE_LATEX_{len(inline_latex_map)}}}"
        inline_latex_map[placeholder] = match.group(0)
        return placeholder

    # Replace LaTeX with placeholders
    text_with_placeholders = block_latex_pattern.sub(block_replacer, text)
    text_with_placeholders = inline_latex_pattern.sub(inline_replacer, text_with_placeholders)

    # Convert to markdown
    markdown_converter = mistune.create_markdown()
    markdown_text = markdown_converter(text_with_placeholders)

    # Restore LaTeX placeholders
    def restore_placeholders(match):
        placeholder = match.group(0)
        return block_latex_map.get(placeholder, inline_latex_map.get(placeholder, placeholder))

    final_output = re.sub(
        r"\{BLOCK_LATEX_\d+\}|\{INLINE_LATEX_\d+\}", restore_placeholders, markdown_text
    )

    return final_output

def replace_angle_brackets_in_latex(text: str) -> str:
    """Replace < and > characters within LaTeX expressions with HTML entities."""
    pattern = re.compile(r"\\[\(\[](.*?)\\[\)\]]", re.DOTALL)

    def replace_brackets(match):
        return match.group(0).replace("<", "&lt;").replace(">", "&gt;")

    return pattern.sub(replace_brackets, text)

def convert_latex_to_html(text: str) -> str:
    """Convert text to basic HTML format."""
    html = "<p>{}</p>".format(text.strip())

    # Split into paragraphs
    paragraphs = text.split("\n\n")
    if len(paragraphs) > 1:
        html = ""
        for paragraph in paragraphs:
            html += "<p>{}</p>".format(paragraph.strip())

    # Replace newlines with <br> tags
    html = html.replace("\n", "<br>\n")
    html = "<div>{}</div>".format(html)

    return html

def inline_to_display_math(text: str) -> str:
    """Convert $ math delimiters to LaTeX \\( \\) format."""
    text = re.sub(r"\$\$([\s\S]*?)\$\$", r"\\(\1\\)", text)
    text = re.sub(r"\$(.*?)\$", r"\\(\1\\)", text)
    return text

def convert_to_table(latex_table: str) -> str:
    """Convert LaTeX tabular environment to array format for Anki."""
    q = latex_table.replace("tabular", "array")
    q = q.replace("\n", " ")
    q = q.replace("$", "")
    q = q.replace("\\(", "")
    q = q.replace("\\)", "")
    return "\\(" + q + "\\)"

def latex_to_custom_table(input_string: str) -> str:
    """Convert LaTeX table environments to custom format for Anki."""
    pattern = r"\\begin\{(array|tabular)\}.*?\\end\{\1\}"
    
    def replacement_function(match):
        table_text = match.group(0)
        return convert_to_table(table_text)
    
    return re.sub(pattern, replacement_function, input_string, flags=re.DOTALL)

def latex_to_html_image(input_string: str) -> str:
    """Convert LaTeX \\includegraphics commands to HTML img tags."""
    pattern = r'\\includegraphics\[.*?\]\{(.*?)\}'
    
    def replacement_function(match):
        image_filename = match.group(1)
        return f'<img src="{image_filename}.jpg">'
    
    return re.sub(pattern, replacement_function, input_string)

def latex_centre_to_html(input_string: str) -> str:
    """Convert LaTeX center environment to HTML."""
    result = re.sub(
        r'\\begin{center}(.*?)\\end{center}',
        r'<div><p style="text-align: center;">\1</p></div>',
        input_string,
        flags=re.DOTALL
    )
    return result

def latex_to_html_headers(input_text: str) -> str:
    """Convert LaTeX section commands to HTML headers."""
    input_text = re.sub(r'\\section\{(.*?)\}', r'<h1>\1</h1>', input_text)
    input_text = re.sub(r'\\subsection\{(.*?)\}', r'<h2>\1</h2>', input_text)
    return input_text

def latex_to_html_number_list(latex_code: str) -> str:
    """Convert LaTeX enumerate environment to HTML ordered list."""
    def convert_enumerate(match):
        items = re.findall(r"\\item\s(.*?)\s*(?=\\item|$)", match.group(), re.DOTALL)
        html_list = "<ol>\n"
        for item in items:
            html_list += f"  <li>{item.strip()}</li>\n"
        html_list += "</ol>"
        return html_list

    modified_code = re.sub(
        r"\\begin{enumerate}.*?\\end{enumerate}",
        convert_enumerate,
        latex_code,
        flags=re.DOTALL
    )
    return modified_code

def preprocess_text(text: str) -> str:
    """Apply all text preprocessing functions in sequence."""
    text = inline_to_display_math(text)
    text = latex_to_html_image(text)
    text = latex_to_custom_table(text)
    text = latex_centre_to_html(text)
    text = latex_to_html_number_list(text)
    text = latex_to_html_headers(text)
    text = text.replace("\\end{enumerate}", "")
    text = text.replace("\\end{document}", "")
    return text

def fix_block_math(text: str) -> str:
    """Fix block math formatting for Anki compatibility."""
    def replace_newlines_and_brackets(match):
        no_newlines = match.group(0)
        return no_newlines.replace('\\[', '\\(').replace('\\]', '\\)').replace("\n", "")
    
    pattern = r'\\\[(.|\n)*?\\\]'
    result = re.sub(pattern, replace_newlines_and_brackets, text)
    return result

def replace_img_links(text: str) -> str:
    """Replace LaTeX includegraphics with HTML img tags."""
    latex_pattern = r"\\begin{center}\s*\\includegraphics\[max width=\\textwidth\]{(\S+)}\s*\\end{center}"
    html_pattern = r'<img src="\g<1>.jpg">'
    return re.sub(latex_pattern, html_pattern, text)

def replace_arrow(text: str) -> str:
    """Fix arrow symbols in probability expressions for HTML compatibility."""
    return re.sub(r'P\([^)]*\)', lambda match: match.group(0).replace('<', ' < '), text)

def process_text_for_anki(content: str) -> str:
    """Complete text processing pipeline for Anki cards."""
    content = fix_block_math(content)
    content = replace_img_links(content)
    content = replace_arrow(content)
    content = r'{}'.format(content).replace("\n", "<br/>")
    return content

def clean_html_content(html_content: str) -> str:
    """Clean HTML content for better Anki compatibility."""
    # Remove excessive whitespace
    html_content = re.sub(r'\s+', ' ', html_content)
    # Fix common HTML issues
    html_content = html_content.replace('< ', '&lt; ')
    html_content = html_content.replace(' >', ' &gt;')
    return html_content.strip()

def sanitize_filename(filename: str) -> str:
    """Sanitize filename for cross-platform compatibility."""
    # Remove or replace invalid characters
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # Remove multiple underscores
    filename = re.sub(r'_+', '_', filename)
    # Trim underscores from ends
    filename = filename.strip('_')
    return filename 