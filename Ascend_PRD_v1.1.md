# Ascend --- Personal Learning & Growth System

## Product Requirements Document --- MVP (v1.1)

### Vision

Ascend is **not a note-taking application**. It is a **Personal Learning
Operating System** that helps transform information into long-term
knowledge and practical execution.

## Core Learning Loop

Capture → Understand → Review → Recall → Promote → Apply → Reflect

### Knowledge Lifecycle

1.  Inbox (captured)
2.  Processed (AI summary + raw source)
3.  Kept
4.  Reviewed (Leitner)
5.  Promoted (Obsidian markdown)
6.  Linked (connected to related concepts/projects)
7.  Applied (used in a project, lab, writing, or task)
8.  Archived

## MVP Goals

-   Capture articles, X posts, YouTube links.
-   Store raw source + AI summary together.
-   Build a bounded daily learning session.
-   Spaced repetition using Leitner.
-   Promote notes into Obsidian.
-   Track domains instead of hard-coded subjects.
-   Weekly reflection dashboard.

## Domains

Domains are configurable and replace fixed counters.

Examples: - AI - Networking - Linux - German - Business - Fitness -
Smart Gift Finder - Audify

Each domain tracks: - Captures - Reviews - Promoted notes - Streak -
Weekly activity

## Data Model Additions

### Items

Additional fields: - learning_state: unread \| reading \| finished \|
reviewed \| mastered - confidence_score - why_saved - application_target

### Concept Links

Relationship graph between notes and concepts.

### Projects

Notes can optionally link to one or more projects.

## Daily Session

Priority: 1. Due reviews 2. High-priority unread captures 3. Recently
failed recalls

Session is finite---never infinite scroll.

## Weekly Reflection

Display: - Items captured - Reviews completed - Recall success rate -
Weak domains - Strong domains - Most active project - Suggested focus
next week

## Non-goals (MVP)

-   RPG UI
-   XP
-   Quests
-   PDF reader
-   Books
-   Mobile sync
-   Quiz engine
-   Gym tracking

## Phase 2

-   AI Tutor
-   Adaptive quizzes
-   Gym module
-   Books/PDF reader
-   Skill tree
-   XP & achievements
-   Multi-device sync

## Design Principles

-   Learning over collecting.
-   Application over memorization.
-   Simplicity over feature creep.
-   Finite sessions over endless feeds.
-   User knowledge over AI-generated notes.
