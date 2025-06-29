"""
Anki Helpers - Consolidated utility functions for creating Anki decks and cards
"""

# Import all functions to maintain the same interface as the original single file

# Anki API functions
from .anki_api import (
    anki_request,
    anki_invoke,
    anki_invoke_requests,
    load_anki_query_to_dataframe,
    get_anki_deck_names,
    import_anki_package,
    get_card_info,
    find_cards,
    add_note,
    update_note_fields,
    delete_notes
)

# Text processing functions
from .text_processing import (
    process_latex_to_markdown,
    replace_angle_brackets_in_latex,
    convert_latex_to_html,
    inline_to_display_math,
    convert_to_table,
    latex_to_custom_table,
    latex_to_html_image,
    latex_centre_to_html,
    latex_to_html_headers,
    latex_to_html_number_list,
    preprocess_text,
    fix_block_math,
    replace_img_links,
    replace_arrow,
    process_text_for_anki,
    clean_html_content,
    sanitize_filename
)

# Card creation functions
from .card_creation import (
    create_basic_model,
    create_cloze_model,
    create_advanced_model,
    create_deck,
    create_note,
    create_advanced_note,
    save_deck_to_file,
    create_deck_from_dataframe,
    merge_decks,
    filter_deck_by_tags,
    add_tags_to_deck,
    create_deck_with_subdeck_structure,
    export_deck_statistics,
    validate_deck,
    batch_create_decks
)

# Q&A parsing functions
from .qa_parsing import (
    extract_qa_pairs,
    extract_qa_pairs_flexible,
    parse_syllabus,
    parse_numbered_list,
    extract_question_from_html,
    remove_question_from_html,
    get_problems,
    get_problem_chapter_num,
    filter_extras,
    parse_markdown_qa,
    parse_csv_qa,
    parse_json_qa,
    extract_cloze_deletions,
    create_cloze_from_qa,
    parse_anki_export,
    clean_parsed_text,
    validate_qa_pairs,
    parse_flashcard_format,
    batch_parse_files
)

# Utility functions
from .utils import (
    AnkiConfig,
    load_config,
    save_config,
    create_deck_with_config,
    create_anki_deck_from_qa_file,
    batch_import_anki_packages,
    setup_output_directory,
    get_file_stats,
    clean_filename,
    validate_anki_connect,
    log_operation,
    chunk_list,
    merge_dictionaries,
    find_duplicates,
    progress_bar,
    estimate_processing_time,
    backup_file,
    count_words,
    count_characters,
    format_file_size,
    get_system_info,
    example_create_simple_deck,
    example_load_and_process_anki_cards,
    print_available_functions,
    run_diagnostics
)

# LLM integration functions (conditionally imported)
try:
    from .llm_integration import (
        check_llm_availability,
        create_llm_model,
        batch_process_with_llm,
        generate_study_schedule_prompt
    )
    
    # LangChain functions (if available)
    try:
        from .llm_integration import (
            AnkiContent,
            AnkiCard,
            RankedAnkiList,
            generate_card_summary,
            summarise_duplicates,
            get_card_order
        )
    except ImportError:
        pass
    
    # OpenAI functions (if available)
    try:
        from .llm_integration import (
            build_qa_prompt,
            query_openai,
            generate_qa_from_topics,
            enhance_qa_with_llm
        )
    except ImportError:
        pass

except ImportError:
    print("LLM integration functions not available. Install langchain-openai and/or openai for full functionality.")

__version__ = "1.0.0"
__author__ = "Your Name"

# Check availability of optional dependencies
try:
    import mistune
    MISTUNE_AVAILABLE = True
except ImportError:
    MISTUNE_AVAILABLE = False

try:
    import genanki
    GENANKI_AVAILABLE = True
except ImportError:
    GENANKI_AVAILABLE = False
    print("Warning: genanki not available. Card creation functions will not work.")

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False
    print("Warning: pandas not available. DataFrame functions will not work.")

# Print welcome message when imported
def _print_welcome():
    print("Anki Helpers loaded successfully!")
    print(f"Version: {__version__}")
    
    # Check essential dependencies
    if not GENANKI_AVAILABLE:
        print("⚠️  genanki not found - install with: pip install genanki")
    if not PANDAS_AVAILABLE:
        print("⚠️  pandas not found - install with: pip install pandas")
    if not MISTUNE_AVAILABLE:
        print("⚠️  mistune not found - install with: pip install mistune")
    
    print("Run print_available_functions() to see all available functions")
    print("Run run_diagnostics() to check system compatibility")

# Only print welcome message if this is the main import
if __name__ != "__main__":
    _print_welcome()

__all__ = [
    # Anki API
    'anki_request', 'anki_invoke', 'anki_invoke_requests', 'load_anki_query_to_dataframe',
    'get_anki_deck_names', 'import_anki_package', 'get_card_info', 'find_cards',
    'add_note', 'update_note_fields', 'delete_notes',
    
    # Text Processing
    'process_latex_to_markdown', 'replace_angle_brackets_in_latex', 'convert_latex_to_html',
    'inline_to_display_math', 'convert_to_table', 'latex_to_custom_table',
    'latex_to_html_image', 'latex_centre_to_html', 'latex_to_html_headers',
    'latex_to_html_number_list', 'preprocess_text', 'fix_block_math',
    'replace_img_links', 'replace_arrow', 'process_text_for_anki',
    'clean_html_content', 'sanitize_filename',
    
    # Card Creation
    'create_basic_model', 'create_cloze_model', 'create_advanced_model', 'create_deck',
    'create_note', 'create_advanced_note', 'save_deck_to_file', 'create_deck_from_dataframe',
    'merge_decks', 'filter_deck_by_tags', 'add_tags_to_deck', 'create_deck_with_subdeck_structure',
    'export_deck_statistics', 'validate_deck', 'batch_create_decks',
    
    # Q&A Parsing
    'extract_qa_pairs', 'extract_qa_pairs_flexible', 'parse_syllabus', 'parse_numbered_list',
    'extract_question_from_html', 'remove_question_from_html', 'get_problems',
    'get_problem_chapter_num', 'filter_extras', 'parse_markdown_qa', 'parse_csv_qa',
    'parse_json_qa', 'extract_cloze_deletions', 'create_cloze_from_qa', 'parse_anki_export',
    'clean_parsed_text', 'validate_qa_pairs', 'parse_flashcard_format', 'batch_parse_files',
    
    # Utilities
    'AnkiConfig', 'load_config', 'save_config', 'create_deck_with_config',
    'create_anki_deck_from_qa_file', 'batch_import_anki_packages', 'setup_output_directory',
    'get_file_stats', 'clean_filename', 'validate_anki_connect', 'log_operation',
    'chunk_list', 'merge_dictionaries', 'find_duplicates', 'progress_bar',
    'estimate_processing_time', 'backup_file', 'count_words', 'count_characters',
    'format_file_size', 'get_system_info', 'example_create_simple_deck',
    'example_load_and_process_anki_cards', 'print_available_functions', 'run_diagnostics',
    
    # LLM Integration (conditionally available)
    'check_llm_availability', 'create_llm_model', 'batch_process_with_llm',
    'generate_study_schedule_prompt'
] 