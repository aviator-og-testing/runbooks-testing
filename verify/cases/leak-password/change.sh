#!/usr/bin/env bash
# Leak the password in the users API response (violates "no secrets in API
# responses").
set -euo pipefail
python3 - <<'PY'
import pathlib
main = next(pathlib.Path("backend_python/src").glob("*_api")) / "main.py"
s = main.read_text()
s = s.replace(
    "    email: str\n    role: str\n",
    "    email: str\n    role: str\n    password: str | None = None\n",
    1,
)
s = s.replace(
    "email=u.email, role=u.role)",
    "email=u.email, role=u.role, password=u.password)",
    1,
)
main.write_text(s)
PY
