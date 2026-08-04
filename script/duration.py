WORDS_PER_SECOND = 2.4
SECONDS_PER_SCENE = 7
MIN_SCENES = 3
MAX_SCENES = 10


def duration_targets(target_duration_seconds: int):
    target_words = max(30, round(target_duration_seconds * WORDS_PER_SECOND))
    target_scenes = min(MAX_SCENES, max(MIN_SCENES, round(target_duration_seconds / SECONDS_PER_SCENE)))
    return target_words, target_scenes
