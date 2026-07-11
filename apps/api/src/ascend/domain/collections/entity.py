from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from ascend.domain.relationships.entity import EntityType


@dataclass
class Collection:
    id: UUID
    name: str
    description: str
    color: str
    icon: str
    created_at: datetime
    updated_at: datetime
    metadata_json: str = "{}"


@dataclass
class Membership:
    id: UUID
    collection_id: UUID
    entity_id: UUID
    entity_type: EntityType
    created_at: datetime
    position: int = 0
