# E2B custom container template for the Aviator verify preview sandbox.
#
# Build this once per account in Aviator: Runbooks > Settings > Sandbox >
# Custom Templates > Add Custom Container Template (paste or upload this file).
# Aviator builds it into an E2B template you can reference by name.
#
# Notes:
# - COPY and ADD are NOT supported; the repo is cloned into the sandbox at
#   preview time, so this image only needs the toolchain, not the app.
# - git, git-lfs, and claude-code are installed automatically on top of this.
FROM e2bdev/code-interpreter:latest

# Node 20 for the frontend server (server.js + http-proxy-middleware).
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
 && apt-get install -y --no-install-recommends nodejs \
 && rm -rf /var/lib/apt/lists/*

# uv for the Python backend.
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:${PATH}"
