from media.video_fetcher import fetch_video


DEFAULT_VIDEO_QUERY = "motivation person"


def fetch_video_with_fallback(query: str, index: int, orientation: str = "landscape", target_width: int = 1280) -> str:
    try:
        return fetch_video(query, index, orientation=orientation, target_width=target_width)
    except Exception:
        return fetch_video(DEFAULT_VIDEO_QUERY, index, orientation=orientation, target_width=target_width)
