from pydantic import BaseModel, Field


class ExtractedFacts(BaseModel):
    headline: str
    summary: str
    key_points: list[str] = Field(default_factory=list)
    entities: list[str] = Field(default_factory=list)
    quotes: list[str] = Field(default_factory=list)


class ScriptScene(BaseModel):
    scene: int
    narration: str
    visual_prompt: str
    search_query: str


class VideoScript(BaseModel):
    title: str
    scenes: list[ScriptScene]


class SimpleScene(BaseModel):
    scene: int
    text: str
    query: str


class SimpleScript(BaseModel):
    scenes: list[SimpleScene]
