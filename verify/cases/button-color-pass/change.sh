#!/usr/bin/env bash
# Make the primary brand color green (so "buttons are green" should PASS).
set -euo pipefail
sed -i.bak 's/--brand: #4f46e5;/--brand: #16a34a;/' frontend/src/index.html
rm -f frontend/src/index.html.bak
