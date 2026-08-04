import os
from urllib.parse import quote

import requests

from config import TEMP_DIR
from utils.retry import retry


POLLINATIONS_BASE_URL = "https://image.pollinations.ai/prompt"
NEGATIVE_SUFFIX = ", no text, no watermark, no logo, no captions"


def generate_image(prompt: str, index: int, width: int = 1280, height: int = 720) -> str:
    encoded_prompt = quote(f"{prompt}{NEGATIVE_SUFFIX}")

    def _request() -> bytes:
        response = requests.get(
            f"{POLLINATIONS_BASE_URL}/{encoded_prompt}",
            params={"width": width, "height": height, "nologo": "true", "model": "flux"},
            timeout=60,
        )
        response.raise_for_status()
        content_type = response.headers.get("content-type", "")
        if not content_type.startswith("image/"):
            raise ValueError(f"Unexpected content type from image provider: {content_type}")
        return response.content

    image_bytes = retry(_request, attempts=3)

    image_path = os.path.join(TEMP_DIR, f"image_{index}.jpg")
    with open(image_path, "wb") as file:
        file.write(image_bytes)

    return image_path
