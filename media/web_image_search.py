from typing import List

from ddgs import DDGS

from core.logger import get_logger


logger = get_logger(__name__)


def search_web_images(query: str, max_results: int = 5) -> List[str]:
    try:
        results = DDGS().images(query, max_results=max_results)
    except Exception as exc:
        logger.warning("Web image search failed for query '%s': %s", query, exc)
        return []

    return [result["image"] for result in results if result.get("image")]
