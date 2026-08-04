from core.logger import get_logger
from config import LLM_PROVIDER_ORDER
from llm.gemini_client import GeminiClient
from llm.ollama_client import OllamaClient
from llm.openai_client import OpenAIClient
from llm.openrouter_client import OpenRouterClient


logger = get_logger(__name__)

CLIENTS = {
    "gemini": GeminiClient,
    "openai": OpenAIClient,
    "openrouter": OpenRouterClient,
    "ollama": OllamaClient,
}


def generate_text(prompt: str, default: str) -> str:
    for provider in LLM_PROVIDER_ORDER:
        client_cls = CLIENTS.get(provider)
        if client_cls is None:
            continue

        try:
            return client_cls().generate_text(prompt)
        except Exception as exc:
            logger.warning("%s failed: %s", provider, exc)

    return default
