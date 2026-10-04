"""Audio loading, validation and pre-processing (Pydub)."""
import io
import shutil

from pydub import AudioSegment
from pydub.effects import high_pass_filter, normalize

from config import CHUNK_SECONDS, SAMPLE_RATE


class AudioError(Exception):
    """User-friendly audio problem."""


def ffmpeg_available() -> bool:
    return shutil.which("ffmpeg") is not None


def load_audio(data: bytes, ext: str) -> AudioSegment:
    ext = ext.lower().lstrip(".")
    if ext != "wav" and not ffmpeg_available():
        raise AudioError(
            f".{ext} files need FFmpeg, which was not found on this computer. "
            "Install FFmpeg and add it to PATH (see README), or upload a WAV file."
        )
    try:
        if ext == "wav":
            try:
                return AudioSegment.from_file(io.BytesIO(data), format="wav")
            except Exception:
                if not ffmpeg_available():
                    raise
        return AudioSegment.from_file(io.BytesIO(data))
    except Exception:
        raise AudioError("This audio file could not be read. It may be corrupted or use an unsupported encoding.")


def prepare(seg: AudioSegment, reduce_noise: bool) -> AudioSegment:
    """Mono, 16 kHz, optional noise clean-up (normalise + high-pass filter)."""
    if seg.duration_seconds < 0.5 or seg.dBFS == float("-inf"):
        raise AudioError("The audio is empty or silent. Record or upload audio that contains speech.")
    seg = seg.set_channels(1).set_frame_rate(SAMPLE_RATE).set_sample_width(2)
    if reduce_noise:
        seg = normalize(high_pass_filter(seg, 100))   # removes low-frequency rumble/hum
    return seg


def split(seg: AudioSegment) -> list:
    step = CHUNK_SECONDS * 1000
    return [seg[i:i + step] for i in range(0, len(seg), step)]
