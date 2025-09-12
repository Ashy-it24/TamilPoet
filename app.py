import streamlit as st
import io
import os
from gtts import gTTS
import base64
from tamil_dictionary import TAMIL_WORD_MAPPING
from openai_tamil_translator import translate_classical_tamil_with_ai, get_word_by_word_translation
from premium_tts_service import PremiumTTSService

def preprocess_classical_tamil(text):
    """Advanced preprocessing for classical Tamil texts to improve TTS pronunciation"""
    import re
    
    # Remove or normalize various Tamil script variations
    text = text.replace('்', '்')  # Normalize virama
    
    # Handle sandhi (euphonic combinations) - basic cases
    # Replace common classical combinations with space-separated words
    sandhi_patterns = {
        r'தல்லும்': 'தான் அல்லும்',
        r'கண்டும்': 'கண்டு உம்',
        r'செய்தும்': 'செய்து உம்',
        r'வந்தும்': 'வந்து உம்',
        r'போனும்': 'போன உம்',
    }
    
    for pattern, replacement in sandhi_patterns.items():
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    
    # Handle classical Tamil phonetic variations
    phonetic_normalizations = {
        r'ழ்': 'ள்',  # Simplify retroflex for TTS
        r'ற்ற': 'ட்ட',  # Common sound changes
        r'ன்ன': 'ண்ண',  # Nasal variations
    }
    
    for pattern, replacement in phonetic_normalizations.items():
        text = re.sub(pattern, replacement, text)
    
    # Handle classical verb endings - convert to modern forms
    classical_verb_patterns = {
        r'(\w+)ுமே$': r'\1ும்',  # -ume to -um
        r'(\w+)வே$': r'\1வது',   # -ve to -vadhu
        r'(\w+)தே$': r'\1ததே',   # -the to -thathe
    }
    
    words = text.split()
    normalized_words = []
    
    for word in words:
        original_word = word
        # Apply classical verb patterns
        for pattern, replacement in classical_verb_patterns.items():
            word = re.sub(pattern, replacement, word)
        
        normalized_words.append(word)
    
    return ' '.join(normalized_words)

def replace_old_tamil_words(text):
    """Replace old Tamil words with modern equivalents using dictionary mapping"""
    words = text.split()
    replaced_words = []
    
    for word in words:
        # Remove punctuation for matching
        clean_word = word.strip('.,!?;:"()[]{}')
        punctuation = word[len(clean_word):]
        
        # Check if word exists in mapping dictionary
        if clean_word in TAMIL_WORD_MAPPING:
            replaced_words.append(TAMIL_WORD_MAPPING[clean_word] + punctuation)
        else:
            replaced_words.append(word)
    
    return ' '.join(replaced_words)

def text_to_speech_tamil(text, provider='gtts', voice_accent='com', speech_speed=False):
    """Convert Tamil text to speech using premium TTS services"""
    try:
        tts_service = PremiumTTSService()
        
        if provider == 'gtts':
            audio_bytes = tts_service.generate_speech(
                text, 
                provider='gtts', 
                voice_accent=voice_accent, 
                slow=speech_speed
            )
        elif provider == 'elevenlabs':
            audio_bytes = tts_service.generate_speech(text, provider='elevenlabs')
        elif provider == 'google_cloud':
            audio_bytes = tts_service.generate_speech(text, provider='google_cloud')
        elif provider == 'azure':
            audio_bytes = tts_service.generate_speech(text, provider='azure')
        else:
            # Fallback to gTTS
            audio_bytes = tts_service.generate_speech(
                text, 
                provider='gtts', 
                voice_accent=voice_accent, 
                slow=speech_speed
            )
        
        return audio_bytes
        
    except Exception as e:
        st.error(f"Error generating speech: {str(e)}")
        return None


def main():
    st.title("Tamil Poetry Text-to-Speech Converter")
    st.markdown("Convert Tamil Unicode poetry text to MP3 audio with voice narration")
    
    # Text input section
    st.header("📝 Enter Tamil Poetry Text")
    tamil_text = st.text_area(
        "Paste your Tamil Unicode poetry text here:",
        height=200,
        placeholder="உங்கள் தமிழ் கவிதை உரையை இங்கே பேஸ்ట் செய்யவும்..."
    )
    
    # Text processing and voice options
    st.header("🔄 Text Processing & Voice Options")
    
    col1, col2 = st.columns(2)
    
    with col1:
        translation_mode = st.selectbox(
            "Translation Method",
            options=[
                ("dictionary", "Dictionary-based (Fast)"),
                ("ai", "AI-powered (Advanced)"),
                ("both", "Both Dictionary + AI")
            ],
            format_func=lambda x: x[1],
            help="Choose how to modernize classical Tamil words"
        )
        
        use_preprocessing = st.checkbox(
            "Advanced classical Tamil preprocessing",
            value=True,
            help="Normalize classical Tamil script, handle sandhi, and improve phonetic representation for TTS"
        )
        
        speech_speed = st.checkbox(
            "Slow speech for better clarity",
            value=False,
            help="Enable for slower, more deliberate pronunciation"
        )
    
    with col2:
        tts_provider = st.selectbox(
            "TTS Provider",
            options=[
                ("gtts", "Google TTS (Free)"),
                ("elevenlabs", "ElevenLabs (Premium)"),
                ("google_cloud", "Google Cloud (Professional)"),
                ("azure", "Microsoft Azure (Professional)")
            ],
            format_func=lambda x: x[1],
            help="Choose text-to-speech quality level. Premium services require API keys."
        )
        
        # Show accent options only for gTTS
        if tts_provider[0] == 'gtts':
            voice_accent = st.selectbox(
                "Voice Accent Region",
                options=[
                    ("com", "Global (Default)"),
                    ("co.in", "India"),
                    ("com.au", "Australia"),
                    ("co.uk", "United Kingdom"),
                    ("com.sg", "Singapore")
                ],
                format_func=lambda x: x[1],
                help="Different Google domains may provide slight accent variations"
            )
            selected_accent = voice_accent[0]
        else:
            selected_accent = 'com'
    
    if tamil_text.strip():
        # Show original text
        st.subheader("Original Text:")
        st.text_area("Original Text", value=tamil_text, height=100, disabled=True, key="original", label_visibility="collapsed")
        
        # Process text with preprocessing and translation
        processed_text = tamil_text
        translation_changes = []
        
        # Apply advanced preprocessing if enabled
        if use_preprocessing:
            processed_text = preprocess_classical_tamil(processed_text)
        
        # Apply translation based on selected method
        selected_translation_mode = translation_mode[0]
        
        if selected_translation_mode == "dictionary":
            processed_text = replace_old_tamil_words(processed_text)
        elif selected_translation_mode == "ai":
            try:
                with st.spinner("AI is analyzing and modernizing your classical Tamil text..."):
                    ai_result = translate_classical_tamil_with_ai(processed_text)
                    processed_text = ai_result['modernized_text']
                    translation_changes = ai_result.get('changes_made', [])
                    confidence = ai_result.get('confidence', 0.0)
                    
                    if confidence < 0.7:
                        st.warning(f"AI translation confidence is {confidence:.1%}. Results may need review.")
            except Exception as e:
                st.error(f"AI translation failed: {str(e)}. Falling back to dictionary method.")
                processed_text = replace_old_tamil_words(processed_text)
        elif selected_translation_mode == "both":
            # First apply dictionary, then AI
            processed_text = replace_old_tamil_words(processed_text)
            try:
                with st.spinner("Enhancing with AI translation..."):
                    ai_result = translate_classical_tamil_with_ai(processed_text)
                    processed_text = ai_result['modernized_text']
                    translation_changes = ai_result.get('changes_made', [])
            except Exception as e:
                st.warning(f"AI enhancement failed: {str(e)}. Using dictionary translation only.")
        
        # Show processed text if different from original
        if processed_text != tamil_text:
            processing_description = []
            if use_preprocessing:
                processing_description.append("classical Tamil preprocessing")
            if selected_translation_mode in ["dictionary", "both"]:
                processing_description.append("dictionary-based word replacements")
            if selected_translation_mode in ["ai", "both"]:
                processing_description.append("AI-powered translation")
            
            description = " and ".join(processing_description)
            st.subheader(f"Processed Text (with {description}):")
            st.text_area("Processed Text", value=processed_text, height=100, disabled=True, key="processed", label_visibility="collapsed")
            
            # Show AI translation changes
            if translation_changes and selected_translation_mode in ["ai", "both"]:
                st.success("🤖 AI Translation Changes:")
                for i, change in enumerate(translation_changes[:5], 1):  # Show max 5 changes
                    st.write(f"{i}. {change}")
                if len(translation_changes) > 5:
                    st.write(f"... and {len(translation_changes) - 5} more changes")
            
            # Show dictionary replacements made (if enabled)
            elif selected_translation_mode == "dictionary":
                original_words = set(tamil_text.split())
                replacements_made = []
                for orig_word in original_words:
                    clean_orig = orig_word.strip('.,!?;:"()[]{}')
                    if clean_orig in TAMIL_WORD_MAPPING:
                        replacements_made.append(f"{clean_orig} → {TAMIL_WORD_MAPPING[clean_orig]}")
                
                if replacements_made:
                    st.info(f"📖 Dictionary replacements: {', '.join(replacements_made)}")
            
            # Show preprocessing changes (if enabled)
            if use_preprocessing and selected_translation_mode not in ["dictionary", "ai", "both"]:
                st.info("Text normalized for better TTS pronunciation (sandhi resolution, phonetic adjustments)")
        else:
            # Show info even if text didn't change
            processing_types = []
            if use_preprocessing:
                processing_types.append("classical Tamil preprocessing")
            processing_types.append(f"{translation_mode[1].lower()}")
            
            st.info(f"Text processing enabled ({', '.join(processing_types)}) but no changes were needed for this text.")
        
        # Audio generation section
        st.header("🎵 Audio Generation")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            if st.button("🔊 Generate Audio", type="primary"):
                with st.spinner(f"Generating audio using {tts_provider[1]}... Please wait..."):
                    audio_bytes = text_to_speech_tamil(
                        processed_text, 
                        provider=tts_provider[0], 
                        voice_accent=selected_accent, 
                        speech_speed=speech_speed
                    )
                    
                    if audio_bytes:
                        st.success(f"Audio generated successfully with {tts_provider[1]}!")
                        
                        # Store audio in session state
                        st.session_state.audio_bytes = audio_bytes
                        st.session_state.audio_ready = True
                        st.session_state.tts_provider = tts_provider[1]
        
        # Audio playback and download section
        if hasattr(st.session_state, 'audio_ready') and st.session_state.audio_ready:
            st.header("🎧 Audio Playback & Download")
            
            # Audio player
            st.audio(st.session_state.audio_bytes, format='audio/mp3')
            
            # Download button
            filename = "tamil_poetry_audio.mp3"
            st.download_button(
                label="📥 Download MP3",
                data=st.session_state.audio_bytes,
                file_name=filename,
                mime="audio/mp3"
            )
            
            # File info
            audio_size = len(st.session_state.audio_bytes)
            st.info(f"Audio file size: {audio_size / 1024:.1f} KB")
    
    else:
        st.info("👆 Please enter Tamil text above to generate audio")
    
    # Instructions section
    with st.expander("ℹ️ How to use this app"):
        st.markdown("""
        1. **Enter Text**: Paste your Tamil Unicode poetry text in the text area above
        2. **Word Processing**: Enable modern word replacement to convert archaic Tamil words
        3. **Generate Audio**: Click the 'Generate Audio' button to create MP3 audio
        4. **Play & Download**: Use the audio player to listen and download the MP3 file
        
        **Supported Features:**
        - Tamil Unicode text input
        - Old Tamil to modern Tamil word conversion
        - High-quality text-to-speech using Google's TTS
        - MP3 audio generation and download
        - Built-in audio player
        """)
    
    # Technical info
    with st.expander("🔧 Technical Information"):
        st.markdown("""
        - **Text-to-Speech Engine**: Google Text-to-Speech (gTTS)
        - **Language**: Tamil (ta)
        - **Audio Format**: MP3
        - **Word Replacement**: Custom dictionary mapping for old Tamil words
        """)

if __name__ == "__main__":
    main()
