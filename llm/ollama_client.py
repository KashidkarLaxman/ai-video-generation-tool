import requests

from config import OLLAMA_BASE_URL, OLLAMA_MODEL


class OllamaClient:
    def generate_text(self, prompt: str, model: str = OLLAMA_MODEL) -> str:
        response = requests.post(
            f"{OLLAMA_BASE_URL}/api/generate",
            json={"model": model, "prompt": prompt, "stream": False},
            timeout=120,
        )
        response.raise_for_status()
        return response.json().get("response", "").strip()
