# Users

The Users area lists accounts and (for admins) lets you create and delete them.
Each user has a role: `admin` or `user`.

## Getting around

- The users list is at `#users`.
- A single user is at `#users/<id>` (click a username).
- The create-user form is at `#users/new` (admins only).
- The signed-in user and their role show in the top header bar.

## Permissions to verify

- **Admin** (`admin` / `admin`): sees the **New User** sidebar link, a
  **Delete** button on each user row, and can open `#users/new`.
- **Regular user** (`alice` / `password`): no New User link, no Delete buttons,
  and navigating to `#users/new` redirects back to the users list.

## Deleting a user

Delete is a two-step confirm: the first click on **Delete** arms the button (it
turns darker red and reads **Confirm?**), and a second click within ~3 seconds
performs the delete. If you wait, it reverts to **Delete**. Deletion is also
enforced on the backend — `DELETE /api/users/<id>` requires the admin role and
returns 403 otherwise.

## What's observable here

All of this works for real against SQLite: creating a user adds it to the list,
deleting removes it, and the role gates render exactly as above. Verify both the
admin and regular-user views by signing in as each.
