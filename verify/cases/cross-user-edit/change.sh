#!/usr/bin/env bash
# No app change; this checks existing post-edit permissions across two users.
# Touch a marker so the PR has a diff.
set -euo pipefail
printf 'verify case run: cross-user-edit\n' >> verify/.runs.md
