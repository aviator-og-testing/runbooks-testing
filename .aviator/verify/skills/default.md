# Aviator verify guidance

runbooks_testing is a small demo web app: a Backbone.js single-page frontend
backed by a FastAPI service (with a separate Go service that the website does
not use). The preview serves the website at the preview URL — a login screen, a
Users area, and a simple blog ("Posts") — all behind a login. This file covers
signing in and the lay of the land; then read the one area file below that
matches the change under test.

## Signing in

The app seeds demo accounts on startup, so sign in with a username + password
(there is no external identity provider):

- Admin: `admin` / `admin` — can create and delete users, and edit any post.
- Regular user: `alice` / `password` (also `bob`, `carol`) — read-only on
  users; can create posts and edit their own.

1. Navigate to the preview URL — you land on the login screen.
2. Fill **Username** and **Password** with one of the accounts above.
3. Click **Log in**. You land on the Dashboard.

A wrong password shows an inline error and keeps you on the login screen.

## Which area file to read

After login the left sidebar switches between areas. Read **only** the file for
the area your change touches — pulling in the other just dilutes the context:

- `users.md` — the Users area: listing, user detail, roles/permissions, and
  creating/deleting users (admin only).
- `posts.md` — Posts: the blog list, creating posts, the single-post page, and
  editing a post.

## What's observable here

Unlike a webhook-driven app, this demo is fully self-contained: the FastAPI
backend persists to a local SQLite database, so the whole flow works in the
preview — logging in, listing/creating/deleting users, and creating, viewing,
and editing posts all execute for real. Rendered UI, DOM, computed styles,
console output, and the data the UI loads are all fair game for evidence.

The frontend talks to the backend under `/api` (proxied to FastAPI). The Go
service is a separate standalone API and is not exercised by the website.
