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
        # Process text with preprocessing and translation first
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
                    # Use comprehensive translation for better context
                    from openai_tamil_translator import get_comprehensive_translation
                    ai_result = get_comprehensive_translation(processed_text, use_ai=True, use_web_research=True)
                    processed_text = ai_result['modernized_text']
                    translation_changes = ai_result.get('changes_made', [])
                    confidence = ai_result.get('confidence', 0.0)
                    
                    # Store enhanced translation info in session state for display
                    st.session_state.ai_translation_info = ai_result
                    
                    if confidence < 0.7:
                        st.warning(f"AI translation confidence is {confidence:.1%}. Results may need review.")
            except Exception as e:
                st.error(f"AI translation failed: {str(e)}. Falling back to dictionary method.")
                processed_text = replace_old_tamil_words(processed_text)
                # Clear AI info if fallback used
                if 'ai_translation_info' in st.session_state:
                    del st.session_state.ai_translation_info
        elif selected_translation_mode == "both":
            # First apply dictionary, then AI
            processed_text = replace_old_tamil_words(processed_text)
            try:
                with st.spinner("Enhancing with AI translation..."):
                    # Use comprehensive translation for better context
                    from openai_tamil_translator import get_comprehensive_translation
                    ai_result = get_comprehensive_translation(processed_text, use_ai=True, use_web_research=True)
                    processed_text = ai_result['modernized_text']
                    translation_changes = ai_result.get('changes_made', [])
                    
                    # Store enhanced translation info for display
                    st.session_state.ai_translation_info = ai_result
            except Exception as e:
                st.warning(f"AI enhancement failed: {str(e)}. Using dictionary translation only.")
                # Clear AI info if enhancement failed
                if 'ai_translation_info' in st.session_state:
                    del st.session_state.ai_translation_info
        
        # True Side-by-Side Text Display
        st.header("📝 Text Comparison")
        
        # Create side-by-side columns for text display
        text_col1, text_col2 = st.columns(2)
        
        with text_col1:
            st.subheader("🎭 Original Classical Text")
            st.text_area(
                "Original Text", 
                value=tamil_text, 
                height=150, 
                disabled=True, 
                key="original_display", 
                label_visibility="collapsed"
            )
            st.caption(f"Length: {len(tamil_text.split())} words")
        
        with text_col2:
            if processed_text != tamil_text:
                processing_description = []
                if use_preprocessing:
                    processing_description.append("classical Tamil preprocessing")
                if selected_translation_mode in ["dictionary", "both"]:
                    processing_description.append("dictionary-based word replacements")
                if selected_translation_mode in ["ai", "both"]:
                    processing_description.append("AI-powered translation")
                
                description = " and ".join(processing_description)
                st.subheader(f"🆕 Modernized Text ({description})")
                st.text_area(
                    "Processed Text", 
                    value=processed_text, 
                    height=150, 
                    disabled=True, 
                    key="processed_display", 
                    label_visibility="collapsed"
                )
                st.caption(f"Length: {len(processed_text.split())} words")
            else:
                st.subheader("🆕 Modernized Text")
                st.info("No changes needed - text is already in modern form")
                st.text_area(
                    "Same as Original", 
                    value=processed_text, 
                    height=150, 
                    disabled=True, 
                    key="same_as_original", 
                    label_visibility="collapsed"
                )
                st.caption("Same as original text")
            
        # Show translation and processing information
        if processed_text != tamil_text:
            # Show AI translation changes and enhanced information
            if translation_changes and selected_translation_mode in ["ai", "both"]:
                st.success("🤖 AI Translation Changes:")
                for i, change in enumerate(translation_changes[:5], 1):  # Show max 5 changes
                    st.write(f"{i}. {change}")
                if len(translation_changes) > 5:
                    st.write(f"... and {len(translation_changes) - 5} more changes")
                
                # Show enhanced AI translation information
                if hasattr(st.session_state, 'ai_translation_info') and st.session_state.ai_translation_info:
                    ai_info = st.session_state.ai_translation_info
                    
                    # Translation method and confidence
                    translation_method = ai_info.get('translation_method', 'AI-powered')
                    confidence = ai_info.get('confidence', 0.0)
                    st.info(f"📊 Translation Method: {translation_method} (Confidence: {confidence:.1%})")
                    
                    # Meaning explanation
                    meaning_explanation = ai_info.get('meaning_explanation', '')
                    if meaning_explanation:
                        with st.expander("📖 Poetic Meaning & Interpretation", expanded=False):
                            st.markdown(meaning_explanation)
                    
                    # Literary analysis  
                    literary_analysis = ai_info.get('literary_analysis', '')
                    if literary_analysis:
                        with st.expander("📚 Literary Analysis", expanded=False):
                            st.markdown(literary_analysis)
                    
                    # Context information
                    context_info = ai_info.get('context_info', {})
                    if context_info and any(context_info.values()):
                        with st.expander("🏛️ Historical & Cultural Context", expanded=False):
                            if context_info.get('period'):
                                st.write(f"**Period:** {context_info['period']}")
                            if context_info.get('themes'):
                                themes = context_info['themes']
                                if isinstance(themes, list):
                                    st.write(f"**Themes:** {', '.join(themes)}")
                                else:
                                    st.write(f"**Themes:** {themes}")
                            if context_info.get('context'):
                                st.write(f"**Context:** {context_info['context']}")
                            if context_info.get('literary_significance'):
                                st.write(f"**Literary Significance:** {context_info['literary_significance']}")
            
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
        
        # Dual audio generation section
        st.header("🎵 Dual Voice Audio Generation")
        
        # Audio generation options
        st.subheader("Select Audio Versions to Generate:")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            generate_original = st.checkbox(
                "🎭 Original Classical Text", 
                value=True,
                help="Generate audio for the original classical Tamil text as-is"
            )
        
        with col2:
            generate_modern = st.checkbox(
                "🆕 Modern Translation", 
                value=True, 
                help="Generate audio for the modern meaning-based translation"
            )
        
        with col3:
            if processed_text != tamil_text:
                st.info("Both versions available")
            else:
                st.info("Only original text available")
                generate_modern = False  # Disable if no processing was done
        
        # Generate audio buttons
        if generate_original or generate_modern:
            col1, col2 = st.columns(2)
            
            # Generate original audio
            if generate_original:
                with col1:
                    if st.button("🔊 Generate Original Audio", type="primary"):
                        with st.spinner(f"Generating original audio using {tts_provider[1]}..."):
                            original_audio_bytes = text_to_speech_tamil(
                                tamil_text, 
                                provider=tts_provider[0], 
                                voice_accent=selected_accent, 
                                speech_speed=speech_speed
                            )
                            
                            if original_audio_bytes:
                                st.success(f"Original audio generated successfully!")
                                
                                # Store original audio in session state
                                st.session_state.original_audio_bytes = original_audio_bytes
                                st.session_state.original_audio_ready = True
                                st.session_state.tts_provider = tts_provider[1]
            
            # Generate modern audio (only if different from original)
            if generate_modern and processed_text != tamil_text:
                with col2:
                    if st.button("🔊 Generate Modern Audio", type="primary"):
                        with st.spinner(f"Generating modern translation audio using {tts_provider[1]}..."):
                            modern_audio_bytes = text_to_speech_tamil(
                                processed_text, 
                                provider=tts_provider[0], 
                                voice_accent=selected_accent, 
                                speech_speed=speech_speed
                            )
                            
                            if modern_audio_bytes:
                                st.success(f"Modern translation audio generated successfully!")
                                
                                # Store modern audio in session state
                                st.session_state.modern_audio_bytes = modern_audio_bytes
                                st.session_state.modern_audio_ready = True
                                st.session_state.tts_provider = tts_provider[1]
            
            # Generate both button (if both are selected)
            if generate_original and generate_modern and processed_text != tamil_text:
                st.markdown("---")
                if st.button("🔊🔊 Generate Both Audio Versions", type="secondary"):
                    with st.spinner(f"Generating both audio versions using {tts_provider[1]}..."):
                        # Generate original audio
                        original_audio_bytes = text_to_speech_tamil(
                            tamil_text, 
                            provider=tts_provider[0], 
                            voice_accent=selected_accent, 
                            speech_speed=speech_speed
                        )
                        
                        # Generate modern audio
                        modern_audio_bytes = text_to_speech_tamil(
                            processed_text, 
                            provider=tts_provider[0], 
                            voice_accent=selected_accent, 
                            speech_speed=speech_speed
                        )
                        
                        if original_audio_bytes and modern_audio_bytes:
                            st.success(f"Both audio versions generated successfully!")
                            
                            # Store both audio versions in session state
                            st.session_state.original_audio_bytes = original_audio_bytes
                            st.session_state.original_audio_ready = True
                            st.session_state.modern_audio_bytes = modern_audio_bytes
                            st.session_state.modern_audio_ready = True
                            st.session_state.tts_provider = tts_provider[1]
                        elif original_audio_bytes:
                            st.warning("Original audio generated, but modern audio failed")
                            st.session_state.original_audio_bytes = original_audio_bytes
                            st.session_state.original_audio_ready = True
                            st.session_state.tts_provider = tts_provider[1]
                        elif modern_audio_bytes:
                            st.warning("Modern audio generated, but original audio failed")
                            st.session_state.modern_audio_bytes = modern_audio_bytes
                            st.session_state.modern_audio_ready = True
                            st.session_state.tts_provider = tts_provider[1]
        
        # Unified Dual Voice Audio Playback Section
        st.header("🎵 Dual Voice Audio Playback")
        
        # Check which audio files are available
        has_original = hasattr(st.session_state, 'original_audio_ready') and st.session_state.original_audio_ready
        has_modern = hasattr(st.session_state, 'modern_audio_ready') and st.session_state.modern_audio_ready
        
        if has_original or has_modern:
            st.info("🎧 Compare pronunciation and clarity between classical and modern versions")
            
            # Create side-by-side audio player columns
            audio_col1, audio_col2 = st.columns(2)
            
            # Original Classical Audio Column
            with audio_col1:
                st.subheader("🎭 Original Classical Tamil")
                if has_original:
                    st.audio(st.session_state.original_audio_bytes, format='audio/mp3')
                    
                    # Download and info section
                    original_size = len(st.session_state.original_audio_bytes)
                    st.caption(f"📊 File size: {original_size / 1024:.1f} KB")
                    
                    original_filename = "classical_tamil_original.mp3"
                    st.download_button(
                        label="📥 Download Original",
                        data=st.session_state.original_audio_bytes,
                        file_name=original_filename,
                        mime="audio/mp3",
                        key="download_original"
                    )
                    
                    # Show provider info if available
                    if hasattr(st.session_state, 'tts_provider'):
                        st.caption(f"🔊 Generated using: {st.session_state.tts_provider}")
                else:
                    st.info("🎭 Original audio not generated yet")
                    st.caption("Click 'Generate Original Audio' above to create this version")
            
            # Modern Translation Audio Column
            with audio_col2:
                st.subheader("🆕 Modern Translation")
                if has_modern:
                    st.audio(st.session_state.modern_audio_bytes, format='audio/mp3')
                    
                    # Download and info section
                    modern_size = len(st.session_state.modern_audio_bytes)
                    st.caption(f"📊 File size: {modern_size / 1024:.1f} KB")
                    
                    modern_filename = "tamil_modern_translation.mp3"
                    st.download_button(
                        label="📥 Download Modern",
                        data=st.session_state.modern_audio_bytes,
                        file_name=modern_filename,
                        mime="audio/mp3",
                        key="download_modern"
                    )
                    
                    # Show provider info if available
                    if hasattr(st.session_state, 'tts_provider'):
                        st.caption(f"🔊 Generated using: {st.session_state.tts_provider}")
                else:
                    if processed_text != tamil_text:
                        st.info("🆕 Modern audio not generated yet")
                        st.caption("Click 'Generate Modern Audio' above to create this version")
                    else:
                        st.info("🔄 Same as original")
                        st.caption("No modernization was applied to the text")
            
            # Show comparison tips if both are available
            if has_original and has_modern:
                st.success("✅ Both audio versions ready! Use the players above to compare pronunciation and clarity.")
                
                # Add some comparison insights
                if hasattr(st.session_state, 'ai_translation_info') and st.session_state.ai_translation_info:
                    ai_info = st.session_state.ai_translation_info
                    confidence = ai_info.get('confidence', 0.0)
                    if confidence > 0.8:
                        st.info(f"💡 High-confidence translation ({confidence:.1%}) - notice the improved clarity in the modern version")
                    elif confidence > 0.6:
                        st.warning(f"⚠️ Moderate-confidence translation ({confidence:.1%}) - compare carefully for accuracy")
        else:
            # No audio generated yet - show helpful message
            st.info("🎵 Select audio versions above and click generate to create audio files")
            
            # Show preview of what will be available
            preview_col1, preview_col2 = st.columns(2)
            
            with preview_col1:
                st.subheader("🎭 Original Classical Tamil")
                st.caption("Will contain the original text as-is")
                st.text_area(
                    "Preview", 
                    value=tamil_text[:100] + "..." if len(tamil_text) > 100 else tamil_text,
                    height=80,
                    disabled=True,
                    key="preview_original",
                    label_visibility="collapsed"
                )
            
            with preview_col2:
                st.subheader("🆕 Modern Translation")
                if processed_text != tamil_text:
                    st.caption("Will contain the modernized translation")
                    st.text_area(
                        "Preview", 
                        value=processed_text[:100] + "..." if len(processed_text) > 100 else processed_text,
                        height=80,
                        disabled=True,
                        key="preview_modern",
                        label_visibility="collapsed"
                    )
                else:
                    st.caption("Same as original - no modernization applied")
                    st.info("No changes were made to the text")
    
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
