from moviepy.editor import concatenate_videoclips


def compose_final_video(clips: list, output_path: str) -> str:
    """Each clip must already have its own audio attached via `set_audio`,
    so concatenation keeps every scene's video and audio locked together
    instead of drifting when video and audio tracks are joined separately."""
    final_video = concatenate_videoclips(clips, method="compose")
    final_video.write_videofile(
        output_path,
        fps=24,
        codec="libx264",
        audio_codec="aac",
    )
    return output_path
