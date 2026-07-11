from typing import Protocol
from uuid import UUID
from ascend.domain.captures.entity import Capture

class CaptureRepository(Protocol):
    def save(self, capture: Capture) -> None:
        ...

    def get(self, capture_id: UUID) -> Capture | None:
        ...

    def list(self) -> list[Capture]:
        ...

    def delete(self, capture_id: UUID) -> None:
        ...
