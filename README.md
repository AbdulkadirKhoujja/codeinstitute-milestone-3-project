# ByteBoard

ByteBoard is a Code Institute Backend Development Milestone Project: a community-driven technology and startup news platform where users will be able to submit stories, discover developments, discuss posts, and rank stories through votes.

Phase 1 establishes the planning and relational data foundation. The public application, authentication journeys, community interfaces, styling, and production deployment are intentionally planned for later phases and are not represented as complete.

## Project goals

External users need a focused place to browse technology and startup news, locate relevant stories, identify authors and dates, and—after authentication—submit, discuss, and rank contributions.

The site owner needs to encourage relevant discussion, organise stories by topic, moderate contributions, preserve content ownership, and protect relational data integrity.

The intended audience includes technology professionals, founders, developers, students, investors, enthusiasts, and readers interested in community-curated technology news.

## Current development status

Phase 1 — Planning and Data Foundation includes:

- project goals, user stories, acceptance criteria, page requirements, and responsive planning;
- sitemap and logical information flow;
- six clearly labelled SVG planning wireframes;
- accessibility requirements and testing intentions;
- relational database design and Mermaid ERD;
- migrated `Category`, `Post`, `Comment`, and `Vote` Django models;
- database-enforced vote value and one-vote-per-user/post constraints;
- protected category deletion and cascading dependent comment/vote deletion;
- useful Django Admin registrations for all four domain models; and
- isolated model and admin tests.

Not yet implemented: public views or templates, authentication pages, post CRUD interfaces, comments UI, voting UI, search, site styling, PostgreSQL production configuration, or deployment. See the [development roadmap](docs/development-roadmap.md) for the agreed sequence.

## Planned core features

- Browse published stories newest first.
- Navigate the initial Artificial Intelligence, Startups, Software Development, Cybersecurity, Gadgets, and Fintech categories.
- Search for stories.
- Register, sign in, and sign out.
- Submit, edit, and delete owned stories.
- Read and manage owned comments.
- Upvote or downvote once per user and post.
- Review authors, dates, categories, scores, and discussion.
- Moderate categories, posts, comments, and votes.

These are planned product requirements; only the Phase 1 foundation described above currently exists.

## Data model summary

ByteBoard uses Django's built-in user model:

- one user can author many posts and comments and cast many votes;
- one category organises many posts, and categories in use are protected from deletion;
- one post can receive many comments and votes;
- deleting a post cascades to its comments and votes;
- votes accept only `-1` or `1`; and
- a user can have only one vote per post.

The complete field design, deletion rules, constraints, and ERD are in [database design](docs/database-design.md).

## Technology stack

The planned full-stack product uses HTML, CSS, JavaScript, Python, Django, and a relational database.

Current Python dependencies are recorded exactly in `requirements.txt`:

- Django 5.2.17 — web framework, ORM, migrations, authentication model, admin, and test framework;
- asgiref — Django's ASGI support dependency;
- sqlparse — SQL parsing used by Django;
- tzdata — time-zone data on platforms that require it;
- gunicorn — production WSGI server planned for deployment; and
- packaging — version and packaging utilities.

SQLite is used for local development. PostgreSQL is planned for production but is not configured in Phase 1.

## Documentation index

- [Project brief](docs/project-brief.md)
- [User stories and acceptance criteria](docs/user-stories.md)
- [Site map and information flow](docs/site-map.md)
- [Page and responsive specifications](docs/page-specification.md)
- [Database design and ERD](docs/database-design.md)
- [Accessibility requirements](docs/accessibility-requirements.md)
- [Development roadmap](docs/development-roadmap.md)
- Wireframes:
  - [Home — desktop](docs/wireframes/home-desktop.svg)
  - [Home — mobile](docs/wireframes/home-mobile.svg)
  - [Post detail — desktop](docs/wireframes/post-detail-desktop.svg)
  - [Post detail — mobile](docs/wireframes/post-detail-mobile.svg)
  - [Post form](docs/wireframes/post-form.svg)
  - [Profile](docs/wireframes/profile.svg)

The SVG files are low-fidelity planning artefacts, not final screenshots or completed interface designs.

## Local setup

Prerequisites:

- Python 3 with `venv` and `pip`;
- Git; and
- a local clone of this repository.

1. Clone the repository and enter its directory:

   ```shell
   git clone https://github.com/AbdulkadirKhoujja/codeinstitute-milestone-3-project.git
   cd codeinstitute-milestone-3-project
   ```

2. Create and activate a virtual environment. For example, on Windows PowerShell:

   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

3. Install the pinned dependencies:

   ```shell
   python -m pip install -r requirements.txt
   ```

4. Provide a local Django secret key. The project reads `SECRET_KEY` from the environment. One local option is an ignored `env.py` file in the repository root:

   ```python
   import os

   os.environ.setdefault("SECRET_KEY", "replace-with-a-unique-local-secret")
   ```

   `env.py`, `.env`, local database files, credentials, and production secrets must never be committed. Confirm ignore behaviour before staging changes.

5. Apply migrations and check the project:

   ```shell
   python manage.py migrate
   python manage.py check
   python manage.py test
   ```

6. Optionally create a local superuser to inspect the configured Django Admin, then start the development server:

   ```shell
   python manage.py createsuperuser
   python manage.py runserver
   ```

At this phase, the only configured route is Django Admin at `/admin/`; no public ByteBoard pages have been built.

## Testing intentions

Phase 1 tests exercise model display strings, default ordering, relationship requirements, category uniqueness, post status choices, category deletion protection, comment and vote cascades, vote constraints, and admin registration/configuration. Tests use Django's isolated test database and do not depend on manually created SQLite records.

Later phases will add view, URL, form, template, authentication, authorisation, community-feature, responsive, accessibility, browser, and deployment tests. Results and defects will be documented only after the corresponding checks are actually run.

## Accessibility and responsive planning

The project plans semantic landmarks and headings, keyboard-operable controls, visible focus, persistent form labels, connected validation feedback, text alternatives, sufficient contrast, zoom support, and mobile-first reflow. See [accessibility requirements](docs/accessibility-requirements.md) for acceptance and test intentions. No conformance claim is made before the implemented interface is evaluated.

## Deployment intentions

Phase 4 plans PostgreSQL, environment-provided production secrets, deployment-safe Django settings, static asset handling, migrations, and verification on a selected hosting provider. A live-site URL and deployment instructions will be added only after a deployment exists and has been tested.

## Future improvements

Potential post-milestone ideas include personalised feeds, follows or bookmarks, notifications, social login, reputation features, email digests, media uploads, public APIs, and native mobile clients. These ideas are outside the agreed four-phase milestone scope unless explicitly reprioritised.

## Credits and attribution

- The project was created for Code Institute's Backend Development milestone requirements.
- Django-generated project/application scaffolding was used as the starting structure.
- Django's official documentation informs framework, model, migration, admin, and testing usage.
- Phase 1 planning, model implementation, tests, and documentation were reviewed through repository diffs, Django checks, migrations, and automated tests.

Any later external code, design assets, images, icons, fonts, data, or learning resources must be credited with their source and licence where required. No third-party visual assets are included in the current wireframes.

## Repository security

- `SECRET_KEY` is loaded from the environment rather than hard-coded in tracked settings.
- `env.py`, `.env`, `db.sqlite3`, and other local environment/database files are ignored.
- Contributors should review staged file names and diffs before every commit.
- Production credentials must be stored in the hosting provider's environment configuration, never in Git.
