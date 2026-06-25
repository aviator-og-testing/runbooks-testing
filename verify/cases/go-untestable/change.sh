#!/usr/bin/env bash
# No app change. This case checks that verify routes a criterion the preview
# can't observe (the Go service, which the preview never runs) to a code scan
# rather than a failed runtime attempt. Touch a marker so the PR has a diff.
set -euo pipefail
printf 'verify case run: go-untestable\n' >> verify/.runs.md
