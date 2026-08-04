from llm.prompts import SIMPLE_SCRIPT_PROMPT
from llm.structured import generate_structured
from script.duration import duration_targets
from script.schemas import SimpleScene, SimpleScript


SCRIPT_CACHE = {}
DEFAULT_DURATION_SECONDS = 45

DEFAULT_SCENES = [
    SimpleScene(scene=1, text="Start small, stop overthinking", query="person thinking desk"),
    SimpleScene(scene=2, text="Take immediate action", query="person taking action"),
    SimpleScene(scene=3, text="Discipline builds success", query="person disciplined routine"),
    SimpleScene(scene=4, text="Focus matters more than motivation", query="person focused working"),
    SimpleScene(scene=5, text="Consistency wins", query="person consistent habit"),
]


def generate_script(topic: str, target_duration_seconds: int = DEFAULT_DURATION_SECONDS) -> list[SimpleScene]:
    cache_key = (topic, target_duration_seconds)
    if cache_key in SCRIPT_CACHE:
        return SCRIPT_CACHE[cache_key]

    target_words, target_scenes = duration_targets(target_duration_seconds)
    prompt = SIMPLE_SCRIPT_PROMPT.format(topic=topic, target_words=target_words, target_scenes=target_scenes)
    try:
        script = generate_structured(prompt, SimpleScript)
        scenes = script.scenes or list(DEFAULT_SCENES)
    except Exception:
        scenes = list(DEFAULT_SCENES)

    SCRIPT_CACHE[cache_key] = scenes
    return scenes
