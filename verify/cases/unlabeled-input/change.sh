#!/usr/bin/env bash
# Drop the <label for="item-title"> on the new-post Title field and fold the text
# into a placeholder, so the field still reads "Title" on screen but exposes no
# programmatic label (violates the accessible-labels invariant).
# Pressure-tests the for=/label routing: because the change re-renders this
# control's labeling it should route RUNTIME, and the missing association is
# invisible in a screenshot (a placeholder looks identical to a label), so the
# plan must confirm it with a dom_snapshot rather than a screenshot.
set -euo pipefail
python3 - <<'PY'
import pathlib
import re

p = pathlib.Path("frontend/src/index.html")
s = p.read_text()

label = re.compile(r'[ \t]*<label for="item-title">Title</label>\n')
assert label.search(s), "item-title label markup not found in index.html"
s = label.sub("", s, count=1)

old_input = '<input type="text" id="item-title" name="title">'
assert old_input in s, "item-title input markup not found in index.html"
s = s.replace(old_input, '<input type="text" id="item-title" name="title" placeholder="Title">', 1)

p.write_text(s)
PY
