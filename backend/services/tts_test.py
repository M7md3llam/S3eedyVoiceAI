import asyncio
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2]))

from backend.services.tts import generate_reply_audio


TEXT = "السلام عليكم يا صاحبي"


async def generate_arabic_voice_test() -> Path:
    return await generate_reply_audio(TEXT)


if __name__ == "__main__":
    output_path = asyncio.run(generate_arabic_voice_test())
    print(output_path)
