from typing import List, Tuple

import numpy as np
from PIL import Image, ImageDraw, ImageFont


FONT_CANDIDATES = (
    "Arial.ttf",
    "/System/Library/Fonts/Supplemental/Arial.ttf",
    "/Library/Fonts/Arial.ttf",
)


def _load_font(size: int) -> ImageFont.ImageFont:
    for candidate in FONT_CANDIDATES:
        try:
            return ImageFont.truetype(candidate, size)
        except Exception:
            continue
    return ImageFont.load_default()


def _wrap_to_width(draw: ImageDraw.ImageDraw, text: str, font, max_width: int) -> List[str]:
    words = text.split()
    lines: List[str] = []
    current = ""

    for word in words:
        candidate = f"{current} {word}".strip()
        if not current or draw.textlength(candidate, font=font) <= max_width:
            current = candidate
        else:
            lines.append(current)
            current = word

    if current:
        lines.append(current)

    return lines or [text]


def create_subtitle_image(text: str, width: int = 1280, font_size: int = 44) -> np.ndarray:
    padding = 40
    line_height = int(font_size * 1.3)

    probe_draw = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    font = _load_font(font_size)
    lines = _wrap_to_width(probe_draw, text, font, width - 2 * padding)

    height = line_height * len(lines) + padding
    image = Image.new("RGB", (width, height), color=(0, 0, 0))
    draw = ImageDraw.Draw(image)

    y = (height - line_height * len(lines)) // 2
    for line in lines:
        line_width = draw.textlength(line, font=font)
        x = (width - line_width) // 2
        draw.text((x, y), line, font=font, fill=(255, 255, 0))
        y += line_height

    return np.array(image)


def _wrap_words_with_indices(
    draw: ImageDraw.ImageDraw, words: List[str], font, max_width: int
) -> List[List[Tuple[int, str]]]:
    lines: List[List[Tuple[int, str]]] = []
    current: List[Tuple[int, str]] = []
    current_text = ""

    for index, word in enumerate(words):
        candidate = f"{current_text} {word}".strip()
        if not current_text or draw.textlength(candidate, font=font) <= max_width:
            current.append((index, word))
            current_text = candidate
        else:
            lines.append(current)
            current = [(index, word)]
            current_text = word

    if current:
        lines.append(current)

    return lines or [[(i, w) for i, w in enumerate(words)]]


def create_karaoke_subtitle_image(
    words: List[str],
    active_index: int,
    width: int = 1280,
    font_size: int = 44,
) -> np.ndarray:
    padding = 40
    line_height = int(font_size * 1.3)

    probe_draw = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    font = _load_font(font_size)
    lines = _wrap_words_with_indices(probe_draw, words, font, width - 2 * padding)

    height = line_height * len(lines) + padding
    image = Image.new("RGB", (width, height), color=(0, 0, 0))
    draw = ImageDraw.Draw(image)

    y = (height - line_height * len(lines)) // 2
    for line in lines:
        line_text = " ".join(word for _, word in line)
        line_width = draw.textlength(line_text, font=font)
        x = (width - line_width) // 2

        for index, word in line:
            color = (255, 70, 70) if index == active_index else (255, 255, 0)
            draw.text((x, y), word, font=font, fill=color)
            x += draw.textlength(word + " ", font=font)

        y += line_height

    return np.array(image)
