"""
Premium TTS service supporting multiple high-quality providers for Tamil
"""
import io
import os
import requests
import json
from gtts import gTTS
from typing import Optional, Dict, Any

class PremiumTTSService:
    """High-quality TTS service with multiple provider support"""
    
    def __init__(self):
        self.providers = {
            'gtts': self._gtts_generate,
            'elevenlabs': self._elevenlabs_generate,
            'google_cloud': self._google_cloud_generate,
            'azure': self._azure_generate
        }
    
    def generate_speech(self, text: str, provider: str = 'gtts', **kwargs) -> Optional[bytes]:
        """Generate speech using specified provider"""
        if provider not in self.providers:
            raise ValueError(f"Provider {provider} not supported")
        
        try:
            return self.providers[provider](text, **kwargs)
        except Exception as e:
            print(f"TTS generation failed for {provider}: {str(e)}")
            # Fallback to gTTS
            if provider != 'gtts':
                return self._gtts_generate(text, **kwargs)
            return None
    
    def _gtts_generate(self, text: str, voice_accent: str = 'com', slow: bool = False, **kwargs) -> Optional[bytes]:
        """Generate using Google Text-to-Speech (gTTS)"""
        try:
            tts = gTTS(text=text, lang='ta', slow=slow, tld=voice_accent)
            audio_buffer = io.BytesIO()
            tts.write_to_fp(audio_buffer)
            audio_buffer.seek(0)
            return audio_buffer.getvalue()
        except Exception as e:
            print(f"gTTS error: {str(e)}")
            return None
    
    def _elevenlabs_generate(self, text: str, voice_id: str = None, **kwargs) -> Optional[bytes]:
        """Generate using ElevenLabs API (premium quality)"""
        api_key = os.getenv('ELEVENLABS_API_KEY')
        if not api_key:
            return self._gtts_generate(text, voice_accent='com', slow=False, **kwargs)  # Fallback to gTTS
        
        # Use a Tamil-suitable voice or multilingual voice
        default_voice_id = "pNInz6obpgDQGcFmaJgB"  # Adam (multilingual)
        voice_id = voice_id or default_voice_id
        
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
        
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": api_key
        }
        
        data = {
            "text": text,
            "model_id": "eleven_multilingual_v2",
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.75,
                "style": 0.0,
                "use_speaker_boost": True
            }
        }
        
        try:
            response = requests.post(url, json=data, headers=headers, timeout=30)
            if response.status_code == 200:
                return response.content
            else:
                print(f"ElevenLabs API error: {response.status_code}")
                return self._gtts_generate(text, voice_accent='com', slow=False, **kwargs)  # Fallback
        except Exception as e:
            print(f"ElevenLabs request error: {str(e)}")
            return self._gtts_generate(text, voice_accent='com', slow=False, **kwargs)  # Fallback
    
    def _google_cloud_generate(self, text: str, voice_name: str = None, **kwargs) -> Optional[bytes]:
        """Generate using Google Cloud Text-to-Speech API"""
        api_key = os.getenv('GOOGLE_CLOUD_API_KEY')
        if not api_key:
            return self._gtts_generate(text, voice_accent='com', slow=False, **kwargs)  # Fallback
        
        url = f"https://texttospeech.googleapis.com/v1/text:synthesize?key={api_key}"
        
        # Tamil voice configuration
        voice_config = {
            "languageCode": "ta-IN",
            "name": voice_name or "ta-IN-Standard-A",
            "ssmlGender": "FEMALE"
        }
        
        audio_config = {
            "audioEncoding": "MP3",
            "sampleRateHertz": 24000
        }
        
        data = {
            "input": {"text": text},
            "voice": voice_config,
            "audioConfig": audio_config
        }
        
        headers = {"Content-Type": "application/json"}
        
        try:
            response = requests.post(url, json=data, headers=headers, timeout=30)
            if response.status_code == 200:
                result = response.json()
                import base64
                return base64.b64decode(result['audioContent'])
            else:
                print(f"Google Cloud TTS error: {response.status_code}")
                return self._gtts_generate(text, voice_accent='com', slow=False, **kwargs)  # Fallback
        except Exception as e:
            print(f"Google Cloud TTS request error: {str(e)}")
            return self._gtts_generate(text, voice_accent='com', slow=False, **kwargs)  # Fallback
    
    def _azure_generate(self, text: str, voice_name: str = None, **kwargs) -> Optional[bytes]:
        """Generate using Azure Speech Services"""
        subscription_key = os.getenv('AZURE_SPEECH_KEY')
        region = os.getenv('AZURE_SPEECH_REGION', 'eastus')
        
        if not subscription_key:
            return self._gtts_generate(text, voice_accent='com', slow=False, **kwargs)  # Fallback
        
        # Get access token
        token_url = f"https://{region}.api.cognitive.microsoft.com/sts/v1.0/issuetoken"
        token_headers = {"Ocp-Apim-Subscription-Key": subscription_key}
        
        try:
            token_response = requests.post(token_url, headers=token_headers, timeout=10)
            access_token = token_response.text
            
            # Synthesize speech
            tts_url = f"https://{region}.tts.speech.microsoft.com/cognitiveservices/v1"
            
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/ssml+xml",
                "X-Microsoft-OutputFormat": "audio-16khz-128kbitrate-mono-mp3"
            }
            
            # SSML for Tamil
            voice_name = voice_name or "ta-IN-PallaviNeural"
            ssml = f"""
            <speak version='1.0' xml:lang='ta-IN'>
                <voice name='{voice_name}'>
                    {text}
                </voice>
            </speak>
            """
            
            response = requests.post(tts_url, headers=headers, data=ssml.encode('utf-8'), timeout=30)
            
            if response.status_code == 200:
                return response.content
            else:
                print(f"Azure TTS error: {response.status_code}")
                return self._gtts_generate(text, voice_accent='com', slow=False, **kwargs)  # Fallback
                
        except Exception as e:
            print(f"Azure TTS request error: {str(e)}")
            return self._gtts_generate(text, voice_accent='com', slow=False, **kwargs)  # Fallback
    
    def get_available_providers(self) -> Dict[str, Dict[str, Any]]:
        """Get available TTS providers with their capabilities"""
        return {
            'gtts': {
                'name': 'Google Text-to-Speech (Free)',
                'quality': 'Good',
                'requires_api_key': False,
                'languages': ['Tamil'],
                'features': ['Multiple accents', 'Speed control']
            },
            'elevenlabs': {
                'name': 'ElevenLabs (Premium)',
                'quality': 'Excellent',
                'requires_api_key': True,
                'languages': ['Tamil (Multilingual)'],
                'features': ['AI voices', 'Emotion control', 'High quality']
            },
            'google_cloud': {
                'name': 'Google Cloud TTS (Professional)',
                'quality': 'Excellent',
                'requires_api_key': True,
                'languages': ['Tamil (ta-IN)'],
                'features': ['Neural voices', 'SSML support', 'Multiple voices']
            },
            'azure': {
                'name': 'Microsoft Azure Speech (Professional)',
                'quality': 'Excellent',
                'requires_api_key': True,
                'languages': ['Tamil (ta-IN)'],
                'features': ['Neural voices', 'SSML support', 'Custom voices']
            }
        }