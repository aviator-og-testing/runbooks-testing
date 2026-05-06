# runbooks_testing

A mono-repo containing three components: a Python backend, a Go backend, and a vanilla JS frontend.

## Project Structure

```
runbooks_testing/
├── backend_python/     # FastAPI application with SQLite/Peewee
├── backend_go/         # Go HTTP server (standard library)
├── frontend/           # Vanilla HTML/JS frontend
├── docker-compose.yml  # Container orchestration
└── .github/workflows/  # CI workflows
```

## Components

### Python Backend (`backend_python/`)

- **Framework**: FastAPI
- **Database**: SQLite with Peewee ORM
- **Entry point**: `src/runbooks_testing_api/main.py`
- **Models**: `src/runbooks_testing_api/models.py` (User, Item)

Run with:
```bash
cd backend_python
uv sync
uv run uvicorn runbooks_testing_api.main:app --reload
```

API endpoints:
- `GET /` - Health check
- `GET /hello/{name}` - Greeting
- `GET/POST /users` - User CRUD
- `GET/POST /items` - Item CRUD

### Go Backend (`backend_go/`)

- **Framework**: Standard library `net/http`
- **Entry point**: `cmd/server/main.go`
- **Handlers**: `internal/handler/handler.go`

Run with:
```bash
cd backend_go
go run ./cmd/server
```

API endpoints:
- `GET /` - Hello World (JSON)
- `GET /hello/{name}` - Greeting
- `GET /health` - Health check

### Frontend (`frontend/`)

- **Framework**: None (vanilla JS)
- **Entry point**: `src/index.html`
- **Logic**: `src/main.js`

Run with:
```bash
cd frontend
npm start
```

## Testing

### Python

Tests use nose and are located in `backend_python/tests/`. Run with:
```bash
cd backend_python
uv run nosetests
```

## Code Style

- **Python**: Use `uvx ruff check` and `uvx ruff format`
- **Go**: Use `go fmt` and `go vet`
- **JS**: No linting configured

## Docker

Each backend has a Dockerfile. Use docker-compose for local development:
```bash
docker-compose up
```

## Database

The Python backend uses SQLite stored in `runbooks_testing.db`. The database is auto-created on first run. To use a different path, set `RUNBOOKS_TESTING_DB_PATH` environment variable.

## Pre-commit

Pre-commit hooks are configured. Install with:
```bash
pip install pre-commit
pre-commit install
```

## Ownership

- See `CODEOWNERS` for GitHub code owners
- See `.aviator/OWNERS` for Aviator ownership
- Each component has its own `aviator-config.yaml` for team notifications

## CI/CD

GitHub Actions workflows in `.github/workflows/`:
- `lint.yaml` - Runs pre-commit hooks (ruff, mypy, go-vet, prettier)
- `test.yaml` - Runs pytest for the Python backend
- `flaky.yaml` - Fails ~50% of the time (configurable via `failure_percentage`)
- `always_pass.yaml` - Test workflow that always passes
- `always_fail.yaml` - Test workflow that always fails (workflow_dispatch only)
- `pass_or_fail.yaml` - Configurable test workflow
