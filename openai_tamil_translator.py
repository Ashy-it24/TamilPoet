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

def translate_classical_tamil_with_ai(text: str, context_info: dict = None, use_web_research: bool = True) -> dict:
    """Use OpenAI to provide meaning-based translation of classical Tamil to modern Tamil
    
    Args:
        text: Classical Tamil text to translate
        context_info: Optional context from web research
        use_web_research: Whether to include web research context in translation
    
    Returns:
        Dict with original_text, modernized_text, meaning_explanation, context_info, translation_method, changes_made
    """
    try:
        # If no context provided and web research is enabled, try to get context
        if context_info is None and use_web_research:
            context_info = research_classical_tamil_context(text)
        
        # Build enhanced prompt with context
        context_section = ""
        if context_info:
            context_section = f"""
            
CONTEXTUAL INFORMATION:
            Historical Period: {context_info.get('period', 'Classical Tamil period')}
            Literary Context: {context_info.get('context', 'Classical Tamil poetry')}
            Common Themes: {', '.join(context_info.get('themes', ['classical poetry']))}
            Cultural Significance: {context_info.get('literary_significance', 'Traditional Tamil literature')}
            """
        
        prompt = f"""
        You are an expert Tamil scholar specializing in classical Tamil literature, poetic meaning, and modern Tamil expression.
        
        TASK: Provide a meaning-based translation of this classical Tamil poetry text into modern Tamil suitable for text-to-speech.
        
        ORIGINAL TEXT: "{text}"
        {context_section}
        
        TRANSLATION APPROACH:
        1. Focus on conveying the complete poetic meaning and emotional content, not just word-for-word substitution
        2. Understand the classical Tamil literary devices, metaphors, and cultural references
        3. Express the essence and sentiment in clear, modern Tamil that preserves the artistic intent
        4. Maintain poetic beauty while ensuring TTS clarity
        5. Consider the historical and cultural context in your interpretation
        6. Explain the deeper meaning and significance of the poetry
        
        REQUIREMENTS:
        - Modernized text should be naturally flowing modern Tamil
        - Preserve the emotional and artistic essence of the original
        - Make cultural and literary references accessible to modern readers
        - Ensure pronunciation clarity for text-to-speech engines
        
        Respond with JSON in this format:
        {{
            "modernized_text": "beautifully expressed modern Tamil that captures the full meaning",
            "meaning_explanation": "detailed explanation of the poetic meaning, themes, and significance",
            "changes_made": ["list of key modernization changes made"],
            "confidence": 0.95,
            "literary_analysis": "brief analysis of the poetic devices and cultural elements"
        }}
        """
        
        response = openai.chat.completions.create(
            model="gpt-5",
            messages=[
                {
                    "role": "system",
                    "content": "You are a distinguished Tamil literature scholar with expertise in classical poetry interpretation and modern Tamil expression. Provide meaning-based translations that capture the artistic and cultural essence. Respond only in valid JSON format."
                },
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.4  # Balanced for creativity while maintaining consistency
        )
        
        content = response.choices[0].message.content
        if not content:
            raise Exception("Empty response from OpenAI")
        
        ai_result = json.loads(content)
        
        # Construct comprehensive response
        result = {
            "original_text": text,
            "modernized_text": ai_result.get("modernized_text", text),
            "meaning_explanation": ai_result.get("meaning_explanation", "AI-powered meaning-based translation of classical Tamil poetry."),
            "context_info": context_info or {},
            "translation_method": "AI-powered with context",
            "changes_made": ai_result.get("changes_made", []),
            "confidence": ai_result.get("confidence", 0.8),
            "literary_analysis": ai_result.get("literary_analysis", "Classical Tamil poetry with traditional elements.")
        }
        
        return result
        
    except Exception as e:
        print(f"AI translation error: {str(e)}")
        # Return to fallback method
        return _fallback_meaning_based_translation(text, context_info)

def get_comprehensive_translation(text: str, use_ai: bool = True, use_web_research: bool = True) -> dict:
    """Main entry point for comprehensive classical Tamil translation
    
    Args:
        text: Classical Tamil text to translate
        use_ai: Whether to attempt AI translation first (falls back if fails)
        use_web_research: Whether to include web research context
    
    Returns:
        Comprehensive translation with meaning, context, and analysis
    """
    try:
        # Get contextual information first if web research enabled
        context_info = None
        if use_web_research:
            try:
                context_info = research_classical_tamil_context(text)
            except Exception as e:
                print(f"Web research failed: {str(e)}")
                context_info = _fallback_classical_context()
        
        # Attempt AI translation first if enabled
        if use_ai:
            try:
                ai_result = translate_classical_tamil_with_ai(text, context_info, use_web_research)
                ai_result['translation_method'] = 'AI-powered'
                return ai_result
            except Exception as e:
                print(f"AI translation failed: {str(e)}. Falling back to context-based method.")
        
        # Use fallback method
        fallback_result = _fallback_meaning_based_translation(text, context_info)
        return fallback_result
        
    except Exception as e:
        print(f"Comprehensive translation error: {str(e)}")
        return {
            "original_text": text,
            "modernized_text": text,
            "meaning_explanation": "Translation system temporarily unavailable. This appears to be classical Tamil text.",
            "context_info": _fallback_classical_context(),
            "translation_method": "Emergency fallback",
            "changes_made": [],
            "confidence": 0.1,
            "literary_analysis": "Classical Tamil text requiring expert interpretation."
        }

def get_word_by_word_translation(text: str, context_info: dict = None) -> dict:
    """Get detailed word-by-word translation mapping with enhanced fallback"""
    try:
        prompt = f"""
        Analyze this classical Tamil text word by word and provide modern equivalents with meaning context:
        
        "{text}"
        
        For each classical/archaic word that needs modernization, provide:
        1. The modern equivalent word
        2. Brief meaning explanation for significant poetic terms
        
        Context: This appears to be classical Tamil poetry with traditional themes.
        
        Respond with JSON in this format:
        {{
            "word_mappings": {{
                "classical_word1": {{"modern": "modern_word1", "meaning": "explanation"}},
                "classical_word2": {{"modern": "modern_word2", "meaning": "explanation"}}
            }},
            "analysis": "Brief explanation of the translation approach and poetic context"
        }}
        """
        
        response = openai.chat.completions.create(
            model="gpt-5",
            messages=[
                {
                    "role": "system", 
                    "content": "You are a Tamil linguistics expert specializing in classical poetry analysis. Provide word-by-word mappings with meaning context. Respond only in valid JSON format."
                },
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.2
        )
        
        content = response.choices[0].message.content
        if not content:
            raise Exception("Empty response from OpenAI")
        
        ai_result = json.loads(content)
        
        return {
            "word_mappings": ai_result.get("word_mappings", {}),
            "analysis": ai_result.get("analysis", "AI word-by-word analysis of classical Tamil text."),
            "translation_method": "AI-powered word analysis"
        }
        
    except Exception as e:
        print(f"AI word mapping error: {str(e)}. Using fallback method.")
        return _fallback_word_mapping(text, context_info)

def _fallback_word_mapping(text: str, context_info: dict = None) -> dict:
    """Fallback word-by-word mapping using dictionary and context"""
    try:
        from tamil_dictionary import TAMIL_WORD_MAPPING
        
        words = text.split()
        word_mappings = {}
        mapped_count = 0
        
        for word in words:
            clean_word = word.strip('.,!?;:"()[]{}༭')
            
            if clean_word in TAMIL_WORD_MAPPING:
                modern_word = TAMIL_WORD_MAPPING[clean_word]
                if clean_word != modern_word:
                    word_mappings[clean_word] = {
                        "modern": modern_word,
                        "meaning": f"Classical word modernized for clarity"
                    }
                    mapped_count += 1
        
        # Add context-based analysis
        themes = context_info.get('themes', ['classical poetry']) if context_info else ['classical poetry']
        theme_text = ', '.join(themes[:2])
        
        analysis = f"Dictionary-based word mapping found {mapped_count} classical terms to modernize. Text appears to contain {theme_text} themes typical of classical Tamil literature."
        
        return {
            "word_mappings": word_mappings,
            "analysis": analysis,
            "translation_method": "Dictionary-based fallback"
        }
        
    except Exception as e:
        print(f"Fallback word mapping error: {str(e)}")
        return {
            "word_mappings": {},
            "analysis": "Word mapping service temporarily unavailable.",
            "translation_method": "Minimal fallback"
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

def _fallback_meaning_based_translation(text: str, context_info: dict = None) -> dict:
    """Provide intelligent fallback translation when OpenAI is unavailable
    
    This uses contextual analysis + enhanced dictionary to provide meaning-based translation
    """
    try:
        # Get context if not provided
        if context_info is None:
            context_info = research_classical_tamil_context(text)
        
        # Apply enhanced dictionary translation
        from tamil_dictionary import TAMIL_WORD_MAPPING
        words = text.split()
        modernized_words = []
        changes_made = []
        
        for word in words:
            clean_word = word.strip('.,!?;:"()[]{}༭')
            punctuation = word[len(clean_word):]
            
            if clean_word in TAMIL_WORD_MAPPING:
                modern_word = TAMIL_WORD_MAPPING[clean_word]
                modernized_words.append(modern_word + punctuation)
                if clean_word != modern_word:
                    changes_made.append(f"{clean_word} → {modern_word}")
            else:
                modernized_words.append(word)
        
        modernized_text = ' '.join(modernized_words)
        
        # Generate meaning explanation based on context
        meaning_explanation = _generate_contextual_meaning_explanation(text, context_info)
        
        # Generate literary analysis
        literary_analysis = _generate_basic_literary_analysis(text, context_info)
        
        return {
            "original_text": text,
            "modernized_text": modernized_text,
            "meaning_explanation": meaning_explanation,
            "context_info": context_info,
            "translation_method": "Context-based fallback",
            "changes_made": changes_made,
            "confidence": 0.6,  # Lower confidence for fallback method
            "literary_analysis": literary_analysis
        }
        
    except Exception as e:
        print(f"Fallback translation error: {str(e)}")
        return {
            "original_text": text,
            "modernized_text": text,
            "meaning_explanation": "This appears to be classical Tamil poetry. Translation service temporarily unavailable.",
            "context_info": context_info or _fallback_classical_context(),
            "translation_method": "Minimal fallback",
            "changes_made": [],
            "confidence": 0.3,
            "literary_analysis": "Classical Tamil text with traditional poetic elements."
        }

def _generate_contextual_meaning_explanation(text: str, context_info: dict) -> str:
    """Generate meaning explanation based on context analysis"""
    try:
        themes = context_info.get('themes', ['classical poetry'])
        period = context_info.get('period', 'Classical Tamil period')
        significance = context_info.get('literary_significance', '')
        
        # Analyze text characteristics
        text_length = len(text.split())
        
        if text_length <= 4:
            meaning_base = "This is a brief classical Tamil poetic phrase"
        elif text_length <= 10:
            meaning_base = "This appears to be a classical Tamil verse or couplet"
        else:
            meaning_base = "This is a substantial classical Tamil poetic composition"
        
        # Add thematic context
        if themes:
            theme_text = ', '.join(themes[:3])
            meaning_base += f" with themes related to {theme_text}"
        
        # Add historical context
        meaning_base += f" from the {period}."
        
        # Add significance if available
        if significance and len(significance) > 50:
            meaning_base += f" {significance[:200]}..."
        
        return meaning_base
        
    except Exception:
        return "This appears to be classical Tamil poetry with traditional linguistic patterns and cultural themes."

def _generate_basic_literary_analysis(text: str, context_info: dict) -> str:
    """Generate basic literary analysis based on text structure and context"""
    try:
        key_terms = extract_key_terms_from_tamil_text(text)
        themes = context_info.get('themes', [])
        
        analysis = "Classical Tamil poetry"
        
        # Add structural observations
        word_count = len(text.split())
        if word_count <= 8:
            analysis += " in concise verse form"
        elif word_count <= 20:
            analysis += " with moderate complexity"
        else:
            analysis += " with elaborate expression"
        
        # Add thematic elements
        if themes:
            analysis += f", featuring {', '.join(themes[:2])} themes"
        
        # Add linguistic observations
        if key_terms:
            analysis += ". Uses traditional Tamil poetic vocabulary"
        
        analysis += " with classical literary conventions."
        
        return analysis
        
    except Exception:
        return "Classical Tamil poetry with traditional elements and linguistic patterns."

def _fallback_classical_context() -> dict:
    """Provide fallback context information when web research is unavailable"""
    return {
        'context': 'Classical Tamil literature encompasses works from the Sangam period (3rd century BCE - 3rd century CE) through medieval times. These texts often feature sophisticated poetic devices, cultural themes, and linguistic complexity.',
        'period': 'Classical Tamil period (Sangam era to Medieval)',
        'themes': ['devotion', 'nature', 'love', 'heroism', 'philosophy', 'ethics'],
        'meaning': 'This text represents classical Tamil poetic tradition. The archaic language and structure suggest it may be from ancient Tamil literature, requiring specialized knowledge for complete interpretation.',
        'literary_significance': 'Tamil classical literature is among the world\'s oldest literary traditions, preserving cultural heritage, philosophical insights, and linguistic evolution over millennia. These works contribute significantly to understanding ancient South Indian civilization and Tamil cultural identity.'
    }