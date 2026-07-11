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
    reading_queue: list[dict]
    daily_stats: dict


class GetWorkspaceUseCase:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    def execute(self) -> WorkspaceSummary:

        with self.uow:
            # 1. Today's Reviews
            now = datetime.utcnow()
            due_reviews = self.uow.reviews.list_due(as_of=now)
            
            # 2. Recent Entities
            recent_captures = self.uow.captures.list(limit=10)
            pinned_spaces = self.uow.collections.list(limit=5)
            recent_sources = self.uow.sources.list(limit=10)
            recent_concepts = self.uow.concepts.list(limit=10)
            recent_collections = self.uow.collections.list(limit=10)

            # 3. Activity Feed
            activity = self.uow.timeline.list(limit=20)

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
            ai_events = self.uow.timeline.list_by_event_type("AIAnalysisCompleted", limit=100)
            pending_proposals = []

            all_captures = self.uow.captures.list(limit=100)
            pending_captures = {c.id: c for c in all_captures if c.status.value == "PENDING"}

            for capture_id, capture in pending_captures.items():
                capture_events = [e for e in ai_events if e.aggregate_id == capture_id]
                if capture_events:
                    latest_event = capture_events[0]
                    payload = json.loads(latest_event.payload_json)
                    metadata = payload.get("metadata", {})
                    proposal = metadata.get("proposal")
                    if proposal:
                        pending_proposals.append(
                            {
                                "capture_id": str(capture_id),
                                "content": capture.content,
                                "proposal": proposal,
                                "occurred_at": latest_event.occurred_at,
                            }
                        )

            pending_proposals.sort(key=lambda x: x["occurred_at"], reverse=True)
            for p in pending_proposals:
                del p["occurred_at"]

            # 6. Continue Learning
            last_concept = None
            last_collection = None
            last_review = None
            last_interaction_time = None

            for event in activity:
                if event.event_type == "ReviewDue":
                    continue
                if not last_interaction_time:
                    last_interaction_time = event.occurred_at

                if not last_concept and event.aggregate_type == "Concept":
                    c = self.uow.concepts.get(event.aggregate_id)
                    if c:
                        last_concept = {"id": str(c.id), "title": c.title, "type": "Concept"}
                
                if not last_collection and event.aggregate_type == "Collection":
                    c = self.uow.collections.get(event.aggregate_id)
                    if c:
                        last_collection = {"id": str(c.id), "title": c.name, "type": "Collection"}
                
                if not last_review and event.aggregate_type == "Review":
                    r = self.uow.reviews.get(event.aggregate_id)
                    if r:
                        title = "Review Session"
                        if r.entity_type == "Concept":
                            rc = self.uow.concepts.get(r.entity_id)
                            if rc:
                                title = f"Review: {rc.title}"
                        last_review = {"id": str(r.id), "title": title, "type": "Review", "entity_id": str(r.entity_id)}

            time_since_str = None
            if last_interaction_time:
                diff = now - last_interaction_time
                if diff.total_seconds() < 3600:
                    mins = int(diff.total_seconds() / 60)
                    time_since_str = f"{mins}m ago"
                elif diff.total_seconds() < 86400:
                    hours = int(diff.total_seconds() / 3600)
                    time_since_str = f"{hours}h ago"
                else:
                    days = int(diff.total_seconds() / 86400)
                    time_since_str = f"{days}d ago"

            continue_learning = {
                "last_concept": last_concept,
                "last_collection": last_collection,
                "last_review": last_review,
                "time_since_last_interaction": time_since_str
            }

            # 7. Reading Queue
            reading_queue = []
            
            for dr in due_reviews[:3]:
                title = f"Due Review: {dr.entity_type}"
                if dr.entity_type == "Concept":
                    c = self.uow.concepts.get(dr.entity_id)
                    if c:
                        title = c.title
                reading_queue.append({
                    "id": str(dr.id),
                    "type": "Review",
                    "title": title,
                    "reason": "Scheduled Review",
                    "priority": 1
                })
            
            for c in recent_concepts[:3]:
                reading_queue.append({
                    "id": str(c.id),
                    "type": "Concept",
                    "title": c.title,
                    "reason": "Recently Created",
                    "priority": 2
                })
            
            for cap in [c for c in recent_captures if c.status.value == "PROCESSED"][:3]:
                reading_queue.append({
                    "id": str(cap.id),
                    "type": "Capture",
                    "title": cap.content[:30] + "...",
                    "reason": "Recently Processed",
                    "priority": 3
                })
            
            for col in recent_collections[:2]:
                reading_queue.append({
                    "id": str(col.id),
                    "type": "Collection",
                    "title": col.name,
                    "reason": "Recent Space",
                    "priority": 4
                })
                
            reading_queue.sort(key=lambda x: x["priority"])

            # 8. Daily Stats & Goal
            today = now.date()
            captures_today = sum(1 for c in all_captures if c.created_at.date() == today)
            reviews_completed_today = sum(
                1 for e in activity if e.event_type == "ReviewCompleted" and e.occurred_at.date() == today
            )
            all_concepts = self.uow.concepts.list(limit=100)
            concepts_today = sum(1 for c in all_concepts if c.created_at.date() == today)

            goal_max = 14
            current_progress = min(goal_max, reviews_completed_today + captures_today)
            goal_progress = (current_progress / goal_max) * 100

            daily_stats = {
                "captures_today": captures_today,
                "reviews_completed_today": reviews_completed_today,
                "concepts_today": concepts_today,
                "pending_proposals": len(pending_proposals),
                "goal_progress": round(goal_progress, 1),
            }

            return WorkspaceSummary(
                due_reviews=due_reviews[:5],
                recent_captures=recent_captures[:5],
                pinned_spaces=pinned_spaces,
                recent_sources=recent_sources[:5],
                activity=activity,
                graph_preview=graph_preview,
                recent_concepts=recent_concepts[:5],
                recent_collections=recent_collections[:5],
                pending_proposals=pending_proposals,
                continue_learning=continue_learning,
                reading_queue=reading_queue,
                daily_stats=daily_stats,
            )
