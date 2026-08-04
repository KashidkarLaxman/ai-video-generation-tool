import os

import requests

from config import PEXELS_API_KEY, TEMP_DIR


def fetch_video(query: str, index: int, orientation: str = "landscape", target_width: int = 1280) -> str:
    response = requests.get(
        "https://api.pexels.com/videos/search",
        headers={"Authorization": PEXELS_API_KEY},
        params={"query": query, "per_page": 3, "orientation": orientation},
        timeout=30,
    )
    response.raise_for_status()

    data = response.json()
    videos = data.get("videos", [])
    if not videos:
        raise ValueError(f"No video found for query: {query}")

    video_files = videos[0].get("video_files", [])
    if not video_files:
        raise ValueError("No video files returned by Pexels")

    video_file = min(
        video_files,
        key=lambda item: abs(item.get("width", 0) - target_width),
    )
    video_url = video_file["link"]
    video_data = requests.get(video_url, timeout=60)
    video_data.raise_for_status()

    video_path = os.path.join(TEMP_DIR, f"video_{index}.mp4")
    with open(video_path, "wb") as file:
        file.write(video_data.content)

    return video_path
