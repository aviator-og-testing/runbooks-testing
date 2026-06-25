#!/usr/bin/env bash
# No app change; the AC is about the API response shape, so verify should route
# it to a code scan rather than the preview. Touch a marker so the PR has a diff.
set -euo pipefail
printf 'verify case run: role-in-api\n' >> verify/.runs.md
