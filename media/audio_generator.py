import asyncio
import os

import edge_tts
from gtts import gTTS
from pydub import AudioSegment

from config import TEMP_DIR


def _silent_audio(audio_path: str, duration_ms: int = 3000) -> str:
    AudioSegment.silent(duration=duration_ms).export(audio_path, format="mp3")
    return audio_path


MAX_TTS_CHARS = 5000


async def _edge_tts_to_file(text: str, audio_path: str) -> None:
    communicate = edge_tts.Communicate(
        text=text[:MAX_TTS_CHARS],
        voice="en-US-AriaNeural",
    )
    await communicate.save(audio_path)


def generate_voice(text: str, index) -> str:
    audio_path = os.path.join(TEMP_DIR, f"audio_{index}.mp3")

    try:
        asyncio.run(_edge_tts_to_file(text, audio_path))
        return audio_path
    except Exception:
        pass

    try:
        gTTS(text=text[:MAX_TTS_CHARS], lang="en").save(audio_path)
        return audio_path
    except Exception:
        return _silent_audio(audio_path)
