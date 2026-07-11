from uuid import UUID

from pydantic import BaseModel

from ascend.application.ai.apply_analysis import ApplyAIAnalysisUseCase
from ascend.application.ai.protocols import AIConceptSuggestion, AIRelationshipSuggestion
from ascend.application.uow import UnitOfWork


class ConceptProposal(BaseModel):
    name: str
    description: str
    confidence: float


class RelationshipProposal(BaseModel):
    from_entity: str
    to_entity: str
    relationship_type: str
    confidence: float


class ApplyProposalUseCase:
    """
    Orchestrates applying a user-approved AI proposal to the system.
    Delegates to the existing ApplyAIAnalysisUseCase to handle entity creation.
    """

    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    def execute(
        self,
        capture_id: UUID,
        concepts: list[ConceptProposal],
        relationships: list[RelationshipProposal],
        collections: list[str],
        review_suggestion: str | None = None,
    ) -> None:
        delegate = ApplyAIAnalysisUseCase(self.uow)

        ai_concepts = [
            AIConceptSuggestion(name=c.name, description=c.description, confidence=c.confidence) for c in concepts
        ]
        ai_relationships = [
            AIRelationshipSuggestion(
                **{"from": r.from_entity, "to": r.to_entity, "type": r.relationship_type}, confidence=r.confidence
            )
            for r in relationships
        ]

        delegate.execute(
            capture_id=capture_id,
            concepts=ai_concepts,
            relationships=ai_relationships,
            collections=collections,
            review_suggestion=review_suggestion,
        )
