"""Central configuration. To add a language, add one line to LANGUAGES."""

APP_TITLE = "AI-Based Speech-to-Text Transcription System"

# Display name -> Google Web Speech API language code (BCP-47)
LANGUAGES = {
    "English": "en-US",
    "Tamil": "ta-IN",
    # "Hindi": "hi-IN",
}

SUPPORTED_FORMATS = ["wav", "mp3", "m4a", "flac"]
MAX_FILE_MB = 100
CHUNK_SECONDS = 25          # Google's free API works best on short clips
SAMPLE_RATE = 16000         # 16 kHz mono is the standard for speech recognition
SILENCE_DBFS = -55          # chunks quieter than this are treated as silence
