# Page Specification

This document describes the implemented Phase 2 pages and identifies community elements that remain reserved for Phase 3.

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

Implemented in Phase 2:

- title, summary, longer commentary, category, author, created/updated dates, and external article URL;
- owner-only edit and delete actions;
- clear sign-in guidance where an anonymous visitor reaches a restricted action.

Reserved for Phase 3: approved comments, comment creation and owner actions, and authenticated voting controls with user vote state.

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

Implemented content and behaviour for post deletion:

- identify the post being deleted;
- explain that related deletion may be irreversible;
- make confirm and cancel actions unambiguous; and
- keep the non-destructive action easy to reach by keyboard.

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
- Loading is server-rendered initially; slow or repeated submissions must not encourage duplicate data.
- Success, error, permission-denied, empty, and not-found states require plain-language messages.
- Dates should be presented consistently and remain machine-readable where practical.
- External links should be identifiable and must not imply ByteBoard authored the linked story.
