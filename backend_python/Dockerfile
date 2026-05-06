# syntax=docker/dockerfile:1
FROM python:3.11-slim AS base

WORKDIR /app

# Install uv for faster dependency management
# https://github.com/astral-sh/uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy dependency files first for better layer caching
COPY pyproject.toml ./

# Development stage
FROM base AS dev
RUN uv sync
COPY src/ ./src/
CMD ["uv", "run", "uvicorn", "runbooks_testing_api.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# Production stage
FROM base AS prod
RUN uv sync --no-dev
COPY src/ ./src/
EXPOSE 8000
CMD ["uv", "run", "uvicorn", "runbooks_testing_api.main:app", "--host", "0.0.0.0", "--port", "8000"]
