# syntax=docker/dockerfile:1
FROM python:3.11-slim AS base

WORKDIR /app

# Install uv for faster dependency management
# https://github.com/astral-sh/uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy project files (uv needs the package source to install the project)
COPY pyproject.toml ./
COPY src/ ./src/

# Directory for the SQLite database
RUN mkdir -p /app/data

# Development stage
FROM base AS dev
RUN uv sync
EXPOSE 8000
CMD ["uv", "run", "uvicorn", "runbooks_testing_api.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# Production stage
FROM base AS prod
RUN uv sync --no-dev
EXPOSE 8000
CMD ["uv", "run", "uvicorn", "runbooks_testing_api.main:app", "--host", "0.0.0.0", "--port", "8000"]
