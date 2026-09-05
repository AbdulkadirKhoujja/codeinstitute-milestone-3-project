# User Stories and Acceptance Criteria

The stories below define the intended product. A delivery phase is recorded so that planned behaviour is not mistaken for functionality already implemented.

## Visitors and members

### Browse published stories

**As a visitor, I want to browse published technology stories so that I can discover relevant developments.**

Acceptance criteria:

- Only published posts appear in the public story list.
- Each result identifies its title, category, author, and publication date.
- Results use newest-first ordering by default.
- The list remains usable at mobile and desktop widths.

Delivery: Phase 2 (implemented).

### Filter and search

**As a visitor, I want to filter by category and search for stories so that I can locate relevant content efficiently.**

Acceptance criteria:

- The six initial categories are available as navigation or filter options.
- Search matches clearly documented post fields.
- Users can order results by newest or aggregate rating.
- Longer result sets are paginated without dropping active controls.
- Empty and no-result states explain what happened.
- Filters and search terms can be cleared without reloading unrelated state.

Delivery: Phase 2 (implemented).

### Read a story and discussion

**As a visitor, I want to open a post and read its discussion so that I can understand the story and community response.**

Acceptance criteria:

- The detail page shows the post content, article link, author, category, and dates.
- Approved comments are shown oldest first.
- The external article link is distinguishable from internal navigation.
- Missing or unavailable posts return an appropriate not-found response.

Delivery: Phase 2 for post details and Phase 3 for approved discussion (implemented).

### Register and sign in

**As a visitor, I want to create an account and sign in so that I can contribute to ByteBoard.**

Acceptance criteria:

- Registration reports invalid or duplicate account details clearly.
- Sign-in errors do not reveal sensitive account information.
- Signing out ends the authenticated session.
- Restricted actions redirect or guide unauthenticated visitors to sign in.

Delivery: Phase 2 (implemented).

### Submit and manage stories

**As a member, I want to submit and manage my own stories so that I can share relevant news and correct or remove my contributions.**

Acceptance criteria:

- A valid submission requires all model-required fields and an existing category.
- A member can edit or delete only posts they own.
- The interface distinguishes drafts from published posts.
- Destructive actions require explicit confirmation.

Delivery: Phase 2 (implemented).

### Comment and manage comments

**As a member, I want to comment and manage my own comments so that I can participate in discussion responsibly.**

Acceptance criteria:

- A comment belongs to one existing post and one authenticated user.
- A member can edit or delete only comments they own.
- Approval state determines whether a comment is publicly visible.
- Deleting a post also removes its comments.

Delivery: Phase 3 (implemented and covered by ownership/moderation tests).

### Vote on stories

**As a member, I want to upvote or downvote a story so that I can influence its community ranking.**

Acceptance criteria:

- A vote value is either `1` or `-1`.
- A user has at most one vote on a post.
- Repeating or changing a vote cannot create duplicate vote records.
- The displayed score reflects the stored votes.

Delivery: Phase 3 (implemented with standard-form and progressively enhanced journeys).

### Discover external stories

**As a visitor, I want to refresh a clearly separated external story feed so that I can discover current technology reporting without confusing it with ByteBoard posts.**

Acceptance criteria:

- The browser requests ByteBoard's same-origin endpoint rather than Hacker News directly.
- Between 20 and 50 ranked stories are requested per refresh cycle, with 30 as the default.
- Completed normalized results are cached for 60 seconds so repeated refreshes cannot create uncontrolled upstream traffic.
- Loading, partial, empty, failure, and refresh states use visible and announced text.
- External titles and URLs are validated and rendered without unsafe HTML insertion.

Delivery: Phase 3 (implemented with mocked upstream tests; manual browser verification remains Phase 4).

## Site owner and moderators

### Organise categories

**As the site owner, I want to manage categories so that stories remain organised by topic.**

Acceptance criteria:

- Category names and slugs are unique.
- Categories appear alphabetically.
- A category associated with existing posts cannot be deleted silently.
- Category records can be searched and maintained in Django Admin.

Delivery: Phase 1 data and admin foundation; interfaces may be refined later.

### Moderate contributions

**As the site owner, I want to moderate posts and comments so that the community remains relevant and safe.**

Acceptance criteria:

- Administrators can find posts by useful identifying fields and filter by status or category.
- Administrators can find comments and filter by approval state.
- Post and comment ownership remains visible during moderation.
- Moderation does not bypass database relationship constraints.

Delivery: Phase 1 admin foundation and Phase 3 pending/edit-remoderation workflow (implemented).

### Protect data integrity

**As the site owner, I want relationship and vote rules enforced by the database so that invalid data cannot be introduced through another interface.**

Acceptance criteria:

- Posts reference an existing user and category.
- Category deletion is protected while posts use it.
- Post deletion cascades to related comments and votes.
- Database constraints reject invalid vote values and duplicate user/post votes.

Delivery: Phase 1.

## Quality stories

### Accessible and responsive experience

**As a user, I want an accessible, responsive interface so that I can use ByteBoard across devices and assistive technologies.**

Acceptance criteria:

- Pages use semantic landmarks, logical headings, keyboard-operable controls, and visible focus states.
- Informative images have meaningful text alternatives; decorative images use empty alternatives.
- Status and validation feedback is not communicated by colour alone.
- Layouts avoid horizontal scrolling at common mobile widths and reflow at larger widths.

Delivery: implemented throughout Phases 2 and 3; formal browser and assistive-technology verification remains Phase 4.
