from openai import OpenAI

from config import OPENROUTER_API_KEY


class OpenRouterClient:
    def __init__(self) -> None:
        self.client = (
            OpenAI(
                api_key=OPENROUTER_API_KEY,
                base_url="https://openrouter.ai/api/v1",
            )
            if OPENROUTER_API_KEY
            else None
        )

    def generate_text(self, prompt: str, model: str = "meta-llama/llama-3.1-8b-instruct") -> str:
        if self.client is None:
            raise RuntimeError("OPENROUTER_API_KEY is not configured")

        response = self.client.responses.create(
            model=model,
            input=prompt,
        )
        return (response.output_text or "").strip()
