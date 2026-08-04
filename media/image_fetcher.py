import os
from io import BytesIO

import requests
from PIL import Image

from config import PEXELS_API_KEY, TEMP_DIR


def fetch_stock_photo(query: str, index, rank: int = 0, orientation: str = "landscape") -> str:
    response = requests.get(
        "https://api.pexels.com/v1/search",
        headers={"Authorization": PEXELS_API_KEY},
        params={"query": query, "per_page": 5, "orientation": orientation},
        timeout=30,
    )
    response.raise_for_status()

    data = response.json()
    photos = data.get("photos", [])
    if not photos:
        raise ValueError(f"No stock photo found for query: {query}")

    photo_url = photos[rank % len(photos)]["src"]["large2x"]
    photo_data = requests.get(photo_url, timeout=60)
    photo_data.raise_for_status()

    photo_path = os.path.join(TEMP_DIR, f"photo_{index}.jpg")
    with open(photo_path, "wb") as file:
        file.write(photo_data.content)

    return photo_path


MIN_ARTICLE_IMAGE_BYTES = 5000


def download_image_from_url(url: str, index, prefix: str = "downloaded_photo") -> str:
    response = requests.get(url, timeout=30, headers={"User-Agent": "Mozilla/5.0"})
    response.raise_for_status()

    content_type = response.headers.get("content-type", "")
    if not content_type.startswith("image/"):
        raise ValueError(f"URL did not return an image ({content_type}): {url}")

    if len(response.content) < MIN_ARTICLE_IMAGE_BYTES:
        raise ValueError(f"Image too small, likely an icon or placeholder: {url}")

    # Web images arrive in inconsistent modes (grayscale, palette, RGBA, CMYK)
    # unlike curated Pexels/Pollinations output, which is always plain RGB.
    # Normalize here so downstream video compositing always gets a 3-channel
    # RGB frame.
    image = Image.open(BytesIO(response.content)).convert("RGB")

    photo_path = os.path.join(TEMP_DIR, f"{prefix}_{index}.jpg")
    image.save(photo_path, format="JPEG", quality=90)

    return photo_path
