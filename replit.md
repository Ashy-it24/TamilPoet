# Overview

This is a Tamil Poetry Text-to-Speech Converter built with Streamlit. The application converts Tamil Unicode poetry text to MP3 audio with voice narration, specifically designed to handle classical Tamil poetry by modernizing archaic words for better text-to-speech pronunciation and comprehension.

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Frontend Architecture
- **Framework**: Streamlit web application framework
- **User Interface**: Simple web-based interface for text input and audio generation
- **File Handling**: In-browser audio playback and MP3 download functionality

## Backend Architecture
- **Core Logic**: Python-based text processing and audio generation
- **Text Processing**: Dictionary-based word replacement system for modernizing classical Tamil words
- **Audio Generation**: Google Text-to-Speech (gTTS) integration for Tamil language synthesis
- **Data Structure**: Dictionary mapping system for word translations stored in separate module

## Text Processing Pipeline
1. **Input Sanitization**: Removes punctuation while preserving word structure
2. **Dictionary Lookup**: Maps classical/archaic Tamil words to modern equivalents
3. **Text Reconstruction**: Rebuilds text with modern words while maintaining original punctuation
4. **Audio Synthesis**: Converts processed text to speech using Tamil language models

## Audio Processing
- **Text-to-Speech Engine**: Google Text-to-Speech (gTTS) with Tamil language support
- **Audio Format**: MP3 output format
- **Memory Management**: Uses BytesIO buffer for in-memory audio processing
- **Delivery Methods**: Both streaming playback and downloadable file generation

# External Dependencies

## Core Libraries
- **streamlit**: Web application framework for user interface
- **gtts**: Google Text-to-Speech API for Tamil audio synthesis
- **io**: Standard library for in-memory file operations
- **base64**: Standard library for audio file encoding/download links

## Language Processing
- **Custom Dictionary**: Internal Tamil word mapping system for classical-to-modern word conversion
- **Unicode Support**: Full Tamil Unicode text processing capabilities

## Third-party Services
- **Google Text-to-Speech API**: External service dependency for audio generation
- **Internet Connection**: Required for gTTS API calls

## File System
- **Memory-based Processing**: No persistent file storage, all operations in memory
- **Temporary Audio Generation**: Audio files created dynamically without disk storage