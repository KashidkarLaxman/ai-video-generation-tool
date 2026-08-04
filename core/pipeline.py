from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from functools import partial
from typing import List

from moviepy.editor import AudioFileClip

from config import OUTPUT_DIR, ensure_directories
from core.logger import get_logger
from core.state import ScenePayload, VideoTimelineState
from fallback.video_fallback import fetch_video_with_fallback
from media.audio_generator import generate_voice
from script.generator import generate_script
from script.schemas import SimpleScene
from video.clip_builder import ORIENTATIONS, create_clip
from video.composer import compose_final_video


logger = get_logger(__name__)

MAX_WORKERS = 5
MAX_SCENE_SECONDS = 12


@dataclass
class SceneAssets:
    index: int
    text: str
    query: str
    video_path: str
    audio_path: str


def _fetch_scene_assets(scene: SimpleScene, orientation: str, width: int) -> SceneAssets:
    video_path = fetch_video_with_fallback(scene.query, scene.scene, orientation=orientation, target_width=width)
    audio_path = generate_voice(scene.text, scene.scene)
    return SceneAssets(
        index=scene.scene,
        text=scene.text,
        query=scene.query,
        video_path=video_path,
        audio_path=audio_path,
    )


def create_video(topic: str, orientation: str = "landscape", target_duration_seconds: int = 45) -> str:
    ensure_directories()
    width, height = ORIENTATIONS.get(orientation, ORIENTATIONS["landscape"])

    raw_scenes = generate_script(topic, target_duration_seconds=target_duration_seconds)
    state = VideoTimelineState(topic=topic)

    worker_count = min(len(raw_scenes), MAX_WORKERS) or 1
    fetch_fn = partial(_fetch_scene_assets, orientation=orientation, width=width)
    with ThreadPoolExecutor(max_workers=worker_count) as executor:
        results: List[SceneAssets] = list(executor.map(fetch_fn, raw_scenes))

    clips = []

    for result in results:
        state.scenes.append(
            ScenePayload(
                index=result.index,
                text=result.text,
                query=result.query,
                video_path=result.video_path,
                audio_path=result.audio_path,
            )
        )

        audio = AudioFileClip(result.audio_path)
        desired_duration = min(MAX_SCENE_SECONDS, audio.duration)
        clip = create_clip(result.video_path, result.text, duration=desired_duration, width=width, height=height)
        clip = clip.set_audio(audio.subclip(0, min(clip.duration, audio.duration)))
        clips.append(clip)

    output_path = compose_final_video(
        clips=clips,
        output_path=f"{OUTPUT_DIR}/final_video.mp4",
    )
    logger.info("Video created at %s", output_path)
    return output_path
