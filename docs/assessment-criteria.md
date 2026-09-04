# Assessment Criteria Tracker

This tracker maps the Level 5 Unit 3 Back End Development criteria to ByteBoard. It is project-specific evidence planning rather than a replacement for the qualification specification. A status is only marked **Complete** where the repository already contains verifiable evidence.

Status meanings:

- **Complete** — implemented and supported by repository evidence.
- **In progress** — partly evidenced, with further Phase 2 or later work required.
- **Planned** — scheduled but not yet implemented.
- **Not applicable** — unsuitable for ByteBoard, with a recorded reason.

## Pass criteria

| Criterion | How ByteBoard will meet it | Feature or evidence | Phase | Status | Final evidence location |
| --- | --- | --- | --- | --- | --- |
| 1.1 Accessible, purpose-led UX design | Build semantic, keyboard-friendly journeys around browsing and contributing technology news. | Wireframes, page specification, accessibility requirements, implemented templates | 1–4 | In progress | `docs/wireframes/`, `docs/accessibility-requirements.md`, templates, final testing evidence |
| 1.2 Responsive custom HTML and CSS | Use template inheritance, semantic HTML, Bootstrap support, and substantial original mobile-first CSS. | Shared templates and `static/css/style.css` | 2; validate in 4 | Planned | Templates, stylesheet, responsive test results |
| 1.3 Database-backed data manipulation | Let authenticated users create and manage posts while visitors locate and read published records. | Post CRUD, profiles, feeds, search, filters | 2 | Planned | Views, forms, templates, automated tests |
| 1.4 Relevant relational database design | Model users, categories, posts, comments, and votes with explicit deletion and integrity rules. | ERD, four domain models, four migrations | 1 | Complete | `docs/database-design.md`, `news/models.py`, `news/migrations/` |
| 1.5 Test procedures | Use isolated automated tests during development, then document manual functionality, usability, responsiveness, and data testing. | Model/admin suite; Phase 2 TDD; full manual matrix later | 1–4 | In progress | Test packages and `docs/testing.md` |
| 1.6 Styled Python and validated front end | Keep Python PEP 8-oriented and prepare HTML/CSS for formal validation after the interface is complete. | Readable Python; validators and style checks | 2–4 | In progress | Application code and Phase 4 validation evidence |
| 1.7 Python proficiency | Use views, forms, ORM filters, aggregation, permissions, validation, and useful return values. | Core application logic | 2–3 | Planned | `accounts/`, `news/views.py`, `news/forms.py`, tests |
| 1.8 Compound Python statements | Use conditionals and iteration where request handling, permissions, sorting, or shared context genuinely needs them. | Views, helpers, and tests | 2–3 | Planned | Application code and tests |
| 1.9 Readable code | Use descriptive names, focused functions, consistent formatting, and comments only for non-obvious decisions. | Whole codebase | 1–4 | In progress | Source review and final audit |
| 1.10 Cross-platform filenames | Keep lower-case descriptive filenames without spaces and group files by responsibility. | Existing docs and planned app/template/static layout | 1–4 | In progress | Repository file tree |
| 2.1 Purposeful data model | Keep entities and relationships aligned with ownership, moderation, discussion, and ranking stories. | Category, Post, Comment, Vote, built-in User | 1 | Complete | `news/models.py`, `docs/database-design.md` |
| 2.2 Usable relational database | Apply reviewed migrations and database constraints with central Django configuration. | SQLite locally, PostgreSQL planned, applied migrations | 1; production in 4 | In progress | `byteboard/settings.py`, migrations, migration checks |
| 3.1 Create, locate, display, edit, and delete records | Deliver complete user-facing Post CRUD plus feed, profiles, category filtering, search, sorting, and pagination. | Core post journeys | 2 | Planned | News/account views, forms, templates, tests |
| 4.1 Cloud deployment and parity | Deploy only after local completion, use PostgreSQL, run migrations, and verify key journeys against development. | Heroku release and parity checks | Final operation after 4 | Planned | Deployment evidence and README |
| 4.2 Clean deployed code and working links | Remove abandoned code, audit internal links, and inspect browser/server errors before and after deployment. | Final code and route/link audit | 4 and final operation | Planned | Testing record and deployed application |
| 4.3 Deployment documentation | Record the verified release process, application purpose, and user value without invented results. | README deployment section | Final operation after 4 | Planned | `README.md` |
| 5.1 Git and GitHub history | Keep small, descriptive commits and independently push completed changes throughout development. | Repository history | 1–final operation | In progress | Git log and GitHub repository |
| 5.2 No committed credentials | Audit tracked and staged files so secrets, passwords, tokens, and local databases never enter Git. | Security checks and ignore rules | 1–final operation | In progress | `.gitignore`, final security audit |
| 5.3 Environment-managed secrets | Continue loading `SECRET_KEY` from the environment and ignoring local environment files. | Settings and ignore rules | 1–final operation | Complete | `byteboard/settings.py`, `.gitignore` |
| 5.4 Production DEBUG disabled | Make debug mode environment-controlled and verify it is disabled in the production release. | Production settings | 4 and final operation | Planned | Settings, Heroku configuration, deployment test |

## Merit criteria

| Criterion | How ByteBoard will meet it | Feature or evidence | Phase | Status | Final evidence location |
| --- | --- | --- | --- | --- | --- |
| M(i) Intuitive accessible UX | Make stories, categories, search, account state, and contribution actions easy to find at mobile and desktop widths. | Navigation, page hierarchy, accessible forms, responsive checks | 2–4 | Planned | Templates, CSS, browser and accessibility evidence |
| M(ii) User-controlled actions and immediate feedback | Use explicit forms, confirmations, messages, Post/Redirect/Get, and immediately updated pages. | Registration, authentication, CRUD, messages | 2–3 | Planned | Views, templates, tests |
| M(iii) Immediately evident purpose | Lead the home page with ByteBoard's technology-news purpose and real site-specific content. | Home hero and story feed | 2 | Planned | Home template and browser verification |
| M(iv) Correct template syntax and logic | Use inheritance, includes, reversal, conditionals, loops, filters, CSRF, context, and empty states only where appropriate. | Shared and feature templates | 2–3 | Planned | `templates/` and template tests |
| M(v) Robust error-free implementation | Handle missing data, invalid input, unsafe redirects, permissions, and unsupported methods without internal errors. | Defensive views/forms and negative-path tests | 2–4 | Planned | Application code, tests, browser checks |
| M(vi) Fully documented testing | Record procedures, actual results, defects, fixes, and any unresolved issues. | Testing document | 2–4 | Planned | `docs/testing.md` |
| M(vii) Complete README schema | Describe every model field, relationship, deletion rule, and constraint directly in the README. | Data-schema section | 2 | Planned | `README.md` |
| M(viii) Central database configuration | Keep the active database configuration in Django settings and make production selection environment-driven later. | Django `DATABASES` setting | 1 and 4 | In progress | `byteboard/settings.py` |
| M(ix) Maintained deployment files | Add and keep requirements, Procfile, settings, and related deployment files accurate when production work begins. | Deployment configuration | 4 | Planned | `requirements.txt`, Procfile, settings |
| M(x) Working CRUD | Provide complete authenticated Post create, read, update, and delete functionality. | Post CRUD | 2 | Planned | Views, forms, URLs, templates, tests |
| M(xi) CRUD immediately reflected | Redirect successful actions to pages that show the saved change or removal immediately. | Detail, feed, and profile journeys | 2 | Planned | Integration tests and rendered pages |
| M(xii) Small feature/fix commits | Keep each green vertical slice coherent, descriptive, reviewed, and independently pushed. | Phase history | 1–final operation | In progress | Git log and remote history |
| M(xiii) Complete deployment procedure | Document the real deployment steps and outcomes after the release succeeds. | README deployment guide | Final operation after 4 | Planned | `README.md` |
| M(xiv) Clear rationale, audience, data, and security | Explain why ByteBoard exists, whom it serves, how its data works, and how user content and secrets are protected. | Brief, README, database and security documentation | 1–4 | In progress | `README.md`, `docs/project-brief.md`, database and testing docs |

## Distinction characteristics

| Characteristic | ByteBoard approach | Phase | Status | Evidence target |
| --- | --- | --- | --- | --- |
| Clear justified real-world purpose | Address fragmented technology discovery with a focused community submission and discussion platform. | 1–2 | In progress | Project brief, README, purpose-led home page |
| Original, fully functioning application | Combine owned community posts, moderation-ready discussion/ranking data, advanced discovery, and later supplementary Hacker News content. | 2–3 | Planned | Working application and automated tests |
| Professional, publishable interface | Use coherent branding, original responsive CSS, accessible interaction, and real ByteBoard wording. | 2–4 | Planned | Templates, stylesheet, browser and validation evidence |
| Clear front-end/back-end relationship | Show how forms, views, templates, ORM queries, permissions, and relational records work together. | 2–3 | Planned | Code, README architecture explanation, tests |
| Well-designed relational data and full CRUD | Retain the Phase 1 model integrity and expose complete Post CRUD with appropriate ownership. | 1–2 | In progress | Models, migrations, CRUD tests and pages |
| Framework conventions and craftsmanship | Keep app boundaries, URLs, templates, forms, settings, messages, and static files understandable and conventional. | 2–4 | Planned | Repository structure and final audit |
| Defensive, secure behaviour | Protect modifying routes, private drafts, redirect targets, ownership, CSRF, and environment secrets. | 2–4 | Planned | Negative-path tests and security review |
| Comprehensive lifecycle evidence | Maintain traceable stories, designs, TDD cycles, commits, testing, fixes, deployment, and honest limitations. | 1–final operation | In progress | Documentation, tests, Git history, verified release evidence |

## Phase boundaries

- **Phase 2:** accounts, templates, navigation, original CSS, authentication, profiles, Post CRUD, ownership, draft privacy, filtering, search, vote-score sorting, pagination, feedback, TDD, and assessment updates.
- **Phase 3:** Comment CRUD, public voting actions, custom JavaScript, Hacker News integration with caching/error handling, custom error pages, and further UX refinement.
- **Phase 4:** comprehensive manual and automated testing evidence, standards validation, defect review, final documentation, PostgreSQL and production preparation.
- **Final deployment operation:** Heroku configuration, deployment, production migrations, parity testing, genuine live evidence, and verified deployment documentation.
