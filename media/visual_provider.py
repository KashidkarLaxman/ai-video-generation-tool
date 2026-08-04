from dataclasses import dataclass
from typing import Literal, Optional, Sequence, Tuple

from core.logger import get_logger
from fallback.image_fallback import generate_image_with_fallback
from fallback.video_fallback import fetch_video_with_fallback
from media.image_fetcher import download_image_from_url, fetch_stock_photo
from media.web_image_search import search_web_images


logger = get_logger(__name__)

VisualKind = Literal["article_photo", "web_photo", "photo", "generated", "video"]

DEFAULT_ORDER: Tuple[VisualKind, ...] = ("web_photo", "photo", "generated", "video")


@dataclass
class VisualAsset:
    kind: VisualKind
    path: str


def get_visual(
    query: str,
    visual_prompt: str,
    index,
    rank: int = 0,
    order: Sequence[VisualKind] = DEFAULT_ORDER,
    orientation: str = "landscape",
    width: int = 1280,
    height: int = 720,
    article_image_url: Optional[str] = None,
) -> VisualAsset:
    if article_image_url:
        try:
            path = download_image_from_url(article_image_url, index, prefix="article_photo")
            return VisualAsset(kind="article_photo", path=path)
        except Exception as exc:
            logger.warning("Article image failed for scene %s, falling back: %s", index, exc)

    last_error: Exception = RuntimeError("No visual providers configured")

    for kind in order:
        try:
            if kind == "web_photo":
                results = search_web_images(query, max_results=5)
                if not results:
                    raise ValueError(f"No web image results for query: {query}")
                path = download_image_from_url(results[rank % len(results)], index, prefix="web_photo")
            elif kind == "photo":
                path = fetch_stock_photo(query, index, rank=rank, orientation=orientation)
            elif kind == "generated":
                path = generate_image_with_fallback(visual_prompt, index, width=width, height=height)
            elif kind == "video":
                path = fetch_video_with_fallback(query, index, orientation=orientation, target_width=width)
            else:
                continue
            return VisualAsset(kind=kind, path=path)
        except Exception as exc:
            logger.warning("Visual provider '%s' failed for scene %s: %s", kind, index, exc)
            last_error = exc

    raise last_error
