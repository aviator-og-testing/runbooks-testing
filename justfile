# Verify testing helpers for this app.
# See verify/ and the README "Aviator Verify Previews" section.

# List available recipes.
default:
    @just --list

# Seed/refresh this app's baseline invariants in the local mergeit DB.
# Wipes the [AUTOGEN] invariants for this repo's account and recreates them from
# verify/baseline-invariants.yaml. Override MERGEIT_DATABASE_URL or
# REPO_FULL_NAME if your local setup differs.
verify-invariants:
    uv run --no-project --with pyyaml --with 'psycopg[binary]' python verify/seed_invariants.py

# Open a test PR for a verify case (verify/cases/<case>/). Branches off the
# current branch, applies the case's change, pushes, and opens a PR with the
# case's acceptance criteria as the body. Requires gh.
verify-pr case:
    #!/usr/bin/env bash
    set -euo pipefail
    dir="verify/cases/{{case}}"
    test -d "$dir" || { echo "no such case: {{case}} (see verify/cases/)" >&2; exit 1; }
    branch="verify/{{case}}-$(date +%Y%m%d-%H%M%S)"
    git switch -c "$branch"
    bash "$dir/change.sh"
    git add -A
    git commit -qm "verify case: {{case}}"
    git push -q -u origin "$branch"
    gh pr create --title "verify: {{case}}" --body-file "$dir/criteria.md"
