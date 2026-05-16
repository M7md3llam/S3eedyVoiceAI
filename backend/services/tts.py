from datetime import datetime, UTC
from pathlib import Path
from uuid import uuid4

import edge_tts


REPLIES_DIR = Path("audio/replies")
VOICE = "ar-EG-ShakirNeural"


class TTSError(RuntimeError):
    pass


def build_reply_audio_path() -> Path:
    timestamp = datetime.now(UTC).strftime("%Y%m%d-%H%M%S")
    return REPLIES_DIR / f"reply-{timestamp}-{uuid4().hex}.mp3"


async def generate_reply_audio(text: str) -> Path:
    if not text.strip():
        raise TTSError("AI reply is empty. Cannot generate audio.")

    REPLIES_DIR.mkdir(parents=True, exist_ok=True)
    output_path = build_reply_audio_path()

    try:
        communicate = edge_tts.Communicate(text, VOICE)
        await communicate.save(str(output_path))
    except Exception as exc:
        if output_path.exists():
            output_path.unlink()
        raise TTSError(f"Failed to generate reply audio: {exc}") from exc

    return output_path
