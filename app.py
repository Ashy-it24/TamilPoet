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

def text_to_speech_tamil(text):
    """Convert Tamil text to speech using gTTS and return audio bytes"""
    try:
        # Create gTTS object for Tamil
        tts = gTTS(text=text, lang='ta', slow=False)
        
        # Save to bytes buffer
        audio_buffer = io.BytesIO()
        tts.write_to_fp(audio_buffer)
        audio_buffer.seek(0)
        
        return audio_buffer.getvalue()
    except Exception as e:
        st.error(f"Error generating speech: {str(e)}")
        return None

def create_download_link(audio_bytes, filename):
    """Create a download link for the audio file"""
    b64 = base64.b64encode(audio_bytes).decode()
    href = f'<a href="data:audio/mp3;base64,{b64}" download="{filename}">Download MP3</a>'
    return href

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
    
    # Word replacement option
    st.header("🔄 Text Processing Options")
    use_modern_words = st.checkbox(
        "Replace old Tamil words with modern equivalents",
        value=True,
        help="This will replace archaic Tamil words with their modern counterparts for better pronunciation"
    )
    
    if tamil_text.strip():
        # Show original text
        st.subheader("Original Text:")
        st.text_area("", value=tamil_text, height=100, disabled=True, key="original")
        
        # Process text if word replacement is enabled
        processed_text = tamil_text
        if use_modern_words:
            processed_text = replace_old_tamil_words(tamil_text)
            
            # Show processed text if different from original
            if processed_text != tamil_text:
                st.subheader("Processed Text (with modern word replacements):")
                st.text_area("", value=processed_text, height=100, disabled=True, key="processed")
                
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
                    audio_bytes = text_to_speech_tamil(processed_text)
                    
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
            download_link = create_download_link(st.session_state.audio_bytes, filename)
            st.markdown(download_link, unsafe_allow_html=True)
            
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
