# Anki Helpers - Modular Utility Functions

This document provides a comprehensive guide to using the modular `anki_helpers` package, which consolidates useful functions for creating Anki decks and cards from various sources across your codebase.

## Table of Contents

1. [Installation & Setup](#installation--setup)
2. [Modular Structure](#modular-structure)
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

## Modular Structure

The package is now organized into separate modules for better maintainability:

### 📁 `anki_helpers/`
```
├── __init__.py          # Main package interface (imports all functions)
├── anki_api.py          # Anki-Connect API integration
├── text_processing.py   # LaTeX/text processing functions
├── card_creation.py     # Deck and card creation with genanki
├── qa_parsing.py        # Q&A parsing and extraction utilities
├── llm_integration.py   # LLM-based functions (LangChain/OpenAI)
└── utils.py             # General utilities and configuration
```

### Module Overview

### 1. **`anki_api.py` - Anki API Integration**
- Connect to Anki via Anki-Connect
- Load existing cards into DataFrames
- Import .apkg files
- CRUD operations on cards and notes

### 2. **`text_processing.py` - Text Processing & LaTeX Conversion**
- Convert LaTeX to HTML/Markdown
- Handle mathematical expressions
- Process tables and images
- Clean and sanitize text

### 3. **`card_creation.py` - Card Creation with genanki**
- Create Anki decks programmatically
- Generate cards from DataFrames
- Save decks as .apkg files
- Multiple model types (Basic, Cloze, Advanced)

### 4. **`qa_parsing.py` - Q&A Parsing**
- Extract question-answer pairs from text
- Parse structured content
- Handle various text formats (CSV, JSON, Markdown)
- Validation and cleaning functions

### 5. **`llm_integration.py` - LLM Integration** (optional)
- Generate summaries using LangChain
- Create Q&A pairs with OpenAI
- Process and rank cards
- Enhance existing content

### 6. **`utils.py` - Utility Functions**
- Configuration management
- Batch operations
- File management
- System diagnostics

## Usage Examples

### Import Options

```python
# Option 1: Import the whole package (recommended)
import anki_helpers as ah

# Option 2: Import specific modules
from anki_helpers import anki_api, text_processing, card_creation

# Option 3: Import specific functions
from anki_helpers import create_deck_from_dataframe, preprocess_text
```

### Quick Start: Create a Simple Deck

```python
import anki_helpers as ah

# Create simple Q&A data
qa_data = [
    {"question": "What is Python?", "answer": "A high-level programming language"},
    {"question": "What is pandas?", "answer": "A data manipulation library for Python"}
]

# Create and save deck
config = ah.AnkiConfig(default_deck_name="Programming Basics")
deck = ah.create_deck_with_config(qa_data, config)
ah.save_deck_to_file(deck, "programming_basics.apkg")
```

### Load Existing Anki Cards

```python
import anki_helpers as ah

# Load cards from an existing deck
df = ah.load_anki_query_to_dataframe('deck:"My Study Deck"')
print(f"Loaded {len(df)} cards")
print("Available fields:", df.columns.tolist())

# Process the text content
df['processed_answer'] = df['Back'].apply(ah.preprocess_text)
```

### Create Deck from DataFrame

```python
import pandas as pd
import anki_helpers as ah

# Your Q&A data
df = pd.DataFrame({
    'question': ['What is ML?', 'What is AI?'],
    'answer': ['Machine Learning...', 'Artificial Intelligence...'],
    'topic': ['ML', 'AI']
})

# Create deck with advanced model
deck = ah.create_deck_from_dataframe(
    df, 
    deck_name="AI/ML Basics",
    question_col='question',
    answer_col='answer',
    extras_col='topic',
    model_type='advanced'  # Options: 'basic', 'cloze', 'advanced'
)

ah.save_deck_to_file(deck, "ai_ml_basics.apkg")
```

### Process LaTeX Content

```python
import anki_helpers as ah

latex_text = """
Here is some math: \\(x^2 + y^2 = z^2\\)

And a table:
\\begin{tabular}{c|cc}
x & 1 & 2 \\
y & 3 & 4 \\
\\end{tabular}
"""

# Process for Anki
processed = ah.preprocess_text(latex_text)
print(processed)
```

### Generate Q&A with OpenAI (if available)

```python
import anki_helpers as ah

# Requires OpenAI API key
api_key = "your-openai-api-key"
topics = ["Linear Algebra", "Statistics", "Probability"]

df = ah.generate_qa_from_topics(
    topics=topics, 
    topic_name="Mathematics", 
    api_key=api_key
)

deck = ah.create_deck_from_dataframe(df, "Math Q&A")
ah.save_deck_to_file(deck, "math_qa.apkg")
```

### Configuration Management

```python
import anki_helpers as ah

# Create configuration
config = ah.AnkiConfig(
    anki_connect_url="http://localhost:8765",
    default_model_name="Advanced",
    default_deck_name="My Study Cards",
    output_directory="./my_output",
    max_cards_per_deck=500
)

# Save configuration
ah.save_config(config, "my_config.json")

# Load configuration later
loaded_config = ah.load_config("my_config.json")
```

## Function Reference

### Module-Specific Functions

#### `anki_api.py`
```python
# Basic API calls
ah.anki_invoke(action, **params)         # Make any Anki-Connect call
ah.get_anki_deck_names()                 # List all deck names
ah.import_anki_package(path)             # Import .apkg file

# Data loading
ah.load_anki_query_to_dataframe(query)   # Load cards to DataFrame
ah.find_cards(query)                     # Find card IDs
ah.get_card_info(card_ids)               # Get card details

# CRUD operations
ah.add_note(deck, model, fields, tags)   # Add single note
ah.update_note_fields(note_id, fields)   # Update note
ah.delete_notes(note_ids)                # Delete notes
```

#### `text_processing.py`
```python
# LaTeX/Math processing
ah.process_latex_to_markdown(text)       # Convert LaTeX to markdown
ah.inline_to_display_math(text)          # Fix math delimiters
ah.preprocess_text(text)                 # Complete preprocessing pipeline

# HTML conversion
ah.convert_latex_to_html(text)           # Basic HTML conversion
ah.latex_to_html_image(text)             # Convert images
ah.latex_to_html_headers(text)           # Convert sections

# Specialized processing
ah.process_text_for_anki(content)        # Complete Anki processing
ah.fix_block_math(text)                  # Fix math blocks
ah.clean_html_content(text)              # Clean HTML
ah.sanitize_filename(filename)           # Clean filenames
```

#### `card_creation.py`
```python
# Models
ah.create_basic_model(name)              # Basic Q&A model
ah.create_cloze_model(name)              # Cloze deletion model
ah.create_advanced_model(name)           # Advanced model with more fields

# Decks and notes
ah.create_deck(name)                     # Create empty deck
ah.create_note(model, q, a, extras)      # Create single note
ah.create_advanced_note(model, ...)      # Create note with all fields

# Bulk operations
ah.create_deck_from_dataframe(df, name)  # Create deck from DataFrame
ah.save_deck_to_file(deck, filename)     # Save to .apkg file
ah.merge_decks(decks, name)              # Merge multiple decks
ah.batch_create_decks(configs)           # Create multiple decks

# Deck management
ah.filter_deck_by_tags(deck, tags)       # Filter by tags
ah.validate_deck(deck)                   # Check for issues
ah.export_deck_statistics(deck)          # Get statistics
```

#### `qa_parsing.py`
```python
# Basic parsing
ah.extract_qa_pairs(text)                # Extract Q: A: pairs
ah.extract_qa_pairs_flexible(text)       # Flexible Q&A extraction
ah.parse_syllabus(text)                  # Parse numbered syllabus

# Format-specific parsing
ah.parse_csv_qa(csv_content)             # Parse CSV format
ah.parse_json_qa(json_content)           # Parse JSON format
ah.parse_markdown_qa(markdown)           # Parse Markdown format
ah.parse_anki_export(anki_text)          # Parse Anki exports

# Advanced parsing
ah.batch_parse_files(file_paths)         # Parse multiple files
ah.validate_qa_pairs(qa_pairs)           # Validate and clean pairs
ah.clean_parsed_text(text)               # Clean extracted text

# Cloze operations
ah.extract_cloze_deletions(text)         # Extract cloze patterns
ah.create_cloze_from_qa(q, a)            # Convert Q&A to cloze
```

#### `llm_integration.py` (if available)
```python
# Availability check
ah.check_llm_availability()              # Check what's available

# LangChain integration
ah.generate_card_summary(text, model)    # Generate summaries
ah.summarise_duplicates(text, model)     # Merge duplicate summaries
ah.get_card_order(titles, model)         # Rank and organize cards

# OpenAI integration
ah.query_openai(prompt, model, api_key)  # Direct OpenAI call
ah.generate_qa_from_topics(topics, ...)  # Generate Q&A pairs
ah.enhance_qa_with_llm(df, api_key)      # Improve existing Q&A

# Utilities
ah.create_llm_model(model_name, api_key) # Create LLM instance
ah.batch_process_with_llm(texts, ...)    # Process in batches
```

#### `utils.py`
```python
# Configuration
ah.AnkiConfig(...)                       # Configuration class
ah.load_config(path)                     # Load from file
ah.save_config(config, path)             # Save to file

# File operations
ah.setup_output_directory(path)          # Create directories
ah.get_file_stats(path)                  # File information
ah.backup_file(path)                     # Create backup

# Utilities
ah.progress_bar(current, total)          # Progress visualization
ah.estimate_processing_time(...)         # Time estimation
ah.format_file_size(bytes)               # Human-readable sizes
ah.chunk_list(list, size)                # Split lists

# Diagnostics
ah.validate_anki_connect()               # Check Anki connection
ah.run_diagnostics()                     # System diagnostics
ah.print_available_functions()           # List all functions
```

## Advanced Usage

### Custom Processing Pipeline

```python
import anki_helpers as ah

def create_deck_from_latex_file(file_path, deck_name):
    """Complete pipeline: LaTeX file → processed Anki deck"""
    
    # Read file
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Extract problems using qa_parsing module
    problems = ah.get_problems(content)
    df = ah.get_problem_chapter_num(problems)
    
    # Process text using text_processing module
    df['processed_content'] = df['content'].apply(ah.preprocess_text)
    
    # Create deck using card_creation module
    deck = ah.create_deck_from_dataframe(
        df, deck_name,
        question_col='problem',
        answer_col='processed_content',
        model_type='advanced'
    )
    
    # Save and import
    output_file = f"{ah.sanitize_filename(deck_name)}.apkg"
    ah.save_deck_to_file(deck, output_file)
    ah.import_anki_package(output_file)
    
    return output_file

# Usage
deck_file = create_deck_from_latex_file("problems.tex", "Math Problems")
print(f"Created and imported: {deck_file}")
```

### Batch Processing with Progress Tracking

```python
import anki_helpers as ah
import time

def process_multiple_topics_with_progress(topics_data, api_key):
    """Process multiple topics with progress tracking"""
    
    all_decks = []
    start_time = time.time()
    
    for i, (topic_name, sections) in enumerate(topics_data.items()):
        print(f"\n{ah.progress_bar(i, len(topics_data))}")
        print(f"Processing: {topic_name}")
        
        # Generate Q&A pairs
        df = ah.generate_qa_from_topics(sections, topic_name, api_key)
        
        # Create deck
        deck = ah.create_deck_from_dataframe(df, topic_name)
        
        # Validate before saving
        issues = ah.validate_deck(deck)
        if issues:
            print(f"⚠️ Issues found: {issues}")
        
        # Save deck
        filename = f"{ah.sanitize_filename(topic_name)}.apkg"
        ah.save_deck_to_file(deck, filename)
        all_decks.append(deck)
        
        # Show estimated time remaining
        if i > 0:
            remaining_time = ah.estimate_processing_time(i, len(topics_data), start_time)
            print(f"⏱️ Estimated time remaining: {remaining_time}")
    
    print(f"\n✅ Processed {len(all_decks)} topics successfully!")
    return all_decks

# Usage
topics_data = {
    "Python Basics": ["Variables", "Functions", "Classes"],
    "Data Science": ["Pandas", "NumPy", "Matplotlib"],
    "Machine Learning": ["Regression", "Classification", "Clustering"]
}

decks = process_multiple_topics_with_progress(topics_data, "your-api-key")
```

### System Diagnostics and Health Check

```python
import anki_helpers as ah

def system_health_check():
    """Comprehensive system health check"""
    
    print("🔍 Running Anki Helpers diagnostics...\n")
    
    # Run diagnostics
    diagnostics = ah.run_diagnostics()
    
    # Check Anki connection
    if diagnostics['anki_connect']:
        print("✅ Anki-Connect is working")
        deck_names = ah.get_anki_deck_names()
        print(f"📚 Found {len(deck_names)} decks in Anki")
    else:
        print("❌ Anki-Connect not available")
        print("   Make sure Anki is running with Anki-Connect add-on")
    
    # Check LLM availability
    llm_status = diagnostics.get('llm_availability', {})
    if llm_status.get('langchain'):
        print("✅ LangChain available")
    if llm_status.get('openai'):
        print("✅ OpenAI available")
    
    # System info
    print(f"\n💻 System: {diagnostics['system_info']['system']}")
    print(f"🐍 Python: {diagnostics['system_info']['python_version']}")
    
    # Show available functions
    print("\n📋 Available function categories:")
    ah.print_available_functions()

# Run health check
system_health_check()
```

## Migration from Single File

If you were using the original `anki_helpers.py` single file, migration is seamless:

```python
# Old way (still works)
from anki_helpers import create_deck_from_dataframe, preprocess_text

# New way (recommended)
import anki_helpers as ah
deck = ah.create_deck_from_dataframe(df, "My Deck")
processed = ah.preprocess_text(text)
```

All functions maintain the same signatures and behavior.

## Tips and Best Practices

1. **Import Strategy**: Use `import anki_helpers as ah` for cleaner code
2. **Configuration**: Use `AnkiConfig` for consistent settings across projects
3. **Error Handling**: Always wrap API calls in try-catch blocks
4. **Validation**: Use `validate_deck()` before saving important decks
5. **Progress Tracking**: Use `progress_bar()` for long operations
6. **File Management**: Use `sanitize_filename()` for cross-platform compatibility
7. **Diagnostics**: Run `run_diagnostics()` when setting up new environments

## Troubleshooting

### Import Errors
```python
# Check what's available
import anki_helpers as ah
ah.run_diagnostics()
```

### Anki-Connect Issues
```python
# Test connection
import anki_helpers as ah
if ah.validate_anki_connect():
    print("Anki-Connect working!")
else:
    print("Check Anki-Connect setup")
```

### Missing Dependencies
Install missing packages as shown in the diagnostic output:
```bash
pip install genanki pandas mistune
pip install langchain-openai openai  # for LLM features
```

For more examples and detailed usage, see the individual module documentation and example functions. 