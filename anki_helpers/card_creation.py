"""
Card Creation Module
Functions for creating Anki cards and decks using genanki
"""

import random
import genanki
import pandas as pd
from typing import List, Dict, Optional
from pathlib import Path

# =============================================================================
# GENANKI CARD CREATION
# =============================================================================

def create_basic_model(model_name: str = "Basic") -> genanki.Model:
    """Create a basic Anki model for cards."""
    model_id = random.randrange(1 << 30, 1 << 31)
    
    return genanki.Model(
        model_id,
        model_name,
        fields=[
            {'name': 'Question'},
            {'name': 'Answer'},
            {'name': 'Extras'},
        ],
        templates=[
            {
                'name': 'Card type 1',
                'qfmt': '{{Question}}',
                'afmt': '{{FrontSide}}<hr id="answer">{{Answer}}',
            },
        ]
    )

def create_cloze_model(model_name: str = "Cloze") -> genanki.Model:
    """Create a cloze deletion model for cards."""
    model_id = random.randrange(1 << 30, 1 << 31)
    
    return genanki.Model(
        model_id,
        model_name,
        fields=[
            {'name': 'Text'},
            {'name': 'Extra'},
        ],
        templates=[
            {
                'name': 'Cloze',
                'qfmt': '{{cloze:Text}}',
                'afmt': '{{cloze:Text}}<br>{{Extra}}',
            },
        ],
        model_type=genanki.Model.CLOZE
    )

def create_advanced_model(model_name: str = "Advanced") -> genanki.Model:
    """Create an advanced Anki model with more fields."""
    model_id = random.randrange(1 << 30, 1 << 31)
    
    return genanki.Model(
        model_id,
        model_name,
        fields=[
            {'name': 'Question'},
            {'name': 'Answer'},
            {'name': 'Source'},
            {'name': 'Tags'},
            {'name': 'Hint'},
            {'name': 'Extra'},
        ],
        templates=[
            {
                'name': 'Card 1',
                'qfmt': '''
                <div class="question">{{Question}}</div>
                {{#Hint}}<div class="hint">Hint: {{Hint}}</div>{{/Hint}}
                ''',
                'afmt': '''
                {{FrontSide}}
                <hr id="answer">
                <div class="answer">{{Answer}}</div>
                {{#Source}}<div class="source">Source: {{Source}}</div>{{/Source}}
                {{#Extra}}<div class="extra">{{Extra}}</div>{{/Extra}}
                ''',
            },
        ],
        css='''
        .card { font-family: arial; font-size: 16px; text-align: left; color: black; background-color: white; }
        .question { font-weight: bold; color: #2c3e50; }
        .answer { margin-top: 10px; }
        .hint { font-style: italic; color: #7f8c8d; margin-top: 5px; }
        .source { font-size: 12px; color: #95a5a6; margin-top: 10px; }
        .extra { color: #34495e; margin-top: 10px; }
        '''
    )

def create_deck(deck_name: str) -> genanki.Deck:
    """Create a new Anki deck."""
    deck_id = random.randrange(1 << 30, 1 << 31)
    return genanki.Deck(deck_id, deck_name)

def create_note(model: genanki.Model, question: str, answer: str, extras: str = "") -> genanki.Note:
    """Create a new note for an Anki card."""
    if len(model.fields) == 2:  # Cloze model
        return genanki.Note(
            model=model,
            fields=[question, answer]
        )
    elif len(model.fields) == 3:  # Basic model
        return genanki.Note(
            model=model,
            fields=[question, answer, extras]
        )
    else:  # Advanced model
        return genanki.Note(
            model=model,
            fields=[question, answer, "", "", "", extras]
        )

def create_advanced_note(model: genanki.Model, question: str, answer: str, 
                       source: str = "", tags: str = "", hint: str = "", extra: str = "") -> genanki.Note:
    """Create a note with all advanced fields."""
    return genanki.Note(
        model=model,
        fields=[question, answer, source, tags, hint, extra]
    )

def save_deck_to_file(deck: genanki.Deck, filename: str, include_media: bool = False) -> None:
    """Save an Anki deck to .apkg file."""
    if not filename.endswith('.apkg'):
        filename += '.apkg'
    
    if include_media:
        # Create package with media files
        media_files = []  # Add your media files here
        package = genanki.Package(deck, media_files=media_files)
    else:
        package = genanki.Package(deck)
    
    package.write_to_file(filename)
    print(f"Deck saved to {filename}")

def create_deck_from_dataframe(df: pd.DataFrame, deck_name: str, 
                             question_col: str = 'question', 
                             answer_col: str = 'answer',
                             extras_col: str = None,
                             model_type: str = 'basic') -> genanki.Deck:
    """
    Create an Anki deck from a pandas DataFrame.
    
    Args:
        df: DataFrame containing card data
        deck_name: Name for the deck
        question_col: Column name for questions
        answer_col: Column name for answers
        extras_col: Optional column name for extra information
        model_type: Type of model ('basic', 'cloze', 'advanced')
        
    Returns:
        genanki.Deck object
    """
    if model_type == 'cloze':
        model = create_cloze_model()
    elif model_type == 'advanced':
        model = create_advanced_model()
    else:
        model = create_basic_model()
    
    deck = create_deck(deck_name)
    
    for idx, row in df.iterrows():
        question = str(row[question_col])
        answer = str(row[answer_col])
        extras = str(row[extras_col]) if extras_col and extras_col in df.columns else ""
        
        note = create_note(model, question, answer, extras)
        deck.add_note(note)
    
    return deck

def merge_decks(decks: List[genanki.Deck], merged_deck_name: str) -> genanki.Deck:
    """Merge multiple decks into a single deck."""
    merged_deck = create_deck(merged_deck_name)
    
    for deck in decks:
        for note in deck.notes:
            merged_deck.add_note(note)
    
    return merged_deck

def filter_deck_by_tags(deck: genanki.Deck, required_tags: List[str]) -> genanki.Deck:
    """Create a new deck containing only notes with specified tags."""
    filtered_deck = create_deck(f"{deck.name}_filtered")
    
    for note in deck.notes:
        if any(tag in note.tags for tag in required_tags):
            filtered_deck.add_note(note)
    
    return filtered_deck

def add_tags_to_deck(deck: genanki.Deck, tags: List[str]) -> None:
    """Add tags to all notes in a deck."""
    for note in deck.notes:
        note.tags.extend(tags)

def create_deck_with_subdeck_structure(base_name: str, subdeck_data: Dict[str, pd.DataFrame]) -> List[genanki.Deck]:
    """
    Create multiple related decks with a subdeck structure.
    
    Args:
        base_name: Base name for the deck hierarchy
        subdeck_data: Dictionary mapping subdeck names to DataFrames
        
    Returns:
        List of created decks
    """
    decks = []
    
    for subdeck_name, df in subdeck_data.items():
        full_deck_name = f"{base_name}::{subdeck_name}"
        deck = create_deck_from_dataframe(df, full_deck_name)
        decks.append(deck)
    
    return decks

def export_deck_statistics(deck: genanki.Deck) -> Dict[str, int]:
    """Get basic statistics about a deck."""
    return {
        'total_notes': len(deck.notes),
        'total_fields': sum(len(note.fields) for note in deck.notes),
        'notes_with_tags': sum(1 for note in deck.notes if note.tags),
        'unique_models': len(set(note.model.model_id for note in deck.notes))
    }

def validate_deck(deck: genanki.Deck) -> List[str]:
    """Validate a deck and return list of issues found."""
    issues = []
    
    if not deck.notes:
        issues.append("Deck is empty")
    
    for i, note in enumerate(deck.notes):
        if not any(field.strip() for field in note.fields):
            issues.append(f"Note {i+1} has all empty fields")
        
        if len(note.fields) != len(note.model.fields):
            issues.append(f"Note {i+1} field count doesn't match model")
    
    return issues

def batch_create_decks(deck_configs: List[Dict]) -> List[genanki.Deck]:
    """
    Create multiple decks from configuration dictionaries.
    
    Args:
        deck_configs: List of dictionaries with keys: 'name', 'data', 'question_col', 'answer_col'
        
    Returns:
        List of created decks
    """
    decks = []
    
    for config in deck_configs:
        deck = create_deck_from_dataframe(
            config['data'],
            config['name'],
            config.get('question_col', 'question'),
            config.get('answer_col', 'answer'),
            config.get('extras_col', None),
            config.get('model_type', 'basic')
        )
        decks.append(deck)
    
    return decks 