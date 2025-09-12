"""
OpenAI-powered Tamil word translator for classical to modern Tamil conversion
"""
import json
import os
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