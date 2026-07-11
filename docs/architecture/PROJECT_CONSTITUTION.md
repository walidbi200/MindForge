# MindForge Project Constitution

This document is the immutable foundation of MindForge. It is never rewritten unless an intentional, systemic architectural or product pivot is formally adopted.

## 1. What is MindForge?
MindForge is a **Personal Knowledge Operating System**. 
It is designed to act as a system of record and learning engine for human intelligence, optimizing for deliberate deep work and long-term knowledge retention.

It exists to help users:
- Transform information into structured knowledge.
- Transform knowledge into practical application.
- Transform application into mastery through deliberate reflection.

## 2. What MindForge is NOT
- **It is not a chatbot.** AI is an infrastructure service that orchestrates insights, not a conversational oracle.
- **It is not an autonomous agent.** It does not take actions on behalf of the user without explicit consent.
- **It is not a note generator or dumping ground.** It is a deliberate graph of synthesized ideas.
- **It is not a replacement for human thinking.** MindForge assists decision-making and reduces friction, but the user must do the critical thinking.
- **It is not an infinite scroll or social feed.** No gamified streak systems, engagement hooks, or notifications.

## 3. Immutable Architectural Rules
1. **Domain Purity:** The Domain layer contains zero infrastructure, framework, or presentation details.
2. **Infrastructure Sovereignty:** Infrastructure owns external integrations (Databases, AI, Event Bus). AI is purely infrastructure.
3. **Application Orchestration:** The Application layer coordinates business logic and transactions. It never knows about HTTP or React.
4. **API Cleanliness:** The API layer never exposes raw domain entities. It strictly accepts and returns explicit, validated schemas.
5. **Durable Timeline:** Every state change emits a synchronous event that is durably logged to the user's Timeline.
6. **AI is Read-Only by Default:** AI cannot mutate the database. AI generates structured suggestions; only the user's explicit approval triggers database mutations via the Application layer.
7. **SQLite First:** The relational database remains the source of truth. No CQRS or event sourcing until scale warrants it.

## 4. Product Principles
Every feature must strengthen one of four pillars:
- **Capture:** Intentionally gathering evidence and inputs.
- **Learn:** Deliberate spaced reviews and knowledge graph synthesis.
- **Apply:** Connecting stored concepts to real-world tasks.
- **Reflect:** Auditing gaps in understanding.

**If a feature does not improve one of these pillars, it should not be built.**

## 5. Feature Evaluation
Future checkpoints are evaluated by a single defining question:
> **"Can a real user accomplish something new that they could not do before?"**

If a checkpoint cannot answer this with a demonstrable user capability, it is likely too infrastructure-focused and should be re-evaluated.
