# ByteBoard

ByteBoard is a server-rendered community technology news application built for the Code Institute Backend Development milestone. Visitors can discover published stories by category, text search, date, or aggregate rating. Registered members can submit stories, keep private drafts, and safely manage only their own contributions.

Phase 3 delivers the community interaction and external discovery experience. Comment CRUD, voting, custom JavaScript, the Hacker News discovery feed, controlled failures, and custom error pages are implemented. Production configuration, deployment, and formal cross-browser validation remain intentionally scheduled for Phase 4.

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
- Aggregate vote scores calculated from positive and negative member votes.
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

### Comments and voting

- Approved comments displayed oldest first beneath their parent story.
- Authenticated comment creation with server-assigned ownership and pending-moderation feedback.
- Owner-only comment editing and deletion, including explicit deletion confirmation.
- Edited comments return to moderation; their author can still see the private pending state.
- Upvote and downvote actions limited to published stories and one current vote per member/story.
- Repeating a vote removes it, while choosing the opposite direction updates the existing record.
- Functional server-rendered voting forms progressively enhanced with same-origin `fetch` requests, immediate score/state updates, CSRF protection, disabled loading controls, and live feedback.

### External discovery

- A separate `/discover/` experience for current Hacker News top stories; external records are never stored as ByteBoard posts.
- The official Hacker News Firebase API accessed only by a server-side service and a same-origin JSON endpoint.
- Ranked, validated story metadata with safe HTTP/HTTPS links and Hacker News discussion fallbacks.
- A server-enforced 20–50 story boundary, using 30 by default.
- Completed normalized collections cached under a stable key for exactly 60 seconds.
- Controlled timeouts, invalid-response handling, partial-result feedback, empty states, and retryable failure states.
- Safe DOM rendering with `textContent`, user-controlled refresh, visible loading feedback, and no direct browser request to Hacker News.

### Interface foundation

- Semantic shared templates with consistent header, navigation, main, and footer landmarks.
- Keyboard skip link, visible focus styles, labelled forms, message announcements, and plain-language states.
- Mobile-first custom CSS for feeds, forms, profiles, story detail, and account journeys.
- Bootstrap components used as a responsive foundation, extended by the project's own visual system.
- Reduced-motion support and flexible layouts without fixed content heights.

## Features reserved for later phases

Phase 4 covers production settings, PostgreSQL, deployment, the complete manual browser/accessibility matrix, standards validation, and final release evidence. Phase 3 does not claim any of that future work.

No live deployment is claimed at this stage.

## Data model

ByteBoard uses Django's built-in `User` model as the identity and authentication source. The application reads `username` for authorship and public profiles and `date_joined` for non-sensitive membership context; passwords are handled by Django's hashed credential system. Reverse relationships expose a user's posts, comments, and votes.

### Category

| Field | Type and rule | Purpose |
| --- | --- | --- |
| `id` | Automatic primary key | Stable record identity |
| `name` | `CharField(100)`, unique | Human-readable topic |
| `slug` | `SlugField(120)`, unique | Predictable category URL |
| `description` | `TextField` | Staff-managed topic context |

Categories sort alphabetically. `Post.category` uses `PROTECT`, preventing deletion of a category that still organises a post.

### Post

| Field | Type and rule | Purpose |
| --- | --- | --- |
| `id` | Automatic primary key | Stable route and record identity |
| `title` | `CharField(200)` | Story headline |
| `summary` | `TextField` | Concise feed and detail introduction |
| `article_url` | `URLField(500)` | Original external source |
| `content` | `TextField` | Member explanation of why the story matters |
| `author` | `ForeignKey(User)`, cascade | Owning member; their deletion removes authored posts |
| `category` | `ForeignKey(Category)`, protect | Required organising topic |
| `status` | `CharField(10)`, draft/published, draft default | Public visibility state |
| `created_at` | `DateTimeField`, set on creation | Submission time and default ordering |
| `updated_at` | `DateTimeField`, refreshed on save | Last revision time |

Posts order newest first. Deleting a post cascades to its comments and votes through their foreign keys.

### Comment

| Field | Type and rule | Purpose |
| --- | --- | --- |
| `id` | Automatic primary key | Stable record identity |
| `post` | `ForeignKey(Post)`, cascade | Parent story |
| `author` | `ForeignKey(User)`, cascade | Owning member |
| `body` | `TextField` | Discussion content |
| `is_approved` | `BooleanField`, false default | Moderation state |
| `created_at` | `DateTimeField`, set on creation | Oldest-first discussion ordering |
| `updated_at` | `DateTimeField`, refreshed on save | Last revision time |

### Vote

| Field | Type and rule | Purpose |
| --- | --- | --- |
| `id` | Automatic primary key | Stable record identity |
| `post` | `ForeignKey(Post)`, cascade | Ranked story |
| `user` | `ForeignKey(User)`, cascade | Member casting the vote |
| `value` | `SmallIntegerField`, `-1` or `1` | Downvote/upvote contribution to aggregate score |
| `created_at` | `DateTimeField`, set on creation | Vote creation time |

A check constraint rejects values outside `-1` and `1`. A composite unique constraint on `post` and `user` prevents duplicate votes. Together, these relationships provide ownership and integrity at the database layer. The [database design](docs/database-design.md) contains the corresponding Mermaid ERD and relationship rationale.

## Application architecture

The project uses Django's model-template-view structure:

- `byteboard/` contains project settings and root URL routing;
- `accounts/` contains registration, authentication presentation, profiles, and their tests;
- `news/` contains domain models, forms, story/comment/vote views, the isolated Hacker News service, URLs, error handlers, admin configuration, migrations, and tests;
- `templates/` contains the shared layout, reusable includes, account, community, discovery, and custom error pages;
- `static/css/style.css` contains the mobile-first ByteBoard visual system; and
- `static/js/` contains focused progressive enhancements for voting and external discovery.

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
| `/posts/<id>/comments/new/` | Add a pending comment | Signed-in member |
| `/posts/<id>/comments/<comment-id>/edit/` | Edit an owned comment | Comment owner |
| `/posts/<id>/comments/<comment-id>/delete/` | Confirm and delete an owned comment | Comment owner |
| `/posts/<id>/vote/` | Create, change, or remove a vote | Signed-in member |
| `/discover/` | Separate external Hacker News discovery page | Public |
| `/discover/feed/` | Cached normalized discovery JSON | Public, GET only |
| `/accounts/register/` | Create and enter an account | Signed-out visitor |
| `/accounts/login/` | Sign in | Signed-out visitor |
| `/accounts/logout/` | Sign out via POST | Signed-in member |
| `/accounts/profile/<username>/` | Public submissions and owner-only drafts | Public/owner |
| `/admin/` | Manage application records | Authorised staff |

## Technology stack

- Python and Django 5.2.17 for routing, forms, authentication, ORM, migrations, admin, and tests.
- HTML5 and Django templates for server-rendered pages and reusable components.
- Custom JavaScript for progressive voting and safe external-feed rendering.
- Custom CSS and Bootstrap 5.3.8 for the responsive interface.
- Python's standard-library HTTP and JSON modules for the official Hacker News Firebase API; no API key or additional HTTP dependency is required.
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

A visitor can search, choose a category, change sorting, move between result pages, open a member profile, read approved discussion, follow a clearly identified source link, and use **Discover** to load validated Hacker News stories. Registration signs the new member in immediately.

A signed-in member can submit and manage stories, add/edit/delete their comments, and upvote, downvote, change, or remove a vote. Comment edits return to moderation. Voting works with standard forms and updates immediately when JavaScript is available. Attempts to view private drafts or mutate another member's content return a not-found response rather than disclosing protected data.

## Testing

The 173-test automated suite creates isolated records and does not depend on `db.sqlite3`. It covers the Phase 2 foundation plus comment visibility/CRUD/permissions, all voting transitions and fallbacks, structured asynchronous responses, custom JavaScript organisation, mocked Hacker News requests/normalisation/limits/cache/failures, discovery presentation, and custom error handlers. No automated test contacts the live Hacker News API.

Run the quality checks with:

```shell
python manage.py test
python manage.py check
python manage.py makemigrations --check --dry-run
```

The development approach and observed Phase 3 results are recorded in [testing](docs/testing.md). Later formal accessibility, compatibility, and deployment validation must not be inferred from these local checks.

## Accessibility and responsive design

The implemented interface includes semantic landmarks, logical headings, persistent labels, native controls, a skip link, high-visibility keyboard focus, live status announcements, pressed vote states, busy discovery state, descriptive links, machine-readable dates, and text-based moderation/loading/error/empty states. Layouts begin as one column and progressively enhance at wider breakpoints; metadata and actions wrap instead of relying on horizontal scrolling.

The interactive browser was unavailable during Phase 3, so no new viewport, keyboard, console, or network observation is claimed. The formal multi-browser, assistive-technology, contrast, zoom, and validator matrix remains Phase 4 work. See [accessibility requirements](docs/accessibility-requirements.md).

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
- Comment ownership and moderation visibility are enforced by server-side queries.
- Vote values are allowlisted before writes; published-story and authentication checks are enforced server-side.
- Asynchronous voting remains same-origin and CSRF protected.
- Hacker News request limits are server-controlled, upstream responses are normalized, unsafe URLs fall back safely, exception details are not exposed, and untrusted text is inserted with DOM `textContent`.
- `env.py`, `.env`, `db.sqlite3`, credentials, and generated static output are ignored.

Production `DEBUG`, hosts, database, and static settings are not Phase 3 deployment claims and must be hardened in Phase 4.

## Credits and attribution

- The project is created for Code Institute's Backend Development milestone requirements.
- [Django documentation](https://docs.djangoproject.com/en/5.2/) informs the framework, authentication, forms, ORM, migrations, admin, and testing implementation. Django is distributed under the BSD 3-Clause licence.
- [Bootstrap 5.3 documentation](https://getbootstrap.com/docs/5.3/) informs the responsive component foundation. Bootstrap is loaded from jsDelivr with integrity attributes and is distributed under the MIT licence.
- [Official Hacker News API](https://github.com/HackerNews/API) supplies top-story identifiers and item metadata for the separate discovery feed. The application stores none of those external records and requires no API key.
- Django project and application scaffolding supplied the conventional starting file structure.
- No third-party images, icon sets, or fonts are included in Phase 3.

Any later external code, media, data, or learning resource must be credited with its source and licence where required.
