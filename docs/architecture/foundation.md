# MindForge Architecture Foundation

This document describes the stable architectural baseline for the MindForge application. It serves as the definitive reference for how the backend is structured, how components interact, and how new features should be integrated.

**Core Philosophy:** *Architecture evolves from implementation.* We do not build speculative architecture, premature microservices, or unnecessary abstractions. We build what is necessary for the current workflow, verify it, learn from reality, and adapt.

---

## 1. Layered Modular Monolith

MindForge is built as a modular monolith in Python using FastAPI. The application enforces strict boundaries between its internal layers to ensure long-term maintainability.

*   **Domain Layer (`src/ascend/domain/`)**: Pure business logic and core entities. Contains no knowledge of databases, external APIs, or web frameworks.
*   **Application Layer (`src/ascend/application/`)**: Application Use Cases orchestrate business processes. They accept requests from the API, interact with repositories through the Unit of Work, and dispatch Domain Events.
*   **Infrastructure Layer (`src/ascend/infrastructure/`)**: Concrete implementations of repositories, database connections (SQLAlchemy/Alembic), event bus routing, and external AI integrations (e.g., OpenRouter).
*   **API Layer (`src/ascend/api/`)**: FastAPI endpoints, request/response validation (Pydantic schemas), and routing. Exclusively delegates work to Application Use Cases.

---

## 2. Domain-Driven Design (DDD) Boundaries

The system is organized into distinct Bounded Contexts, each focusing on a specific part of the user's workflow:

*   **Sources**: The origin of information (e.g., web articles, books).
*   **Captures**: Raw evidence, highlights, or observations.
*   **Concepts**: Synthesized knowledge derived from evidence.
*   **Relationships**: Directed edges connecting entities to form the Knowledge Graph.
*   **Collections**: Workspaces or organizational groupings for any entity (via Memberships).
*   **Reviews**: Scheduling nodes for active recall or spaced repetition (Status: PENDING, COMPLETED, SKIPPED).
*   **Timeline**: An immutable append-only ledger of all meaningful system actions.

---

## 3. Data Access & Integrity

### Repository Pattern
Data access is abstracted through Repositories. The Application layer only knows about Repository Protocols defined in the Domain. The Infrastructure layer implements these protocols (e.g., `SqlAlchemyReviewRepository`).

### Unit of Work (UoW)
The Unit of Work pattern (`SqlAlchemyUnitOfWork`) guarantees atomic transactions across multiple repositories. Use Cases wrap operations in a `with self.uow:` context block. If a Use Case fails, the transaction automatically rolls back.

### Domain Exceptions
Exceptions are strictly typed in the Domain layer (`ValidationError`, `ConflictError`, `EntityNotFoundError`, `IntegrityError`). 
The Application layer raises these domain-specific exceptions, and the API layer intercepts them globally (via `core/errors.py`) to translate them into standard HTTP status codes (400, 404, 409, 422). The Application layer never touches HTTP.

---

## 4. Event-Driven Workflows

### Domain Events & The Event Bus
All meaningful state changes (e.g., `CaptureCreated`, `ReviewCompleted`, `EntityAddedToCollection`) yield Domain Events.
The Unit of Work automatically collects these events and dispatches them synchronously to the `EventBus` right before committing the database transaction.

### Timeline
The Timeline acts as the universal system ledger. It observes the `EventBus` and durably logs every emitted Domain Event. This provides a complete historical audit trail and enables retroactive analysis of how knowledge was built.

---

## 5. Knowledge Graph

MindForge is fundamentally a graph. Instead of rigid hierarchical folders, entities (`Sources`, `Captures`, `Concepts`) act as nodes. `Relationships` act as directed, typed edges.
*   Entities are completely standalone.
*   Graph Integrity is strongly protected: Deleting an entity fails with a `ConflictError` if it has existing relationships or active Collection memberships.

---

## 6. Testing Philosophy

Testing focuses on business rules and architectural invariants, not just CRUD operations.

*   **Integration Tests via Docker**: Tests run against real, isolated SQLite databases managed by Docker.
*   **Lifecycle Tests**: We test full entity lifecycles from creation, updates, and relationship mapping, to protected deletion.
*   **Integrity Tests**: We explicitly verify rollback behaviors, duplicate prevention (e.g., overlapping collections, duplicate relationships), and domain exception mapping.
*   **Event Verification**: Tests assert that the `EventBus` correctly routes events and that the `Timeline` records them.

---

## 7. Future Directions: AI & Workflows

With the core architecture established, future iterations shift focus towards:

1.  **Workflow Integration**: MindForge grows by integrating existing capabilities into complete user workflows, not by continuously introducing new isolated domains. Every checkpoint should leave the system capable of accomplishing a meaningful new end-to-end task. AI is an infrastructure service that assists these workflows but never owns business logic or becomes the source of truth. Every future checkpoint must satisfy all three conditions:
    *   Build on an existing bounded context.
    *   Connect at least two existing domains (e.g., Capture → AI → Concept → Relationship).
    *   Produce a complete user workflow, not merely a CRUD endpoint.
2.  **AI as an Assistant, Not the Center**: AI enhances the system but never defines it. The ultimate source of truth remains the SQLite database, Knowledge Graph, Collections, and Timeline. MindForge must remain completely functional even if the AI provider is down or removed.
3.  **OpenRouter AI Abstraction**: AI integration occurs purely through a generic `AIService` Protocol defined in the Application layer, with a concrete `OpenRouterAIService` implementation in the Infrastructure layer.
    *   **Capability-Agnostic Interface**: The interface accepts standard generic parameters (`AIRequest` with `system_prompt`, `user_prompt`, `temperature`, `max_tokens`) rather than brittle, use-case specific methods (like `generate_summary()`).
    *   **Stable AI Response Schema**: Every AI call must return structured JSON data mapping to an `AIResponse` model, never free-form text. The Infrastructure layer (`OpenRouterAIService`) is responsible for translating provider-specific output into the standard response schema.
    *   **No Database Mutation**: AI is advisory. It returns suggestions which the Application layer validates, uses to create entities, and commits via the Unit of Work. AI never bypasses repositories, validation, or the Timeline, and it never touches SQLite directly.
    *   **Prompt Management**: Prompts are stored externally (e.g., in `prompts/` as `.md` files) rather than hardcoded in Python, so they can be iterated on cleanly.
    *   **Centralized Resilience & Tracking**: The Infrastructure layer centrally handles retries, timeouts, rate-limiting, and tracks telemetry/usage accounting (model, tokens, latency) for all AI calls.
4.  **Client Sync**: Advancing real-world synchronization layers (e.g., Obsidian vaults) using the stable UoW and Event systems.
