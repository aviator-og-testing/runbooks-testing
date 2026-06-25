#!/usr/bin/env bash
# Rename the dashboard heading (a runtime text check that requires logging in).
set -euo pipefail
sed -i.bak 's|<h1>Dashboard</h1>|<h1>Control Center</h1>|' frontend/src/index.html
rm -f frontend/src/index.html.bak
