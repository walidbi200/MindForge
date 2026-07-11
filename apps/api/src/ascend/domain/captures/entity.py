from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from uuid import UUID


class CaptureStatus(str, Enum):
    PENDING = "PENDING"
    PROCESSED = "PROCESSED"


@dataclass
class Capture:
    id: UUID
    content: str
    created_at: datetime
    status: CaptureStatus = CaptureStatus.PENDING
