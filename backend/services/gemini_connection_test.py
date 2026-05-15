import os
from pathlib import Path

from dotenv import load_dotenv
from google import genai


PERSONALITY_PATH = Path("docs/personality.txt")
TEST_QUESTIONS = [
    "عامل ايه؟",
    "اسمك ايه؟",
    "احكي نكتة",
    "انت منين؟",
    "ممكن تساعدني في البرمجة؟",
]


def load_personality_prompt() -> str:
    return PERSONALITY_PATH.read_text(encoding="utf-8")


def test_gemini_connection() -> str:
    load_dotenv()

    if not os.getenv("GEMINI_API_KEY") and not os.getenv("GOOGLE_API_KEY"):
        raise RuntimeError("GEMINI_API_KEY or GOOGLE_API_KEY is missing. Add one to your .env file.")

    client = genai.Client()
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents="hello",
    )

    return response.text or ""


def test_personality_manually() -> list[tuple[str, str]]:
    load_dotenv()

    if not os.getenv("GEMINI_API_KEY") and not os.getenv("GOOGLE_API_KEY"):
        raise RuntimeError("GEMINI_API_KEY or GOOGLE_API_KEY is missing. Add one to your .env file.")

    personality = load_personality_prompt()
    client = genai.Client()
    questions = "\n".join(f"{index}. {question}" for index, question in enumerate(TEST_QUESTIONS, start=1))
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=(
            f"{personality}\n\n"
            "Answer each test question in order using this exact format:\n"
            "1. <answer>\n"
            "2. <answer>\n"
            "Keep each answer short, natural, and non-cringe.\n\n"
            f"{questions}"
        ),
    )

    lines = [line.strip() for line in (response.text or "").splitlines() if line.strip()]
    return list(zip(TEST_QUESTIONS, lines, strict=False))


if __name__ == "__main__":
    results = test_personality_manually()

    for question, answer in results:
        print(f"User: {question}")
        print(f"Assistant: {answer}")
        print()
