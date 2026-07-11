from uuid import UUID

from pydantic import BaseModel

from ascend.api.v1.endpoints.captures.schemas import CaptureResponse
from ascend.api.v1.endpoints.collections.schemas import CollectionResponse
from ascend.api.v1.endpoints.concepts.schemas import ConceptResponse
from ascend.api.v1.endpoints.reviews.schemas import ReviewResponse
from ascend.api.v1.endpoints.sources.schemas import SourceResponse
from ascend.api.v1.endpoints.timeline.schemas import TimelineEventResponse


class GraphPreviewNode(BaseModel):
    id: str
    from_id: str
    to_id: str
    type: str


class ConceptSuggestionResponse(BaseModel):
    name: str
    description: str
    confidence: float


class RelationshipSuggestionResponse(BaseModel):
    from_entity: str
    to_entity: str
    relationship_type: str
    confidence: float


class AIProposalResponse(BaseModel):
    summary: str
    concepts: list[ConceptSuggestionResponse]
    relationships: list[RelationshipSuggestionResponse]
    collections: list[str]
    review_suggestion: str | None = None


class PendingProposalResponse(BaseModel):
    capture_id: UUID
    content: str
    proposal: AIProposalResponse


class ContinueLearningResponse(BaseModel):
    last_concept: dict | None = None
    last_collection: dict | None = None
    last_review: dict | None = None
    time_since_last_interaction: str | None = None


class ReadingQueueItem(BaseModel):
    id: UUID
    type: str
    title: str
    reason: str
    priority: int


class DailyStatsResponse(BaseModel):
    captures_today: int
    reviews_completed_today: int
    concepts_today: int
    pending_proposals: int
    goal_progress: float


class WorkspaceSummaryResponse(BaseModel):
    due_reviews: list[ReviewResponse]
    recent_captures: list[CaptureResponse]
    pinned_spaces: list[CollectionResponse]
    recent_sources: list[SourceResponse]
    activity: list[TimelineEventResponse]
    graph_preview: list[GraphPreviewNode]
    recent_concepts: list[ConceptResponse]
    recent_collections: list[CollectionResponse]
    pending_proposals: list[PendingProposalResponse]
    continue_learning: ContinueLearningResponse | None = None
    reading_queue: list[ReadingQueueItem]
    daily_stats: DailyStatsResponse


class SearchResultResponse(BaseModel):
    id: UUID
    type: str
    title: str
    snippet: str


class ProcessCaptureRequest(BaseModel):
    content: str


class ProcessCaptureResponse(BaseModel):
    capture_id: UUID
    proposal: AIProposalResponse


class ApplyProposalRequest(BaseModel):
    capture_id: UUID
    proposal: AIProposalResponse
