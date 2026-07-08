# Milestone 1 Checkpoints

Milestone 1 should be executed as vertical checkpoints. Each checkpoint must leave the repository runnable and deployable.

## Checkpoint 1: Repository Foundation

Release:

```text
0.0.1
```

Scope:

- Initialize Git repository
- Create monorepo structure
- Configure `uv` for the API
- Create React and Vite app
- Configure Docker Compose
- Add `.env.example`
- Add `.gitignore`

Verify:

- `docker compose up`
- frontend starts
- backend starts

Commit:

```text
feat: initialize monorepo foundation
```

## Checkpoint 2: FastAPI Skeleton

Release:

```text
0.0.2
```

Scope:

- FastAPI app
- `/health`
- `/api/v1/health`
- configuration
- structured logging
- global exception handling
- OpenAPI docs

Verify:

```text
GET /health -> 200 OK
GET /api/v1/health -> 200 OK
```

Commit:

```text
feat(api): bootstrap FastAPI application
```

## Checkpoint 3: Database

Release:

```text
0.0.3
```

Scope:

- SQLModel
- SQLite
- Alembic
- session factory
- Unit of Work
- first migration

Verify:

```text
uv run alembic upgrade head
```

Commit:

```text
feat(db): add persistence foundation
```

## Checkpoint 4: Event System

Release:

```text
0.0.4
```

Scope:

- event base class
- event bus
- publish
- subscribe
- one demo event

Verify:

```text
HealthChecked -> timeline entry created
```

Commit:

```text
feat(core): add event bus foundation
```

## Checkpoint 5: Timeline

Release:

```text
0.0.5
```

Scope:

- create `activity_log`
- write one record
- read one record

Verify:

- database contains the timeline record
- API can read the timeline record through an internal or test path

Commit:

```text
feat(core): add timeline foundation
```

## Checkpoint 6: Frontend Shell

Release:

```text
0.0.6
```

Scope:

- sidebar
- router
- layout
- empty pages
- health badge shell

Verify these pages load:

- Dashboard
- Inbox
- Today
- Reviews
- Resources
- Domains
- Weekly Review
- Settings

Commit:

```text
feat(web): add application shell
```

## Checkpoint 7: API Integration

Release:

```text
0.1.0
```

Scope:

- frontend fetches `GET /api/v1/health`
- frontend displays backend health status

Verify:

```text
Backend Healthy
```

Commit:

```text
feat(web): connect health endpoint
```
