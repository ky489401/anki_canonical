"""
Anki API Integration Module
Functions for connecting to Anki via Anki-Connect API
"""

import json
import urllib.request
import requests
import pandas as pd
from typing import List, Dict, Any

# =============================================================================
# ANKI API INTEGRATION
# =============================================================================

def anki_request(action: str, **params) -> Dict[str, Any]:
    """Create a request dictionary for Anki-Connect API."""
    return {'action': action, 'params': params, 'version': 6}

def anki_invoke(action: str, **params) -> Any:
    """Invoke an Anki-Connect API call."""
    request_json = json.dumps(anki_request(action, **params)).encode('utf-8')
    response = json.load(urllib.request.urlopen(urllib.request.Request('http://localhost:8765', request_json)))
    
    if len(response) != 2:
        raise Exception('response has an unexpected number of fields')
    if 'error' not in response:
        raise Exception('response is missing required error field')
    if 'result' not in response:
        raise Exception('response is missing required result field')
    if response['error'] is not None:
        raise Exception(response['error'])
    
    return response['result']

def anki_invoke_requests(action: str, **params) -> Any:
    """Alternative Anki-Connect API call using requests library."""
    return requests.post(
        "http://localhost:8765",
        json={"action": action, "version": 6, "params": params},
    ).json()

def load_anki_query_to_dataframe(query: str) -> pd.DataFrame:
    """
    Load Anki cards matching a query into a pandas DataFrame.
    
    Args:
        query: Anki search query (e.g., 'deck:MyDeck')
        
    Returns:
        DataFrame with card information and field contents
    """
    # Get all card IDs from the specified query
    card_ids_response = anki_invoke_requests("findCards", query=query)
    card_ids = card_ids_response["result"]

    # Get information about each card
    cards_info_response = anki_invoke_requests("cardsInfo", cards=card_ids)
    cards_info = cards_info_response["result"]

    # Prepare data for the DataFrame
    data = []
    field_names = set()

    for card in cards_info:
        fields = card["fields"]
        card_data = {"card_number": str(card.get("cardId", ""))}
        for field_name, field_content in fields.items():
            card_data[field_name] = field_content["value"]
            field_names.add(field_name)
        data.append(card_data)

    # Create DataFrame
    df = pd.DataFrame(data, columns=["card_number"] + sorted(field_names))
    return df

def get_anki_deck_names() -> List[str]:
    """Get list of all Anki deck names."""
    return anki_invoke('deckNames')

def import_anki_package(file_path: str) -> bool:
    """Import an .apkg file into Anki."""
    try:
        anki_invoke('importPackage', path=file_path)
        return True
    except Exception as e:
        print(f"Error importing package: {e}")
        return False

def get_card_info(card_ids: List[int]) -> List[Dict]:
    """Get detailed information about specific cards."""
    return anki_invoke("cardsInfo", cards=card_ids)

def find_cards(query: str) -> List[int]:
    """Find card IDs matching a query."""
    return anki_invoke("findCards", query=query)

def add_note(deck_name: str, model_name: str, fields: Dict[str, str], tags: List[str] = None) -> int:
    """Add a single note to Anki."""
    note = {
        "deckName": deck_name,
        "modelName": model_name,
        "fields": fields,
        "tags": tags or []
    }
    return anki_invoke("addNote", note=note)

def update_note_fields(note_id: int, fields: Dict[str, str]) -> None:
    """Update fields of an existing note."""
    anki_invoke("updateNoteFields", note={"id": note_id, "fields": fields})

def delete_notes(note_ids: List[int]) -> None:
    """Delete multiple notes by their IDs."""
    anki_invoke("deleteNotes", notes=note_ids) 