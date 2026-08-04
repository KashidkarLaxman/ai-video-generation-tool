import json
import re
from dataclasses import dataclass, field
from typing import List, Optional
from urllib.parse import urlparse

import trafilatura


IMAGE_MARKDOWN_RE = re.compile(r"!\[[^\]]*\]\(([^)\s]+)\)")
EXCLUDED_IMAGE_PATTERNS = ("logo", "icon", "avatar", "sprite", "pixel", "spacer", "advert", "banner-ad")
MAX_ARTICLE_IMAGES = 15


@dataclass
class Article:
    url: str
    title: str
    text: str
    source: str
    published: Optional[str] = None
    images: List[str] = field(default_factory=list)


def _extract_images(markdown_text: str) -> List[str]:
    seen = set()
    images = []
    for url in IMAGE_MARKDOWN_RE.findall(markdown_text):
        if url in seen:
            continue
        seen.add(url)

        lower = url.lower()
        if lower.endswith(".svg") or any(pattern in lower for pattern in EXCLUDED_IMAGE_PATTERNS):
            continue

        images.append(url)
        if len(images) >= MAX_ARTICLE_IMAGES:
            break

    return images


def scrape_article(url: str) -> Article:
    downloaded = trafilatura.fetch_url(url)
    if not downloaded:
        raise ValueError(f"Could not fetch URL: {url}")

    extracted = trafilatura.extract(
        downloaded,
        url=url,
        output_format="json",
        with_metadata=True,
        include_images=True,
        include_comments=False,
        include_tables=False,
    )
    if not extracted:
        raise ValueError(f"Could not extract article content from: {url}")

    data = json.loads(extracted)
    raw_text = (data.get("text") or "").strip()
    if not raw_text:
        raise ValueError(f"No article text extracted from: {url}")

    images = _extract_images(raw_text)
    hero_image = data.get("image")
    if hero_image and hero_image not in images:
        images.insert(0, hero_image)

    text = IMAGE_MARKDOWN_RE.sub("", raw_text).strip()

    return Article(
        url=url,
        title=(data.get("title") or "").strip(),
        text=text,
        source=data.get("hostname") or urlparse(url).netloc,
        published=data.get("date"),
        images=images[:MAX_ARTICLE_IMAGES],
    )
