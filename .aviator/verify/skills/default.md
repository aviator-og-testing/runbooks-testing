# Aviator verify guidance

This is a small demo web app for exercising Aviator's verify pipeline: a
Backbone.js single-page frontend backed by a FastAPI service. The preview serves
the website behind a login, a Users area and a simple blog ("Posts"). This file
covers the test accounts, how to sign in, the lay of the land, and what the
preview can and can't show. Then read the one area file below that matches the
change under test.

## Test accounts (credentials)

The app seeds fixed demo accounts on startup, and their credentials are provided
to verify as account secrets. Reference them with `{{ secrets.<name> }}`
placeholders in fill values (standalone or embedded). Aviator substitutes the
real value at fill time, so never type a literal username or password.

| Account | Role  | Username placeholder           | Password placeholder           |
| ------- | ----- | ------------------------------ | ------------------------------ |
| admin   | admin | `{{ secrets.admin_username }}` | `{{ secrets.admin_password }}` |
| alice   | user  | `{{ secrets.alice_username }}` | `{{ secrets.alice_password }}` |
| bob     | user  | `{{ secrets.bob_username }}`   | `{{ secrets.bob_password }}`   |
| carol   | user  | `{{ secrets.carol_username }}` | `{{ secrets.carol_password }}` |

The **admin** account can create and delete users and edit any post. The **user**
accounts (alice, bob, carol) are read-only on users and can publish posts and
edit only their own. Three regular users exist so you can test cross-user
behavior, e.g. publish a post as `{{ secrets.bob_username }}`, then confirm
`{{ secrets.alice_username }}` cannot edit it.

There is also one extra regular user with a randomly generated name each boot; it
has no secret, so don't rely on it.

## Signing in

1. Navigate to the preview URL, you land on the login screen.
2. Fill **Username** with the chosen account's username placeholder and
   **Password** with its password placeholder. For example, to sign in as a
   regular user, fill Username with `{{ secrets.alice_username }}` and Password
   with `{{ secrets.alice_password }}`; for the admin, use
   `{{ secrets.admin_username }}` / `{{ secrets.admin_password }}`.
3. Click **Log in**. A valid account lands on the Dashboard; a wrong password
   shows an inline error and stays on the login screen.

## Which area file to read

After login the left sidebar switches between areas. Read **only** the file for
the area the change touches:

- `users.md` — the Users area: listing, user detail, roles/permissions, and
  creating/deleting users (admin only).
- `posts.md` — Posts: the blog list, creating posts, the single-post page, and
  editing a post (author or admin only).

## What the preview can and can't show

The app is self-contained (the FastAPI backend persists to a local SQLite
database), so most of it is exercisable in the browser: logging in, the role
gates, creating and deleting users, and creating, viewing, and editing posts all
run for real. Rendered UI, DOM, computed styles, console output, and the data the
UI loads are all fair game for evidence.

What the preview **cannot** verify, judge these from the code instead:

- **The Go service.** It is not started in the preview and the website never
  calls it (the frontend proxies only to the Python API), so nothing it serves is
  reachable here.
- **Raw API contracts.** The collector drives the browser UI, so HTTP status
  codes, JSON response shapes, and endpoints with no UI surface (the health and
  greeting endpoints) are only observable as far as the UI reflects them.
- **Persistence and the random user.** The database is recreated and reseeded on
  every preview boot. The four fixed accounts and the demo posts are always
  present, but data does not survive a reboot and one regular user's name is
  random each time, don't depend on either.
- **The frontend's CDN dependency.** jQuery, Backbone, Underscore, and moment load
  from a CDN at runtime, so the preview browser needs outbound internet for the
  page to render. A blank page usually means no egress, not a regression in the
  change under test.
- **External side effects.** The app sends no email, fires no webhooks, and calls
  no third-party services, so there is nothing of that kind to verify.
