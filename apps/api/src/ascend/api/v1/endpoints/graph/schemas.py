from uuid import UUID

from pydantic import BaseModel

from ascend.api.v1.endpoints.relationships.schemas import RelationshipResponse
from ascend.domain.relationships.entity import EntityType


class NodeResponse(BaseModel):
    id: UUID
    type: EntityType
    title: str


class GraphResponse(BaseModel):
    nodes: list[NodeResponse]
    relationships: list[RelationshipResponse]


class KnowledgeNeighborhoodResponse(BaseModel):
    center: dict
    concepts: list[dict]
    captures: list[dict]
    sources: list[dict]
    collections: list[dict]
    relationships: list[RelationshipResponse]


class DuplicateSuggestionResponse(BaseModel):
    concept_id: UUID
    title: str
    similarity_score: float
    reason: str


class KnowledgeRecommendationResponse(BaseModel):
    id: UUID
    type: str
    title: str
    reason: str
    score: float
