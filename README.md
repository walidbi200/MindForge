# Ascend

Ascend is a Personal Learning Operating System for transforming information into knowledge, knowledge into application, and application into mastery.

This repository is currently at Checkpoint 1, release `v0.0.1`: repository foundation.

## Requirements

- Docker with Docker Compose
- Git

Local `uv`, Python, Node, and npm installs are optional for this checkpoint because Docker builds the API and web services inside containers.

## Quick Start

Copy the example environment file if you want local overrides:

```bash
cp .env.example .env
```

Start the stack:

```bash
docker compose up
```

The stack also has safe development defaults, so `docker compose up` works before `.env` exists.

Expected services:

- API: `http://localhost:8000`
- API docs: `http://localhost:8000/docs`
- Web: `http://localhost:5173`

Checkpoint 1 does not include health endpoints. `/health` and `/api/v1/health` are part of Checkpoint 2.

## Repository Structure

```text
apps/
  api/        FastAPI application
  web/        React, Vite, Tailwind, shadcn/ui frontend
packages/
  shared/     future shared runtime utilities
  types/      future shared type definitions
docs/         product and engineering documents
docker/       service Dockerfiles
scripts/      future developer scripts
```

## API Development

The API uses `uv` and a `src` package layout.

Inside `apps/api`:

```bash
uv sync
uv run uvicorn ascend.main:app --reload
```

## Web Development

The web app uses React, TypeScript, Vite, TailwindCSS, and shadcn/ui conventions.

Inside `apps/web`:

```bash
npm install
npm run dev
```

## Checkpoint 1 Verification

The checkpoint is complete when:

- `docker compose up` starts successfully
- backend starts
- frontend starts
- API docs load at `http://localhost:8000/docs`
- web loads at `http://localhost:5173`

## Deferred

The following are intentionally deferred to later checkpoints:

- health endpoints
- database
- SQLModel
- Alembic
- authentication
- AI
- events
- timeline
- learning engine
- feature flags
- business logic
