# Contributing

This project favors small, runnable checkpoints over large unfinished branches.

Before contributing, read:

- [Ascend North Star](docs/north_star.md)
- [Architecture Principles](docs/architecture_principles.md)
- [Definition of Done](docs/definition_of_done.md)

## Branch Naming

Use short, descriptive branch names:

```text
feat/api-health
feat/web-shell
fix/docker-startup
docs/milestone-checkpoints
```

## Commits

Use Conventional Commits:

```text
feat(api): add health endpoint
fix(db): correct migration path
docs: update definition of done
test(api): cover health endpoint
```

Each commit should leave the repository runnable.

## Main Branch

`main` must always be runnable.

Experimental work happens on feature branches.

Merge only when the checkpoint satisfies the Definition of Done.

## Releases

Treat every checkpoint as a release candidate.

Before marking a checkpoint complete, verify:

- `docker compose up` works
- the project builds from a clean checkout
- another engineer can follow the README successfully
- the version would be comfortable to tag

Update `CHANGELOG.md` for every release candidate.

## Documentation

Do not add new documentation unless it directly supports implementation or explains a decision discovered during implementation.

## Local Development

The standard local startup path is:

```text
docker compose up
```

Milestone-specific commands should be documented in the README as they are introduced.

## Code Style

Prefer simple, typed, documented functions with one responsibility.

Keep business logic out of routes.

Keep the Domain layer pure.

Keep AI, filesystem, database, and HTTP concerns out of the Domain layer.

## Testing Expectations

Add or update tests for behavior changes.

At minimum, each checkpoint should verify:

- backend startup
- frontend startup
- migrations, once introduced
- relevant API endpoints
- relevant unit tests

## Pull Request Checklist

Before merging:

- Tests pass
- Docker still works
- Project builds from a clean checkout
- Migrations are tested if changed
- API behavior is documented if changed
- ADR is added if architecture changed
- Feature flag is added if needed
- Errors are handled
- Logging is added where useful
- UI works on desktop if frontend changed
- No TODOs are left behind

## Architecture Changes

No architectural changes should be made without working code that demonstrates the need.

If a real limitation appears after implementation, update the relevant ADR and architecture documents then.
