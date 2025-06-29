"""
Utilities Module
General utility functions and configuration management for Anki helpers
"""

from dataclasses import dataclass
from typing import List, Dict, Optional, Any
from pathlib import Path
import json
import datetime

# =============================================================================
# CONFIGURATION
# =============================================================================

@dataclass
class AnkiConfig:
    """Configuration for Anki operations."""
    anki_connect_url: str = "http://localhost:8765"
    default_model_name: str = "Basic"
    default_deck_name: str = "Generated Cards"
    openai_api_key: Optional[str] = None
    langchain_model: str = "gpt-4o-mini"
    output_directory: str = "./output"
    max_cards_per_deck: int = 1000
    enable_media: bool = False

def load_config(config_path: str) -> AnkiConfig:
    """Load configuration from JSON file."""
    try:
        with open(config_path, 'r') as f:
            config_data = json.load(f)
        return AnkiConfig(**config_data)
    except FileNotFoundError:
        print(f"Config file {config_path} not found. Using defaults.")
        return AnkiConfig()
    except Exception as e:
        print(f"Error loading config: {e}. Using defaults.")
        return AnkiConfig()

def save_config(config: AnkiConfig, config_path: str) -> None:
    """Save configuration to JSON file."""
    config_dict = {
        'anki_connect_url': config.anki_connect_url,
        'default_model_name': config.default_model_name,
        'default_deck_name': config.default_deck_name,
        'langchain_model': config.langchain_model,
        'output_directory': config.output_directory,
        'max_cards_per_deck': config.max_cards_per_deck,
        'enable_media': config.enable_media
    }
    
    with open(config_path, 'w') as f:
        json.dump(config_dict, f, indent=2)

# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def create_deck_with_config(qa_data: List[Dict[str, str]], 
                          config: AnkiConfig) -> Any:
    """Create an Anki deck with configuration."""
    from .card_creation import create_basic_model, create_deck, create_note
    
    model = create_basic_model(config.default_model_name)
    deck = create_deck(config.default_deck_name)
    
    for item in qa_data:
        question = item.get('question', '')
        answer = item.get('answer', '')
        extras = item.get('extras', '')
        
        note = create_note(model, question, answer, extras)
        deck.add_note(note)
    
    return deck

def create_anki_deck_from_qa_file(file_path: str, deck_name: str, 
                                 output_path: str = None) -> str:
    """
    Create an Anki deck from a Q&A file and optionally save it.
    
    Args:
        file_path: Path to file containing Q&A pairs
        deck_name: Name for the Anki deck
        output_path: Optional path to save the .apkg file
        
    Returns:
        Path to the created .apkg file
    """
    from .qa_parsing import extract_qa_pairs
    from .card_creation import create_deck_from_dataframe, save_deck_to_file
    import pandas as pd
    
    with open(file_path, 'r', encoding='utf-8') as f:
        text = f.read()
    
    qa_pairs = extract_qa_pairs(text)
    df = pd.DataFrame(qa_pairs, columns=['question', 'answer'])
    
    deck = create_deck_from_dataframe(df, deck_name)
    
    if not output_path:
        output_path = f"{deck_name.replace(' ', '_')}.apkg"
    
    save_deck_to_file(deck, output_path)
    return output_path

def batch_import_anki_packages(directory: str) -> None:
    """Import all .apkg files from a directory into Anki."""
    from .anki_api import import_anki_package
    
    package_dir = Path(directory)
    apkg_files = list(package_dir.glob("*.apkg"))
    
    for apkg_file in apkg_files:
        print(f"Importing {apkg_file.name}...")
        success = import_anki_package(str(apkg_file))
        if success:
            print(f"✅ Successfully imported {apkg_file.name}")
        else:
            print(f"❌ Failed to import {apkg_file.name}")

def setup_output_directory(output_dir: str) -> Path:
    """Create output directory if it doesn't exist."""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    return output_path

def get_file_stats(file_path: str) -> Dict[str, Any]:
    """Get basic statistics about a file."""
    path = Path(file_path)
    
    if not path.exists():
        return {"exists": False}
    
    stat = path.stat()
    return {
        "exists": True,
        "size_bytes": stat.st_size,
        "size_mb": stat.st_size / (1024 * 1024),
        "modified": stat.st_mtime,
        "extension": path.suffix
    }

def clean_filename(filename: str) -> str:
    """Clean filename for cross-platform compatibility."""
    import re
    
    # Remove or replace invalid characters
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # Remove multiple underscores
    filename = re.sub(r'_+', '_', filename)
    # Trim underscores from ends
    filename = filename.strip('_')
    return filename

def validate_anki_connect() -> bool:
    """Check if Anki-Connect is available."""
    try:
        from .anki_api import anki_invoke
        anki_invoke('version')
        return True
    except Exception:
        return False

def log_operation(operation: str, details: str = "", success: bool = True) -> None:
    """Simple logging function."""
    import datetime
    
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    status = "✅" if success else "❌"
    print(f"[{timestamp}] {status} {operation}: {details}")

def chunk_list(lst: List[Any], chunk_size: int) -> List[List[Any]]:
    """Split a list into chunks of specified size."""
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]

def merge_dictionaries(*dicts: Dict) -> Dict:
    """Merge multiple dictionaries, with later ones taking precedence."""
    result = {}
    for d in dicts:
        result.update(d)
    return result

def find_duplicates(items: List[str]) -> List[str]:
    """Find duplicate items in a list."""
    seen = set()
    duplicates = set()
    
    for item in items:
        if item in seen:
            duplicates.add(item)
        seen.add(item)
    
    return list(duplicates)

def progress_bar(current: int, total: int, width: int = 50) -> str:
    """Create a simple progress bar."""
    progress = current / total
    filled = int(width * progress)
    bar = '█' * filled + '░' * (width - filled)
    percentage = progress * 100
    return f'[{bar}] {percentage:.1f}% ({current}/{total})'

def estimate_processing_time(items_processed: int, total_items: int, 
                           start_time: float) -> str:
    """Estimate remaining processing time."""
    import time
    
    if items_processed == 0:
        return "Calculating..."
    
    elapsed = time.time() - start_time
    rate = items_processed / elapsed
    remaining_items = total_items - items_processed
    estimated_remaining = remaining_items / rate
    
    hours = int(estimated_remaining // 3600)
    minutes = int((estimated_remaining % 3600) // 60)
    seconds = int(estimated_remaining % 60)
    
    if hours > 0:
        return f"{hours}h {minutes}m {seconds}s"
    elif minutes > 0:
        return f"{minutes}m {seconds}s"
    else:
        return f"{seconds}s"

def backup_file(file_path: str) -> str:
    """Create a backup copy of a file."""
    import shutil
    import datetime
    
    path = Path(file_path)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = path.with_suffix(f".{timestamp}{path.suffix}")
    
    shutil.copy2(file_path, backup_path)
    return str(backup_path)

def count_words(text: str) -> int:
    """Count words in text."""
    return len(text.split())

def count_characters(text: str, include_spaces: bool = True) -> int:
    """Count characters in text."""
    if include_spaces:
        return len(text)
    else:
        return len(text.replace(' ', ''))

def format_file_size(size_bytes: int) -> str:
    """Format file size in human-readable format."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"

def get_system_info() -> Dict[str, str]:
    """Get basic system information."""
    import platform
    import sys
    
    return {
        "python_version": sys.version,
        "platform": platform.platform(),
        "system": platform.system(),
        "machine": platform.machine(),
        "processor": platform.processor()
    }

# =============================================================================
# EXAMPLE USAGE FUNCTIONS
# =============================================================================

def example_create_simple_deck():
    """Example: Create a simple Anki deck."""
    qa_data = [
        {"question": "What is Python?", "answer": "A high-level programming language"},
        {"question": "What is machine learning?", "answer": "A subset of AI that learns from data"},
    ]
    
    config = AnkiConfig(default_deck_name="Python Basics")
    deck = create_deck_with_config(qa_data, config)
    
    from .card_creation import save_deck_to_file
    save_deck_to_file(deck, "python_basics.apkg")
    print("Created example deck: python_basics.apkg")

def example_load_and_process_anki_cards():
    """Example: Load existing Anki cards and process them."""
    try:
        from .anki_api import load_anki_query_to_dataframe
        df = load_anki_query_to_dataframe('deck:"My Deck"')
        print(f"Loaded {len(df)} cards from Anki")
        print("Columns:", df.columns.tolist())
        return df
    except Exception as e:
        print(f"Error loading cards: {e}")
        return None

def print_available_functions():
    """Print available functions in the anki_helpers package."""
    print("Anki Helpers - Available functions:")
    print("- Anki API: anki_invoke, load_anki_query_to_dataframe, get_anki_deck_names")
    print("- Text Processing: process_latex_to_markdown, preprocess_text, convert_latex_to_html")
    print("- Card Creation: create_deck_from_dataframe, save_deck_to_file")
    print("- Q&A Parsing: extract_qa_pairs, parse_syllabus")
    
    try:
        from .llm_integration import check_llm_availability
        availability = check_llm_availability()
        if availability["langchain"]:
            print("- LLM Integration: generate_card_summary, summarise_duplicates")
        if availability["openai"]:
            print("- OpenAI Integration: generate_qa_from_topics, query_openai")
    except ImportError:
        print("- LLM Integration: Not available")

def run_diagnostics() -> Dict[str, Any]:
    """Run diagnostic checks on the system."""
    diagnostics = {
        "anki_connect": validate_anki_connect(),
        "system_info": get_system_info(),
        "timestamp": str(datetime.datetime.now())
    }
    
    try:
        from .llm_integration import check_llm_availability
        diagnostics["llm_availability"] = check_llm_availability()
    except ImportError:
        diagnostics["llm_availability"] = {"langchain": False, "openai": False}
    
    return diagnostics 