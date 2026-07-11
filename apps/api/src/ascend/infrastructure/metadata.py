from sqlmodel import SQLModel

from ascend.infrastructure.models.capture import CaptureModel  # noqa: F401
from ascend.infrastructure.models.collection import CollectionModel, MembershipModel  # noqa: F401
from ascend.infrastructure.models.concept import ConceptModel  # noqa: F401
from ascend.infrastructure.models.relationship import RelationshipModel  # noqa: F401
from ascend.infrastructure.models.source import SourceModel  # noqa: F401
from ascend.infrastructure.models.timeline_event import TimelineEventModel  # noqa: F401

# This file serves as the permanent metadata location for Alembic.
# All domain models should be imported here when they are created,
# so Alembic can detect them for autogenerating migrations.

metadata = SQLModel.metadata
