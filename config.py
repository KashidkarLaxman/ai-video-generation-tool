import os

from dotenv import load_dotenv


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
TEMP_DIR = os.path.join(BASE_DIR, "temp")
LOG_DIR = os.path.join(BASE_DIR, "logs")

load_dotenv(os.path.join(BASE_DIR, ".env"))

GOOGLE_GEN_AI_KEY = os.getenv("GOOGLE_GEN_AI_KEY", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY", "")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.1:8b")
LLM_PROVIDER_ORDER = [
    provider.strip().lower()
    for provider in os.getenv(
        "LLM_PROVIDER_ORDER",
        "gemini,openai,openrouter,ollama",
    ).split(",")
    if provider.strip()
]


def ensure_directories() -> None:
    for path in (OUTPUT_DIR, TEMP_DIR, LOG_DIR):
        os.makedirs(path, exist_ok=True)
