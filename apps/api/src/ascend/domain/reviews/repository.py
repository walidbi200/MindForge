from __future__ import annotations

from datetime import datetime
from typing import Protocol
from uuid import UUID

from ascend.domain.reviews.entity import Review


class ReviewRepository(Protocol):
    def save(self, review: Review) -> None:
        """Save a review to the repository."""
        ...

    def get(self, review_id: UUID) -> Review | None:
        """Retrieve a review by its ID."""
        ...

    def delete(self, review_id: UUID) -> None:
        """Delete a review from the repository."""
        ...

    def list(self) -> list[Review]:
        """List all reviews."""
        ...

    def list_due(self, as_of: datetime) -> list[Review]:
        """List all PENDING reviews where due_at <= as_of."""
        ...

    def list_by_entity(self, entity_id: UUID) -> list[Review]:
        """List all reviews for a specific entity."""
        ...
