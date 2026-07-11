from pydantic import BaseModel, Field


class ConceptSuggestionResponse(BaseModel):
    name: str
    description: str
    confidence: float


class RelationshipSuggestionResponse(BaseModel):
    from_entity: str = Field(alias="from")
    to_entity: str = Field(alias="to")
    relationship_type: str = Field(alias="type")
    confidence: float


class AnalyzeCaptureResponse(BaseModel):
    summary: str
    concepts: list[ConceptSuggestionResponse] = Field(default_factory=list)
    relationships: list[RelationshipSuggestionResponse] = Field(default_factory=list)
    questions: list[str] = Field(default_factory=list)
