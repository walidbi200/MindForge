import re
import unicodedata
from dataclasses import dataclass
from uuid import UUID

from ascend.application.uow import UnitOfWork
from ascend.domain.concepts.entity import Concept


@dataclass
class DuplicateSuggestion:
    concept: Concept
    similarity_score: float
    reason: str


class CheckDuplicatesUseCase:
    """
    Lightweight duplicate detection.
    For this checkpoint, we detect duplicates purely by exact or high textual overlap
    in titles, rather than full semantic vectors or graph similarity logic,
    to remain within the frozen architecture without new bounded contexts.
    """

    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    def _normalize(self, text: str) -> str:
        # Normalize unicode to ASCII, remove punctuation, lowercase, strip extra whitespace
        text = unicodedata.normalize("NFKD", text).encode("ASCII", "ignore").decode("ASCII")
        text = re.sub(r"[^\w\s]", "", text)
        text = re.sub(r"\s+", " ", text)
        return text.strip().lower()

    def execute(self, title: str, exclude_id: UUID | None = None) -> list[DuplicateSuggestion]:
        if not title or len(title.strip()) < 3:
            return []

        suggestions = []
        with self.uow:
            # We fetch a slightly broader match to check textually
            # A more advanced version would use graph neighborhood overlap,
            # but title overlap is sufficient for demonstration.
            # Using partial match
            concepts = self.uow.concepts.list(limit=100) # Check recent 100 concepts for duplicates

            title_norm = self._normalize(title)

            for c in concepts:
                if exclude_id and c.id == exclude_id:
                    continue

                c_title_norm = self._normalize(c.title)

                # Exact match
                if c_title_norm == title_norm:
                    suggestions.append(DuplicateSuggestion(concept=c, similarity_score=1.0, reason="Exact title match"))
                # Substring match
                elif title_norm in c_title_norm or c_title_norm in title_norm:
                    import difflib
                    ratio = difflib.SequenceMatcher(None, title_norm, c_title_norm).ratio()
                    if ratio > 0.7:
                        suggestions.append(
                            DuplicateSuggestion(concept=c, similarity_score=ratio, reason="Similar title match")
                        )
                else:
                    import difflib
                    ratio = difflib.SequenceMatcher(None, title_norm, c_title_norm).ratio()
                    if ratio > 0.8:
                        suggestions.append(
                            DuplicateSuggestion(concept=c, similarity_score=ratio, reason="Fuzzy title match")
                        )

        # Sort by highest similarity
        suggestions.sort(key=lambda s: s.similarity_score, reverse=True)
        return suggestions[:5]
