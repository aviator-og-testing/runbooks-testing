# Posts

Posts is a simple blog. Any signed-in user can publish a post; each post records
its author and creation time.

## Getting around

- The posts list is at `#items`, newest first, each showing title, author, and
  relative time.
- A single post page is at `#items/<id>` (click a post title).
- The edit-post page is at `#items/<id>/edit`.
- The new-post form is inline at the top of the posts list (`#items`).

## Creating and editing

- **Create:** any signed-in user fills the title + content form on `#items` and
  submits; the new post appears at the top with their username as author.
- **Edit:** reachable from the single-post page (an **Edit** button) and from an
  **Edit** link on posts you may change in the list. Editing is allowed for the
  post's author or an admin; others are blocked in the UI and by the backend
  (`PUT /api/items/<id>` returns 403 for a non-author, non-admin).

## What's observable here

The blog is fully functional against SQLite: create a post and watch it appear,
open its page, edit it as the author (or as admin), and confirm a non-author
cannot edit someone else's post. Sign in as different seeded users to exercise
the permission cases.
