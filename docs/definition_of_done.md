# Definition of Done

A milestone is complete only if:

- Tests pass
- Documentation is updated
- ADR is added if architecture changed
- API is documented
- Docker still works
- Migrations are tested
- No TODOs are left behind
- Feature flag is added if needed
- Logging is added
- Errors are handled
- UI works on desktop
- Code is reviewed by AI

Every checkpoint must leave the repository deployable.

No commit should knowingly break:

- `docker compose up`
- backend startup
- frontend startup
- migrations
- test suite

No checkpoint should exceed 1-2 days of work. If a checkpoint feels larger, split it.
