from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

@dataclass
class Capture:
    id: UUID
    content: str
    created_at: datetime
