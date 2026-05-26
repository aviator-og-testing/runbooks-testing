"""
runbooks_testing API - Main application entry point.

This module sets up the FastAPI application and defines the core routes.
For larger applications, consider splitting routes into separate routers.
"""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from datetime import UTC, datetime
from typing import Any

from fastapi import FastAPI, HTTPException
from peewee import IntegrityError
from pydantic import BaseModel

from .models import Item, User, close_db, init_db


# Request/Response schemas
class UserCreate(BaseModel):
    username: str
    email: str


class UserResponse(BaseModel):
    id: int
    username: str
    email: str

    model_config = {"from_attributes": True}


class ItemCreate(BaseModel):
    name: str
    description: str | None = None


class ItemResponse(BaseModel):
    id: int
    name: str
    description: str | None

    model_config = {"from_attributes": True}


class HealthResponse(BaseModel):
    message: str
    status: str


class HealthCheckResponse(BaseModel):
    status: str
    service: str
    timestamp: str


class HelloResponse(BaseModel):
    message: str


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    """Handle startup and shutdown events."""
    init_db()
    yield
    close_db()


app = FastAPI(
    title="runbooks_testing API",
    description="Backend API for runbooks_testing",
    version="0.1.0",
    lifespan=lifespan,
)


@app.get("/")
async def root() -> dict[str, str]:
    """Health check endpoint."""
    return {"message": "Hello World", "status": "ok"}


@app.get("/health", response_model=HealthCheckResponse)
async def health_check() -> HealthCheckResponse:
    """Health check endpoint with service info and current UTC timestamp."""
    return HealthCheckResponse(
        status="ok",
        service="runbooks_testing_api",
        timestamp=datetime.now(UTC).isoformat(),
    )


@app.get("/hello/{name}")
async def hello(name: str) -> dict[str, str]:
    """Personalized greeting endpoint."""
    return {"message": f"Hello {name}"}


# User endpoints
@app.post("/users", response_model=UserResponse, status_code=201)
async def create_user(user: UserCreate) -> UserResponse:
    """Create a new user."""
    try:
        db_user: Any = User.create(username=user.username, email=user.email)
        return UserResponse(id=db_user.id, username=db_user.username, email=db_user.email)
    except IntegrityError as e:
        raise HTTPException(status_code=400, detail="Username or email already exists") from e


@app.get("/users", response_model=list[UserResponse])
async def list_users() -> list[UserResponse]:
    """List all users."""
    users: Any = User.select()
    return [UserResponse(id=u.id, username=u.username, email=u.email) for u in users]


@app.get("/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: int) -> UserResponse:
    """Get a specific user by ID."""
    user: Any = User.get_or_none(User.id == user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserResponse(id=user.id, username=user.username, email=user.email)


# Item endpoints
@app.post("/items", response_model=ItemResponse, status_code=201)
async def create_item(item: ItemCreate) -> ItemResponse:
    """Create a new item."""
    db_item: Any = Item.create(name=item.name, description=item.description)
    return ItemResponse(id=db_item.id, name=db_item.name, description=db_item.description)


@app.get("/items", response_model=list[ItemResponse])
async def list_items() -> list[ItemResponse]:
    """List all items."""
    items: Any = Item.select()
    return [ItemResponse(id=i.id, name=i.name, description=i.description) for i in items]
