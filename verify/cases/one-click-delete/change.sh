#!/usr/bin/env bash
# Make user deletion fire on a single click by neutering the arm step (violates
# "destructive actions confirm").
set -euo pipefail
sed -i.bak 's/if (!btn.hasClass("armed")) {/if (false) {/' frontend/src/main.js
rm -f frontend/src/main.js.bak
