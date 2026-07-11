# MindForge Checkpoint Template

Every future checkpoint (starting with Checkpoint 17) must follow this exact structure to ensure consistency in both the prompt used to initiate the checkpoint, and the documentation generated upon its completion.

---

## Part 1: The Prompt Template
When initiating a new checkpoint, the prompt provided to the AI MUST follow this structure. This ensures a complete, unambiguous execution boundary.

```markdown
# Checkpoint XX Prompt

## Phase 0 — Research
Before writing any code:
- Review previous checkpoint.
- Review architecture constraints.
- Identify affected bounded contexts.
- Search for existing implementations.
- Identify migrations required.
- Produce implementation plan.
No implementation begins before the plan is approved.

## Goal
[Provide a clear, high-level goal for the checkpoint. Explain what it accomplishes.]

## User Workflow
[Explain the end-to-end user workflow changes. What can the user do now that they couldn't before? Use a diagram.]
Example:
Capture
↓
AI Analysis
↓
Preview
↓
User edits
↓
Apply
↓
Concepts
↓
Collections
↓
Reviews
↓
Timeline
↓
Workspace Refresh

## Domain Layer
- Create: [list entities, exceptions, events]
- Modify: [list entities, exceptions, events]
- Delete: [list entities, exceptions, events]

## Application Layer
- Create: [list use cases]
- Modify: [list use cases]
- Delete: [list use cases]

## Infrastructure Layer
- Repositories: [list repository changes]
- Migrations: [list alembic migrations needed]
- AI: [list changes to AI services]

## API
- Endpoints: [list routes to create/modify]
- Schemas: [list request/response schemas]
- Errors: [list HTTP error mappings]

## Frontend
- Views: [list views]
- Components: [list components]
- UX: [describe UI behavior]
- Loading: [describe loading states]
- Errors: [describe error states]
- Empty states: [describe empty states]

## AI (if applicable)
- Prompt updates: [list prompt changes]
- Protocol updates: [list protocol changes]
- OpenRouter changes: [list implementation changes]
- Structured JSON: [describe expected JSON shapes]

## Events
- Events emitted: [list domain events]
- Timeline entries: [list timeline mappings]

## Tests
- Repository: [list repository tests]
- Application: [list use case tests]
- API: [list API tests]
- Frontend: [list frontend tests/verification]
- Manual verification: [list manual steps]

## Documentation
Update:
- PROJECT_STATUS
- CHANGELOG
- DEVELOPMENT_JOURNAL
- walkthrough.md
- task.md
- foundation.md (only if architecture changes)

## Acceptance Criteria
- [ ] [Criterion 1]
- [ ] [Criterion 2]

## Deliverables
[List exactly what files should exist or be modified.]

## Definition of Done
Implementation
☐ Complete

Tests
☐ Passing

Frontend
☐ Builds

Docker
☐ Verified

Documentation
☐ Updated

Migration
☐ Verified

Timeline
☐ Verified

Walkthrough
☐ Written

Version
☐ Tagged

Next Checkpoint
☐ Prepared
```

---

## Part 2: The Documentation Completion Template

When a checkpoint is successfully completed, the final documentation (specifically `walkthrough.md`, and summaries in `DEVELOPMENT_JOURNAL.md` and `CHANGELOG.md`) MUST follow this structure.

```markdown
# Checkpoint [XX]
**Version:** v0.0.[XX]

## 1. Goal
[Briefly describe the goal that was achieved.]

## 2. Scope
**Included**
✓ Backend
✓ Frontend
✓ API
✓ Tests
✓ Documentation
✓ Migration

**Not Included**
✗ [List what was explicitly avoided]

## 3. Architecture Impact
**Affected Domains**
- [Domain 1]
- [Domain 2]

**New Domains**
- [None / Name]

**Breaking Changes**
- [None / Description]

**Migration Required**
- [Yes / No]

**Database Version**
v0.0.[XX]

## 4. Files Created
**NEW**
[List new files organized by layer (application/, domain/, api/, frontend/, etc.)]

## 5. Files Modified
**MODIFIED**
[List modified files]

## 6. Architecture Decisions
**Decision:** [What was decided]
**Reason:** [WHY it was decided]

## 7. User Workflow
[Include a text-based workflow diagram of the newly implemented flow]
Example:
Capture
↓
AI Analysis
↓
Preview
↓
User edits
↓
Apply
↓
Concepts
↓
Collections
↓
Reviews
↓
Timeline
↓
Workspace Refresh

## 8. Feature Acceptance Test
**Can a real user accomplish something new that they could not do before?**
**Before:** [Describe what was possible]
**After:** [Describe the new capability]

## 9. Demo Script
[Write a step-by-step manual test script that can be used to visually verify the feature in the UI]
Example:
1. Open Daily Workspace.
2. Create Capture: "I learned Docker volumes."
3. Click Process with AI.
4. AI suggests: ...
5. Accept.
6. Open Graph. Docker is connected.
7. Timeline shows every event.

## 10. Future Debt
**Not implemented:**
- [Feature 1]
- [Feature 2]

**Reason:**
[Why it was deferred]

## 11. Architectural Debt
- [List any conscious technical tradeoffs made]
- Accepted for [Current Release].
- Revisit before [Future Release].

## 12. DDD Checklist
✓ Domain has no infrastructure dependency
✓ Application owns orchestration
✓ Infrastructure owns implementation
✓ API contains no business logic
✓ AI remains infrastructure
✓ Timeline events emitted
✓ UoW transaction boundary respected
✓ Repository interfaces unchanged unless required

## 13. AI Checklist (If applicable)
✓ Uses AIService protocol
✓ Uses OpenRouter implementation
✓ Prompt stored in prompts/
✓ Structured JSON only
✓ Stable AIResponse schema
✓ Provider agnostic
✓ Timeout configured
✓ Retry configured
✓ Token accounting recorded
✓ AI never mutates database directly

## 14. UX Checklist
✓ Loading state
✓ Empty state
✓ Error state
✓ Success feedback
✓ Confirmation dialog
✓ Responsive layout
✓ Keyboard accessible

## 15. Performance Checklist
✓ Pagination
✓ No N+1 queries
✓ Indexed queries
✓ Transaction boundaries
✓ Query count reviewed
✓ AI requests async where appropriate

## 16. Verification
**Backend**
✓ pytest
✓ ruff
✓ mypy

**Frontend**
✓ npm build

**Docker**
✓ docker compose

**API**
✓ curl

**Manual**
✓ workflow verified

## 17. Documentation Updated
✓ CHANGELOG
✓ PROJECT_STATUS
✓ DEVELOPMENT_JOURNAL
✓ walkthrough.md
✓ task.md

## 18. Next Checkpoint
**Next:** Checkpoint [XX+1] - [Name of next checkpoint]
```
