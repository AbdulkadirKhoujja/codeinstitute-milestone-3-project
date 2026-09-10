# Assessment Criteria Tracker

This tracker maps the Level 5 Unit 3 Back End Development criteria to ByteBoard. It is project-specific evidence planning rather than a replacement for the qualification specification. A status is marked **Complete** only where the repository contains verifiable evidence; formal validation and deployment criteria remain open.

Status meanings:

- **Complete** — implemented and supported by repository evidence.
- **In progress** — partly evidenced, with Phase 4 validation or later work required.
- **Planned** — scheduled but not implemented.
- **Not applicable** — unsuitable for ByteBoard, with a recorded reason.

Current baseline: Phases 1–3 complete; Phase 4 underway. The 11 September 2026 audit at `4eb7e86` passed 209 Django tests, 8 JavaScript interaction tests, JavaScript lint without errors or warnings, Python style checks, Django system checks, migration drift checks and Git whitespace checks. See [Phase 4 verification](phase-4-verification.md). No deployment/live URL or manual browser/accessibility/hosted-runtime pass is recorded.

## Pass criteria

| Criterion | ByteBoard evidence | Phase | Status | Evidence location |
| --- | --- | --- | --- | --- |
| 1.1 Accessible, purpose-led UX design | Purpose-led pages, semantic landmarks, skip link, visible focus, labelled forms, associated errors, descriptive states | 1–4 | In progress | `templates/`, `static/css/style.css`, `docs/accessibility-requirements.md`; formal checks remain Phase 4 |
| 1.2 Responsive custom HTML and CSS | Template inheritance, semantic HTML, Bootstrap support, substantial original mobile-first CSS | 2; validate in 4 | In progress | `templates/`, `static/css/style.css`; formal viewport matrix remains |
| 1.3 Database-backed data manipulation | Tested Post and Comment CRUD, voting transitions, profiles, feeds, search, filters, sorting, and pagination | 2–3 | Complete | `news/views.py`, `news/forms.py`, `accounts/views.py`, test packages |
| 1.4 Relevant relational database design | User, Category, Post, Comment, and Vote relationships with explicit deletion and integrity rules | 1 | Complete | `docs/database-design.md`, `news/models.py`, `news/migrations/` |
| 1.5 Test procedures | 209 passing Django tests, 8 passing JavaScript interaction tests, mocked upstream responses and documented historical TDD/results; manual matrices remain outstanding | 1–4 | In progress | Test packages and `docs/testing.md` |
| 1.6 Styled Python and validated front end | Python style and JavaScript lint pass; 23 HTML samples recorded with zero errors/warnings; CSS validator returned HTTP 500 | 2–4 | In progress | `docs/formal-validation.md`, `docs/testing.md`; CSS and final validation coverage remain open |
| 1.7 Python proficiency | Views, model forms, ORM filters/aggregation, permissions, validation, pagination, cache use, HTTP/JSON normalization, and controlled exceptions | 2–3 | Complete | `accounts/`, `news/views.py`, `news/forms.py`, `news/services/`, tests |
| 1.8 Compound Python statements | Request handling, privacy branches, sorting, search, form configuration, and template iteration | 2–3 | Complete | Views, forms, templates, and tests |
| 1.9 Readable code | Descriptive names, focused functions, conventional app boundaries, and concise docstrings | 1–4 | In progress | Source tree; final audit remains Phase 4 |
| 1.10 Cross-platform filenames | Lower-case descriptive names without spaces, grouped by responsibility | 1–4 | Complete | Repository file tree |
| 2.1 Purposeful data model | Entities and relationships support ownership, moderation-ready discussion, and story ranking | 1 | Complete | `news/models.py`, `docs/database-design.md` |
| 2.2 Usable relational database | Local SQLite migrations 0001–0005 applied; environment-driven PostgreSQL configuration and local cross-process cache evidence | 1; production in 4 | In progress | `byteboard/settings.py`, `docs/feed-refresh-design.md`; full current-suite PostgreSQL and hosted verification remain |
| 3.1 Create, locate, display, edit, and delete records | Full owner-restricted Post and Comment CRUD plus feeds, profiles, discovery, voting, ownership, moderation visibility, and privacy | 2–3 | Complete | News/account views, forms, templates, and tests |
| 4.1 Cloud deployment and parity | PostgreSQL-backed cloud release and local/production parity verification | Final operation after 4 | Planned | Deployment evidence and README |
| 4.2 Clean deployed code and working links | Route/link, browser/server, and abandoned-code audits before and after release | 4 and final operation | Planned | Testing record and deployed application |
| 4.3 Deployment documentation | Verified release process, purpose, and user value | Final operation after 4 | Planned | README deployment section |
| 5.1 Git and GitHub history | Small descriptive commits independently pushed throughout development | 1–final operation | In progress | Git log and GitHub repository |
| 5.2 No committed credentials | Ignore rules plus tracked/staged secret and local-database audits | 1–final operation | In progress | `.gitignore` and final security audit |
| 5.3 Environment-managed secrets | `SECRET_KEY` loaded from the environment; local environment files ignored | 1–final operation | Complete | `byteboard/settings.py`, `.gitignore` |
| 5.4 Production DEBUG disabled | DEBUG defaults off with isolated settings tests; hosted verification remains | 4 and final operation | In progress | `news/tests/test_release_settings.py`, `docs/deployment-preparation.md` |

## Merit criteria

| Criterion | ByteBoard evidence | Phase | Status | Evidence location |
| --- | --- | --- | --- | --- |
| M(i) Intuitive accessible UX | Clear stories, categories, search, account state, and contribution actions with accessible forms | 2–4 | In progress | Templates, CSS, accessibility/testing documents; formal browser matrix remains |
| M(ii) User-controlled actions and immediate feedback | Explicit forms, confirmation, messages, Post/Redirect/Get, and updated destinations | 2–3 | Complete | Views, templates, and tests |
| M(iii) Immediately evident purpose | Technology-news purpose is stated in the home hero above the public feed | 2 | Complete | `templates/news/post-list.html`, foundation tests |
| M(iv) Correct template syntax and logic | Inheritance, includes, URL reversal, conditionals, loops, filters, CSRF, context, and empty states | 2–3 | Complete | `templates/` and template/view tests |
| M(v) Robust error-free implementation | Missing-data, invalid-input, redirect, permission, privacy, and unsupported-method paths are tested | 2–4 | In progress | Application code and tests; browser pass remains unavailable |
| M(vi) Fully documented testing | Historical Phase 2/3 results and current Phase 4 automation, corrections, HTML validation and evidence gaps recorded | 2–4 | In progress | `docs/testing.md`; later formal evidence remains |
| M(vii) Complete README schema | Every domain-model field, relationship, deletion rule, and constraint described | 2 | Complete | README data-model section |
| M(viii) Central database configuration | SQLite/PostgreSQL selection, URL parsing and connection options centralised and tested; hosted verification remains | 1 and 4 | In progress | `byteboard/settings.py` |
| M(ix) Maintained deployment files | Pinned requirements, Procfile, runtime declaration and WhiteNoise settings prepared; hosted verification remains | 4 | In progress | `requirements.txt`, `Procfile`, `.python-version`, `docs/deployment-preparation.md` |
| M(x) Working CRUD | Complete authenticated owner-restricted Post and Comment create, read, update, and delete | 2–3 | Complete | Views, forms, URLs, templates, and tests |
| M(xi) CRUD immediately reflected | Successful Post/Comment actions redirect to updated destinations; votes update immediately when enhanced and still work by redirect fallback | 2–3 | Complete | Integration tests, JavaScript, and rendered pages |
| M(xii) Small feature/fix commits | Green vertical slices are coherent, descriptive, reviewed, and independently pushed | 1–final operation | In progress | Git log and remote history |
| M(xiii) Complete deployment procedure | Real deployment steps and outcomes documented after a successful release | Final operation after 4 | Planned | README deployment guide |
| M(xiv) Clear rationale, audience, data, and security | Purpose, audience, architecture, full schema, ownership, privacy, and secret handling documented | 1–4 | Complete | README, project brief, database design, and testing docs |

## Distinction characteristics

| Characteristic | ByteBoard evidence | Phase | Status | Evidence location |
| --- | --- | --- | --- | --- |
| Clear justified real-world purpose | Focused discovery and owned community submissions address fragmented technology reporting | 1–2 | Complete | Project brief, README, purpose-led home page |
| Original, fully functioning application | Accounts, private drafts, owner-restricted Post/Comment CRUD, voting, and separate cached external discovery are working; formal release validation remains | 2–4 | In progress | Application and automated tests |
| Professional, publishable interface | Coherent identity, original responsive CSS, accessible interaction, and ByteBoard-specific wording | 2–4 | In progress | Templates and stylesheet; browser/validation evidence remains |
| Clear front-end/back-end relationship | Forms, views, templates, ORM queries, JSON endpoints, cache/service boundaries, progressive JavaScript, permissions, messages, and relational records are connected and explained | 2–3 | Complete | Code, README architecture section, and tests |
| Well-designed relational data and full CRUD | Database integrity supports complete owner-restricted Post CRUD | 1–2 | Complete | Models, migrations, README schema, CRUD tests/pages |
| Framework conventions and craftsmanship | App boundaries, named URLs, template inheritance, model forms, settings, messages, and static assets are conventional | 2–4 | In progress | Repository structure and final audit |
| Defensive, secure behaviour | CSRF, authenticated mutations, private drafts/comments, vote allow-listing, safe redirects/URLs/DOM rendering, bounded upstream work, controlled errors, ownership, method restrictions, and environment secrets | 2–4 | In progress | Negative-path tests and future production security review |
| Comprehensive lifecycle evidence | Stories, designs, TDD cycles, commits, tests, limitations, and later release evidence remain traceable | 1–final operation | In progress | Documentation, tests, Git history, future deployment evidence |

## Phase boundaries

- **Phase 1 complete:** planning, wireframes, relational models/migrations, constraints, Admin and model/admin tests.
- **Phase 2 complete:** accounts, templates, navigation, original CSS, authentication, profiles, Post CRUD, ownership, draft privacy, filtering, search, vote-score sorting, pagination, feedback, TDD, and assessment updates.
- **Phase 3 complete:** Comment CRUD/moderation visibility, voting actions and fallback, custom JavaScript, bounded/cached Hacker News discovery, failure handling, custom error pages, community UX refinement, and automated evidence.
- **Phase 4 underway:** release settings, PostgreSQL configuration, bounded/shared feed refresh, executable JavaScript checks, Python style tooling, corrective tests, local static preparation and HTML sample validation are evidenced. Manual browser/responsive/accessibility checks, CSS validation, full current-suite PostgreSQL checks, hosted-runtime verification and final submission evidence remain open.
- **Final deployment operation planned:** hosting configuration, deployment, production migrations, parity testing, genuine live evidence, and verified deployment documentation.
