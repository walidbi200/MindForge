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


# Checkpoint 13: Technical Debt Resolution & Review Domain Redesign (v0.0.13)

## Goal
Resolve post-Checkpoint 12 architectural blockers (exception handling, delete integrity) and completely redesign the **Review Domain** to support workflow scheduling instead of static grading.

## Phase 1 — Technical Debt Resolution

### Domain Exception Hierarchy
- Replaced all generic `ValueError` exceptions in the Application Layer with precise DDD exceptions: `ConflictError`, `ValidationError`, `EntityNotFoundError`, `DuplicateCollectionError`, `MembershipAlreadyExistsError`, `CollectionNotEmptyError`.
- Fast API application layer handles mapping of these domain exceptions into appropriate HTTP status codes (400, 404, 409, 422) centrally via `core/errors.py`. The Application layer now correctly knows nothing about HTTP.

### Delete Integrity 
- Confirmed collections correctly block deletion if memberships exist.
- Verified Captures and Sources block deletion if any semantic relationships exist.
- Implemented `DeleteConceptUseCase` and fully enforced relational checking and the `cleanup_entity_memberships` helper upon deletion.

## Phase 2 — Review Domain Redesign

### Domain Layer
- Stripped the legacy Review schema (which mixed flashcards, grading, and notes).
- Created a purely scheduling-oriented model centered on three states: `PENDING`, `COMPLETED`, `SKIPPED`.
- Enums: `ReviewStatus`
- Entities: `Review` containing `due_at`, `completed_at`, `metadata_json`.

### Infrastructure Layer
- Replaced the existing `ReviewModel` with the new schema constraints.
- Generated and executed Alembic migration dropping the legacy review table and adding the new structure. Handled SQLite constraints natively.
- Rewrote `SqlAlchemyReviewRepository` exposing strictly focused queries like `list_due(time)`, `list_by_entity(id)`.

### Application Use Cases
- Removed old updating loops, replacing with discrete actions.
- Added `CreateReviewUseCase`, `GetReviewUseCase`, `ListDueReviewsUseCase`, `ListEntityReviewsUseCase`, `CompleteReviewUseCase`, `SkipReviewUseCase`, `DeleteReviewUseCase`.
- Completion logs `completed_at` and accepts unstructured `metadata_json` (for capturing notes or future telemetry).

### Web UI
- Re-architected `ReviewsView.tsx` into a pipeline: "Due Reviews", "Completed", "Upcoming".
- Provides execution options natively matching the API: "Mark Completed" and "Skip Review".

## Verification
- Wrote integration tests mapping duplicate prevention, exception triggering, lifecycle transitions, and API status codes (`test_review_api.py`, `test_review_repository.py`).
- 32 strict business-rule tests passing seamlessly in the containerized Docker environment.

# Checkpoint 14: AI-Assisted Capture Processing (v0.0.14)

## Goal
Implement the first complete vertical slice of MindForge leveraging AI. A user creates a Capture, selects "Process with AI", and MindForge uses OpenRouter to analyze it, returning structured suggestions. The user reviews those suggestions before anything is persisted, enforcing the rule that AI cannot mutate the database.

## Scope
- Abstracted the AI interface with `AIService` Protocol, `AIRequest`, and `AIResponse`.
- Implemented `OpenRouterAIService` interacting directly with OpenRouter via `httpx` and `tenacity` for resilience against network failures.
- Created declarative Markdown prompts (`system.md`, `analyze_capture.md`).
- Implemented `AnalyzeCaptureUseCase` fetching a capture and generating an AI analysis.
- Defined AI-related domain events for the Timeline (`AIAnalysisRequested`, `AIAnalysisCompleted`, `AIAnalysisFailed`).
- Built `/api/v1/ai/analyze-capture/{id}` endpoint.
- Updated `CapturesView.tsx` with an AI Preview UI.

## Decisions
- **AI Mutability Rule**: AI is strictly read-only. It takes input text and returns JSON suggestions. It NEVER writes directly to the knowledge graph.
- **Protocol Abstraction**: The Application layer only knows about `AIService.generate(request)`. Infrastructure layer handles OpenRouter implementation details.
- **Prompts as Content**: Prompts are stored as external Markdown files (`system.md`, `analyze_capture.md`) rather than hardcoded Python strings.

## Verification
- Unit tested `AnalyzeCaptureUseCase` validating AI interaction and event emission.
- Integration tested `api/v1/ai` endpoints with mocked AI services to ensure correct request and response mapping.
- Validated via automated tests that exceptions appropriately emit `AIAnalysisFailed` events before re-raising.

# Checkpoint 15: Daily Workspace (v0.0.15)

## Goal
Establish the **Integration Phase** by building the `DailyWorkspace` - a unified frontend dashboard that replaces isolated CRUD pages with a comprehensive tool mapping capturing, searching, activity feeds, collections, and AI.

## Scope
- Base Repositories (`Capture`, `Concept`, `Source`, `Collection`, `Relationship`) updated with native paginated SQL queries (`list()`).
- New `GetWorkspaceUseCase` returning a unified timeline of recent captures, pinned spaces, recent sources, activity timelines, today's due reviews, and graph connectivity previews.
- New `SearchWorkspaceUseCase` offering generic text querying across multiple internal domains.
- Exposed `api/v1/workspace` REST orchestration endpoints.
- Designed `DailyWorkspace.tsx` applying a DOM-native multi-column layout aggregating everything on one screen.

## Decisions
- **Orchestration on Backend:** Unified API calls in the application layer via `GetWorkspaceUseCase` prevent frontend waterfall fetching and N+1 API problems.
- **Frontend as Consumer:** The UI remains purely a display layer without containing business logic, respecting the frozen architecture.
- **Review System Friction:** Fixed Review repository and unit of work implementations to smoothly integrate the new chronological Review architecture correctly.

## Verification
- Wrote API tests validating correct data aggregation and schema parsing for workspace models (`test_workspace_api.py`).
- Integrated and built frontend `DailyWorkspace.tsx` cleanly verifying UI interactions and display behaviors.

---

# Checkpoint 16: AI Inbox & 1-Click Apply

## Goal
Implement the first vertical end-to-end AI workflow in MindForge without breaking architectural constraints. AI acts as a read-only suggestion engine whose output is applied via user consent.

## Scope
- Added `CaptureStatus` (`PENDING`, `PROCESSED`) to `Capture` entity.
- Updated AI protocols and prompts to support `collections` and `review_suggestion`.
- Developed `ApplyAIAnalysisUseCase` to orchestrate multi-domain creation of Concepts, Relationships, Collections, Memberships, and Reviews based on AI output.
- Exposed `POST /api/v1/ai/apply-analysis/{capture_id}` endpoint.
- Updated frontend `DailyWorkspace.tsx` to include an **AI Inbox** for pending captures and an **AI Sidebar** for a 1-Click Apply workflow.

## Decisions
- **Immutable Database rule respected:** The AI service remains an external query tool. It never mutates the database. The Application layer use case purely accepts structured JSON suggestions and translates them into domain entity creations.
- **Status workflow:** Introduces state to raw Captures to separate raw unprocessed items from actively analyzed intelligence.

## Verification
- Wrote comprehensive API tests verifying validation, relationships, and transaction coordination in `test_ai_api.py`.
- Backend linter, type-checker, and frontend tests successfully verified via `make verify`.

---

# Checkpoint 17: Guided Capture Workflow (v0.0.17)

## Goal
Implement a guided knowledge capture workflow, transforming the Daily Workspace from an inbox into an interactive suggestion review process, ensuring a frictionless capture -> organize -> learn flow.

## Scope
- Created `StartGuidedCaptureUseCase` and `ApplyProposalUseCase` orchestration layer in `application/workspace`.
- Exposed `POST /api/v1/workspace/process-capture` and `POST /api/v1/workspace/apply-proposal` endpoints, centralizing orchestration.
- Rebuilt `DailyWorkspace.tsx` to include an interactive AI Review panel allowing inline editing of concepts, relationships, and review schedules before application.
- Quick Capture auto-processing using `Ctrl+Enter`.
- Formalized project lifecycle via `PROJECT_CONSTITUTION.md` and `CHECKPOINT_TEMPLATE.md`.

## Decisions
- **Orchestration in Application Layer**: Cross-domain coordination lives in Use Cases, not the router or domain layer.
- **Interactive Review**: Users must have the ability to edit AI suggestions *before* they are applied to the knowledge graph, reinforcing the principle that AI is an assistant, not an autonomous agent.

## Verification
- Verified with backend unit and API tests in `test_workspace_process.py` and `test_apply_proposal.py`.
- Performed end-to-end manual verification in the React UI via `docker compose up`.

---

# Checkpoint 18: Daily Learning & Home Experience (v0.0.18)

## Goal
Transform MindForge into a true "Daily Operating System" instead of a mere database application by enriching the workspace aggregation and entirely redesigning the frontend dashboard, without introducing any new bounded contexts.

## Scope
- Enriched `GetWorkspaceUseCase` to calculate real-time **Daily Stats** and extract **Continue Learning** context from the Timeline.
- Enhanced `TimelineRepository` to fetch `AIAnalysisCompleted` events and derived pending AI proposals.
- Updated `AnalyzeCaptureUseCase` to natively embed the AI proposal payload directly into the `TimelineEventModel` metadata, preventing complex schema migrations for volatile AI workflow states.
- Rebuilt `DailyWorkspace.tsx` into a comprehensive dashboard with a Welcome Header, Today's Progress widget, prioritized Action Cards, and an inline global search overlay (`Ctrl+K`).
- Seamlessly transitioned the AI pending captures out of an "inbox" and directly into interactive dashboard cards.

## Decisions
- **Event Metadata over Schema Expansion:** Persisted AI Proposals cleanly in the `Timeline` Event Store rather than creating a new `AIProposals` table. This keeps the core domain lean and handles transient AI state perfectly.
- **UI Decoupling:** Maintained the rule that the Frontend contains no AI business logic; it acts entirely as an interactive display for the aggregated `WorkspaceSummaryResponse`.

## Verification
- Added automated assertions to `test_workspace_api.py` validating the newly introduced stats and suggestion shapes.
- Successfully executed `make verify` resolving Python static analysis issues.
- Frontend builds cleanly via Vite/TypeScript.
- Conducted manual end-to-end verification via Docker ensuring the workspace UI correctly surfaces stats, opens AI reviews, and applies suggestions to the graph.

---

# Checkpoint 19: Knowledge Exploration & Discovery (v0.0.19)

## Goal
Make the Knowledge Graph the primary navigation method for MindForge by replacing isolated CRUD pages with a unified Explorer. Implement Nexos-style friction-less graph traversal and duplicate detection.

## Scope
- Defined `list_by_ids` protocol method and implemented it across `Concept`, `Capture`, `Source`, and `Collection` SQL repositories to prevent N+1 queries during graph traversal.
- Updated `TimelineRepository.list()` to support query filtering by `aggregate_type` and `event_type`.
- Created `GetKnowledgeNeighborhoodUseCase` which orchestrates fetching a 1-hop relationship graph and resolving all entity contents in bulk.
- Created `CheckDuplicatesUseCase` which uses NLP similarity scoring to flag potential duplicate concepts before they are created.
- Created `KnowledgeExplorer.tsx` component to replace the placeholder `GraphExplorer.tsx` with a rich, interactive center-panel design featuring connected entities and backlinks.
- Centralized `App.tsx` and `DailyWorkspace.tsx` navigation to route all entity clicks to the `KnowledgeExplorer`.

## Decisions
- **Graph Traversal at the Application Layer**: Avoiding complex SQL recursion, the `GetKnowledgeNeighborhoodUseCase` orchestrates fetching relationships and then queries individual repositories by ID. This maintains bounded contexts perfectly.
- **Unified Explorer Navigation**: Eliminating the CRUD pages as the primary user navigation mechanism shifts the product paradigm to true Knowledge Navigation.

## Verification
- Added automated assertions to `test_graph_explorer.py` confirming successful neighborhood structure parsing and duplicate detection filtering.
- Successfully executed `make verify` resolving Python static analysis issues.
- Frontend builds cleanly via Vite/TypeScript.
- Conducted manual end-to-end verification via Docker ensuring the workspace UI correctly surfaces graph neighborhood context.

---

# Checkpoint 20: Complete the Daily Learning Loop (v0.0.20)

## Goal
Complete the Daily Learning Loop by integrating all existing capabilities (Daily Workspace, Knowledge Explorer, Reviews, and Timeline) without introducing any new bounded contexts. This allows the user to spend an entire learning session inside MindForge without needing to switch screens.

## Scope
- Added `GetKnowledgeRecommendationsUseCase` which leverages heuristic deterministic graph traversal to suggest related knowledge.
- Exposed `/api/v1/graph/recommendations/{entity_id}` endpoint for Knowledge Recommendations.
- Enhanced `/workspace` endpoint to aggregate and prioritize a `Reading Queue` from pending reviews, proposals, concepts, and captures.
- Enriched `Continue Learning` to show the most recent concept, collection, and time since last interaction.
- Improved `CheckDuplicatesUseCase` with robust unicode/whitespace normalization for better accuracy.
- Enhanced `SearchWorkspaceUseCase` with sliding-window snippets.
- Rebuilt `DailyWorkspace.tsx` to display `Reading Queue` and `Continue Learning` effectively.
- Updated `KnowledgeExplorer.tsx` to fetch and render `Recommendations` natively.

## Decisions
- **Deterministic Recommendations**: Avoiding black-box AI logic, we built a deterministic engine ranking suggestions based on direct graph proximity, shared collections, and time-based timeline proximity.
- **Reading Queue Consolidation**: Consolidated reviews, pending proposals, recent concepts, and unread captures into a unified queue natively prioritizing Due Reviews.
- **String Normalization**: Ensuring strict whitespace, casing, and accent stripping handles user typos and inconsistencies organically, improving the duplication-check hit rate.

## Verification
- Added automated assertions to `test_workspace_api.py` validating the reading queue and detailed `ContinueLearningResponse`.
- Successfully executed `make verify` resolving Python static analysis issues.
- Frontend builds cleanly via Vite/TypeScript.
- Conducted manual end-to-end verification via Docker ensuring the workspace UI correctly surfaces the queue and recommendations.

---

# Checkpoint 21: MindForge v1.0 Production Release (v0.0.21)

## Goal
Deliver the first production-ready version of MindForge. Enhance existing workflows by implementing "Edit Mode" and "Merge into Duplicate" functionalities for Concepts within the Knowledge Explorer to eliminate UX friction and solidify the product as a true Personal Knowledge Operating System.

## Scope
- Created `UpdateConceptUseCase` for updating title and summary attributes of concepts.
- Exposed `PATCH /api/v1/concepts/{id}` for fast concept edits.
- Created `MergeConceptsUseCase` to deduplicate and merge concepts natively handling semantic relationship re-pointing, review migration, and collection membership transfer.
- Included `ConceptsMerged` domain event ensuring Timeline captures the trace of merging.
- Exposed `POST /api/v1/concepts/{source_id}/merge/{target_id}`.
- Refactored all SQLAlchemy persistence `save` methods from `session.add()` to `session.merge()` resolving duplicate identity uniqueness errors within UnitOfWork.
- Integrated "Edit Mode" in `KnowledgeExplorer.tsx` enabling in-place editing for Concepts.
- Implemented the "Merge into Duplicate" UI action triggered directly from the Potential Duplicate Alert.

## Decisions
- **Merge Integrity**: Merging must gracefully re-point relationships and transfer nested sub-resources instead of deleting history.
- **SQLAlchemy Merging**: Transitioning to `session.merge()` allows clean idempotent updates instead of forcing manual detached object handling for updating existing persisted records.

## Verification
- Added automated assertions to `test_concept_usecases.py` ensuring successful node deletion, event emission, and attribute updates.
- Verified backend testing via Docker `pytest`.
- Ran frontend type-checking compilation natively validating TypeScript constraints.
- Fully satisfied production Checkpoint requirements to complete Milestone v1.0.
