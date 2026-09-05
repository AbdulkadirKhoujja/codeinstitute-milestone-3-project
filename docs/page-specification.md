# Page Specification

This document describes the implemented Phase 3 pages and community interactions. Production/deployment presentation and formal browser validation remain Phase 4.

## Home and story feed

Purpose: help visitors discover published stories quickly.

Implemented content and behaviour:

- site identity, primary navigation, account state, and search entry point;
- category navigation for the six initial topics;
- repeatable story summaries with title, summary, category, author, date, and aggregate score;
- newest-first default ordering with a clear empty state;
- pagination when the result set grows; and
- a prominent story-submission action for authenticated members.

Responsive intent: use a single-column feed on small screens; introduce a supporting category or information region only when width permits. Story metadata must wrap without overlap.

## Search and category results

Purpose: narrow the story feed while retaining context.

Implemented content and behaviour:

- a heading that states the active category or search term;
- the same accessible story-summary pattern as the home feed;
- result count or clear no-result feedback where useful; and
- controls to clear the active filter or return to all stories.

## Post detail

Purpose: present one submission, connect to its source, and host community activity.

Implemented content and behaviour:

- title, summary, longer commentary, category, author, created/updated dates, and external article URL;
- owner-only edit and delete actions;
- clear sign-in guidance where an anonymous visitor reaches a restricted action;
- approved comments oldest first, author-visible pending states, and an authenticated comment form;
- owner-only comment edit/delete actions with edited-state and remoderation feedback;
- an aggregate score with accessible upvote/downvote pressed state; and
- standard-form vote fallback plus immediate same-origin JavaScript updates.

Responsive intent: keep the primary reading column at a comfortable line length. Metadata and actions may wrap or stack, but source, ownership, and destructive-action labels remain explicit.

## Post create and edit form

Purpose: let authenticated members submit or revise owned stories.

Implemented content and behaviour:

- labelled inputs for title, summary, article URL, content, category, and status;
- required-field indicators explained in text;
- field-level validation messages linked to their inputs;
- safe retention of valid submitted values after a validation error;
- submit and cancel actions; and
- distinct create/edit headings and button labels.

Responsive intent: one column by default, with controls sized for touch and no dependence on placeholder text as a label.

## Delete confirmation

Purpose: prevent accidental removal of owned content.

Implemented content and behaviour for post and comment deletion:

- identify the post being deleted;
- explain that related deletion may be irreversible;
- make confirm and cancel actions unambiguous; and
- keep the non-destructive action easy to reach by keyboard.

## Comment edit form

Purpose: let a comment owner correct their discussion contribution without changing ownership or its parent story.

Implemented content and behaviour:

- a persistent body label and character guidance;
- safe retention and linked feedback after invalid input;
- server-filtered ownership and post/comment pairing;
- a clear warning that edits return to moderation; and
- submit/cancel actions returning to the parent discussion.

## External discovery

Purpose: let visitors explore current Hacker News stories without presenting them as ByteBoard database content.

Implemented content and behaviour:

- a separate `/discover/` heading, explanation, attribution, and cached-refresh guidance;
- a same-origin endpoint URL embedded as data rather than a direct browser call to Hacker News;
- a visible initial loading state, `aria-busy`, live result text, and temporarily disabled refresh;
- safely created external cards containing title, source, author, date, score, comment count, and Hacker News discussion link;
- partial, empty, unavailable, and user-controlled retry/refresh states; and
- one-column cards by default with a two-column enhancement at wider widths.

## Profile and member posts

Purpose: help a member understand their account activity and manage submissions.

Implemented content and behaviour:

- username and non-sensitive account information;
- owned posts, including visible draft/published status;
- direct links to create, view, edit, or request deletion of a post; and
- empty-state guidance for a member with no posts.

Responsive intent: transform multi-column metadata into labelled stacked values at narrow widths rather than relying on horizontal scrolling.

## Authentication pages

Purpose: support registration, sign-in, and sign-out through a consistent account journey.

Implemented content and behaviour:

- concise headings and explanations;
- autocomplete-compatible, properly labelled fields;
- safe validation and authentication feedback;
- links between registration and sign-in; and
- a POST sign-out control with success feedback.

## Administration

Purpose: let authorised staff organise and moderate relational content.

Phase 1 provides Django Admin model registrations with useful columns, search, filters, date navigation, and slug prepopulation. Public-facing moderation screens remain later work.

## Shared states and content rules

- Every page needs a unique, descriptive title and one clear main heading.
- Navigation and messages should use consistent language for posts, comments, votes, categories, and account state.
- Loading is server-rendered initially for external discovery, then managed by focused JavaScript; active vote/feed controls are temporarily disabled to prevent duplicate requests.
- Success, error, permission-denied, empty, and not-found states require plain-language messages.
- Dates should be presented consistently and remain machine-readable where practical.
- External links should be identifiable and must not imply ByteBoard authored the linked story.
