# Changelog

All notable changes to MindForge will be documented in this file.

The format is inspired by Keep a Changelog, and this project uses small release candidates for each checkpoint.

## [Unreleased]

## [0.0.12] - 2026-07-11

### Added
- `Collection` and `Membership` domain entities, enabling structural grouping of knowledge.
- Unique constraints: `Collection.name` (UNIQUE) and `Membership(collection_id, entity_id, entity_type)` (UNIQUE).
- Strict validation rules: collection deletion is blocked if memberships are active.
- Reusable `cleanup_entity_memberships` helper, ensuring entity deletions clean up active memberships.
- API endpoints under `/api/v1/collections` managing collections and membership entities.
- Frontend view `CollectionsView.tsx` with a standard metadata form and member list dashboard.

## [0.0.11] - 2026-07-11

### Added
- `Source` domain entity and `SourceType` enum representing origins like `WEB_ARTICLE`, `BOOK`, `PDF`.
- `SourceModel` mapping to SQLite table `sources` with indexes on type, uri, and title.
- `CreateSourceUseCase`, `GetSourceUseCase`, `UpdateSourceUseCase`, `DeleteSourceUseCase`, and `ListSourcesUseCase`.
- Validation preventing deletion of any `Source` that has active relationships.
- Support for `Source` nodes in relationship creations and graph traversals.
- API endpoints under `/api/v1/sources` with filtering and pagination.
- Frontend view `SourcesView.tsx` with a standard metadata CRUD form.

## [0.0.10] - 2026-07-11

### Added
- deterministic read-only graph traversal use cases (`GetRelationshipGraphUseCase`, `GetEntityNeighborhoodUseCase`, `GetConnectedEntitiesUseCase`).
- Traversal boundaries: max depth 2, max node returns 100, and cycle-protection.
- API endpoints `/api/v1/graph/entity/{id}`, `/api/v1/graph/neighborhood/{id}`, and `/api/v1/graph/path-preview/{id}`.
- Lightweight `GraphExplorer` React view for visualization.

## [0.0.9] - 2026-07-11

### Added
- strongly-typed `Relationship` entity with validation rules preventing self-loops and duplicate edges.
- `RelationshipModel` (SQLite) with composite indexes.
- Deletion checks on `Capture` preventing delete if relationships exist.
- API endpoints `/api/v1/relationships`.

## [0.0.8] - 2026-07-11

### Added
- Sync Event Bus for MindForge publishing events inside UoW transactions.
- Timeline event listener writing to `TimelineEventModel`.
- API endpoints `/api/v1/timeline`.

## [0.0.7] - 2026-07-11

### Added

- `Concept` domain entity to represent processed knowledge.
- Concept Repository and SQLModel persistence (`ConceptModel`).
- Unit of Work integration for `concepts`.
- `Create Concept` and `Get Concept` application use cases.
- `POST /api/v1/concepts` and `GET /api/v1/concepts/{id}` endpoints.

## [0.0.5] - 2026-07-11

### Added

- GitHub Actions CI pipeline (.github/workflows/ci.yml).
- Testing foundation using `pytest` and `sqlite:///:memory:` with test cases for the Capture vertical slice.
- Linting and formatting configurations using `ruff`.
- Makefile and standard `.editorconfig` / `.pre-commit-config.yaml` for developer experience.

## [0.0.4] - 2026-07-11

### Added

- `Capture` domain entity, repository protocol, and SQLModel infrastructure.
- `CreateCapture` and `GetCapture` use cases.
- Dedicated mapping and HTTP transport schemas.
- `get_uow` FastAPI dependency injection.
- End-to-end `/api/v1/captures` POST and GET endpoints.
- Auto-generated alembic migration for `captures` table.

### Added

- Initial planning documents.
- Project North Star.
- Architecture principles.
- Definition of Done.
- Milestone 1 checkpoint roadmap.
- Contribution guide.
- Project status tracker.

## [0.0.3] - 2026-07-11

### Added

- SQLModel and Alembic dependencies.
- Database URL configuration and permanent metadata location.
- SQLModel engine, session factory, and Unit of Work interfaces.
- Alembic migration initialization and initial setup script.
- Minimal database health check endpoint (`/api/v1/health/db`).

### Changed

- Updated API and frontend shell versions to `0.0.3`.


## [0.0.2] - 2026-07-11

### Added

- FastAPI application startup skeleton.
- Centralized settings, logging, and error handling.
- Versioned `/api/v1/health` endpoint.
- React frontend shell with sidebar placeholder.
- React frontend connection to backend health check.

## [0.0.1] - TBD

### Added

- Repository foundation.
- Docker Compose foundation.
- Backend skeleton.
- Frontend skeleton.
