# Development Roadmap

ByteBoard is planned in four phases so that data integrity and documented user needs guide the interface. Status labels in this file should be updated as work is completed; planned items are not implemented-feature claims.

## Status key

- **Completed:** merged and verified in the repository.
- **Current:** actively in scope for the named phase.
- **Planned:** agreed future work, not yet implemented.
- **Excluded:** deliberately outside the four-phase milestone scope unless reprioritised.

## Phase 1 — Planning and Data Foundation

Status: **Completed**. The planning artefacts, four migrated domain models, database constraints, Django Admin registrations, automated model/admin tests, and initial README are present.

Scope:

- audit repository state, ignore rules, environment handling, and baseline Django checks;
- document purpose, audience, user and owner goals, user stories, and acceptance criteria;
- plan information flow, pages, responsive behaviour, and accessibility requirements;
- produce clearly labelled home, post-detail, form, and profile wireframes;
- document the relational design and Mermaid ERD;
- implement Category, Post, Comment, and Vote models with migrations;
- enforce protected category deletion and vote integrity at database level;
- register domain models with useful Django Admin configuration;
- add isolated model and admin tests; and
- establish an honest README and this roadmap.

Exit criteria:

- Django reports no system-check issues.
- No model change lacks a migration.
- All Phase 1 automated tests pass in an isolated test database.
- Planning documents agree with implemented data relationships.
- Secrets and local database files remain ignored and untracked.

Explicitly not in this phase: authentication pages, post CRUD views, templates, comments UI, voting UI, search, styling, production configuration, or deployment.

## Phase 2 — Core Application

Status: **Completed**. The core visitor and member journeys are implemented, covered by isolated tests, and documented without representing later community or deployment work as complete.

Scope:

- add public URL patterns, views, and templates;
- implement registration, sign-in, and sign-out with the selected Django authentication approach;
- build a published-post feed and category filtering;
- add text search, score/date/title sorting, pagination, and contextual empty states;
- build post detail and safe external-article linking;
- implement authenticated post create, read, update, and delete journeys;
- enforce post ownership and permission handling on the server;
- add profile/member-post functionality needed to manage contributions;
- introduce the base responsive layout and reusable components; and
- test views, forms, URLs, authentication, permissions, and primary templates.

Exit criteria met: visitors can discover and read published stories; members can register, sign in, sign out, manage only their own stories, and keep drafts private; the shared responsive interface is present; and the Phase 2 automated suite, Django check, and migration drift check pass. Community interactions and deployment remain explicitly separate.

## Phase 3 — Community and UX

Status: **Completed**. Community discussion, voting, the separate Hacker News discovery experience, custom JavaScript, controlled failures, and custom error pages are implemented and were verified by 173 tests at Phase 3 closure. The current Phase 4 audit passes 209 Django tests. The browser capability exposed no usable session, so formal interactive verification remains honestly assigned to Phase 4.

Scope:

- add approved comment display and authenticated comment creation;
- add owner-restricted comment edit and delete journeys;
- add upvote/downvote behaviour without duplicate votes;
- expose accurate vote scores and user vote state;
- refine moderation workflow and feedback;
- add the approved custom JavaScript enhancement and external-news integration with caching and failure handling;
- add custom navigable error pages and community-specific interface refinements; and
- extend automated tests for comments, voting, integration, moderation, and accessibility-sensitive behaviour.

Exit criteria met: approved comments are public while pending comments remain visible only to their author; members can create, edit, and delete only their own comments; published stories support create/change/remove voting with and without JavaScript; external stories are normalized through a same-origin cached service with a 20–50 limit and 60-second cache; failures remain controlled; custom error pages are navigable; and all automated, system, migration, and JavaScript syntax checks pass.

## Phase 4 — Testing, Documentation and Deployment

Status: **Current**. Phases 1–3 are complete. Phase 4 implementation and verification are underway; deployment has not occurred.

Completed preparation includes explicit release security settings, PostgreSQL configuration, Gunicorn/WhiteNoise setup, shared database feed coordination and bounded refresh, guarded sample data, executable JavaScript tests, markup/security/moderation corrections and Python style tooling. The 11 September 2026 audit at `4eb7e86` passed 209 Django tests, 8 JavaScript interaction tests, JavaScript lint without errors or warnings, Python style checks, Django system checks, migration drift checks and Git whitespace checks.

Recorded evidence includes local PostgreSQL cross-process feed coordination and 23 HTML samples with zero validator errors or warnings. Official CSS validation remains unresolved after HTTP 500 responses. Manual browser, responsive, accessibility, full current-suite PostgreSQL and hosted-runtime verification remain outstanding. See [Phase 4 verification](phase-4-verification.md) for evidence and limits.

Scope:

- execute the documented manual functional test matrix across supported browsers and viewports;
- perform keyboard, screen-reader spot, contrast, zoom, and reflow accessibility checks;
- run automated tests and record real results only;
- validate rendered HTML/CSS and run performance/accessibility tooling where applicable;
- configure PostgreSQL and production environment variables;
- harden deployment settings, allowed hosts, static assets, and error handling;
- deploy to the selected host and verify production data/migrations;
- add real deployment, testing, validation, and defect-resolution evidence to the README; and
- complete credits and attribution required by the course.

Exit criteria include a reproducible deployment and accurate evidence. No live URL, score, validator result, or browser result should be documented before it exists.

## Testing strategy across phases

- Model constraints and ordering are tested as soon as the relevant model exists.
- View, form, permission, and template tests arrive with their Phase 2 or Phase 3 behaviour.
- Tests create their own isolated records and never depend on the local SQLite database.
- Regression tests are added for every material defect that can be reproduced automatically.
- Manual tests supplement automation for usability, responsive layout, accessibility, and external-service behaviour.

## Deployment intentions

PostgreSQL configuration, Gunicorn, environment-provided secrets and WhiteNoise static serving are prepared for the intended Heroku deployment. The [deployment preparation](deployment-preparation.md) records local checks and the separate deployment procedure. Hosting resources, hosted-runtime verification and a live URL remain outstanding. `env.py`, `.env`, local databases, and credentials must never be committed.

## Future improvements outside the agreed phases

The following ideas are **excluded** from the milestone unless separately planned after the four phases:

- real-time notifications or chat;
- social login;
- user follows, bookmarks, or personalised recommendation feeds;
- image or file uploads;
- reputation, badges, or gamification;
- email digests;
- native mobile applications;
- public APIs; and
- machine-learning ranking or automated moderation.

## Credits and attribution checklist

Before final submission:

- list each third-party Python, JavaScript, CSS, icon, font, image, and data dependency actually used;
- link to original sources and licences where required;
- identify adapted code in nearby comments and the README;
- document learning resources that materially shaped the implementation;
- retain evidence that all included media and code can be used in the project.
