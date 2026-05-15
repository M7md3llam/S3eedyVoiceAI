import os
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai import errors


PERSONALITY_PATH = Path("docs/personality.txt")
GEMINI_MODEL = "gemini-2.5-flash"


class GeminiError(RuntimeError):
    pass


def load_personality_prompt() -> str:
    return PERSONALITY_PATH.read_text(encoding="utf-8")


def generate_ai_reply(user_text: str) -> str:
    load_dotenv()

    if not user_text.strip():
        raise GeminiError("Transcript is empty. Cannot generate AI reply.")

    if not os.getenv("GEMINI_API_KEY") and not os.getenv("GOOGLE_API_KEY"):
        raise GeminiError("GEMINI_API_KEY or GOOGLE_API_KEY is missing. Add one to your .env file.")

    personality = load_personality_prompt()
    client = genai.Client()

    try:
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=(
                f"{personality}\n\n"
                "Reply to the user in character. Keep the response short and natural.\n\n"
                f"User: {user_text}\n"
                "Assistant:"
            ),
        )
    except errors.APIError as exc:
        raise GeminiError(f"Gemini request failed: {exc}") from exc
    except Exception as exc:
        raise GeminiError(f"Failed to generate AI reply: {exc}") from exc

    return (response.text or "").strip()
