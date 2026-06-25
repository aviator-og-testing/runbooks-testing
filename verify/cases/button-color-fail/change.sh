#!/usr/bin/env bash
# Make the primary brand color red while the AC claims "green", so verify should
# FAIL this one (the discriminating case).
set -euo pipefail
sed -i.bak 's/--brand: #4f46e5;/--brand: #dc2626;/' frontend/src/index.html
rm -f frontend/src/index.html.bak
