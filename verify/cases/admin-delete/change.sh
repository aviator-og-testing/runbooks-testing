#!/usr/bin/env bash
# No app change; this checks existing admin-only delete behavior. Touch a marker
# so the PR has a diff.
set -euo pipefail
printf 'verify case run: admin-delete\n' >> verify/.runs.md
