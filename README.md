# runbooks_testing

A mono-repo with FastAPI, Go, and Backbone.js components.

## Components

- **backend_python/** - FastAPI application with SQLite/Peewee
- **backend_go/** - Go HTTP server (standard library)
- **frontend/** - Backbone.js SPA

## Running Each Component

### Python Backend

```bash
cd backend_python
uv sync
uv run uvicorn runbooks_testing_api.main:app --reload
```

### Go Backend

```bash
cd backend_go
go run ./cmd/server
```

### Frontend

```bash
cd frontend
npm install
npm start            # serves the SPA on :3000 and proxies /api to the Python backend
```

Set `API_TARGET` if the Python backend is not on `http://localhost:8000`.

### Docker

Run all services:
```bash
docker compose up --build
```

Then open http://localhost:3000 and sign in as `admin` / `admin` (admin role) or a regular user such as `alice` / `password` (also `bob`, `carol`). Admins can create and delete users; regular users have read-only access.

| Service            | URL                   |
|--------------------|-----------------------|
| Frontend (website) | http://localhost:3000 |
| Python API         | http://localhost:8000 |
| Go API             | http://localhost:8080 |

## Aviator Verify Previews

This repo ships everything needed for Aviator to spin up a live preview and run Verify against the website:

- `e2b.Dockerfile` — the sandbox image (Python + uv + Node toolchain).
- `.aviator/scripts/preview-setup.sh` — starts the backend and frontend in the preview sandbox on port 3000.
- `.aviator/verify/skills/` — guidance for the Verify agent (sign-in, navigation, what's observable).

Two one-time setup steps in Aviator:

1. Build the container template: Runbooks > Settings > Sandbox > Custom Templates > Add Custom Container Template, then paste or upload `e2b.Dockerfile` and give it a name.
2. Add a preview config in the repo's Runbooks settings:

```yaml
runbooks:
  preview:
    - name: default
      image: "<your custom template name>"
      port: 3000
      setup: .aviator/scripts/preview-setup.sh
```

The preview name `default` maps to `.aviator/verify/skills/default.md`. Aviator brings up the sandbox, runs the setup script, exposes port 3000 as the preview URL, and the Verify agent drives it. Sign-in uses the seeded `admin` / `admin` or `alice` / `password` accounts.

## Testing

### Python Backend

```bash
cd backend_python
uv sync
uv run pytest                    # Run all tests
uv run pytest -v                 # Verbose output
uv run pytest --cov              # With coverage
```

## Pre-commit Hooks

Setup:
```bash
pip install pre-commit
pre-commit install
```

Run manually:
```bash
pre-commit run --all-files
```

## CI Workflows

| Workflow | Behavior |
|----------|----------|
| `lint.yaml` | Runs pre-commit hooks |
| `test.yaml` | Runs pytest |
| `flaky.yaml` | Fails ~50% of the time (configurable) |
| `always_pass.yaml` | Always succeeds |
| `always_fail.yaml` | Always fails (manual trigger only) |
| `pass_or_fail.yaml` | Configurable pass/fail |
