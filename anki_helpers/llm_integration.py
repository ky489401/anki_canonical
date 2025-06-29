"""
LLM Integration Module
Functions for LLM-based Anki card generation and processing
"""

import pandas as pd
from typing import List, Dict, Optional

# Optional imports for LLM functionality
try:
    from langchain_core.pydantic_v1 import BaseModel, Field
    from langchain_openai import ChatOpenAI
    from langchain_core.prompts import ChatPromptTemplate
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    print("Warning: LangChain not available. LLM-based functions will not work.")

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("Warning: OpenAI not available. OpenAI-based functions will not work.")

# =============================================================================
# LANGCHAIN INTEGRATION
# =============================================================================

if LANGCHAIN_AVAILABLE:
    class AnkiContent(BaseModel):
        """Structured output for individual Anki card summaries."""
        title: str = Field(description="Title of the Anki card")
        body: str = Field(description="Concise bullet point summary of the given text in markdown")
        short_summary: str = Field(description="Short two-line summary of the text")

    class AnkiCard(BaseModel):
        """Structured output for ranked Anki cards including deduplication info."""
        rank: int = Field(description="Ranking position based on course order")
        title: str = Field(description="Anki card title")
        card_number: str = Field(description="Anki card number, e.g., 1629065002858")
        topic: str = Field(description="Broad topic that this card falls into")
        is_duplicate: bool = Field(description="True if this card is a duplicate")
        duplicate_group: Optional[int] = Field(default=None, description="Unique id for the group of duplicates")
        duplicate_of: Optional[str] = Field(default=None, description="Title of the card it duplicates")

    class RankedAnkiList(BaseModel):
        """A list of ranked Anki cards."""
        ranked_list: List[AnkiCard]

    def generate_card_summary(card_text: str, llm_model: ChatOpenAI) -> AnkiContent:
        """Generate a structured summary for an individual Anki card using LLM."""
        system_prompt = (
            "Write a concise bullet point summary of the given text in markdown. "
            "Section headers also start with a bullet. "
            "Put the bullet point summary into the field 'body'. "
            "Then write a two-line summary and put it into the field 'short_summary'.\n\n"
            "Follow this format:\n\n"
            "- **First level item 1**\n"
            "  - **Second level item 1.1**: ...\n"
            "  - **Second level item 1.2**: ...\n"
            "  ...\n"
        )

        prompt_template = ChatPromptTemplate([
            ("system", system_prompt),
            ("user", "{card_text}"),
        ])
        
        prompt_instance = prompt_template.invoke({"card_text": card_text})
        summary = llm_model.invoke(prompt_instance)
        return summary

    def summarise_duplicates(duplicate_summaries: str, llm_model: ChatOpenAI) -> str:
        """Consolidate multiple duplicate summaries into a single summary."""
        duplicate_system_prompt = (
            "You are given the summaries of duplicated Anki cards in markdown. Bold words as necessary. "
            "Rewrite them into a single summary while preserving the original wording. "
            "Remove duplicated items/concepts and rearrange items only if necessary so that the flow is improved.\n\n"
            "Section headers also start with a bullet. Follow this format:\n\n"
            "- **First level item 1**\n"
            "  - **Second level item 1.1**: ...\n"
            "  - **Second level item 1.2**: ...\n"
            "  ...\n"
        )

        prompt_template = ChatPromptTemplate([
            ("system", duplicate_system_prompt),
            ("user", "{duplicate_text}"),
        ])
        
        prompt_instance = prompt_template.invoke({"duplicate_text": duplicate_summaries})
        merged_result = llm_model.invoke(prompt_instance)
        return merged_result.content

    def get_card_order(anki_titles_text: str, llm_model: ChatOpenAI) -> pd.DataFrame:
        """Rank and organize Anki cards using LLM."""
        ranking_prompt_template = ChatPromptTemplate.from_template(
            """Given the following Anki card titles from a course, rank them based on their natural material order.
                - Identify if any cards cover the same or highly similar material and mark them as duplicates.
                - Place duplicates next to each other in terms of ranking and mark them (both the duplicate and the original) as is_duplicate.
                - Assign a broad topic to each card.

                Anki Card Titles:
                {anki_titles}

                Output the results in JSON format following the provided structured schema.
    """
        )
        
        structured_ranking_llm = llm_model.with_structured_output(RankedAnkiList)
        ranking_prompt_instance = ranking_prompt_template.invoke(
            {"anki_titles": anki_titles_text}
        )
        ranking_response = structured_ranking_llm.invoke(ranking_prompt_instance)

        # Convert the ranked list into a DataFrame
        ranking_data = [
            {
                "rank": card.rank,
                "title": card.title,
                "card_number": getattr(card, "card_number", None),
                "topic": getattr(card, "topic", None),
                "is_duplicate": card.is_duplicate,
                "duplicate_group": card.duplicate_group,
                "duplicate_of": card.duplicate_of,
            }
            for card in ranking_response.ranked_list
        ]
        ranking_df = pd.DataFrame(ranking_data)
        return ranking_df

# =============================================================================
# OPENAI INTEGRATION
# =============================================================================

if OPENAI_AVAILABLE:
    def build_qa_prompt(section_name: str, topic_name: str) -> str:
        """Build a prompt for generating Q&A pairs on a topic."""
        return f"""
Generate an extremely detailed list of interview questions and answers on the topic: {topic_name} ------ {section_name}
Keep the questions broad rather than overly specific. 

Write answers in bullet points. 
Answers should be intuitive and beginner/intermediate friendly, but avoid using metaphors unnecessarily.

Use ONLY this format with NO markdown:
Q: [Your question here]
A: [Detailed answer here with code examples if needed]

Keep everything strictly in this Q: ... A: ... format.
"""

    def query_openai(prompt: str, model: str = "gpt-4o", api_key: str = None) -> str:
        """Query OpenAI API with a prompt."""
        if not api_key:
            raise ValueError("OpenAI API key is required")
        
        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )
        return response.choices[0].message.content

    def generate_qa_from_topics(topics: List[str], topic_name: str, api_key: str) -> pd.DataFrame:
        """Generate Q&A pairs from a list of topics using OpenAI."""
        from .qa_parsing import extract_qa_pairs
        
        results = []
        
        for section in topics:
            print(f"⏳ Generating: {section}")
            prompt = build_qa_prompt(section, topic_name)
            
            try:
                response_text = query_openai(prompt, api_key=api_key)
                qa_pairs = extract_qa_pairs(response_text)
                
                for q, a in qa_pairs:
                    results.append({"section": section, "question": q, "answer": a})
                    
            except Exception as e:
                print(f"❌ Failed on {section}: {e}")
        
        return pd.DataFrame(results, columns=["section", "question", "answer"])

    def enhance_qa_with_llm(qa_df: pd.DataFrame, api_key: str, model: str = "gpt-4o") -> pd.DataFrame:
        """Enhance existing Q&A pairs with LLM improvements."""
        enhanced_qa = []
        
        for _, row in qa_df.iterrows():
            enhancement_prompt = f"""
Improve this Q&A pair by making the question more precise and the answer more comprehensive:

Original Question: {row['question']}
Original Answer: {row['answer']}

Provide an improved version that:
1. Makes the question clearer and more specific
2. Enhances the answer with better structure and examples
3. Maintains the same core content

Format:
Q: [Improved question]
A: [Improved answer]
"""
            
            try:
                response = query_openai(enhancement_prompt, model=model, api_key=api_key)
                # Parse the response to extract improved Q&A
                from .qa_parsing import extract_qa_pairs
                improved_pairs = extract_qa_pairs(response)
                
                if improved_pairs:
                    enhanced_qa.append({
                        "original_question": row['question'],
                        "original_answer": row['answer'],
                        "enhanced_question": improved_pairs[0][0],
                        "enhanced_answer": improved_pairs[0][1],
                        "section": row.get('section', '')
                    })
                else:
                    # Fallback to original if parsing fails
                    enhanced_qa.append({
                        "original_question": row['question'],
                        "original_answer": row['answer'],
                        "enhanced_question": row['question'],
                        "enhanced_answer": row['answer'],
                        "section": row.get('section', '')
                    })
                    
            except Exception as e:
                print(f"Error enhancing Q&A: {e}")
                # Fallback to original
                enhanced_qa.append({
                    "original_question": row['question'],
                    "original_answer": row['answer'],
                    "enhanced_question": row['question'],
                    "enhanced_answer": row['answer'],
                    "section": row.get('section', '')
                })
        
        return pd.DataFrame(enhanced_qa)

# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def check_llm_availability() -> Dict[str, bool]:
    """Check which LLM libraries are available."""
    return {
        "langchain": LANGCHAIN_AVAILABLE,
        "openai": OPENAI_AVAILABLE
    }

def create_llm_model(model_name: str = "gpt-4o-mini", api_key: str = None):
    """Create an LLM model instance if available."""
    if LANGCHAIN_AVAILABLE and api_key:
        return ChatOpenAI(model=model_name, temperature=0, api_key=api_key)
    else:
        raise ValueError("LangChain not available or API key not provided")

def batch_process_with_llm(texts: List[str], processing_function, llm_model, 
                          batch_size: int = 10) -> List:
    """Process texts in batches using LLM to avoid rate limits."""
    results = []
    
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        print(f"Processing batch {i//batch_size + 1}/{(len(texts) + batch_size - 1)//batch_size}")
        
        for text in batch:
            try:
                result = processing_function(text, llm_model)
                results.append(result)
            except Exception as e:
                print(f"Error processing text: {e}")
                results.append(None)
        
        # Simple rate limiting
        import time
        time.sleep(1)
    
    return results

def generate_study_schedule_prompt(topics: List[str], days: int = 30) -> str:
    """Generate a study schedule prompt for the given topics."""
    return f"""
Create a {days}-day study schedule for the following topics:
{', '.join(topics)}

For each day, specify:
1. Which topic(s) to focus on
2. Recommended study duration
3. Key concepts to review
4. Practice exercises or questions

Format as a structured daily plan.
""" 