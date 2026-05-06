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
npm start
```

### Docker

Run all services:
```bash
docker-compose up
```

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
