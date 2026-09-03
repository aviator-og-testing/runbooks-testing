#!/usr/bin/env bash
# A composite case: two genuine improvements plus three defects introduced the
# way real PRs introduce them. Nothing in the diff declares the defects as
# intended, so catching them falls to the runtime baseline invariants, not to
# diff-derived criteria.
#
# Improvements (should pass): home heading copy; create-post form placeholders
# and a "Publish post" button.
# Defects (should fail): the users page reads a profile field the API does not
# return (uncaught TypeError on render); post detail stamps a freshness date
# from a model field that does not exist (HTTP 500); index.html references a
# widgets.js that was never added (404 on every page load).
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

# Defect: a script reference whose file was never added; 404s on every load.
replace_once(
    index,
    '<script src="main.js"></script>',
    '<script src="widgets.js"></script>\n    <script src="main.js"></script>',
)

# Defect: "prefer display names" on the users page — but the API returns no
# profile object, so render throws an uncaught TypeError.
replace_once(
    pathlib.Path("frontend/src/main.js"),
    '          id: user.get("id"),\n'
    '          username: user.get("username"),',
    '          id: user.get("id"),\n'
    '          username: user.get("profile").display_name || '
    'user.get("username"),',
)

# Defect: "show freshness" on post detail — but Item has no updated_at, so
# the endpoint 500s while the posts list stays healthy.
replace_once(
    next(pathlib.Path("backend_python/src").glob("*_api")) / "main.py",
    "    item: Any = Item.get_or_none(Item.id == item_id)\n"
    "    if not item:\n"
    '        raise HTTPException(status_code=404, detail="Item not found")\n'
    "    return _item_response(item)",
    "    item: Any = Item.get_or_none(Item.id == item_id)\n"
    "    if not item:\n"
    '        raise HTTPException(status_code=404, detail="Item not found")\n'
    "    response = _item_response(item)\n"
    "    response.description = (\n"
    '        f"{response.description or \'\'} (updated {item.updated_at:%b %d})".strip()\n'
    "    )\n"
    "    return response",
)
PY
