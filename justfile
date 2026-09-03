# Verify testing helpers for this app.
# See verify/ and the README "Aviator Verify Previews" section.

# List available recipes.
default:
    @just --list

# Open a test PR for a verify case (verify/cases/<case>/). Branches off the
# current branch, applies the case's change, pushes, and opens a PR, then
# switches back to main. Requires gh. Run without a case to list the cases.
verify-pr case="":
    #!/usr/bin/env bash
    set -euo pipefail
    if [ -z "{{case}}" ]; then
        echo "usage: just verify-pr <case>" >&2
        echo "available cases:" >&2
        for dir in verify/cases/*/; do
            name="$(basename "$dir")"
            desc="$(awk 'NR==1{next} /^#/{sub(/^#[[:space:]]?/,""); printf "%s ", $0; next} {exit}' "$dir/change.sh")"
            printf '  %-18s %s\n' "$name" "$desc" >&2
        done
        exit 0
    fi
    dir="verify/cases/{{case}}"
    test -d "$dir" || { echo "no such case: {{case}} (see verify/cases/)" >&2; exit 1; }
    branch="verify/{{case}}-$(date +%Y%m%d-%H%M%S)"
    git switch -c "$branch"
    bash "$dir/change.sh"
    # verify/ holds the case definitions; keeping them out of the test PR
    # diff stops criteria generation from reading the case's own notes.
    git add -A -- ':(exclude)verify'
    git commit -qm "verify case: {{case}}"
    git push -q -u origin "$branch"
    gh pr create --title "verify: {{case}}" --body "Automated verify test case: {{case}}."
    git switch main
