"""
Q&A Parsing Module
Functions for parsing and extracting question-answer pairs from various text formats
"""

import re
import pandas as pd
from typing import List, Tuple, Dict, Any

# =============================================================================
# Q&A PARSING UTILITIES
# =============================================================================

def extract_qa_pairs(text: str) -> List[Tuple[str, str]]:
    """Extract Q&A pairs from formatted text."""
    qa_pairs = re.findall(r"Q:\s*(.*?)\s*A:\s*(.*?)(?=\nQ:|\Z)", text, re.DOTALL)
    return qa_pairs

def extract_qa_pairs_flexible(text: str) -> List[Tuple[str, str]]:
    """Extract Q&A pairs with more flexible formatting."""
    patterns = [
        r"Q:\s*(.*?)\s*A:\s*(.*?)(?=\nQ:|\Z)",  # Q: ... A: ...
        r"Question:\s*(.*?)\s*Answer:\s*(.*?)(?=\nQuestion:|\Z)",  # Question: ... Answer: ...
        r"Q\d+[.:]?\s*(.*?)\s*A\d+[.:]?\s*(.*?)(?=\nQ\d+|\Z)",  # Q1. ... A1. ...
        r"\*\*Q\*\*:\s*(.*?)\s*\*\*A\*\*:\s*(.*?)(?=\n\*\*Q\*\*:|\Z)",  # **Q**: ... **A**: ...
    ]
    
    for pattern in patterns:
        qa_pairs = re.findall(pattern, text, re.DOTALL | re.IGNORECASE)
        if qa_pairs:
            return qa_pairs
    
    return []

def parse_syllabus(text: str) -> List[str]:
    """Parse syllabus text into clean section names."""
    lines = text.strip().split("\n")
    return [re.sub(r"^\d+\.\s*", "", line).strip() for line in lines if line.strip()]

def parse_numbered_list(text: str) -> List[Tuple[str, str]]:
    """Parse numbered list into (number, content) pairs."""
    pattern = r"(\d+)\.\s*(.*?)(?=\n\d+\.|\Z)"
    matches = re.findall(pattern, text, re.DOTALL)
    return matches

def extract_question_from_html(html_content: str) -> str:
    """Extract question from HTML content."""
    pattern = r'<b>Question:</b>(.*?)<ul>'
    match = re.search(pattern, html_content, re.DOTALL)
    
    if match:
        return match.group(1).strip()
    else:
        return "Question not found in the HTML content."

def remove_question_from_html(html_content: str) -> str:
    """Remove question section from HTML content."""
    pattern = r'<b>Question:</b>(.*?)<ul>'
    return re.sub(pattern, '<ul>', html_content, flags=re.DOTALL)

def get_problems(text: str) -> List[Tuple[str, str]]:
    """Extract problem numbers and content from text."""
    pattern = r'(?:\\section{Problem |Problem )(\d+)(?:\.)?(?:})?(.*?)(?=\n(?:\\section{Problem |\nProblem \d)|$)'
    matches = re.findall(pattern, text, re.DOTALL)
    return matches

def get_problem_chapter_num(problems: List[Tuple[str, str]], starting_chapter: int = 1) -> pd.DataFrame:
    """Assign chapter numbers to problems and create DataFrame."""
    i = starting_chapter - 1
    p_prev = 10000
    data = []

    for p in problems:
        if int(p[0]) < int(p_prev):
            i += 1
        
        p_prev = p[0]
        question = f"{i}.{p[0]}"
        data.append((question, p[1]))

    return pd.DataFrame(data, columns=["problem", "content"])

def filter_extras(strings: List[str]) -> List[str]:
    """Filter out 'extras' fields from list of strings."""
    pattern = r"\bextras?\b"
    return [s for s in strings if not re.search(pattern, s, re.IGNORECASE)]

def parse_markdown_qa(markdown_text: str) -> List[Dict[str, str]]:
    """Parse Q&A from markdown format with headers."""
    qa_pairs = []
    
    # Pattern for markdown headers followed by content
    pattern = r"#{1,6}\s*(.*?)\n(.*?)(?=\n#{1,6}|\Z)"
    matches = re.findall(pattern, markdown_text, re.DOTALL)
    
    for i in range(0, len(matches), 2):
        if i + 1 < len(matches):
            question = matches[i][0].strip()
            answer = matches[i+1][1].strip()
            qa_pairs.append({"question": question, "answer": answer})
    
    return qa_pairs

def parse_csv_qa(csv_content: str, delimiter: str = ',') -> pd.DataFrame:
    """Parse Q&A from CSV format."""
    import io
    
    # Create a StringIO object from the CSV content
    csv_io = io.StringIO(csv_content)
    df = pd.read_csv(csv_io, delimiter=delimiter)
    
    # Standardize column names
    columns = df.columns.str.lower().str.strip()
    
    # Try to identify question and answer columns
    question_col = None
    answer_col = None
    
    for col in columns:
        if 'question' in col or 'q' == col:
            question_col = df.columns[list(columns).index(col)]
        elif 'answer' in col or 'a' == col:
            answer_col = df.columns[list(columns).index(col)]
    
    if question_col and answer_col:
        return df[[question_col, answer_col]].rename(columns={
            question_col: 'question',
            answer_col: 'answer'
        })
    else:
        # Return first two columns as question and answer
        return df.iloc[:, :2].rename(columns={
            df.columns[0]: 'question',
            df.columns[1]: 'answer'
        })

def parse_json_qa(json_content: str) -> List[Dict[str, str]]:
    """Parse Q&A from JSON format."""
    import json
    
    data = json.loads(json_content)
    
    if isinstance(data, list):
        # List of Q&A objects
        qa_pairs = []
        for item in data:
            if isinstance(item, dict):
                # Try different key combinations
                question_keys = ['question', 'q', 'prompt', 'query']
                answer_keys = ['answer', 'a', 'response', 'reply']
                
                question = None
                answer = None
                
                for key in question_keys:
                    if key in item:
                        question = item[key]
                        break
                
                for key in answer_keys:
                    if key in item:
                        answer = item[key]
                        break
                
                if question and answer:
                    qa_pairs.append({"question": question, "answer": answer})
        
        return qa_pairs
    
    elif isinstance(data, dict):
        # Single Q&A object or nested structure
        if 'questions' in data or 'qa_pairs' in data:
            key = 'questions' if 'questions' in data else 'qa_pairs'
            return parse_json_qa(json.dumps(data[key]))
        else:
            # Try to extract as single Q&A
            return parse_json_qa(json.dumps([data]))
    
    return []

def extract_cloze_deletions(text: str) -> List[str]:
    """Extract cloze deletion patterns from text."""
    # Pattern for Anki cloze deletions: {{c1::answer}}
    pattern = r'\{\{c\d+::(.*?)(?:::.*?)?\}\}'
    matches = re.findall(pattern, text)
    return matches

def create_cloze_from_qa(question: str, answer: str, cloze_num: int = 1) -> str:
    """Convert Q&A pair to cloze deletion format."""
    # Simple approach: replace the answer in the question with cloze deletion
    if answer.lower() in question.lower():
        cloze_text = question.replace(answer, f"{{{{c{cloze_num}::{answer}}}}}")
        return cloze_text
    else:
        # If answer not found in question, create a statement
        return f"{question} {{{{c{cloze_num}::{answer}}}}}"

def parse_anki_export(anki_export_text: str) -> List[Dict[str, str]]:
    """Parse Anki export format (tab-separated)."""
    lines = anki_export_text.strip().split('\n')
    qa_pairs = []
    
    for line in lines:
        fields = line.split('\t')
        if len(fields) >= 2:
            qa_pairs.append({
                "question": fields[0],
                "answer": fields[1],
                "tags": fields[2] if len(fields) > 2 else ""
            })
    
    return qa_pairs

def clean_parsed_text(text: str) -> str:
    """Clean parsed text by removing extra whitespace and formatting."""
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Remove HTML tags if present
    text = re.sub(r'<[^>]+>', '', text)
    
    # Remove markdown formatting
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)  # Bold
    text = re.sub(r'\*(.*?)\*', r'\1', text)      # Italic
    text = re.sub(r'`(.*?)`', r'\1', text)        # Code
    
    return text.strip()

def validate_qa_pairs(qa_pairs: List[Tuple[str, str]]) -> List[Tuple[str, str]]:
    """Validate and clean Q&A pairs."""
    valid_pairs = []
    
    for q, a in qa_pairs:
        # Clean the text
        q = clean_parsed_text(q)
        a = clean_parsed_text(a)
        
        # Skip if either is empty or too short
        if len(q.strip()) < 3 or len(a.strip()) < 3:
            continue
        
        # Skip duplicates
        if (q, a) not in valid_pairs:
            valid_pairs.append((q, a))
    
    return valid_pairs

def parse_flashcard_format(text: str) -> List[Dict[str, str]]:
    """Parse various flashcard formats into standardized Q&A."""
    qa_pairs = []
    
    # Try different parsing methods
    methods = [
        extract_qa_pairs_flexible,
        lambda t: [(m[0], m[1]) for m in parse_markdown_qa(t)],
    ]
    
    for method in methods:
        try:
            pairs = method(text)
            if pairs:
                qa_pairs = [{"question": q, "answer": a} for q, a in pairs]
                break
        except:
            continue
    
    return qa_pairs

def batch_parse_files(file_paths: List[str]) -> pd.DataFrame:
    """Parse multiple files and combine into single DataFrame."""
    all_qa_pairs = []
    
    for file_path in file_paths:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Determine file type and parse accordingly
            if file_path.endswith('.csv'):
                df = parse_csv_qa(content)
                pairs = [{"question": row.question, "answer": row.answer, "source": file_path} 
                        for _, row in df.iterrows()]
            elif file_path.endswith('.json'):
                pairs = parse_json_qa(content)
                for pair in pairs:
                    pair["source"] = file_path
            else:
                # Assume text format
                pairs = parse_flashcard_format(content)
                for pair in pairs:
                    pair["source"] = file_path
            
            all_qa_pairs.extend(pairs)
            
        except Exception as e:
            print(f"Error parsing {file_path}: {e}")
    
    return pd.DataFrame(all_qa_pairs) 