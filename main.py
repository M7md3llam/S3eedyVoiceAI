import logging
from pathlib import Path
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from backend.services.gemini import GeminiError, generate_ai_reply
from backend.services.transcription import TranscriptionError, transcribe_audio_file


app = FastAPI()
UPLOAD_DIR = Path("temp")
logger = logging.getLogger(__name__)
FRONTEND_DIR = Path("frontend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")


@app.get("/")
async def root():
    return FileResponse(FRONTEND_DIR / "index.html")


@app.post("/api/upload")
async def upload_audio(request: Request):
    form = await request.form()
    audio = form.get("audio")

    if audio is None:
        for value in form.values():
            if hasattr(value, "filename") and hasattr(value, "read"):
                audio = value
                break

    if audio is None or not hasattr(audio, "read"):
        raise HTTPException(status_code=400, detail="No audio file found in form data.")

    contents = await audio.read()
    UPLOAD_DIR.mkdir(exist_ok=True)

    suffix = Path(audio.filename or "recording.webm").suffix or ".webm"
    saved_filename = f"recording-{uuid4().hex}{suffix}"
    saved_path = UPLOAD_DIR / saved_filename
    saved_path.write_bytes(contents)

    try:
        transcript = transcribe_audio_file(saved_path)
    except TranscriptionError as exc:
        logger.exception("Transcription failed for %s", saved_path)
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    try:
        reply = generate_ai_reply(transcript)
    except GeminiError as exc:
        logger.exception("Gemini reply failed for %s", saved_path)
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    return {
        "success": True,
        "filename": audio.filename,
        "content_type": audio.content_type,
        "size": len(contents),
        "saved_as": str(saved_path),
        "transcript": transcript,
        "reply": reply,
    }
