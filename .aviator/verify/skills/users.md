# Users

The Users area lists accounts and (for admins) lets you create and delete them.
Each user has a role: `admin` or `user`. Sign in using the credential
placeholders from `default.md`.

## Getting around

- The users list is at `#users`.
- A single user is at `#users/<id>` (click a username).
- The create-user form is at `#users/new` (admins only).
- The signed-in user and their role show in the top header bar.

## Permissions to verify

- As the **admin** (`{{ secrets.admin_username }}` / `{{ secrets.admin_password }}`):
  the **New User** sidebar link is present, each user row has a **Delete**
  button, and `#users/new` is reachable.
- As a **regular user** (`{{ secrets.alice_username }}` / `{{ secrets.alice_password }}`):
  no New User link, no Delete buttons, and navigating to `#users/new` redirects
  back to the users list.

## Deleting a user

Delete is a two-step confirm: the first click on **Delete** arms it (it turns
darker red and reads **Confirm?**), and a second click within ~3 seconds performs
the delete. It reverts to **Delete** if you wait. Deletion is also enforced
server-side, a non-admin's attempt is rejected, not just hidden in the UI.

## Not observable here

Create and delete run for real, but the underlying status codes (e.g. the 403 a
non-admin delete returns) are only visible as the UI's rejection. Judge the exact
response from code.
