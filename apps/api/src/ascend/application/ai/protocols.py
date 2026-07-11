from typing import Protocol

from pydantic import BaseModel, Field


class AIConceptSuggestion(BaseModel):
    name: str
    description: str
    confidence: float


class AIRelationshipSuggestion(BaseModel):
    from_entity: str = Field(alias="from")
    to_entity: str = Field(alias="to")
    relationship_type: str = Field(alias="type")
    confidence: float


class AIResponse(BaseModel):
    summary: str
    concepts: list[AIConceptSuggestion] = Field(default_factory=list)
    relationships: list[AIRelationshipSuggestion] = Field(default_factory=list)
    questions: list[str] = Field(default_factory=list)
    metadata: dict = Field(default_factory=dict)


class AIRequest(BaseModel):
    system_prompt: str
    user_prompt: str
    temperature: float = 0.7
    max_tokens: int = 2000
    metadata: dict = Field(default_factory=dict)
    # The expected response schema (Pydantic model) is handled by the AIService implementation
    # mapping this request to the provider's specific structural requirements.


class AIService(Protocol):
    def generate(self, request: AIRequest) -> AIResponse:
        """Generates an AI response for the given request."""
        ...
