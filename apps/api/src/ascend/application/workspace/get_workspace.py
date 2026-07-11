import json
from dataclasses import dataclass
from datetime import datetime

from ascend.application.uow import UnitOfWork
from ascend.domain.captures.entity import Capture
from ascend.domain.collections.entity import Collection
from ascend.domain.concepts.entity import Concept
from ascend.domain.reviews.entity import Review
from ascend.domain.sources.entity import Source
from ascend.infrastructure.models.timeline_event import TimelineEventModel


@dataclass(frozen=True)
class WorkspaceSummary:
    due_reviews: list[Review]
    recent_captures: list[Capture]
    pinned_spaces: list[Collection]
    recent_sources: list[Source]
    activity: list[TimelineEventModel]
    graph_preview: list[dict]
    recent_concepts: list[Concept]
    recent_collections: list[Collection]
    pending_proposals: list[dict]
    continue_learning: dict | None
    daily_stats: dict


class GetWorkspaceUseCase:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    def execute(self) -> WorkspaceSummary:

        with self.uow:
            # 1. Today's Reviews
            now = datetime.utcnow()
            due_reviews = self.uow.reviews.list_due(as_of=now)
            due_reviews = due_reviews[:5]

            # 2. Recent Entities
            recent_captures = self.uow.captures.list(limit=5)
            pinned_spaces = self.uow.collections.list(limit=5)
            recent_sources = self.uow.sources.list(limit=5)
            recent_concepts = self.uow.concepts.list(limit=5)
            recent_collections = self.uow.collections.list(limit=5)

            # 3. Activity Feed
            activity = self.uow.timeline.list(limit=10)

            # 4. Graph Preview
            recent_rels = self.uow.relationships.list(limit=10)
            graph_preview = [
                {
                    "id": str(r.id),
                    "from_id": str(r.from_id),
                    "to_id": str(r.to_id),
                    "type": r.relationship_type.value,
                }
                for r in recent_rels
            ]

            # 5. Pending Proposals
            # Fetch AIAnalysisCompleted events to find proposals for pending captures
            ai_events = self.uow.timeline.list_by_event_type("AIAnalysisCompleted", limit=100)
            pending_proposals = []
            
            # Find all pending captures
            all_captures = self.uow.captures.list(limit=100)
            pending_captures = {c.id: c for c in all_captures if c.status.value == "PENDING"}
            
            for capture_id, capture in pending_captures.items():
                # Find the most recent AIAnalysisCompleted event for this capture
                capture_events = [e for e in ai_events if e.aggregate_id == capture_id]
                if capture_events:
                    latest_event = capture_events[0]
                    payload = json.loads(latest_event.payload_json)
                    metadata = payload.get("metadata", {})
                    proposal = metadata.get("proposal")
                    if proposal:
                        pending_proposals.append({
                            "capture_id": str(capture_id),
                            "content": capture.content,
                            "proposal": proposal,
                            "occurred_at": latest_event.occurred_at
                        })
            
            # Sort pending proposals by occurred_at desc
            pending_proposals.sort(key=lambda x: x["occurred_at"], reverse=True)
            # Remove datetime from dict before returning to avoid issues with schemas if not needed
            for p in pending_proposals:
                del p["occurred_at"]

            # 6. Continue Learning
            continue_learning = None
            for event in activity:
                # Find the most recent read or interaction event (for now, any source/collection creation or review)
                # This could be more sophisticated later
                if event.aggregate_type in ["Source", "Collection", "Review"] and event.event_type != "ReviewDue":
                    continue_learning = {
                        "id": str(event.aggregate_id),
                        "type": event.aggregate_type,
                        "title": "Continue your recent work",
                        "event_type": event.event_type
                    }
                    # We might want to look up the actual title if needed, but the frontend can render generically 
                    # or we can fetch the title here:
                    if event.aggregate_type == "Source":
                        source = self.uow.sources.get(event.aggregate_id)
                        if source:
                            continue_learning["title"] = source.title
                            break
                    elif event.aggregate_type == "Collection":
                        collection = self.uow.collections.get(event.aggregate_id)
                        if collection:
                            continue_learning["title"] = collection.name
                            break
                    elif event.aggregate_type == "Review":
                        continue_learning["title"] = "Review Session"
                        break

            # 7. Daily Stats & Goal
            today = now.date()
            captures_today = sum(1 for c in all_captures if c.created_at.date() == today)
            
            # Use timeline to count completed reviews today
            reviews_completed_today = sum(
                1 for e in activity if e.event_type == "ReviewCompleted" and e.occurred_at.date() == today
            )
            
            all_concepts = self.uow.concepts.list(limit=100)
            concepts_today = sum(1 for c in all_concepts if c.created_at.date() == today)
            
            # Goal logic: 10 reviews, 3 captures, 1 AI proposal processed
            # Let's say goal max is 14 items
            goal_max = 14
            current_progress = min(goal_max, reviews_completed_today + captures_today)
            goal_progress = (current_progress / goal_max) * 100

            daily_stats = {
                "captures_today": captures_today,
                "reviews_completed_today": reviews_completed_today,
                "concepts_today": concepts_today,
                "pending_proposals": len(pending_proposals),
                "goal_progress": round(goal_progress, 1)
            }

            return WorkspaceSummary(
                due_reviews=due_reviews,
                recent_captures=recent_captures,
                pinned_spaces=pinned_spaces,
                recent_sources=recent_sources,
                activity=activity,
                graph_preview=graph_preview,
                recent_concepts=recent_concepts,
                recent_collections=recent_collections,
                pending_proposals=pending_proposals,
                continue_learning=continue_learning,
                daily_stats=daily_stats
            )
