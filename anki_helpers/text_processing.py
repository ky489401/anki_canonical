import re

import mistune
from flask import Flask
from markdown2 import Markdown

app = Flask(__name__)

markdowner = Markdown()

# Config variable for LaTeX delimiter style: 'dollar' or 'bracket'
LATEX_DELIMITER_STYLE = 'dollar'  # Change to 'bracket' to use \\[...\\] and \\(...\\)


def process_latex_to_markdown(text):
    """prompt
    Write python code to first identify all block latex $$.....$$ and inline latex $.....$ (or \\[...\\] and \\(...\\) based on config). Then replace them with a placeholder. Then convert them into markdown text using a library. Then replace the placeholders with the corresponding latex blocks (including the original brackets)
    """

    # Choose patterns based on config
    if LATEX_DELIMITER_STYLE == 'dollar':
        block_latex_pattern = re.compile(r"\$\$(.*?)\$\$", re.DOTALL)
        inline_latex_pattern = re.compile(r"(?<!\$)\$(?!\$)(.+?)(?<!\$)\$(?!\$)", re.DOTALL)
    else:  # 'bracket'
        block_latex_pattern = re.compile(r"\\\[(.*?)\\\]", re.DOTALL)
        inline_latex_pattern = re.compile(r"\\\((.*?)\\\)")

    # Store placeholders for replacement later
    block_latex_map = {}
    inline_latex_map = {}

    def block_replacer(match):
        placeholder = f"{{BLOCK_LATEX_{len(block_latex_map)}}}"
        block_latex_map[placeholder] = match.group(0)  # Store original LaTeX block
        return placeholder

    def inline_replacer(match):
        placeholder = f"{{INLINE_LATEX_{len(inline_latex_map)}}}"
        inline_latex_map[placeholder] = match.group(0)  # Store original LaTeX inline
        return placeholder

    # Replace LaTeX with placeholders
    text_with_placeholders = block_latex_pattern.sub(block_replacer, text)
    text_with_placeholders = inline_latex_pattern.sub(
        inline_replacer, text_with_placeholders
    )

    # Step 2: Convert placeholders markdown text to HTML
    markdown_converter = mistune.create_markdown()
    markdown_text = markdown_converter(text_with_placeholders)

    # Step 3: Replace placeholders with original LaTeX blocks
    def restore_placeholders(match):
        placeholder = match.group(0)
        return block_latex_map.get(
            placeholder, inline_latex_map.get(placeholder, placeholder)
        )

    final_output = re.sub(
        r"\{BLOCK_LATEX_\d+\}|\{INLINE_LATEX_\d+\}", restore_placeholders, markdown_text
    )

    # Convert all $$...$$ to \[...\] and $...$ to \(...\)
    # Block: $$...$$ -> \[...\]
    final_output = re.sub(r"\$\$(.*?)\$\$", r"\\[\1\\]", final_output, flags=re.DOTALL)
    # Inline: $...$ (not $$...$$) -> \(...\)
    final_output = re.sub(r"(?<!\$)\$(?!\$)(.+?)(?<!\$)\$(?!\$)", r"\\(\1\\)", final_output, flags=re.DOTALL)

    return final_output