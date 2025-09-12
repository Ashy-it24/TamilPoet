import streamlit as st
import io
import os
from gtts import gTTS
import base64
from tamil_dictionary import TAMIL_WORD_MAPPING

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

def text_to_speech_tamil(text, voice_accent='com', speech_speed=False):
    """Convert Tamil text to speech using gTTS and return audio bytes"""
    try:
        # Create gTTS object for Tamil with voice options
        tts = gTTS(text=text, lang='ta', slow=speech_speed, tld=voice_accent)
        
        # Save to bytes buffer
        audio_buffer = io.BytesIO()
        tts.write_to_fp(audio_buffer)
        audio_buffer.seek(0)
        
        return audio_buffer.getvalue()
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
        use_modern_words = st.checkbox(
            "Replace old Tamil words with modern equivalents",
            value=True,
            help="This will replace archaic Tamil words with their modern counterparts for better pronunciation"
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
        
        # Extract the domain value from the selected tuple
        selected_accent = voice_accent[0]
    
    if tamil_text.strip():
        # Show original text
        st.subheader("Original Text:")
        st.text_area("Original Text", value=tamil_text, height=100, disabled=True, key="original", label_visibility="collapsed")
        
        # Process text with preprocessing and word replacement
        processed_text = tamil_text
        
        # Apply advanced preprocessing if enabled
        if use_preprocessing:
            processed_text = preprocess_classical_tamil(processed_text)
        
        # Apply word replacement if enabled
        if use_modern_words:
            processed_text = replace_old_tamil_words(processed_text)
        
        # Show processed text if different from original
        if processed_text != tamil_text:
            processing_description = []
            if use_preprocessing:
                processing_description.append("classical Tamil preprocessing")
            if use_modern_words:
                processing_description.append("modern word replacements")
            
            description = " and ".join(processing_description)
            st.subheader(f"Processed Text (with {description}):")
            st.text_area("Processed Text", value=processed_text, height=100, disabled=True, key="processed", label_visibility="collapsed")
            
            # Show word replacements made (if enabled)
            if use_modern_words:
                original_words = set(tamil_text.split())
                
                replacements_made = []
                for orig_word in original_words:
                    clean_orig = orig_word.strip('.,!?;:"()[]{}')
                    if clean_orig in TAMIL_WORD_MAPPING:
                        replacements_made.append(f"{clean_orig} → {TAMIL_WORD_MAPPING[clean_orig]}")
                
                if replacements_made:
                    st.info(f"Word replacements made: {', '.join(replacements_made)}")
            
            # Show preprocessing changes (if enabled and no word replacements to avoid redundancy)
            if use_preprocessing and not use_modern_words:
                st.info("Text normalized for better TTS pronunciation (sandhi resolution, phonetic adjustments)")
        elif use_preprocessing or use_modern_words:
            # Show info even if text didn't change to indicate processing was attempted
            processing_types = []
            if use_preprocessing:
                processing_types.append("classical Tamil preprocessing")
            if use_modern_words:
                processing_types.append("modern word replacement")
            
            st.info(f"Text processing enabled ({', '.join(processing_types)}) but no changes were needed for this text.")
        
        # Audio generation section
        st.header("🎵 Audio Generation")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            if st.button("🔊 Generate Audio", type="primary"):
                with st.spinner("Generating audio... Please wait..."):
                    audio_bytes = text_to_speech_tamil(processed_text, selected_accent, speech_speed)
                    
                    if audio_bytes:
                        st.success("Audio generated successfully!")
                        
                        # Store audio in session state
                        st.session_state.audio_bytes = audio_bytes
                        st.session_state.audio_ready = True
        
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
