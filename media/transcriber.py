import threading
from dataclasses import dataclass
from typing import List

from faster_whisper import WhisperModel


_MODEL = None
_MODEL_LOCK = threading.Lock()


@dataclass
class WordTiming:
    word: str
    start: float
    end: float


def _get_model() -> WhisperModel:
    global _MODEL
    if _MODEL is None:
        with _MODEL_LOCK:
            if _MODEL is None:
                _MODEL = WhisperModel("base.en", device="cpu", compute_type="int8")
    return _MODEL


def transcribe_words(audio_path: str) -> List[WordTiming]:
    model = _get_model()
    words: List[WordTiming] = []

    # ctranslate2 models are not safe for concurrent calls on one instance,
    # so inference is serialized even though scenes fetch in parallel.
    with _MODEL_LOCK:
        segments, _ = model.transcribe(audio_path, word_timestamps=True)
        for segment in segments:
            if not segment.words:
                continue
            for word in segment.words:
                text = word.word.strip().lstrip("-")
                if text:
                    words.append(WordTiming(word=text, start=word.start, end=word.end))

    return words
