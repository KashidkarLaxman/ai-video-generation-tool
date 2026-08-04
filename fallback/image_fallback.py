from media.image_generator import generate_image


DEFAULT_VISUAL_PROMPT = "a calm abstract background, soft gradient colors, no text"


def generate_image_with_fallback(prompt: str, index: int, width: int = 1280, height: int = 720) -> str:
    try:
        return generate_image(prompt, index, width=width, height=height)
    except Exception:
        return generate_image(DEFAULT_VISUAL_PROMPT, index, width=width, height=height)
