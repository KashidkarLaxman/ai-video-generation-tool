from typing import List, Tuple

from core.logger import get_logger
from llm.prompts import NEWS_FACTS_PROMPT, NEWS_SCRIPT_PROMPT
from llm.structured import generate_structured
from news.scraper import Article, scrape_article
from script.duration import duration_targets
from script.schemas import ExtractedFacts, VideoScript


logger = get_logger(__name__)

MAX_ARTICLE_CHARS = 8000
DEFAULT_DURATION_SECONDS = 45


def extract_facts(article: Article) -> ExtractedFacts:
    prompt = NEWS_FACTS_PROMPT.format(
        title=article.title,
        source=article.source,
        text=article.text[:MAX_ARTICLE_CHARS],
    )
    return generate_structured(prompt, ExtractedFacts)


def generate_grounded_script(
    facts: ExtractedFacts, source: str, target_duration_seconds: int = DEFAULT_DURATION_SECONDS
) -> VideoScript:
    target_words, target_scenes = duration_targets(target_duration_seconds)
    prompt = NEWS_SCRIPT_PROMPT.format(
        headline=facts.headline,
        summary=facts.summary,
        key_points="\n".join(f"- {point}" for point in facts.key_points),
        entities=", ".join(facts.entities) or "none",
        source=source,
        target_words=target_words,
        target_scenes=target_scenes,
    )
    return generate_structured(prompt, VideoScript)


def generate_script_from_url(
    url: str, target_duration_seconds: int = DEFAULT_DURATION_SECONDS
) -> Tuple[VideoScript, List[str]]:
    article = scrape_article(url)
    logger.info("Scraped article: %s (%s), %d usable images", article.title, article.source, len(article.images))

    facts = extract_facts(article)
    logger.info("Extracted %d key points from article", len(facts.key_points))

    script = generate_grounded_script(facts, source=article.source, target_duration_seconds=target_duration_seconds)
    logger.info("Generated grounded script with %d scenes", len(script.scenes))
    return script, article.images
