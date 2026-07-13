#!/usr/bin/env bash
# Send an X-CSRF-Token header on every API request (observable only on the wire).
# Pressure-tests capture_network: the header is a property of the request the
# app itself sends, invisible to screenshots/DOM and to http_request (which
# issues its own request), so a "requests send X-CSRF-Token" criterion should
# route RUNTIME and be confirmed by capturing the app's outgoing request.
set -euo pipefail
python3 - <<'PY'
import pathlib

p = pathlib.Path("frontend/src/main.js")
s = p.read_text()

anchor = '  var API_BASE = "/api";\n'
assert anchor in s, "anchor not found in main.js"
inject = (
    anchor
    + "\n"
    + "  // Send a CSRF token header on every API request.\n"
    + '  $.ajaxSetup({ headers: { "X-CSRF-Token": "static-demo-token" } });\n'
)
p.write_text(s.replace(anchor, inject, 1))
PY
