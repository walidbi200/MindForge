# MindForge AI Development Guide

This document is the permanent operating manual for Gemini (and any other AI collaborators) working inside the MindForge repository. It defines our project philosophy, architectural standards, product constraints, development lifecycle, and quality standards.

This is **NOT** a user manual or generic documentation. It is an authoritative set of execution constraints designed to ensure clean, high-quality, and idiomatic development.

---

## Project Overview

MindForge is a knowledge-first personal operating system. It is designed to act as a system of record and learning engine for human intelligence, optimizing for deliberate deep work and long-term knowledge retention.

### Core Philosophy

1.  **Capture Intentionally:** Capture ideas, inputs, and observations directly with low friction, but treating them strictly as unvalidated inputs (evidence).
2.  **Convert Information to Knowledge:** Formulate structure, map relationships, and synthesize signals into persistent concepts.
3.  **Learn Deliberately:** Schedule spaced reviews, track recall, and engage in constructive cognitive habits.
4.  **Apply Knowledge:** Connect stored concepts to actual real-world tasks, executions, and output.
5.  **Reflect and Improve:** Evaluate progress, audit gaps in understanding, and systematically optimize learning routines.

The product is finite, deliberate, and knowledge-centered.

### What MindForge Is NOT:
*   **NOT a social feed:** No notifications, likes, comments, or external distraction hooks.
*   **NOT a note-dumping app:** No unstructured, orphaned folders of endless documents.
*   **NOT a bookmark manager:** We do not hoard links; we extract value.
*   **NOT an AI chat wrapper:** AI is a tool to automate routine synthesis, not an oracle or a substitute for genuine human thought.
*   **NOT an infinite scroll experience:** Layouts are deliberate, task-oriented, and structured.

AI assists the workflow but **never** replaces human critical thinking.

---

## Architecture

The MindForge architecture is fully structured, clean, and frozen. Redesigning layers, introducing external architectural concepts, or rewriting system boundaries is prohibited unless implementation exposes a genuine, unworkable limitation.

```text
               +----------------------------------------+
               |                 Web UI                 |
               +-------------------+--------------------+
                                   | HTTP / JSON
               +-------------------v--------------------+
               |                api                     |
               +-------------------+--------------------+
                                   |
               +-------------------v--------------------+
               |              application               |
               +---------+--------------------+---------+
                         |                    |
        +----------------v---+            +---v----------------+
        |       domain       |            |   learning_engine  |
        +--------------------+            +--------------------+
                         ^                    ^
                         |                    |
        +----------------+--------------------+----------------+
        |                  infrastructure                      |
        |  (SQLite/Postgres, SQLModel, Alembic, AI, EventBus)  |
        +------------------------------------------------------+
```

### Monorepo Layout
*   `apps/api`: FastAPI (Python) backend using SQLModel, Alembic migrations, and Python 3.12 (`uv` package manager).
*   `apps/web`: React + Vite + TypeScript + TailwindCSS.
*   `packages/`: Shared packages and workspace-wide types.
*   `docker/`: Development container definitions.

### System Layers
*   **api:** HTTP endpoints, route definition, FastAPI controller decorators, versioning, request/response validation schemas, and global exception-to-JSON handlers.
*   **application:** Core workflow orchestrators and Use Cases. Governs transaction boundaries, service coordination, and system operations.
*   **domain:** Pure business entities and domain services. Must be completely free of persistence, framework, or presentation details.
*   **infrastructure:** Database connections, physical schema mappings, external APIs, AI integration logic, local file storage, and the synchronous Event Bus.
*   **learning_engine:** Specialized engine orchestrating recall schedules, spaced-repetition logic, and review intervals.
*   **knowledge_graph:** Graph relationship management, concept nodes, and multi-dimensional edge connections.
*   **core:** Application configuration variables, structured logging initialization, security middleware, and shared utility helpers.
*   **schemas:** Presentation/transport-specific request and response serialization schemas.

---

## Core Architectural Rules

1.  **Domain Purity:** The domain layer contains zero persistence or external infrastructure knowledge. No imports from repositories, databases, or client libraries.
2.  **Infrastructure Sovereignty:** The infrastructure layer completely owns databases, search indexes, local disk storage, event transport, and third-party API clients.
3.  **Application Orchestration:** The application layer coordinates business operations. Controllers in the API layer delegate immediately to application use cases.
4.  **No Entity Exposure:** The API layer never exposes raw domain or persistence entities. It accepts and returns explicit, validated schemas.
5.  **Durable Timeline:** Every key user interaction or state change emits a synchronous event that is durably logged to the user's Timeline.
6.  **Lightweight Synchronous Event Bus:** Side effects are decoupled via an in-memory, synchronous, lightweight event publisher.
7.  **No Event Sourcing:** Events represent a log of what happened (timeline) and trigger immediate handlers. They are not used to rebuild application state.
8.  **No Premature CQRS:** Read and write patterns reside on the same relational database schema. Do not implement separate read-model projections until scale warrants it.
9.  **AI Is Optional:** MindForge remains completely operational if AI endpoints or API keys are unavailable. AI features must degrade gracefully.

---

## Product Rules

*   **Items are Evidence:** Any raw note, web clip, PDF, or imported text is an *Item*. Items represent raw evidence, not validated knowledge.
*   **Concepts are Knowledge:** Synthesized ideas, definitions, and mental models are *Concepts*.
*   **Promotion Targets Concepts:** Items are promoted to Concepts through conscious human synthesis.
*   **Knowledge is Curated:** MindForge does not automate the creation of concepts. Humans must curate, tag, and approve.
*   **No Auto-Acceptance:** AI-suggested concepts, tags, or links are displayed as non-binding recommendations. They are never written to the knowledge graph without explicit user approval.
*   **Anti-Addiction:** No gamified streak systems, infinite feeds, or engagement-maximizing triggers.
*   **System of Quietness:** Interface elements must focus on readability, structural hierarchy, and low visual noise.

---

## Development Workflow

We practice a highly disciplined, checkpoint-based vertical execution flow.

1.  **Frozen Architecture & Plan:** Before coding, confirm the scope matches the frozen architecture and the specified checkpoint.
2.  **Vertical Execution:** Implement from the inner layers (domain/infrastructure) outward to the outer layers (application/api/web).
3.  **No Multi-Checkpoint Bleeding:** Every checkpoint must produce compiling, tested, and fully functional software. Do not start work on Checkpoint $N+1$ until Checkpoint $N$ has been verified, tested, and locked.
4.  **Inspect, Don't Guess:** Analyze existing patterns, codebase layouts, and imports before modifying files. If an idiom is established, replicate it exactly.

---

## Git Workflow

*   **Repository:** `https://github.com/walidbi200/MindForge`
*   **Branch Strategy:** `main` (We push directly or merge short-lived PRs to a stable, single trunk).
*   **Conventional Commits:** All commit messages must follow the standard conventional format:
    *   `feat(api): description`
    *   `fix(web): description`
    *   `test(core): description`
    *   `chore(deps): description`
*   **Checkpoint Lifecycle:** Every checkpoint is completed and locked with:
    1.  Successful automated verification.
    2.  Staging and committing only the relevant files (never use `git add .` blindly).
    3.  A git tag matching the checkpoint release (e.g., `v0.0.1`, `v0.0.2`).
    4.  Pushing the commit and tags to the remote repository.

---

## Coding Standards

### Prefer:
*   **Small, single-responsibility functions:** Focus on readability and quick debugging.
*   **Explicit over implicit:** Avoid magic global hooks, implicit class transformations, or dynamic monkey-patching.
*   **Robust Type Annotation:** Strict Python type hints in the API and full TypeScript types in the Frontend. No `Any` casts or `as any` bypasses unless absolutely unavoidable and documented.
*   **Explicit Dependency Injection:** Utilize FastAPI's `Depends` or simple constructor injection. Avoid globally mutable singletons.
*   **Composition over Inheritance:** Build reusable system blocks by delegating behavior rather than subclassing.

### Avoid:
*   **Giant Service Files:** Break large services down into focused query or command Use Cases.
*   **Premature Abstractions:** Do not build "generic" factories, abstract registries, or reusable wrappers until you have at least three distinct concrete use cases.
*   **Magic Frameworks:** Stick to basic, readable, well-understood patterns using SQLModel and plain Python.

---

## Implementation Rules

1.  **Surgical Changes:** Modify the minimum number of lines and files necessary to fulfill the checkpoint.
2.  **Preserve Layout:** Follow the folder and package layout exactly. Do not invent root folder directories or move architectural layers.
3.  **No Unrelated Refactoring:** Do not clean up, rename, or touch surrounding code that is not directly within the scope of your active checkpoint.
4.  **No Assumptions:** If a path, library function, or package version is uncertain, query or run a shell inspect command. Never make assumptions.

---

## Documentation Rules

*   **Documentation is Frozen:** Do not draft architectural wikis, user manuals, or new markdown documentation unless explicitly requested.
*   **Decision Logging Only:** The only exception is when implementation reveals a critical architectural constraint or bug-fix pattern that must be documented inside `GEMINI.md` or a private memory index.
*   **No Doc-Only PRs:** Documentation must accompany active, functional code changes.

---

## Milestone Discipline

Every task must progress and finish in the exact sequence:
1.  **Implementation:** Write clean, typed code conforming to the active checkpoint scope.
2.  **Verification:** Run the application locally or inside Docker to verify functionality.
3.  **Tests:** Add and run targeted unit or integration tests verifying the change.
4.  **Cleanup:** Run linters, formatters, and type checkers (`ruff`, `tsc`, `eslint`). Fix all warnings.
5.  **Commit:** Create a structured conventional commit.
6.  **Tag:** Tag the commit with the appropriate release version.
7.  **Push:** Push the commit and tag to `main`.
8.  **Update CHANGELOG.md:** Note the version release date and changes.
9.  **Update PROJECT_STATUS.md:** Update status, milestone, blockers, metrics, and next steps.

---

## Current Status

*   **Planning Phase:** Complete.
*   **Checkpoint 1 (Repository Foundation):** Complete (Monorepo structure, `uv` configuration, React skeleton, and basic Docker orchestration have been initialized).
*   **Active Checkpoint:** Checkpoint 2 (FastAPI Skeleton).

### Objective of Checkpoint 2:
Establish the runtime foundation of the MindForge application.
1.  Initialize FastAPI application instance in `apps/api/src/ascend/main.py`.
2.  Implement version-routed API paths.
3.  Expose `/health` (system check) and `/api/v1/health` (API framework check).
4.  Set up application configuration settings (using Pydantic-settings or similar).
5.  Set up structured JSON logging.
6.  Establish global exception handling and custom JSON HTTP error responses.
7.  Configure OpenAPI documentation endpoints.

*Note: Database storage, user authentication, event bus mechanics, and business domain logic are completely out of scope for the current checkpoint.*

---

## AI Collaboration Rules

1.  **Inspect First:** Always read the corresponding module files and configurations before editing. Replicate the import styles, naming syntax, and error-handling patterns already present.
2.  **Be Direct & Precise:** Provide minimal explanations. Write correct, complete, and compile-ready code without placeholders or omission comments (`...`).
3.  **Architectural Alignment:** If a user request contradicts the frozen architecture rules (e.g., asking to put raw SQL queries in the API router or creating an active-record DB model), politely explain the architectural rule and refuse the non-conforming implementation.
4.  **Optimize for Long-Term Maintainability:** Choose simple, transparent, and debuggable implementations over clever, complex patterns. Keep the system easy to reason about.

---

## MindForge Development Rules (Checkpoints & Documentation)

### Core Philosophy
The project must adhere to a strict loop: **Build → Verify → Learn → Adjust → Continue**.
- **Never design everything first and build later.**
- Implement only what belongs to the current checkpoint.
- After implementation, thoroughly verify all moving parts (tests, migrations, Docker, API, UI).
- Use real implementation as the reviewer, not speculative architecture.

### Documentation Rules
1. **Stable Documentation:** Documents that describe permanent decisions (Architecture, Repository Structure, DDD Rules) remain stable.
2. **Implementation Documentation:** Written *only after* a checkpoint ships. Should include Goal, Scope, Files Created/Modified, Decisions, Verification Results, and Technical Debt.
3. **No Pre-documentation:** Do not document future features, speculative AI pipelines, or UI screens that do not yet exist. Future checkpoints should remain lightweight outlines (e.g. Goal, Success Criteria, Status) until execution begins.

### Development Journal
Maintain the **MindForge Development Journal** (`DEVELOPMENT_JOURNAL.md`). Every completed checkpoint appends a new section describing the reality of what was built. Do not rewrite history unless implementation explicitly requires it.

### Decision Making
If implementation reveals friction:
1. Stop.
2. Explain the issue to the user.
3. Propose the smallest architectural change.
4. Justify it using real implementation evidence.
5. Wait for approval before making the change.
Architecture should evolve from working code—not speculation.
