"""Speech recognition (SpeechRecognition + Google Web Speech API) and text processing."""
import io
import re

import speech_recognition as sr

from config import SILENCE_DBFS


class TranscriptionError(Exception):
    """User-friendly transcription problem."""


def transcribe_segments(chunks, language_code, progress=None):
    """Return (list_of_text_parts, number_of_unclear_chunks)."""
    recognizer = sr.Recognizer()
    parts, unclear = [], 0
    for i, chunk in enumerate(chunks, 1):
        if progress:
            progress(i, len(chunks))
        if chunk.dBFS < SILENCE_DBFS:        # skip silence
            continue
        buf = io.BytesIO()
        chunk.export(buf, format="wav")
        buf.seek(0)
        try:
            with sr.AudioFile(buf) as src:
                audio = recognizer.record(src)
            parts.append(recognizer.recognize_google(audio, language=language_code))
        except sr.UnknownValueError:
            unclear += 1
        except sr.RequestError:
            raise TranscriptionError(
                "The speech recognition service could not be reached. "
                "Check your internet connection and try again in a moment."
            )
        except Exception:
            raise TranscriptionError("Speech recognition failed for this audio. Try a different file or language.")
    return parts, unclear


def format_text(parts, chunks_per_paragraph=3):
    """Capitalise, add end punctuation, and group into paragraphs."""
    clean = []
    for p in parts:
        p = re.sub(r"\s+", " ", p).strip()
        if not p:
            continue
        p = p[0].upper() + p[1:]
        if p[-1] not in ".!?":
            p += "."
        clean.append(p)
    paras = [" ".join(clean[i:i + chunks_per_paragraph]) for i in range(0, len(clean), chunks_per_paragraph)]
    return "\n\n".join(paras)
