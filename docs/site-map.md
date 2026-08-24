# Site Map and Information Flow

This planning document describes the intended application structure. Routes and pages beyond Django Admin have not yet been implemented.

## Planned site map

```text
ByteBoard
|-- Home / story feed
|   |-- Category-filtered feed
|   |-- Search results
|   `-- Post detail
|       |-- External article
|       |-- Comments
|       `-- Voting controls
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
6. A member can comment and vote from post detail; ownership rules govern later edits and deletion.
7. Staff use Django Admin to organise categories and moderate posts, comments, and votes.

## Navigation planning

- Global navigation should expose the home feed, categories, search, and authentication state.
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
| Django Admin | No | No | Authorised staff only |

## Error and empty-state paths

- Empty feeds should suggest changing filters or returning to all stories.
- Invalid forms should preserve safe user input and associate messages with affected fields.
- Unauthorised ownership actions should return an appropriate response without exposing private data.
- Missing posts, categories, or comments should use a consistent not-found experience.
- External-link failures remain outside ByteBoard's control, so the original URL should be clearly identified.
