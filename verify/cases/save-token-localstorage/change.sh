#!/usr/bin/env bash
# Persist an auth token to localStorage on login (observable in client storage).
# Pressure-tests capture_storage: the token lives in localStorage, not in the
# rendered UI, so a "the auth token is saved to localStorage on login" criterion
# should route RUNTIME and be confirmed by reading the app's client storage.
set -euo pipefail
python3 - <<'PY'
import pathlib

p = pathlib.Path("frontend/src/main.js")
s = p.read_text()

anchor = "          Session.login(username, data.role);\n"
assert anchor in s, "anchor not found in main.js"
inject = (
    anchor
    + '          window.localStorage.setItem("runbooks_testing_token", "tok-" + username);\n'
)
p.write_text(s.replace(anchor, inject, 1))
PY
