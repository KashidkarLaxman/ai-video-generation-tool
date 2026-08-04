import json
from typing import Type, TypeVar

import json_repair
from pydantic import BaseModel, ValidationError

from core.logger import get_logger
from llm.router import generate_text


logger = get_logger(__name__)

T = TypeVar("T", bound=BaseModel)

MAX_ATTEMPTS = 3


def _extract_json_payload(content: str) -> str:
    if "```" in content:
        parts = content.split("```")
        if len(parts) > 1:
            content = parts[1]
            if content[:4].lower().startswith("json"):
                content = content[4:]

    obj_start, obj_end = content.find("{"), content.rfind("}") + 1
    arr_start, arr_end = content.find("["), content.rfind("]") + 1

    if obj_start != -1 and obj_end > obj_start:
        return content[obj_start:obj_end]
    if arr_start != -1 and arr_end > arr_start:
        return content[arr_start:arr_end]

    raise ValueError("No JSON object or array found in response")


def generate_structured(prompt: str, schema: Type[T]) -> T:
    schema_prompt = (
        f"{prompt}\n\n"
        "Respond with ONLY valid JSON matching this schema. "
        "No prose, no markdown fences, no explanation.\n"
        f"{json.dumps(schema.model_json_schema())}"
    )

    last_error: Exception = ValueError("LLM returned no content")

    for attempt in range(1, MAX_ATTEMPTS + 1):
        content = generate_text(schema_prompt, default="")
        if not content:
            last_error = ValueError("LLM returned no content")
            continue

        try:
            payload = _extract_json_payload(content)
        except ValueError as exc:
            last_error = exc
            logger.warning("Attempt %d: no JSON found in response: %s", attempt, exc)
            continue

        try:
            return schema.model_validate_json(payload)
        except ValidationError:
            pass

        # The model produced JSON-shaped but syntactically broken output
        # (e.g. an unescaped quote inside a copied string) - repair it
        # instead of discarding an otherwise-good response.
        try:
            repaired = json_repair.repair_json(payload)
            return schema.model_validate_json(repaired)
        except ValidationError as exc:
            last_error = exc
            logger.warning("Attempt %d: structured output failed validation: %s", attempt, exc)

    raise last_error
