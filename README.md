# AI Video Generation Tool

An end-to-end Python pipeline that turns a topic or a news-article URL into a narrated video with synced captions — script generation, text-to-speech narration, visual sourcing, and video composition, all automated.

## How it works

1. **Script generation** — a custom multi-provider LLM router (Gemini, OpenAI, OpenRouter, Ollama, with automatic fallback between providers) generates a scene-by-scene script for the given topic or article.
2. **Narration** — `edge-tts` / `gTTS` synthesizes narration audio for each scene.
3. **Captions** — `faster-whisper` transcribes the narration for word-level synced captions (karaoke-style).
4. **Visuals** — a multi-tier sourcing cascade finds visuals for each scene: article images → web image search → Pexels stock photos → AI-generated images (Pollinations/Flux) → Pexels stock video, falling back automatically if a source fails or returns nothing.
5. **Composition** — `MoviePy` assembles the final video with transitions, captions, and landscape/portrait export, using `ThreadPoolExecutor` to process multiple scenes concurrently.

Two workflows are supported via a Streamlit UI:
- **Topic → Video**: direct generation from a topic prompt.
- **News Article → Video**: scrapes an article URL, generates a script, and lets you review/edit the script before rendering.

## Project structure

```
app.py                 # Streamlit UI
main.py                # CLI entry point (topic → video)
run_news_video.py       # CLI entry point (article URL → video)
config.py               # Environment/config loading

core/                   # Pipeline orchestration (create_video, news pipeline, state, logging)
llm/                    # Multi-provider LLM router + clients (Gemini, OpenAI, OpenRouter, Ollama)
script/                 # Script generation, duration planning, schemas
media/                  # Audio (TTS), transcription, image/video fetching & generation, visual provider cascade
video/                  # Clip building, subtitles, composition, transitions
news/                   # Article scraping
fallback/               # Image/video fallback sourcing
utils/                  # File management, retry logic, text cleaning
```

## Tech stack

Python, Streamlit, MoviePy, faster-whisper, edge-tts/gTTS, Google Gemini API, OpenAI API, OpenRouter, Ollama, Pexels API, Pollinations/Flux image generation.

## Setup

```bash
pip install -r requirements.txt
```

Create a `.env` file with your API keys (see `config.py` for the expected variables): `GOOGLE_GEN_AI_KEY`, `OPENAI_API_KEY`, `OPENROUTER_API_KEY`, `PEXELS_API_KEY`, `OLLAMA_BASE_URL`, `OLLAMA_MODEL`.

```bash
streamlit run app.py
```

## Note

This is a personal project built to explore practical LLM application design — multi-provider fallback routing, agentic-style multi-stage pipelines, and automated media generation.
