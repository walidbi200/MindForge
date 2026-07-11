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
