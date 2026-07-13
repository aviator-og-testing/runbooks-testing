#!/usr/bin/env bash
# Append a leftover ?ref=list query parameter to every post-detail link in the
# posts list, so opening a post no longer lands on a clean URL.
# Pressure-tests the pre-pass URL guidance: a URL / query-parameter fact has no
# evidence capture of its own and isn't reliably on the trace (a click doesn't
# record where it landed), so the plan must confirm it by capturing the post
# link's href in the DOM (dom_snapshot), not a screenshot or a bare navigation.
set -euo pipefail
python3 - <<'PY'
import pathlib

p = pathlib.Path("frontend/src/index.html")
s = p.read_text()

anchor = '<a href="#items/<%= item.id %>"><%- item.name %></a>'
assert anchor in s, "post-detail link markup not found in index.html"
p.write_text(
    s.replace(anchor, '<a href="#items/<%= item.id %>?ref=list"><%- item.name %></a>', 1)
)
PY
