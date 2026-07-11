from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass
class Concept:
    id: UUID
    title: str
    summary: str
    created_at: datetime
    updated_at: datetime
