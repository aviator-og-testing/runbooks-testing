#!/usr/bin/env bash
# Render the username unescaped in the users list (violates "user content renders
# inert" — an XSS hole).
set -euo pipefail
sed -i.bak 's/<%- user.username %>/<%= user.username %>/' frontend/src/index.html
rm -f frontend/src/index.html.bak
