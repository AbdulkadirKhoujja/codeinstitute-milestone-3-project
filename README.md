# ByteBoard

ByteBoard is a server-rendered community technology news application built for the Code Institute Backend Development milestone. Visitors can discover published stories by category, text search, date, or aggregate rating. Registered members can submit stories, keep private drafts, and safely manage only their own contributions.

Phase 2 delivers the complete core application. Comment interactions, voting interactions, production configuration, deployment, and final cross-browser validation remain intentionally scheduled for later phases.

## Purpose and audience

Technology reporting is spread across many sources. ByteBoard gives developers, founders, students, investors, and interested readers a focused place to find useful stories and the community context behind each submission.

The core experience supports two goals:

- visitors can locate relevant reporting quickly and understand who submitted it; and
- members can publish, revise, privately draft, or remove their own story records without gaining control of another member's content.

## Implemented features

### Story discovery

- A public feed containing published stories only, newest first by default.
- Dedicated category URLs and a category query-string filter.
- Case-insensitive search across title, summary, and member commentary.
- Newest, highest-rated, oldest, and title sorting with deterministic tie-breakers.
- Aggregate vote scores calculated from existing vote records without exposing Phase 3 voting controls.
- Ten stories per page with active search, category, and sort settings preserved between pages.
- Contextual empty states for an empty platform, category, or search result.
- Reusable story cards showing category, author, date, summary, and score.

### Accounts and profiles

- Registration using Django's password validation and built-in user model.
- Sign-in with safe internal redirects and a generic invalid-credentials response.
- POST-only sign-out with confirmation feedback.
- Navigation that changes appropriately for visitors and signed-in members.
- Public profiles containing a username, join date, and published stories without exposing email addresses.
- An owner-only private-drafts section and story-management links.

### Story management

- Authenticated create, detail, update, and delete journeys.
- A model form restricted to member-editable fields with persistent labels and field-specific help.
- Server-assigned authorship; submitted author values are ignored.
- Draft or published status selection with clear feedback.
- Owner-filtered edit and delete queries returning `404` for another member's records.
- Explicit deletion confirmation and POST-only mutation.
- Published story detail for everyone and private draft preview for its owner only.
- Safe external article links that announce a new tab to assistive technology.

### Interface foundation

- Semantic shared templates with consistent header, navigation, main, and footer landmarks.
- Keyboard skip link, visible focus styles, labelled forms, message announcements, and plain-language states.
- Mobile-first custom CSS for feeds, forms, profiles, story detail, and account journeys.
- Bootstrap components used as a responsive foundation, extended by the project's own visual system.
- Reduced-motion support and flexible layouts without fixed content heights.

## Features reserved for later phases

The relational foundations for comments and votes already exist, but Phase 2 deliberately does not include comment CRUD, public comment display, or voting actions. Phase 3 will implement and test those community interactions. Phase 4 covers production settings, PostgreSQL, deployment, and formal browser, accessibility, and validation evidence.

No live deployment is claimed at this stage.

## Data model

ByteBoard uses Django's built-in user model with four domain models:

- `Category` organises posts and cannot be deleted while a post refers to it.
- `Post` belongs to one author and one category and records draft/published state and timestamps.
- `Comment` belongs to one post and author, retains moderation state, and is deleted with its post.
- `Vote` belongs to one post and user, accepts only `-1` or `1`, and is unique per user/post pair.

These relationships provide ownership and integrity at the database layer. The complete Mermaid ERD, field table, constraints, and deletion rules are documented in [database design](docs/database-design.md).

## Application architecture

The project uses Django's model-template-view structure:

- `byteboard/` contains project settings and root URL routing;
- `accounts/` contains registration, authentication presentation, profiles, and their tests;
- `news/` contains the domain models, model form, story queries, CRUD views, URLs, admin configuration, migrations, and tests;
- `templates/` contains the shared layout, reusable includes, account pages, and story pages; and
- `static/css/style.css` contains the mobile-first ByteBoard visual system.

Views use Django ORM filtering, `Q` queries, aggregation, deterministic ordering, `select_related`, and pagination. Django messages carry success feedback across post/redirect/get journeys.

## Routes

| Route | Purpose | Access |
| --- | --- | --- |
| `/` | Published story feed, search, filtering, sorting, pagination | Public |
| `/categories/<slug>/` | Named category feed | Public |
| `/posts/<id>/` | Published detail or an owner's draft preview | Public/owner |
| `/posts/new/` | Create a story | Signed-in member |
| `/posts/<id>/edit/` | Edit an owned story | Owner only |
| `/posts/<id>/delete/` | Confirm and delete an owned story | Owner only |
| `/accounts/register/` | Create and enter an account | Signed-out visitor |
| `/accounts/login/` | Sign in | Signed-out visitor |
| `/accounts/logout/` | Sign out via POST | Signed-in member |
| `/accounts/profile/<username>/` | Public submissions and owner-only drafts | Public/owner |
| `/admin/` | Manage application records | Authorised staff |

## Technology stack

- Python and Django 5.2.17 for routing, forms, authentication, ORM, migrations, admin, and tests.
- HTML5 and Django templates for server-rendered pages and reusable components.
- Custom CSS and Bootstrap 5.3.8 for the responsive interface.
- SQLite for local development.
- Git and GitHub for incremental version control.

All Python package versions are pinned in `requirements.txt`. PostgreSQL and a production WSGI configuration are later-phase work.

## Local setup

Prerequisites are Python 3 with `venv` and `pip`, Git, and a local repository clone.

1. Clone and enter the repository:

   ```shell
   git clone https://github.com/AbdulkadirKhoujja/codeinstitute-milestone-3-project.git
   cd codeinstitute-milestone-3-project
   ```

2. Create and activate a virtual environment. On Windows PowerShell:

   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

3. Install the pinned dependencies:

   ```shell
   python -m pip install -r requirements.txt
   ```

4. Set a unique local `SECRET_KEY` environment variable. An ignored `env.py` may be used locally:

   ```python
   import os

   os.environ.setdefault("SECRET_KEY", "replace-with-a-unique-local-secret")
   ```

   Never commit the real key, `env.py`, `.env`, credentials, or the local database.

5. Prepare and run the application:

   ```shell
   python manage.py migrate
   python manage.py runserver
   ```

6. Open `http://127.0.0.1:8000/`. Categories are staff-managed records; create the planned categories in Django Admin before testing story submission in a new local database.

## Using ByteBoard

A visitor can search, choose a category, change sorting, move between result pages, open a member profile, read a story, and follow its clearly identified source link. Registration signs the new member in immediately.

A signed-in member can use **Submit story**, choose **Draft** to keep work private or **Published** to add it to public feeds, then manage the record from its detail page or their profile. Sign-out is submitted as a POST form from the navigation. Attempting to view another member's draft or mutate another member's story returns a not-found response rather than disclosing protected data.

## Testing

The automated suite creates isolated test records and does not depend on `db.sqlite3`. It covers models, admin, forms, routes, authentication, safe redirects, profiles, draft privacy, published feeds, detail visibility, story CRUD, ownership, filtering, search, sorting, vote-score aggregation, pagination, feedback, and method restrictions.

Run the quality checks with:

```shell
python manage.py test
python manage.py check
python manage.py makemigrations --check --dry-run
```

The development approach and observed Phase 2 results are recorded in [testing](docs/testing.md). Later formal accessibility, compatibility, and deployment validation must not be inferred from these local checks.

## Accessibility and responsive design

The implemented interface includes semantic landmarks, logical headings, persistent labels, native controls, a skip link, high-visibility keyboard focus, screen-reader message announcements, descriptive links, machine-readable dates, and text-based draft/filter/empty states. Layouts begin as one column and progressively enhance at wider breakpoints; metadata and actions wrap instead of relying on horizontal scrolling.

Phase 2 browser checks provide implementation feedback, while the formal multi-browser, assistive-technology, contrast, zoom, and validator matrix remains Phase 4 work. See [accessibility requirements](docs/accessibility-requirements.md).

## Documentation

- [Project brief](docs/project-brief.md)
- [User stories and acceptance criteria](docs/user-stories.md)
- [Site map and information flow](docs/site-map.md)
- [Page and responsive specifications](docs/page-specification.md)
- [Database design and ERD](docs/database-design.md)
- [Accessibility requirements](docs/accessibility-requirements.md)
- [Testing](docs/testing.md)
- [Assessment criteria tracker](docs/assessment-criteria.md)
- [Development roadmap](docs/development-roadmap.md)
- [Planning wireframes](docs/wireframes/)

The wireframes are low-fidelity planning artefacts, not final screenshots.

## Security

- `SECRET_KEY` is read from the environment rather than stored in tracked source.
- Django CSRF tokens protect every local POST form.
- Standard password validators and authentication views handle credentials.
- Login redirects accept safe internal destinations and reject external destinations.
- Registration and login redirect already-authenticated members.
- Logout and story mutations require POST; unsupported mutation methods return `405`.
- Ownership is enforced in server-side queries and authorship comes from the session.
- Draft queries restrict non-public records to their owner.
- `env.py`, `.env`, `db.sqlite3`, credentials, and generated static output are ignored.

Production `DEBUG`, hosts, database, and static settings are not Phase 2 deployment claims and must be hardened in Phase 4.

## Credits and attribution

- The project is created for Code Institute's Backend Development milestone requirements.
- [Django documentation](https://docs.djangoproject.com/en/5.2/) informs the framework, authentication, forms, ORM, migrations, admin, and testing implementation. Django is distributed under the BSD 3-Clause licence.
- [Bootstrap 5.3 documentation](https://getbootstrap.com/docs/5.3/) informs the responsive component foundation. Bootstrap is loaded from jsDelivr with integrity attributes and is distributed under the MIT licence.
- Django project and application scaffolding supplied the conventional starting file structure.
- No third-party images, icon sets, or fonts are included in Phase 2.

Any later external code, media, data, or learning resource must be credited with its source and licence where required.
