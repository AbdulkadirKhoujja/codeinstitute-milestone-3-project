# Assessment Criteria Tracker

This tracker maps the Level 5 Unit 3 Back End Development criteria to ByteBoard. It is project-specific evidence planning rather than a replacement for the qualification specification. A status is marked **Complete** only where the repository contains verifiable evidence.

Status meanings:

- **Complete** — implemented and supported by repository evidence.
- **In progress** — partly evidenced, with Phase 4 validation or later work required.
- **Planned** — scheduled but not implemented.
- **Not applicable** — unsuitable for ByteBoard, with a recorded reason.

Current baseline: Phases 1–4 complete. The 11 September 2026 audit at `4eb7e86` passed 209 Django tests, 8 JavaScript interaction tests, JavaScript lint without errors or warnings, Python style checks, Django system checks, migration drift checks and Git whitespace checks. The final comprehensive disposable-local PostgreSQL run passed 212/212 tests in 101.521 seconds, with Heroku production excluded. ByteBoard is live on Heroku in Europe at [https://byteboard-app-69f958f78ff4.herokuapp.com/](https://byteboard-app-69f958f78ff4.herokuapp.com/). Focused hosted smoke evidence covers HTTPS, static assets, Discover, Django Admin reachability, authentication, permission handling and PostgreSQL-backed draft persistence. See [Phase 4 verification](phase-4-verification.md).

## Pass criteria

| Criterion | ByteBoard evidence | Phase | Status | Evidence location |
| --- | --- | --- | --- | --- |
| 1.1 Accessible, purpose-led UX design | Purpose-led pages, semantic landmarks, skip link, visible focus, labelled forms, associated errors, descriptive states | 1–4 | In progress | `templates/`, `static/css/style.css`, `docs/accessibility-requirements.md`; sampled evidence is recorded, with documented zoom and broader screen-reader limits |
| 1.2 Responsive custom HTML and CSS | Template inheritance, semantic HTML, Bootstrap support, substantial original mobile-first CSS | 2; validate in 4 | In progress | `templates/`, `static/css/style.css`; sampled viewport evidence is recorded and genuine zoom remains environment-blocked |
| 1.3 Database-backed data manipulation | Tested Post and Comment CRUD, voting transitions, profiles, feeds, search, filters, sorting, and pagination | 2–3 | Complete | `news/views.py`, `news/forms.py`, `accounts/views.py`, test packages |
| 1.4 Relevant relational database design | User, Category, Post, Comment, and Vote relationships with explicit deletion and integrity rules | 1 | Complete | `docs/database-design.md`, `news/models.py`, `news/migrations/` |
| 1.5 Test procedures | 212/212 disposable-local PostgreSQL Django tests, 8 JavaScript interaction tests, mocked upstream responses, documented TDD/results, local/hosted browser evidence and durable screenshots | 1–4 | Complete | Test packages, `docs/testing.md`, `docs/manual-browser-verification.md` |
| 1.6 Styled Python and validated front end | Python style and JavaScript lint pass; 23 HTML samples passed with zero errors/warnings; CSS validator is externally blocked by HTTP 500 | 2–4 | In progress | `docs/formal-validation.md`, `docs/testing.md`; CSS limitation remains documented |
| 1.7 Python proficiency | Views, model forms, ORM filters/aggregation, permissions, validation, pagination, cache use, HTTP/JSON normalization, and controlled exceptions | 2–3 | Complete | `accounts/`, `news/views.py`, `news/forms.py`, `news/services/`, tests |
| 1.8 Compound Python statements | Request handling, privacy branches, sorting, search, form configuration, and template iteration | 2–3 | Complete | Views, forms, templates, and tests |
| 1.9 Readable code | Descriptive names, focused functions, conventional app boundaries, and concise docstrings | 1–4 | Complete | Source tree and final verification evidence |
| 1.10 Cross-platform filenames | Lower-case descriptive names without spaces, grouped by responsibility | 1–4 | Complete | Repository file tree |
| 2.1 Purposeful data model | Entities and relationships support ownership, moderation-ready discussion, and story ranking | 1 | Complete | `news/models.py`, `docs/database-design.md` |
| 2.2 Usable relational database | Local SQLite migrations 0001–0005 applied; environment-driven PostgreSQL, local cross-process cache evidence, deployed Heroku Postgres persistence after refresh/navigation, and 212/212 disposable-local PostgreSQL tests | 1; production in 4 | Complete | `docs/feed-refresh-design.md`, `docs/deployment-preparation.md`, `docs/testing.md` |
| 3.1 Create, locate, display, edit, and delete records | Full owner-restricted Post and Comment CRUD plus feeds, profiles, discovery, voting, ownership, moderation visibility, and privacy | 2–3 | Complete | News/account views, forms, templates, and tests |
| 4.1 Cloud deployment and parity | PostgreSQL-backed Heroku deployment in Europe; HTTPS, migrations and focused runtime smoke evidence | 4 | Complete | `docs/deployment-preparation.md`, `docs/phase-4-verification.md` |
| 4.2 Clean deployed code and working links | Live HTTPS home, static assets, Discover, access boundary and Admin reachability passed | 4 | Complete | `docs/manual-browser-verification.md`, deployed application |
| 4.3 Deployment documentation | Verified app URL, Heroku/Postgres setup, migrations and smoke outcomes recorded | 4 | Complete | README and `docs/deployment-preparation.md` |
| 5.1 Git and GitHub history | Small descriptive commits independently pushed throughout development; final release state is clean and synchronized | 1–final operation | Complete | Git log and GitHub repository |
| 5.2 No committed credentials | Ignore rules plus targeted tracked-file and Git-history secret reviews found no real credential; current-tree security review passed | 1–final operation | Complete | `.gitignore` and `docs/security-verification.md` |
| 5.3 Environment-managed secrets | `SECRET_KEY` loaded from the environment; local environment files ignored | 1–final operation | Complete | `byteboard/settings.py`, `.gitignore` |
| 5.4 Production DEBUG disabled | DEBUG defaults off with isolated settings tests; focused hosted HTTPS smoke and security evidence recorded | 4 and final operation | Complete | `docs/deployment-preparation.md`, `docs/security-verification.md` |

## Merit criteria

| Criterion | ByteBoard evidence | Phase | Status | Evidence location |
| --- | --- | --- | --- | --- |
| M(i) Intuitive accessible UX | Clear stories, categories, search, account state, and contribution actions with accessible forms | 2–4 | In progress | Templates, CSS and accessibility/testing documents; sampled evidence is recorded, with documented zoom and broader screen-reader limits |
| M(ii) User-controlled actions and immediate feedback | Explicit forms, confirmation, messages, Post/Redirect/Get, and updated destinations | 2–3 | Complete | Views, templates, and tests |
| M(iii) Immediately evident purpose | Technology-news purpose is stated in the home hero above the public feed | 2 | Complete | `templates/news/post-list.html`, foundation tests |
| M(iv) Correct template syntax and logic | Inheritance, includes, URL reversal, conditionals, loops, filters, CSRF, context, and empty states | 2–3 | Complete | `templates/` and template/view tests |
| M(v) Robust error-free implementation | Missing-data, invalid-input, redirect, permission, privacy, unsupported-method paths and hosted smoke paths are evidenced | 2–4 | Complete | Tests and `docs/manual-browser-verification.md` |
| M(vi) Fully documented testing | Historical Phase 2/3 results and current Phase 4 automation, corrections, formal validation and documented limitations recorded | 2–4 | Complete | `docs/testing.md` |
| M(vii) Complete README schema | Every domain-model field, relationship, deletion rule, and constraint described | 2 | Complete | README data-model section |
| M(viii) Central database configuration | SQLite/PostgreSQL selection, URL parsing and connection options centralised and tested; deployed PostgreSQL persistence and final disposable-local suite passed | 1 and 4 | Complete | `docs/deployment-preparation.md`, `docs/testing.md` |
| M(ix) Maintained deployment files | Pinned requirements, Procfile, runtime declaration and WhiteNoise settings deployed; hosted static-asset smoke check passed | 4 | Complete | `requirements.txt`, `Procfile`, `.python-version`, `docs/deployment-preparation.md` |
| M(x) Working CRUD | Complete authenticated owner-restricted Post and Comment create, read, update, and delete | 2–3 | Complete | Views, forms, URLs, templates, and tests |
| M(xi) CRUD immediately reflected | Successful Post/Comment actions redirect to updated destinations; votes update immediately when enhanced and still work by redirect fallback | 2–3 | Complete | Integration tests, JavaScript, and rendered pages |
| M(xii) Small feature/fix commits | Green vertical slices are coherent, descriptive, reviewed, and independently pushed | 1–final operation | In progress | Git log and remote history |
| M(xiii) Complete deployment procedure | Real Heroku deployment steps and focused outcomes documented | 4 | Complete | README and `docs/deployment-preparation.md` |
| M(xiv) Clear rationale, audience, data, and security | Purpose, audience, architecture, full schema, ownership, privacy, and secret handling documented | 1–4 | Complete | README, project brief, database design, and testing docs |

## Distinction characteristics

| Characteristic | ByteBoard evidence | Phase | Status | Evidence location |
| --- | --- | --- | --- | --- |
| Clear justified real-world purpose | Focused discovery and owned community submissions address fragmented technology reporting | 1–2 | Complete | Project brief, README, purpose-led home page |
| Original, fully functioning application | Accounts, private drafts, owner-restricted Post/Comment CRUD, voting, and separate cached external discovery are working; release validation is recorded | 2–4 | Complete | Application and automated tests |
| Professional, publishable interface | Coherent identity, original responsive CSS, accessible interaction, and ByteBoard-specific wording; documented zoom, screen-reader and CSS-validator limitations remain | 2–4 | Complete | Templates, stylesheet and verification records |
| Clear front-end/back-end relationship | Forms, views, templates, ORM queries, JSON endpoints, cache/service boundaries, progressive JavaScript, permissions, messages, and relational records are connected and explained | 2–3 | Complete | Code, README architecture section, and tests |
| Well-designed relational data and full CRUD | Database integrity supports complete owner-restricted Post CRUD | 1–2 | Complete | Models, migrations, README schema, CRUD tests/pages |
| Framework conventions and craftsmanship | App boundaries, named URLs, template inheritance, model forms, settings, messages, and static assets are conventional | 2–4 | Complete | Repository structure and final audit |
| Defensive, secure behaviour | CSRF, authenticated mutations, private drafts/comments, vote allow-listing, safe redirects/URLs/DOM rendering, bounded upstream work, controlled errors, ownership, method restrictions, and environment secrets | 2–4 | Complete | Negative-path tests and security verification |
| Comprehensive lifecycle evidence | Stories, designs, TDD cycles, commits, tests, limitations, deployment and release evidence remain traceable | 1–final operation | Complete | Documentation, tests and Git history |

## Phase boundaries

- **Phase 1 complete:** planning, wireframes, relational models/migrations, constraints, Admin and model/admin tests.
- **Phase 2 complete:** accounts, templates, navigation, original CSS, authentication, profiles, Post CRUD, ownership, draft privacy, filtering, search, vote-score sorting, pagination, feedback, TDD, and assessment updates.
- **Phase 3 complete:** Comment CRUD/moderation visibility, voting actions and fallback, custom JavaScript, bounded/cached Hacker News discovery, failure handling, custom error pages, community UX refinement, and automated evidence.
- **Phase 4 complete:** release settings, PostgreSQL configuration, bounded/shared feed refresh, executable JavaScript checks, Python style tooling, corrective tests, static preparation, formal validation, local browser checks, hosted Heroku smoke evidence, security/performance evidence, screenshots, final PostgreSQL testing, and final release evidence are recorded. Genuine zoom/reflow remains environment-blocked; official CSS validation remains externally blocked by HTTP 500 with `java.lang.IllegalStateException: Reader used`; broader screen-reader coverage is not claimed.
- **Deployment complete:** Heroku hosting, production migrations, PostgreSQL-backed persistence, focused live evidence and the final release check are recorded.
