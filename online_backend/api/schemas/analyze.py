from pydantic import BaseModel


class AnalyzeRequest(BaseModel):
    text: str


class EntitiesResponse(BaseModel):
    persons: list[str]
    organizations: list[str]
    dates: list[str]
    laws: list[str]
    courts: list[str]
    judges: list[str]


class AnalyzeResponse(BaseModel):
    summary: str
    legal_issue: str
    holding: str
    reasoning: str
    entities: EntitiesResponse
