import streamlit as st
import io
import os
from gtts import gTTS
import base64
from tamil_dictionary import TAMIL_WORD_MAPPING

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
        
        # Process text if word replacement is enabled
        processed_text = tamil_text
        if use_modern_words:
            processed_text = replace_old_tamil_words(tamil_text)
            
            # Show processed text if different from original
            if processed_text != tamil_text:
                st.subheader("Processed Text (with modern word replacements):")
                st.text_area("Processed Text", value=processed_text, height=100, disabled=True, key="processed", label_visibility="collapsed")
                
                # Show word replacements made
                original_words = set(tamil_text.split())
                processed_words = set(processed_text.split())
                
                replacements_made = []
                for orig_word in original_words:
                    clean_orig = orig_word.strip('.,!?;:"()[]{}')
                    if clean_orig in TAMIL_WORD_MAPPING:
                        replacements_made.append(f"{clean_orig} → {TAMIL_WORD_MAPPING[clean_orig]}")
                
                if replacements_made:
                    st.info(f"Word replacements made: {', '.join(replacements_made)}")
        
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
