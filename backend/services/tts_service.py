from gtts import gTTS
import io
import base64

def generate_audio(text: str) -> str:
    """
    Converts text to MP3 audio and returns it as a Base64 string.
    """
    try:
        # Create an in-memory byte stream
        mp3_fp = io.BytesIO()
        
        # Generate speech (lang='en' is English)
        tts = gTTS(text=text, lang='en', slow=False)
        
        # Write to the memory stream
        tts.write_to_fp(mp3_fp)
        
        # Reset stream position to the beginning
        mp3_fp.seek(0)
        
        # Encode bytes to Base64 string
        audio_base64 = base64.b64encode(mp3_fp.read()).decode('utf-8')
        
        return audio_base64
    except Exception as e:
        print(f"TTS Error: {e}")
        return None