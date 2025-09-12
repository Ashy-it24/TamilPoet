"""
OpenAI-powered Tamil word translator for classical to modern Tamil conversion
with web research capabilities for classical Tamil poetry context
"""
import json
import os
import re
from openai import OpenAI

# the newest OpenAI model is "gpt-5" which was released August 7, 2025.
# do not change this unless explicitly requested by the user

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
openai = OpenAI(api_key=OPENAI_API_KEY)

def translate_classical_tamil_with_ai(text: str) -> dict:
    """Use OpenAI to intelligently translate classical Tamil to modern Tamil"""
    try:
        prompt = f"""
        You are an expert in Tamil language, specializing in classical Tamil literature and modern Tamil. 
        
        Please modernize this classical Tamil text for better text-to-speech pronunciation while preserving its poetic meaning and structure:
        
        "{text}"
        
        Rules:
        1. Replace archaic Tamil words with their modern equivalents
        2. Normalize classical grammar constructions to modern forms
        3. Handle sandhi (euphonic combinations) appropriately  
        4. Maintain the poetic meter and meaning
        5. Ensure the output is suitable for Tamil text-to-speech engines
        6. Only change what needs to be modernized - don't over-translate
        
        Respond with JSON in this format:
        {{
            "modernized_text": "the modernized Tamil text",
            "changes_made": ["list of key changes made"],
            "confidence": 0.95
        }}
        """
        
        response = openai.chat.completions.create(
            model="gpt-5",
            messages=[
                {
                    "role": "system",
                    "content": "You are a Tamil language expert specializing in classical to modern Tamil translation. Respond only in valid JSON format."
                },
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.3  # Lower temperature for more consistent translations
        )
        
        content = response.choices[0].message.content
        if not content:
            raise Exception("Empty response from OpenAI")
        result = json.loads(content)
        return result
        
    except Exception as e:
        print(f"AI translation error: {str(e)}")
        return {
            "modernized_text": text,  # Return original if AI fails
            "changes_made": [],
            "confidence": 0.0
        }

def get_word_by_word_translation(text: str) -> dict:
    """Get detailed word-by-word translation mapping"""
    try:
        prompt = f"""
        Analyze this classical Tamil text word by word and provide modern equivalents:
        
        "{text}"
        
        For each classical/archaic word that needs modernization, provide the modern equivalent.
        Ignore common modern words that don't need translation.
        
        Respond with JSON in this format:
        {{
            "word_mappings": {{
                "classical_word1": "modern_word1",
                "classical_word2": "modern_word2"
            }},
            "analysis": "Brief explanation of the translation approach"
        }}
        """
        
        response = openai.chat.completions.create(
            model="gpt-5",
            messages=[
                {
                    "role": "system", 
                    "content": "You are a Tamil linguistics expert. Provide word-by-word classical to modern Tamil mappings. Respond only in valid JSON format."
                },
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.2
        )
        
        content = response.choices[0].message.content
        if not content:
            raise Exception("Empty response from OpenAI")
        result = json.loads(content)
        return result
        
    except Exception as e:
        print(f"Word mapping error: {str(e)}")
        return {
            "word_mappings": {},
            "analysis": "Translation service unavailable"
        }

def extract_key_terms_from_tamil_text(text: str) -> list:
    """Extract key terms and phrases from Tamil text for web search"""
    try:
        # Remove common punctuation and split into words
        words = re.findall(r'[\u0B80-\u0BFF]+', text)  # Tamil Unicode range
        
        # Look for significant words (longer than 2 characters)
        key_terms = [word for word in words if len(word) > 2]
        
        # Return first few significant terms for search
        return key_terms[:5]
    except Exception:
        return []

def generate_research_queries(text: str) -> list:
    """
    Generate targeted search queries for classical Tamil poetry research.
    This helper function creates search queries based on the input text.
    """
    key_terms = extract_key_terms_from_tamil_text(text)
    search_terms = " ".join(key_terms[:3]) if key_terms else text[:50]
    
    return [
        f"classical Tamil poetry {search_terms} literary analysis meaning",
        f"ancient Tamil literature {search_terms} historical period themes", 
        f"Tamil sangam literature {search_terms} poet author context",
        f"classical Tamil verses {search_terms} literary significance interpretation"
    ]

def research_classical_tamil_context(text: str, search_results: list = None) -> dict:
    """
    Analyze classical Tamil poetry and gather contextual information.
    
    Args:
        text: The Tamil text to analyze
        search_results: Optional list of web search results to analyze
    
    Returns:
        Dictionary with keys: 'context', 'period', 'themes', 'meaning', 'literary_significance'
    """
    try:
        context_info = {
            'context': '',
            'period': 'Classical Tamil period',
            'themes': [],
            'meaning': '',
            'literary_significance': ''
        }
        
        # If search results are provided, analyze them
        if search_results and isinstance(search_results, list):
            # Process and structure the research results
            all_content = " ".join(str(result) for result in search_results if result)
            
            if all_content:
                # Extract context information using pattern matching and keywords
                context_keywords = ['sangam', 'classical', 'ancient', 'medieval', 'chola', 'pandya', 'pallava']
                period_keywords = ['century', 'BCE', 'CE', 'AD', 'era', 'period', 'dynasty']
                theme_keywords = ['love', 'war', 'devotion', 'nature', 'heroism', 'spirituality', 'ethics', 'philosophy']
                
                # Build context information from search results
                if any(keyword in all_content.lower() for keyword in context_keywords):
                    context_info['context'] = "This appears to be from classical Tamil literature. The text shows characteristics of traditional Tamil poetic forms with themes commonly found in ancient Tamil works."
                
                # Identify potential historical period
                for period_word in period_keywords:
                    if period_word in all_content.lower():
                        # Look for century mentions or historical periods
                        period_match = re.search(rf'\b(\d+(?:st|nd|rd|th)?\s+century|sangam\s+period|chola\s+period|medieval\s+tamil)', all_content.lower())
                        if period_match:
                            context_info['period'] = period_match.group(1).title()
                            break
                
                # Extract themes
                found_themes = [theme for theme in theme_keywords if theme in all_content.lower()]
                context_info['themes'] = found_themes[:4] if found_themes else ['classical poetry', 'literary expression']
                
                # Generate meaning summary from search results
                if len(all_content) > 100:
                    # Extract meaningful sentences that might contain interpretation
                    sentences = re.split(r'[.!?]+', all_content)
                    meaningful_sentences = [s.strip() for s in sentences if len(s.strip()) > 50 and 'tamil' in s.lower()]
                    if meaningful_sentences:
                        context_info['meaning'] = meaningful_sentences[0][:200] + "..."
                
                # Literary significance
                significance_keywords = ['significant', 'important', 'renowned', 'famous', 'classic', 'masterpiece']
                if any(keyword in all_content.lower() for keyword in significance_keywords):
                    context_info['literary_significance'] = "This text appears to be from a significant work in Tamil literature, representing classical poetic traditions and cultural heritage."
    
        # Apply text analysis even without web search results
        key_terms = extract_key_terms_from_tamil_text(text)
        if key_terms:
            # Analyze text characteristics for basic context
            text_length = len(text.split())
            if text_length > 10:
                context_info['context'] = "This appears to be a substantial classical Tamil text, likely poetic in nature based on its structure and length."
            else:
                context_info['context'] = "Short classical Tamil text, possibly a verse or poetic line."
        
        # Ensure all fields have meaningful content
        _ensure_complete_context(context_info)
        
        return context_info
        
    except Exception as e:
        print(f"Research error: {str(e)}")
        return _fallback_classical_context()

def _ensure_complete_context(context_info: dict) -> None:
    """Ensure all context fields have meaningful content"""
    if not context_info['context']:
        context_info['context'] = "Classical Tamil poetry text with traditional linguistic patterns and poetic structure."
    
    if not context_info['meaning']:
        context_info['meaning'] = "This appears to be a classical Tamil poetic composition. The exact meaning may require expert interpretation due to archaic language and cultural references."
    
    if not context_info['literary_significance']:
        context_info['literary_significance'] = "Represents the rich tradition of Tamil literature and poetic expression spanning over two millennia."
    
    if not context_info['themes']:
        context_info['themes'] = ['classical poetry', 'tamil literature']

def _fallback_classical_context() -> dict:
    """Provide fallback context information when web research is unavailable"""
    return {
        'context': 'Classical Tamil literature encompasses works from the Sangam period (3rd century BCE - 3rd century CE) through medieval times. These texts often feature sophisticated poetic devices, cultural themes, and linguistic complexity.',
        'period': 'Classical Tamil period (Sangam era to Medieval)',
        'themes': ['devotion', 'nature', 'love', 'heroism', 'philosophy', 'ethics'],
        'meaning': 'This text represents classical Tamil poetic tradition. The archaic language and structure suggest it may be from ancient Tamil literature, requiring specialized knowledge for complete interpretation.',
        'literary_significance': 'Tamil classical literature is among the world\'s oldest literary traditions, preserving cultural heritage, philosophical insights, and linguistic evolution over millennia. These works contribute significantly to understanding ancient South Indian civilization and Tamil cultural identity.'
    }