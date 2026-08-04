import os
import threading
from collections import deque
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from functools import partial
from typing import Callable, Dict, List, Optional, Tuple

from moviepy.editor import AudioFileClip

from config import OUTPUT_DIR, ensure_directories
from core.logger import get_logger
from core.state import ScenePayload, VideoTimelineState
from media.audio_generator import generate_voice
from media.transcriber import WordTiming, transcribe_words
from media.visual_provider import get_visual
from script.news_script import generate_script_from_url
from script.schemas import ScriptScene, VideoScript
from utils.text_cleaner import clean_query
from video.clip_builder import ORIENTATIONS, create_scene_clip
from video.composer import compose_final_video


logger = get_logger(__name__)

MAX_SCENE_SECONDS = 12
MIN_SCENE_SECONDS = 0.5
SHOT_TARGET_SECONDS = 4.5
MAX_SHOTS_PER_SCENE = 3
MAX_WORKERS = 5
BOUNDARY_SEARCH_WINDOW = 6

VIDEO_EXTENSIONS = {".mp4", ".mov", ".webm", ".avi", ".mkv", ".m4v"}


@dataclass
class SceneTiming:
    scene: ScriptScene
    start: float
    end: float
    duration: float
    words: List[WordTiming] = field(default_factory=list)  # timestamps rebased to this scene's own 0


@dataclass
class SceneAssets:
    scene: ScriptScene
    query: str
    words: List[WordTiming]
    shots: List[Tuple[str, str, float]] = field(default_factory=list)  # (path, kind, duration)


def _make_image_pool(images: List[str]) -> Callable[[], Optional[str]]:
    pool = deque(images)
    lock = threading.Lock()

    def pop_next() -> Optional[str]:
        with lock:
            return pool.popleft() if pool else None

    return pop_next


def _infer_visual_kind(path: str) -> str:
    ext = os.path.splitext(path)[1].lower()
    return "video" if ext in VIDEO_EXTENSIONS else "photo"


def _find_scene_word_ranges(word_counts: List[int], all_words: List[WordTiming]) -> List[Tuple[int, int]]:
    """Split one continuous transcript into per-scene (start_index, end_index)
    ranges. Each scene's own word count gives an approximate boundary
    position, then the actual split snaps to the largest nearby silence gap
    - robust to TTS/ASR disagreeing on how numbers or contractions tokenize,
    since we don't trust the word count to be exactly right, just close."""
    n = len(word_counts)
    ranges = []
    cursor = 0
    cumulative = 0

    for i, count in enumerate(word_counts):
        cumulative += count

        if i == n - 1 or cursor >= len(all_words):
            ranges.append((cursor, len(all_words)))
            break

        expected_index = min(cumulative, len(all_words) - 1)
        search_start = max(cursor, expected_index - BOUNDARY_SEARCH_WINDOW)
        search_end = min(len(all_words) - 1, expected_index + BOUNDARY_SEARCH_WINDOW)

        best_split = expected_index
        best_gap = -1.0
        for j in range(search_start, max(search_start, search_end)):
            gap = all_words[j + 1].start - all_words[j].end
            if gap > best_gap:
                best_gap = gap
                best_split = j + 1

        best_split = max(best_split, cursor + 1)
        ranges.append((cursor, best_split))
        cursor = best_split

    return ranges


def _time_scenes_from_combined_audio(scenes: List[ScriptScene]) -> Tuple[str, List[SceneTiming]]:
    """Synthesize the ENTIRE script as one continuous narration instead of a
    separate TTS call per scene, so prosody carries across scene boundaries
    instead of resetting at each cut. Scene boundaries are then recovered
    from the single transcript's natural pauses."""
    combined_text = " ".join(scene.narration.strip() for scene in scenes)
    audio_path = generate_voice(combined_text, index="combined_narration")

    audio_probe = AudioFileClip(audio_path)
    try:
        total_duration = audio_probe.duration
    finally:
        audio_probe.close()

    try:
        all_words = transcribe_words(audio_path)
    except Exception as exc:
        logger.warning("Transcription of combined narration failed: %s", exc)
        all_words = []

    timings: List[SceneTiming] = []

    if all_words:
        word_counts = [len(scene.narration.split()) for scene in scenes]
        ranges = _find_scene_word_ranges(word_counts, all_words)
        for scene, (start_idx, end_idx) in zip(scenes, ranges):
            scene_words = all_words[start_idx:end_idx]
            if scene_words:
                start = scene_words[0].start
                end = scene_words[-1].end
            else:
                start = end = timings[-1].end if timings else 0.0
            duration = max(min(end - start, MAX_SCENE_SECONDS), MIN_SCENE_SECONDS)
            rebased = [WordTiming(word=w.word, start=w.start - start, end=w.end - start) for w in scene_words]
            timings.append(SceneTiming(scene=scene, start=start, end=start + duration, duration=duration, words=rebased))
    else:
        # No transcription available - fall back to splitting total audio
        # duration proportionally by expected word count. No word-level
        # captions in this path; create_scene_clip falls back to a static
        # caption per scene when words is empty.
        logger.warning("Falling back to proportional scene timing without word-level captions")
        total_words = sum(len(scene.narration.split()) for scene in scenes) or 1
        cursor = 0.0
        for scene in scenes:
            share = len(scene.narration.split()) / total_words
            duration = max(min(total_duration * share, MAX_SCENE_SECONDS), MIN_SCENE_SECONDS)
            timings.append(SceneTiming(scene=scene, start=cursor, end=cursor + duration, duration=duration, words=[]))
            cursor += duration

    return audio_path, timings


def _fetch_scene_visuals(
    timing: SceneTiming,
    orientation: str,
    width: int,
    height: int,
    next_article_image: Callable[[], Optional[str]],
    overrides: Dict[int, str],
) -> SceneAssets:
    scene = timing.scene
    index = scene.scene
    query = clean_query(scene.search_query)

    override_path = overrides.get(index)
    if override_path:
        shots: List[Tuple[str, str, float]] = [(override_path, _infer_visual_kind(override_path), timing.duration)]
    else:
        num_shots = max(1, min(MAX_SHOTS_PER_SCENE, round(timing.duration / SHOT_TARGET_SECONDS)))
        shot_duration = timing.duration / num_shots

        shots = []
        for shot_index in range(num_shots):
            asset = get_visual(
                query=query,
                visual_prompt=scene.visual_prompt,
                index=f"{index}_{shot_index}",
                rank=shot_index,
                orientation=orientation,
                width=width,
                height=height,
                article_image_url=next_article_image(),
            )
            shots.append((asset.path, asset.kind, shot_duration))

    return SceneAssets(scene=scene, query=query, words=timing.words, shots=shots)


def generate_news_script(url: str, target_duration_seconds: int = 45) -> Tuple[VideoScript, List[str]]:
    """Stage 1: scrape the article and write the script. No visuals, audio,
    or rendering yet - this is the point where the script/scenes can be
    reviewed and edited before paying for the expensive stage below."""
    ensure_directories()
    return generate_script_from_url(url, target_duration_seconds=target_duration_seconds)


def render_news_video(
    script: VideoScript,
    article_images: List[str],
    orientation: str = "landscape",
    overrides: Optional[Dict[int, str]] = None,
) -> str:
    """Stage 2: synthesize one continuous narration for the whole script,
    recover per-scene timing from it, fetch visuals per scene (skipping the
    automatic cascade for any scene with a manual override), and render."""
    ensure_directories()
    width, height = ORIENTATIONS.get(orientation, ORIENTATIONS["landscape"])
    overrides = overrides or {}

    audio_path, timings = _time_scenes_from_combined_audio(script.scenes)
    full_audio = AudioFileClip(audio_path)

    worker_count = min(len(timings), MAX_WORKERS) or 1
    next_article_image = _make_image_pool(article_images)
    fetch_fn = partial(
        _fetch_scene_visuals,
        orientation=orientation,
        width=width,
        height=height,
        next_article_image=next_article_image,
        overrides=overrides,
    )
    with ThreadPoolExecutor(max_workers=worker_count) as executor:
        results: List[SceneAssets] = list(executor.map(fetch_fn, timings))

    state = VideoTimelineState(topic=script.title)
    clips = []

    for timing, result in zip(timings, results):
        clip = create_scene_clip(result.shots, result.scene.narration, words=result.words, width=width, height=height)

        scene_audio = full_audio.subclip(timing.start, min(timing.end, full_audio.duration))
        clip = clip.set_audio(scene_audio.set_duration(min(clip.duration, scene_audio.duration)))
        clips.append(clip)

        state.scenes.append(
            ScenePayload(
                index=result.scene.scene,
                text=result.scene.narration,
                query=result.query,
                video_path=result.shots[0][0] if result.shots else "",
                audio_path=audio_path,
            )
        )

    output_path = compose_final_video(
        clips=clips,
        output_path=f"{OUTPUT_DIR}/news_video.mp4",
    )
    logger.info("News video created at %s", output_path)
    return output_path


def create_video_from_url(url: str, orientation: str = "landscape", target_duration_seconds: int = 45) -> str:
    """Convenience wrapper: both stages in one call, for callers that don't
    need to review the script in between (e.g. the legacy one-shot flow)."""
    script, article_images = generate_news_script(url, target_duration_seconds=target_duration_seconds)
    logger.info("Generated script '%s' with %d scenes", script.title, len(script.scenes))
    return render_news_video(script, article_images, orientation=orientation)
