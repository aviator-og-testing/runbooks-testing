# Posts

Posts is a simple blog. Any signed-in user can publish a post; each post records
its author and creation time. Sign in using the credential placeholders from
`default.md`.

## Getting around

- The posts list is at `#items`, newest first, each showing title, author, and
  relative time.
- A single post page is at `#items/<id>` (click a post title).
- The edit-post page is at `#items/<id>/edit`.
- The new-post form is inline at the top of the posts list (`#items`).

## Creating and editing

- **Create:** any signed-in user fills the title + content form on `#items` and
  submits; the new post appears at the top with their username as author.
- **Edit:** allowed for the post's author or an admin. To verify the gate, use
  two different regular users, publish as `{{ secrets.bob_username }}`, then
  confirm `{{ secrets.alice_username }}` has no Edit affordance and cannot edit
  that post. The admin (`{{ secrets.admin_username }}` /
  `{{ secrets.admin_password }}`) can edit any post.

## Not observable here

Author and timestamp are rendered, but they originate from the server. The edit
authorization is enforced server-side, only its UI effect (no Edit button, or a
rejected save) is visible in the preview; judge the rejection itself from code.
