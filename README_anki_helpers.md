# Anki Helpers - Consolidated Utility Functions

This document provides a comprehensive guide to using the `anki_helpers.py` module, which consolidates useful functions for creating Anki decks and cards from various sources across your codebase.

## Table of Contents

1. [Installation & Setup](#installation--setup)
2. [Core Functionality](#core-functionality)
3. [Usage Examples](#usage-examples)
4. [Function Reference](#function-reference)
5. [Advanced Usage](#advanced-usage)

## Installation & Setup

### Required Dependencies

```bash
pip install pandas genanki requests
```

### Optional Dependencies (for enhanced functionality)

```bash
# For LLM integration
pip install langchain-openai langchain-core

# For OpenAI direct integration
pip install openai

# For LaTeX processing
pip install mistune
```

### Anki-Connect Setup

1. Install the Anki-Connect add-on in Anki (code: 2055492159)
2. Restart Anki
3. Ensure Anki is running when using API functions

## Core Functionality

The module provides 6 main categories of functions:

### 1. **Anki API Integration**
- Connect to Anki via Anki-Connect
- Load existing cards into DataFrames
- Import .apkg files

### 2. **Text Processing & LaTeX Conversion**
- Convert LaTeX to HTML/Markdown
- Handle mathematical expressions
- Process tables and images

### 3. **Card Creation with genanki**
- Create Anki decks programmatically
- Generate cards from DataFrames
- Save decks as .apkg files

### 4. **Q&A Parsing**
- Extract question-answer pairs from text
- Parse structured content
- Handle various text formats

### 5. **LLM Integration** (optional)
- Generate summaries using LangChain
- Create Q&A pairs with OpenAI
- Process and rank cards

### 6. **Utility Functions**
- Batch operations
- Configuration management
- Helper functions

## Usage Examples

### Quick Start: Create a Simple Deck

```python
from anki_helpers import *

# Create simple Q&A data
qa_data = [
    {"question": "What is Python?", "answer": "A high-level programming language"},
    {"question": "What is pandas?", "answer": "A data manipulation library for Python"}
]

# Create and save deck
config = AnkiConfig(default_deck_name="Programming Basics")
deck = create_deck_with_config(qa_data, config)
save_deck_to_file(deck, "programming_basics.apkg")
```

### Load Existing Anki Cards

```python
# Load cards from an existing deck
df = load_anki_query_to_dataframe('deck:"My Study Deck"')
print(f"Loaded {len(df)} cards")
print("Available fields:", df.columns.tolist())

# Process the text content
df['processed_answer'] = df['Back'].apply(preprocess_text)
```

### Create Deck from DataFrame

```python
import pandas as pd

# Your Q&A data
df = pd.DataFrame({
    'question': ['What is ML?', 'What is AI?'],
    'answer': ['Machine Learning...', 'Artificial Intelligence...'],
    'topic': ['ML', 'AI']
})

# Create deck
deck = create_deck_from_dataframe(
    df, 
    deck_name="AI/ML Basics",
    question_col='question',
    answer_col='answer',
    extras_col='topic'
)

save_deck_to_file(deck, "ai_ml_basics.apkg")
```

### Process LaTeX Content

```python
latex_text = """
Here is some math: \\(x^2 + y^2 = z^2\\)

And a table:
\\begin{tabular}{c|cc}
x & 1 & 2 \\
y & 3 & 4 \\
\\end{tabular}
"""

# Process for Anki
processed = preprocess_text(latex_text)
print(processed)
```

### Extract Q&A from Text

```python
qa_text = """
Q: What is the capital of France?
A: Paris is the capital of France.

Q: What is 2+2?
A: 2+2 equals 4.
"""

# Extract pairs
pairs = extract_qa_pairs(qa_text)
df = pd.DataFrame(pairs, columns=['question', 'answer'])

# Create deck
deck = create_deck_from_dataframe(df, "General Knowledge")
save_deck_to_file(deck, "general_knowledge.apkg")
```

### Generate Q&A with OpenAI (if available)

```python
# Requires OpenAI API key
api_key = "your-openai-api-key"
topics = ["Linear Algebra", "Statistics", "Probability"]

df = generate_qa_from_topics(
    topics=topics, 
    topic_name="Mathematics", 
    api_key=api_key
)

deck = create_deck_from_dataframe(df, "Math Q&A")
save_deck_to_file(deck, "math_qa.apkg")
```

### Batch Import .apkg Files

```python
# Import all .apkg files from a directory
batch_import_anki_packages("./output/")
```

## Function Reference

### Anki API Functions

```python
# Basic API calls
anki_invoke(action, **params)  # Make any Anki-Connect call
get_anki_deck_names()          # List all deck names
import_anki_package(path)      # Import .apkg file

# Data loading
load_anki_query_to_dataframe(query)  # Load cards to DataFrame
```

### Text Processing Functions

```python
# LaTeX/Math processing
process_latex_to_markdown(text)      # Convert LaTeX to markdown
inline_to_display_math(text)         # Fix math delimiters
preprocess_text(text)                # Complete preprocessing pipeline

# HTML conversion
convert_latex_to_html(text)          # Basic HTML conversion
latex_to_html_image(text)            # Convert images
latex_to_html_headers(text)          # Convert sections

# Anki-specific processing
process_text_for_anki(content)       # Complete Anki processing
fix_block_math(text)                 # Fix math blocks
replace_arrow(text)                  # Fix probability symbols
```

### Card Creation Functions

```python
# Models and decks
create_basic_model(name)             # Create Anki model
create_deck(name)                    # Create empty deck
create_note(model, q, a, extras)     # Create single note

# Bulk operations
create_deck_from_dataframe(df, name) # Create deck from DataFrame
save_deck_to_file(deck, filename)   # Save to .apkg file
```

### Parsing Functions

```python
# Q&A extraction
extract_qa_pairs(text)               # Extract Q: A: pairs
parse_syllabus(text)                 # Parse numbered syllabus

# HTML processing
extract_question_from_html(html)     # Extract questions
remove_question_from_html(html)      # Remove question sections

# Problem parsing
get_problems(text)                   # Extract numbered problems
get_problem_chapter_num(problems)    # Assign chapter numbers
```

### LLM Functions (if libraries available)

```python
# LangChain integration
generate_card_summary(text, model)   # Generate summaries
summarise_duplicates(text, model)    # Merge duplicate summaries

# OpenAI integration
query_openai(prompt, model, api_key) # Direct OpenAI call
build_qa_prompt(section, topic)      # Build Q&A prompt
generate_qa_from_topics(topics, name, key)  # Generate Q&A
```

## Advanced Usage

### Custom Configuration

```python
config = AnkiConfig(
    anki_connect_url="http://localhost:8765",
    default_model_name="Custom Model",
    default_deck_name="My Custom Deck",
    openai_api_key="your-key-here",
    langchain_model="gpt-4"
)

deck = create_deck_with_config(qa_data, config)
```

### Processing Pipeline Example

```python
def create_deck_from_latex_file(file_path, deck_name):
    """Complete pipeline: LaTeX file → processed Anki deck"""
    
    # Read file
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Extract problems
    problems = get_problems(content)
    df = get_problem_chapter_num(problems)
    
    # Process text
    df['processed_content'] = df['content'].apply(preprocess_text)
    
    # Create deck
    deck = create_deck_from_dataframe(
        df, deck_name,
        question_col='problem',
        answer_col='processed_content'
    )
    
    # Save
    output_file = f"{deck_name.replace(' ', '_')}.apkg"
    save_deck_to_file(deck, output_file)
    
    return output_file

# Usage
deck_file = create_deck_from_latex_file("problems.tex", "Math Problems")
print(f"Created: {deck_file}")
```

### Error Handling

```python
try:
    df = load_anki_query_to_dataframe('deck:"Non-existent Deck"')
except Exception as e:
    print(f"Error loading deck: {e}")

# Check if optional libraries are available
if LANGCHAIN_AVAILABLE:
    # Use LangChain functions
    pass
else:
    print("LangChain not available, skipping LLM features")
```

## Tips and Best Practices

1. **Always check Anki-Connect**: Ensure Anki is running with Anki-Connect installed
2. **Text preprocessing**: Use `preprocess_text()` for LaTeX content before creating cards
3. **Batch operations**: Use DataFrames for bulk card creation
4. **Error handling**: Wrap API calls in try-catch blocks
5. **File management**: Use descriptive names for .apkg files
6. **API keys**: Store API keys securely, never in code

## Troubleshooting

### Common Issues

**Anki-Connect not responding**:
- Ensure Anki is running
- Check if Anki-Connect add-on is installed
- Verify the URL (default: http://localhost:8765)

**LaTeX not rendering properly**:
- Use `preprocess_text()` function
- Check math delimiters (use `\(` and `\)` for inline math)
- Ensure HTML entities are properly escaped

**Import failures**:
- Check file paths are correct
- Ensure .apkg files are not corrupted
- Verify Anki is not busy with other operations

For more examples and detailed usage, see the example functions in the module itself. 