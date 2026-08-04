from dataclasses import dataclass, field
from typing import List


@dataclass
class ScenePayload:
    index: int
    text: str
    query: str = ""
    video_path: str = ""
    audio_path: str = ""


@dataclass
class VideoTimelineState:
    topic: str
    scenes: List[ScenePayload] = field(default_factory=list)
