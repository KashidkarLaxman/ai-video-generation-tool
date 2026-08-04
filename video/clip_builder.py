from typing import List, Optional

from moviepy.editor import CompositeVideoClip, ImageClip, VideoFileClip, concatenate_videoclips
from moviepy.video.fx.crop import crop
from moviepy.video.fx.loop import loop

from media.transcriber import WordTiming
from video.subtitle import create_karaoke_subtitle_image, create_subtitle_image


TARGET_WIDTH = 1280
TARGET_HEIGHT = 720

ORIENTATIONS = {
    "landscape": (1280, 720),
    "portrait": (720, 1280),
}


def _fit_to_canvas(clip, width: int = TARGET_WIDTH, height: int = TARGET_HEIGHT):
    """Scale to fully cover the target canvas, then center-crop to it, so every
    shot ends up at the same resolution regardless of its source dimensions."""
    scale = max(width / clip.w, height / clip.h)
    resized = clip.resize(scale)
    return crop(
        resized,
        width=width,
        height=height,
        x_center=resized.w / 2,
        y_center=resized.h / 2,
    )


def create_clip(video_path: str, text: str, duration: float = 5, width: int = TARGET_WIDTH, height: int = TARGET_HEIGHT):
    video = VideoFileClip(video_path)
    duration = min(duration, video.duration)
    video = _fit_to_canvas(video.subclip(0, duration), width, height)

    subtitle = (
        ImageClip(create_subtitle_image(text, width=video.w))
        .set_duration(duration)
        .set_position(("center", "bottom"))
    )
    return CompositeVideoClip([video, subtitle])


def build_still_visual(image_path: str, duration: float, zoom: float = 0.08, width: int = TARGET_WIDTH, height: int = TARGET_HEIGHT):
    base = ImageClip(image_path).set_duration(duration)
    base = _fit_to_canvas(base, width, height)
    animated = base.resize(lambda t: 1 + zoom * (t / duration if duration else 0))
    return CompositeVideoClip(
        [animated.set_position("center")], size=(width, height)
    ).set_duration(duration)


def build_video_visual(video_path: str, duration: float, width: int = TARGET_WIDTH, height: int = TARGET_HEIGHT):
    video = VideoFileClip(video_path)
    if video.duration < duration:
        # A source clip shorter than the scene's actual narration (common
        # with manually uploaded overrides) - loop it to fill the needed
        # duration instead of silently truncating narration/captions to
        # match the short clip.
        video = loop(video, duration=duration)
    else:
        video = video.subclip(0, duration)
    return _fit_to_canvas(video, width, height)


def build_shot_visual(path: str, kind: str, duration: float, width: int = TARGET_WIDTH, height: int = TARGET_HEIGHT):
    if kind == "video":
        return build_video_visual(path, duration, width, height)
    return build_still_visual(path, duration, width=width, height=height)


def _subtitle_clip(text: str, width: int, duration: float):
    return (
        ImageClip(create_subtitle_image(text, width=width))
        .set_duration(duration)
        .set_position(("center", "bottom"))
    )


def build_karaoke_captions(words: List[WordTiming], width: int, total_duration: float):
    """Each word stays on screen from when it's spoken until the next word
    starts (not just its own speech window), so pauses and trailing silence
    don't leave the caption blank."""
    display_words = [w.word for w in words]
    clips = []

    for index, word in enumerate(words):
        start = 0.0 if index == 0 else max(0.0, word.start)
        if start >= total_duration:
            continue

        next_start = words[index + 1].start if index + 1 < len(words) else total_duration
        end = min(max(next_start, start), total_duration)
        duration = max(end - start, 0.05)

        image = create_karaoke_subtitle_image(display_words, active_index=index, width=width)
        clips.append(
            ImageClip(image)
            .set_start(start)
            .set_duration(duration)
            .set_position(("center", "bottom"))
        )

    return clips


def create_scene_clip(
    shots,
    text: str,
    words: Optional[List[WordTiming]] = None,
    width: int = TARGET_WIDTH,
    height: int = TARGET_HEIGHT,
):
    """shots: sequence of (path, kind, duration) shown back-to-back within one scene.
    words: word-level timings from the actual TTS audio, for synced karaoke captions.
    Falls back to a single static caption if no usable word timings are available."""
    shot_visuals = [
        build_shot_visual(path, kind, duration, width=width, height=height) for path, kind, duration in shots
    ]
    visual = concatenate_videoclips(shot_visuals, method="compose")
    total_duration = visual.duration

    if words:
        caption_clips = build_karaoke_captions(words, width=visual.w, total_duration=total_duration)
        if caption_clips:
            return CompositeVideoClip([visual, *caption_clips])

    subtitle = _subtitle_clip(text, width=visual.w, duration=total_duration)
    return CompositeVideoClip([visual, subtitle])
