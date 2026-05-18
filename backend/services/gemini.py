import os
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai import errors
import requests
# ...existing code...

def generate_ai_reply(user_text: str) -> str:
    load_dotenv()

    if not user_text.strip():
        raise GeminiError("Transcript is empty. Cannot generate AI reply.")

    openrouter_key = os.getenv("OPENROUTER_API_KEY")

    personality = load_personality_prompt()

    if openrouter_key:
        # Use OpenRouter API
        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {openrouter_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "openai/gpt-3.5-turbo",  # Change model if needed
            "messages": [
                {"role": "system", "content": f"{personality}\nReply to the user in character. Keep the response short and natural."},
                {"role": "user", "content": user_text}
            ]
        }
        try:
            resp = requests.post(url, headers=headers, json=data, timeout=30)
            resp.raise_for_status()
            result = resp.json()
            return result["choices"][0]["message"]["content"].strip()
        except requests.RequestException as exc:
            raise GeminiError(f"OpenRouter request failed: {exc}") from exc
        except Exception as exc:
            raise GeminiError(f"Failed to parse OpenRouter response: {exc}") from exc

    elif gemini_key:
        # ...existing Gemini code...
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
            if getattr(exc, "status_code", None) == 429:
                raise GeminiQuotaError(
                    "Gemini quota is exhausted for now. Try again later or use another API key/project."
                ) from exc
            raise GeminiError(f"Gemini request failed: {exc}") from exc
        except Exception as exc:
            raise GeminiError(f"Failed to generate AI reply: {exc}") from exc
        return (response.text or "").strip()
    else:
        raise GeminiError("No API key found. Add OPENROUTER_API_KEY, GEMINI_API_KEY, or GOOGLE_API_KEY to your .env file.")

PERSONALITY_PATH = Path("docs/personality.txt")
GEMINI_MODEL = "gemini-1.5-flash"


class GeminiError(RuntimeError):
    pass


class GeminiQuotaError(GeminiError):
    pass


def load_personality_prompt() -> str:
    return PERSONALITY_PATH.read_text(encoding="utf-8")


