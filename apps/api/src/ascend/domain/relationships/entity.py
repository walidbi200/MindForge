from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from uuid import UUID


class EntityType(str, Enum):
    CAPTURE = "Capture"
    CONCEPT = "Concept"
    SOURCE = "Source"


class CreatorType(str, Enum):
    SYSTEM = "SYSTEM"
    USER = "USER"
    AI = "AI"
    IMPORT = "IMPORT"
    SYNC = "SYNC"


class RelationshipType(str, Enum):
    RELATED_TO = "RELATED_TO"
    DERIVED_FROM = "DERIVED_FROM"
    REFERENCES = "REFERENCES"
    SUPPORTS = "SUPPORTS"
    CONTRADICTS = "CONTRADICTS"
    SUMMARIZES = "SUMMARIZES"
    EXPLAINS = "EXPLAINS"
    GENERATED_FROM = "GENERATED_FROM"
    TAGGED_AS = "TAGGED_AS"


@dataclass
class Relationship:
    id: UUID
    from_id: UUID
    from_type: EntityType
    to_id: UUID
    to_type: EntityType
    relationship_type: RelationshipType
    confidence: float
    created_by: CreatorType
    created_at: datetime
    metadata_json: str
