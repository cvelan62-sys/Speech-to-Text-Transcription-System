# 🎙️ AI-Based Speech-to-Text Transcription System

Audio Input → Audio Processing → Speech Recognition → Text Processing → Transcription → Editing → Export

## Setup (Windows)
1. Install Python 3.9+ and **FFmpeg** (needed for MP3/M4A/FLAC): `winget install Gyan.FFmpeg`, then reopen the terminal. Check with `ffmpeg -version`. WAV works without it.
2. In this folder:
```
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```
(macOS/Linux: `source venv/bin/activate`; FFmpeg via `brew install ffmpeg` / `sudo apt install ffmpeg`.)

## Design decisions
- **No PyAudio.** PyAudio often fails to install on Windows and can only reach the server's microphone. `st.audio_input` records in the browser, so it works on any machine with no extra install.
- **Google Web Speech API** (via SpeechRecognition) supports English and Tamil with no API key, but needs internet.
- Audio is converted to 16 kHz mono, optionally normalised + high-pass filtered (noise reduction), then split into 25-second chunks with a progress bar.
- Silent chunks are skipped; unclear chunks are counted and reported; network/service errors show friendly messages (details only in the log).

## Files
| File | Purpose |
|---|---|
| `app.py` | Streamlit UI, session state, dashboard, history |
| `audio_utils.py` | Loading, validation, pre-processing, chunking (Pydub) |
| `transcriber.py` | Speech recognition + text formatting |
| `exporter.py` | TXT / DOCX export (python-docx) |
| `styles.py` | CSS, dashboard cards, workflow bar |
| `config.py` | Languages, formats, limits |

## Add a language
Add one line in `config.py`, e.g. `"Hindi": "hi-IN"`.

## Limitations (good viva answers)
Accuracy depends on audio quality and accent; no punctuation is predicted by the engine (the app adds sentence casing/full stops); chunk boundaries may occasionally split a word; history lives only in the browser session.
