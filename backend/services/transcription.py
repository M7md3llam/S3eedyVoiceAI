from pathlib import Path

from dotenv import load_dotenv
from faster_whisper import WhisperModel


SUPPORTED_AUDIO_EXTENSIONS = {
    ".flac",
    ".mp3",
    ".mp4",
    ".mpeg",
    ".mpga",
    ".m4a",
    ".ogg",
    ".wav",
    ".webm",
}

MAX_AUDIO_SIZE_BYTES = 25 * 1024 * 1024
MODEL_SIZE = "small"
_model = None


class TranscriptionError(RuntimeError):
    pass


def get_transcription_model() -> WhisperModel:
    global _model

    if _model is None:
        try:
            _model = WhisperModel(MODEL_SIZE, device="cpu", compute_type="int8")
        except Exception as exc:
            raise TranscriptionError(f"Failed to load local Whisper model '{MODEL_SIZE}': {exc}") from exc

    return _model


def transcribe_audio_file(audio_path: str | Path) -> str:
    load_dotenv()
    path = Path(audio_path)

    if not path.exists():
        raise TranscriptionError(f"Audio file not found: {path}")

    if path.suffix.lower() not in SUPPORTED_AUDIO_EXTENSIONS:
        supported = ", ".join(sorted(SUPPORTED_AUDIO_EXTENSIONS))
        raise TranscriptionError(
            f"Unsupported audio file type '{path.suffix}'. Supported types: {supported}"
        )

    if path.stat().st_size > MAX_AUDIO_SIZE_BYTES:
        raise TranscriptionError("Audio file is larger than the 25 MB transcription limit.")

    model = get_transcription_model()

    try:
        segments, _info = model.transcribe(str(path), beam_size=5, language="ar")
        text = " ".join(segment.text.strip() for segment in segments).strip()
    except Exception as exc:
        raise TranscriptionError(f"Local Whisper transcription failed: {exc}") from exc

    return text
