SIMPLE_SCRIPT_PROMPT = """
Create a short video script about this topic, narrated the way an engaging
YouTube explainer would present it to camera - not a flat list of facts.
Open with a hook, use natural spoken language, and connect scenes with
transitions rather than disconnected statements.

Each scene needs two fields:
- "text": concise spoken narration text, in that explainer voice
- "query": 3 to 5 words for a stock video search engine. Must be visual,
  focus on a person and action, and include the main subject as a literal
  keyword. No questions, no long sentences.

Target length: about {target_words} words of narration in total, told across
about {target_scenes} scenes.

Topic:
{topic}

Return JSON with:
- "scenes": array of objects, each with "scene" (integer), "text", and "query"
"""

NEWS_FACTS_PROMPT = """
You are extracting factual content from a news article for a short video script.
Only use information present in the article text below. Do not add outside
knowledge, speculation, or anything not stated in the text.

Return JSON with:
- "headline": a short factual headline (max 12 words)
- "summary": a neutral 2 to 3 sentence summary of the article
- "key_points": 3 to 6 short factual bullet points, each grounded in the article text
- "entities": notable people, places, or organizations named in the article
- "quotes": a list of direct quotes copied verbatim from the article, empty
  list if none exist. Include only the quotes themselves, no commentary or
  notes about them. Do not include quotation mark characters in the quote
  text itself - the JSON string quoting already marks it as a quote

Article title: {title}
Article source: {source}
Article text:
{text}
"""

NEWS_SCRIPT_PROMPT = """
Write this as a news reporter or YouTube explainer would present it on
camera - telling the story to a viewer, not reading a dry encyclopedia
summary.

Style:
- Open with a hook: a striking fact, a question, or a "here's what
  happened" framing. Do not open with a flat textbook sentence like
  "X happened in year Y."
- Write like natural spoken language: contractions are fine, vary sentence
  length, use short punchy sentences for emphasis where it fits.
- Connect scenes into one flowing story using the kind of transitions a
  reporter uses ("But here's where it gets interesting...", "That changed
  when...", "Here's why that matters..."), not a disconnected list of facts.
- End with a closing line that wraps the story up - a takeaway or a final
  beat - rather than trailing off after the last fact.
- The delivery style is yours to shape. The facts are not: use ONLY the
  facts listed below, and do not invent numbers, quotes, or claims that
  are not listed.

Each scene needs three fields:
- "narration": 1 to 2 spoken sentences, in the reporter/explainer voice
  described above.
- "visual_prompt": a concrete, descriptive prompt for an AI image
  generator depicting that scene: specific subjects, setting, mood,
  grounded in this story's own subject matter. Do not request text or
  captions inside the image itself.
- "search_query": 3 to 5 words for a stock photo/video search engine.
  It MUST include the main visible subject of the scene as a literal
  keyword (the physical object, place, or thing being discussed - not
  filler words like "a photo of" or "a scene showing"). This is used
  verbatim as a search query, so lead with the subject noun.

Do not describe named real individuals photorealistically in
"visual_prompt" or "search_query". If a scene involves a specific named
person, depict a relevant setting, object, or symbolic detail from this
story's own subject matter instead of their likeness - do not reuse a
generic placeholder scene unrelated to the story.

Naturally attribute the source in the first or last scene by mentioning
"{source}".

Target length: about {target_words} words of narration in total, told
across about {target_scenes} scenes.

Headline: {headline}
Summary: {summary}
Key points:
{key_points}
Entities: {entities}

Return JSON with:
- "title": short video title
- "scenes": array of objects, each with "scene" (integer), "narration",
  "visual_prompt", and "search_query"
"""
