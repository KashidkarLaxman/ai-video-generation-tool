from google import genai

from config import GOOGLE_GEN_AI_KEY


class GeminiClient:
    def __init__(self) -> None:
        self.client = genai.Client(api_key=GOOGLE_GEN_AI_KEY) if GOOGLE_GEN_AI_KEY else None

    def generate_text(self, prompt: str, model: str = "gemini-2.5-flash") -> str:
        if self.client is None:
            raise RuntimeError("GOOGLE_GEN_AI_KEY is not configured")

        response = self.client.models.generate_content(model=model, contents=prompt)
        return (response.text or "").strip()
