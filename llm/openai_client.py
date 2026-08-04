from openai import OpenAI

from config import OPENAI_API_KEY


class OpenAIClient:
    def __init__(self) -> None:
        self.client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

    def generate_text(self, prompt: str, model: str = "gpt-4o-mini") -> str:
        if self.client is None:
            raise RuntimeError("OPENAI_API_KEY is not configured")

        response = self.client.responses.create(
            model=model,
            input=prompt,
        )
        return (response.output_text or "").strip()
