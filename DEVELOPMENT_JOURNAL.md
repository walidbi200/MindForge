# MindForge Development Journal

## Introduction

MindForge is a knowledge-first personal operating system designed to act as a system of record and learning engine for human intelligence. The core philosophy is to optimize for deliberate deep work and long-term knowledge retention.

## Architecture Overview

MindForge follows a strict, layered modular monolith architecture:
- **Domain Layer:** Pure business entities and domain events.
- **Application Layer:** Core workflow orchestrators (Use Cases) governing transaction boundaries and service coordination.
- **Infrastructure Layer:** Database connections (SQLModel, SQLite), repositories, external APIs, and the synchronous Event Bus.
- **API Layer:** FastAPI HTTP endpoints, routing, and Pydantic validation schemas.
- **Web UI:** React + Vite + TypeScript frontend.

## Development Rules

**Core Philosophy:** Build → Verify → Learn → Adjust → Continue
- Real implementation is the reviewer, not architecture speculation.
- Keep the architecture frozen unless implementation proves a change is necessary.
- Prefer simple solutions over premature abstractions.
- Build vertical slices end-to-end.
- Verify every checkpoint before continuing.
- Keep documentation proportional to what actually exists.

## Checkpoint 1: Repository Foundation
- **Goal:** Initialize the monorepo structure.
- **Summary:** Configured the `uv` package manager, React skeleton, and basic Docker orchestration.
- **Verification:** Docker builds and containers start successfully without restart loops.

## Checkpoint 2: FastAPI Skeleton
- **Goal:** Establish the application foundation.
- **Summary:** Set up the FastAPI application entrypoint, versioned routing, structured JSON logging, and centralized error handling.
- **Verification:** `GET /api/v1/health` returns HTTP 200. React successfully communicates with the backend.

## Checkpoint 3: Persistence Foundation
- **Goal:** Establish the database infrastructure.
- **Summary:** Integrated SQLModel and Alembic with a SQLite database. Implemented the base database engine, session factory, and a non-wired Unit of Work pattern.
- **Verification:** Initial migration generated and applied. `GET /api/v1/health/db` checks connectivity.

## Checkpoint 4: End-to-End Persistence (Captures)
- **Goal:** Implement the first vertical slice (Capture).
- **Summary:** Created the `Capture` domain entity (representing raw information). Built out the SQLModel infrastructure, Unit of Work integration, and application use cases for creating and retrieving Captures.
- **Verification:** Full CRUD operations over `api/v1/captures` successfully validated.

## Checkpoint 5: Engineering Quality Foundation
- **Goal:** Harden the repository stability and developer experience.
- **Summary:** Configured `Ruff` for linting and formatting, introduced `pytest` with a clean isolated database structure, and established CI pipelines and a `Makefile`.
- **Verification:** `make verify` passes successfully without lint or test failures.

## Checkpoint 6: Complete Capture Vertical Slice
- **Goal:** Expand the Capture feature.
- **Summary:** Implemented listing with pagination (`GET`), updating content (`PATCH`), and deleting (`DELETE`). Set up a functional minimalist React UI placeholder for these actions.
- **Verification:** Backend endpoints correctly handle HTTP status codes and Pydantic validation constraints.

## Checkpoint 7: Concept Domain
- **Goal:** Introduce processed knowledge (Concepts).
- **Summary:** Built out the `Concept` vertical slice (Entity, Repository, Application Use Cases, and Endpoints) mirroring the architecture of Captures, representing manually created structured knowledge.
- **Verification:** Alembic migrations applied; `make verify` passes; `POST` and `GET` for concepts functioning.

## Checkpoint 8: Event Bus & Timeline Foundation
- **Goal:** Establish an event-driven foundation to log a durable user Timeline.
- **Summary:** Introduced pure `DomainEvent` dataclasses (`CaptureCreated`, `ConceptCreated`, etc.), a synchronous `EventBus`, and a `TimelineEventModel`. Wired the `UnitOfWork` to collect emitted events from Use Cases and persist them to the Timeline after the primary transaction commits.
- **Verification:** Timeline securely records nested JSON event payloads correctly ordered; rollbacks appropriately discard events before publishing.

# Checkpoint 9: Knowledge Graph Foundation (v0.0.9)

## Goal
Establish the persistence model and API for relationships between entities (Captures, Concepts) without introducing graph traversal, embeddings, or AI features. Keep it simple, strictly typed, and aligned with Domain-Driven Design (DDD).

## Scope
- Created the `Relationship` entity.
- Implemented `RelationshipModel` (SQLite) with composite indexes for efficient edge lookups.
- Implemented application use cases (`CreateRelationship`, `GetRelationship`, `DeleteRelationship`, `ListRelationships`).
- Updated deletion logic in `Capture` and `Concept` (where applicable) to prevent deleting entities with active relationships.
- Registered endpoints in the `api/v1/relationships` router.

## Decisions
- **CreatorType Enum:** We chose to replace nullable UUIDs with a clean `CreatorType` enum (`SYSTEM`, `USER`, `AI`, `IMPORT`, `SYNC`).
- **Entity Validation:** Instead of creating generic multi-entity repositories, the `CreateRelationshipUseCase` explicitly validates node existence using the specific repository for that entity type (e.g., `uow.captures.get(id)`).
- **Deletion Policy:** Deletion of nodes (Captures/Concepts) is blocked if relationships exist to maintain referential integrity.
- **RESTful Endpoints:** We utilized standard endpoints (`POST /api/v1/relationships`, `GET /api/v1/relationships/{id}`) and resource-specific sub-routes (`GET /api/v1/relationships/entity/{id}/incoming`) rather than single overly-flexible endpoints.

## Verification
- Wrote and passed comprehensive unit tests covering repository CRUD operations, entity validation rules, deletion prevention, and API status codes.
- `make verify` ensures code formatting, linting, and testing are preserved.
- Executed successful manual tests verifying API structure natively using Docker.


# Checkpoint 10: Knowledge Graph Exploration (v0.0.10)

## Goal
Implement read-only graph traversal capabilities to make the Knowledge Graph usable. Introduce traversal endpoints and a simple frontend Graph Explorer to navigate relationships and visualize connected entities deterministically, without AI or external algorithms.

## Scope
- Created graph traversal application use cases:
  - `GetRelationshipGraphUseCase`: A generalized BFS traversal logic with configurable max depth (cap 2) and max node returns (cap 100). Validates against infinite cycles by utilizing a visited-nodes list.
  - `GetEntityNeighborhoodUseCase`: Fetch the 1-hop neighborhood.
  - `GetConnectedEntitiesUseCase`: Extracted direct neighbors outputting solely Nodes.
- Created `/api/v1/graph` router exposing nodes and relationships seamlessly decoupled from direct DB queries.
- Extended `apps/web/src/App.tsx` natively replacing a heavy router library with a simple view-switcher to render the newly created `GraphExplorer.tsx`.

## Decisions
- **BFS Logic over DB Recursion:** Implementing graph traversal safely inside Python using BFS over direct raw SQL `WITH RECURSIVE` queries was chosen to keep domain logic explicitly in the Application Layer and decouple from SQLite nuances, making limits on depth and count straightforward to implement.
- **Frontend Visualization:** Decided not to install Cytoscape or D3. Instead built a CSS grid-based hierarchical layout representing the target node and its direct connections in the `GraphExplorer` component, reducing heavy UI bloat and dependencies.
- **Max Hop Limits:** Hardcoded depth to a maximum of 2 to avoid unintended performance lags while allowing basic pathway previews.

## Verification
- Unit tested the graph traversal algorithms verifying depth boundaries and cyclic cycle prevention against graph definitions like `A -> B -> C -> D -> A`.
- `make verify` passes perfectly. Docker natively hosts the new frontend mapping the `GraphExplorer` perfectly against the API endpoints.


# Checkpoint 11: Source Domain Foundation (v0.0.11)

## Goal
Introduce the `Source` domain as the origin of knowledge within MindForge. This checkpoint establishes the Source domain context, its SQLModel database persistence, CRUD application use cases, API routing under `/api/v1/sources`, and a lightweight frontend view `SourcesView.tsx`. It also integrates `Source` into the existing Knowledge Graph (`EntityType.SOURCE`) and verifies referential integrity on deletions.

## Scope
- Created Source entity and `SourceType` enum representing origins like `WEB_ARTICLE`, `BOOK`, `PDF`, etc.
- Created `SourceModel` mapping to SQLite table `sources` with indexes on type, uri, and title.
- Created `CreateSourceUseCase`, `GetSourceUseCase`, `UpdateSourceUseCase`, `DeleteSourceUseCase`, and `ListSourcesUseCase`.
- Enforced delete protection: deleting a `Source` is blocked if relationships exist referencing it.
- Extended the `EntityType` enum with `SOURCE = "Source"` and updated relationship creations, graph traversals, and neighbor fetches to support `Source` nodes.
- Exposed API endpoints `/api/v1/sources` with filtering and pagination.
- Added `SourcesView` navigation option in `App.tsx` and created a functional CRUD interface.

## Decisions
- **UoW clearing verification:** To properly check timeline events after a use case calls `uow.commit()`, we modified assertions to query the database-backed `TimelineRepository(db_session)` instead of checking in-memory `uow.collect_events()` directly.
- **Filtering by Type:** Kept standard paginated queries with optional query filters on type using simple standard parameters rather than nested graphql-like formats.

## Verification
- Wrote and passed comprehensive unit tests covering repository CRUD operations, entity validation rules, deletion prevention, and API status codes.
- `make verify` passes perfectly. Docker compose holds the containerized services mapping both the backend API and the frontend components correctly.


# Checkpoint 12: Collections Domain Foundation (v0.0.12)

## Goal
Introduce the **Collections** (spaces) organizational layer to group knowledge. We established the `Collection` and `Membership` domains, mapping captures, concepts, and sources structural memberships cleanly without overloading semantic knowledge graph relationships.

## Scope
- Defined `Collection` and `Membership` entities. Memberships support mapping any `EntityType` to a collection.
- Enforced strict uniqueness index on both database and application level: `Collection.name` UNIQUE and `Membership(collection_id, entity_id, entity_type)` UNIQUE.
- Enforced delete safety rules:
  - Collection deletion is blocked if memberships are active.
  - Introduced `cleanup_entity_memberships(uow, entity_id)` helper invoked in `DeleteCaptureUseCase` and `DeleteSourceUseCase` to clean up memberships when entities are deleted.
- Created `/api/v1/collections` endpoint hierarchy.
- Developed `CollectionsView` in the React frontend representing simple spaces, forms to create/edit spaces, and an entity list management interface.

## Decisions
- **Shared Helpers for Cleanup:** Deleting entities maps cleanly using the `cleanup_entity_memberships` helper, preventing redundant deletes copy-pasted into individual delete use cases.
- **Structural vs Semantic:** Decided collections exist completely independent of relationships, which keeps structural group hierarchies clean from semantic linkage edges.

## Verification
- Added test coverage inside `test_collection_repository.py`, `test_collection_usecases.py`, and `test_collection_api.py`.
- Verified live cURL tests matching duplicate insertions, delete locks, and cascade deletion.
- Bumped versions to `0.0.12`.

