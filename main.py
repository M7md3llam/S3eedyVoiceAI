import logging
import os
import time
from pathlib import Path
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from backend.services.gemini import GeminiError, GeminiQuotaError, generate_ai_reply
from backend.services.transcription import (
    MAX_AUDIO_SIZE_BYTES,
    TranscriptionError,
    transcribe_audio_file,
)
from backend.services.tts import TTSError, generate_reply_audio


app = FastAPI()
UPLOAD_DIR = Path("temp")
FRONTEND_DIR = Path("frontend")
AUDIO_DIR = Path("audio")
REPLIES_DIR = AUDIO_DIR / "replies"
MAX_FILE_AGE_SECONDS = int(os.getenv("MAX_FILE_AGE_SECONDS", "3600"))
ALLOWED_ORIGINS = [
    origin.strip()
    for origin in os.getenv(
        "ALLOWED_ORIGINS",
        "http://127.0.0.1:8000,http://localhost:8000",
    ).split(",")
    if origin.strip()
]
logger = logging.getLogger(__name__)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_methods=["POST"],
    allow_headers=["Content-Type"],
)

app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")
app.mount("/audio", StaticFiles(directory=AUDIO_DIR), name="audio")


def remove_expired_files(directory: Path) -> None:
    if not directory.exists():
        return

    cutoff = time.time() - MAX_FILE_AGE_SECONDS
    for path in directory.iterdir():
        if not path.is_file() or path.stat().st_mtime >= cutoff:
            continue
        try:
            path.unlink()
        except OSError:
            logger.warning("Could not remove expired file %s", path, exc_info=True)


@app.get("/")
async def root():
    return FileResponse(FRONTEND_DIR / "index.html")


@app.post("/api/upload")
async def upload_audio(request: Request):
    content_length = request.headers.get("content-length")
    if content_length:
        try:
            declared_size = int(content_length)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail="Invalid Content-Length header.") from exc
        if declared_size > MAX_AUDIO_SIZE_BYTES:
            raise HTTPException(status_code=413, detail="Audio file exceeds the 25 MB limit.")

    try:
        form = await request.form()
    except Exception as exc:
        raise HTTPException(status_code=400, detail="Invalid multipart form data.") from exc

    audio = form.get("audio")
    if audio is None or not hasattr(audio, "read"):
        raise HTTPException(status_code=400, detail="No audio file found in form data.")

    contents = await audio.read()
    if not contents:
        raise HTTPException(status_code=400, detail="Audio file is empty.")
    if len(contents) > MAX_AUDIO_SIZE_BYTES:
        raise HTTPException(status_code=413, detail="Audio file exceeds the 25 MB limit.")

    suffix = Path(audio.filename or "recording.webm").suffix.lower() or ".webm"
    saved_path = UPLOAD_DIR / f"recording-{uuid4().hex}{suffix}"

    remove_expired_files(UPLOAD_DIR)
    remove_expired_files(REPLIES_DIR)
    UPLOAD_DIR.mkdir(exist_ok=True)
    saved_path.write_bytes(contents)

    try:
        transcript = transcribe_audio_file(saved_path)
        reply = generate_ai_reply(transcript)
        reply_audio_path = await generate_reply_audio(reply)
    except TranscriptionError as exc:
        logger.exception("Transcription failed for %s", saved_path)
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except GeminiQuotaError as exc:
        logger.warning("Gemini quota exhausted")
        raise HTTPException(
            status_code=429,
            detail={"message": str(exc), "transcript": transcript},
        ) from exc
    except GeminiError as exc:
        logger.exception("LLM reply failed")
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except TTSError as exc:
        logger.exception("TTS failed")
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    finally:
        try:
            saved_path.unlink(missing_ok=True)
        except OSError:
            logger.warning("Could not remove upload %s", saved_path, exc_info=True)

    return {
        "success": True,
        "filename": audio.filename,
        "content_type": audio.content_type,
        "size": len(contents),
        "transcript": transcript,
        "reply": reply,
        "audio_url": f"/{reply_audio_path.as_posix()}",
    }
