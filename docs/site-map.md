# Site Map and Information Flow

This document records the implemented Phase 3 application structure while keeping future deployment work outside the site map.

## Site map

```text
ByteBoard
|-- Home / story feed
|   |-- Category-filtered feed
|   |-- Search results
|   `-- Post detail
|       |-- External article
|       |-- Approved/personal pending comments
|       `-- Voting controls
|-- Discover external stories
|   `-- Same-origin cached JSON feed
|-- Account
|   |-- Register
|   |-- Sign in
|   `-- Sign out
|-- Member area
|   |-- Profile
|   |-- My posts
|   |-- Create post
|   `-- Edit/delete own post
|-- Comment actions
|   `-- Edit/delete own comment
`-- Administration
    |-- Categories
    |-- Posts
    |-- Comments
    `-- Votes
```

## Logical information flow

1. A visitor enters through the home feed and sees published stories ordered newest first.
2. The visitor narrows the feed with a category or search, or opens a story directly.
3. Post detail connects the ByteBoard summary and discussion to the original external article.
4. Registration and sign-in turn a visitor into an authenticated member.
5. A member can create a story, then reach permitted edit or delete actions from the post or profile area.
6. A member comments and votes from post detail; owner-filtered queries govern comment edits and deletion while vote transitions preserve one record per member/story.
7. A visitor opens Discover, whose JavaScript requests ByteBoard's same-origin endpoint; the server then supplies a bounded, validated, cached Hacker News collection.
8. Staff use Django Admin to organise categories and moderate posts, comments, and votes.

## Navigation planning

- Global navigation exposes the home feed, external discovery, and authentication state; category/search controls remain within the community feed.
- Member-only actions should be visible when useful, but the server must always enforce authorisation.
- Breadcrumbs are most useful on category, post detail, form, and administration contexts.
- The current page or selected category should be communicated in text and semantics, not colour alone.
- Mobile navigation should preserve access to primary tasks without hiding essential controls behind hover behaviour.

## Access rules

| Destination or action | Visitor | Member | Staff |
| --- | --- | --- | --- |
| Browse published posts | Yes | Yes | Yes |
| Read approved comments | Yes | Yes | Yes |
| Register or sign in | Yes | When signed out | When signed out |
| Create posts | No | Yes | Yes |
| Edit/delete a post | No | Own only | Moderation policy |
| Add comments or votes | No | Yes | Yes |
| Edit/delete a comment | No | Own only | Moderation policy |
| Browse external discovery | Yes | Yes | Yes |
| Django Admin | No | No | Authorised staff only |

## Error and empty-state paths

- Empty feeds should suggest changing filters or returning to all stories.
- Invalid forms should preserve safe user input and associate messages with affected fields.
- Unauthorised ownership actions should return an appropriate response without exposing private data.
- Missing posts, categories, or comments use the custom navigable not-found experience.
- Bad requests, denied access, missing pages, and server errors use status-correct plain-language pages with a home route.
- Hacker News failures return controlled JSON and visible retry guidance without affecting community stories.
- External-link failures remain outside ByteBoard's control, so sources and Hacker News discussion fallbacks are clearly identified.
