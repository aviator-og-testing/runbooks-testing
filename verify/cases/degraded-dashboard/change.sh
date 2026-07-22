#!/usr/bin/env bash
# A composite case that mixes real improvements with regressions, so verify
# must pass the healthy paths and fail the broken ones with named causes —
# not blame the environment, and not let ambient noise flip a passing page.
#
# Should PASS:
#   1. Home heading reads "Team dashboard".
#   2. Posts page: create form gains placeholders and a "Publish post" button.
#      Listing and creating posts still works.
# Should FAIL, each with a browser-observable cause:
#   3. The users page throws an uncaught TypeError while rendering.
#   4. GET /api/items/{id} returns 500, breaking the post-detail page while
#      the posts list stays healthy.
# Ambient noise on every page load (should not flip the passing criteria):
#   5. index.html references widgets.js, which does not exist — a same-origin
#      404 + failed script request at boot.
set -euo pipefail

python3 - <<'PY'
import pathlib


def replace_once(path: pathlib.Path, old: str, new: str) -> None:
    s = path.read_text()
    assert old in s, f"anchor not found in {path}: {old!r}"
    path.write_text(s.replace(old, new, 1))


index = pathlib.Path("frontend/src/index.html")

# Improvement: home heading.
replace_once(index, "<h1>Dashboard</h1>", "<h1>Team dashboard</h1>")

# Improvement: create-post form placeholders + button label.
replace_once(
    index,
    '<input type="text" id="item-title" name="title">',
    '<input type="text" id="item-title" name="title" '
    'placeholder="Give your post a title">',
)
replace_once(
    index,
    '<textarea id="item-body" name="body"></textarea>',
    '<textarea id="item-body" name="body" '
    'placeholder="Write something worth reading"></textarea>',
)
replace_once(index, ">Add post</button>", ">Publish post</button>")

# Ambient noise: a script reference that 404s on every page load.
replace_once(
    index,
    '<script src="main.js"></script>',
    '<script src="widgets.js"></script>\n    <script src="main.js"></script>',
)

# Regression: users page throws an uncaught TypeError during render.
replace_once(
    pathlib.Path("frontend/src/main.js"),
    "      var users = this.collection.map(function (user) {",
    "      var stats = window.userStats.totals;\n"
    "      var users = this.collection.map(function (user) {",
)

# Regression: post-detail endpoint 500s; the posts list stays healthy.
replace_once(
    next(pathlib.Path("backend_python/src").glob("*_api")) / "main.py",
    '    """Get a single item."""\n',
    '    """Get a single item."""\n'
    '    raise RuntimeError("post detail lookup exploded")\n',
)
PY
