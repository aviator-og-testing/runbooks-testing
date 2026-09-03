"""
runbooks_testing API - Main application entry point.

This module sets up the FastAPI application and defines the core routes.
For larger applications, consider splitting routes into separate routers.
"""

import os
import random
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, Header, HTTPException
from peewee import IntegrityError
from pydantic import BaseModel

from .models import Item, User, close_db, init_db


# Request/Response schemas
class UserCreate(BaseModel):
    username: str
    email: str
    password: str = ""
    role: str = "user"


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    role: str

    model_config = {"from_attributes": True}


class ItemCreate(BaseModel):
    name: str
    description: str | None = None
    author: str = ""


class ItemResponse(BaseModel):
    id: int
    name: str
    description: str | None
    author: str
    created_at: str

    model_config = {"from_attributes": True}


class ItemUpdate(BaseModel):
    name: str
    description: str | None = None


class HealthResponse(BaseModel):
    message: str
    status: str


class HelloResponse(BaseModel):
    message: str


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    success: bool
    username: str
    role: str


STABLE_DEMO_USERS = [
    ("admin", "admin@example.com", "admin"),
    ("alice", "alice@example.com", "user"),
    ("bob", "bob@example.com", "user"),
    ("carol", "carol@example.com", "user"),
]
DEMO_PASSWORD = "password"


def seed_demo_users() -> None:
    """Seed demo users for local logins (idempotent for the stable accounts)."""
    for username, email, role in STABLE_DEMO_USERS:
        if User.get_or_none(User.username == username) is None:
            password = "admin" if username == "admin" else DEMO_PASSWORD
            User.create(username=username, email=email, password=password, role=role)
    random_username = f"user_{random.randint(1000, 9999)}"
    if User.get_or_none(User.username == random_username) is None:
        User.create(
            username=random_username,
            email=f"{random_username}@example.com",
            password=DEMO_PASSWORD,
            role="user",
        )


STABLE_DEMO_POSTS = [
    ("Welcome to the blog", "A sample blog built on the demo stack. Sign in and add your own posts.", "admin"),
    ("Getting started", "Each post is just an item with a title, some content, and an author.", "alice"),
    ("Notes on testing", "Handy for poking at Runbooks, FlexReview, and MergeQueue flows.", "bob"),
]


def seed_demo_posts() -> None:
    """Seed a few demo blog posts (idempotent by title)."""
    for title, content, author in STABLE_DEMO_POSTS:
        if Item.get_or_none(Item.name == title) is None:
            Item.create(name=title, description=content, author=author)


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    """Handle startup and shutdown events."""
    init_db()
    if os.getenv("RUNBOOKS_TESTING_SEED_DEMO"):
        seed_demo_users()
        seed_demo_posts()
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


@app.get("/hello/{name}")
async def hello(name: str) -> dict[str, str]:
    """Personalized greeting endpoint."""
    return {"message": f"Hello {name}"}


@app.post("/login", response_model=LoginResponse)
async def login(credentials: LoginRequest) -> LoginResponse:
    """Authenticate a user against the database."""
    user: Any = User.get_or_none(User.username == credentials.username)
    if user is None or not user.password or user.password != credentials.password:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    return LoginResponse(success=True, username=user.username, role=user.role)


# User endpoints
@app.post("/users", response_model=UserResponse, status_code=201)
async def create_user(user: UserCreate) -> UserResponse:
    """Create a new user."""
    try:
        db_user: Any = User.create(
            username=user.username,
            email=user.email,
            password=user.password,
            role=user.role,
        )
        return UserResponse(
            id=db_user.id, username=db_user.username, email=db_user.email, role=db_user.role
        )
    except IntegrityError as e:
        raise HTTPException(status_code=400, detail="Username or email already exists") from e


@app.get("/users", response_model=list[UserResponse])
async def list_users() -> list[UserResponse]:
    """List all users."""
    users: Any = User.select()
    return [
        UserResponse(id=u.id, username=u.username, email=u.email, role=u.role) for u in users
    ]


@app.get("/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: int) -> UserResponse:
    """Get a specific user by ID."""
    user: Any = User.get_or_none(User.id == user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserResponse(id=user.id, username=user.username, email=user.email, role=user.role)


@app.delete("/users/{user_id}")
async def delete_user(
    user_id: int, x_user_role: str | None = Header(default=None)
) -> dict[str, int]:
    """Delete a user. Requires the caller to act as an admin."""
    if x_user_role != "admin":
        raise HTTPException(status_code=403, detail="Admin role required")
    user: Any = User.get_or_none(User.id == user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.delete_instance()
    return {"deleted": user_id}


# Item endpoints
def _item_response(item: Any) -> ItemResponse:
    return ItemResponse(
        id=item.id,
        name=item.name,
        description=item.description,
        author=item.author,
        created_at=item.created_at.isoformat(),
    )


@app.post("/items", response_model=ItemResponse, status_code=201)
async def create_item(item: ItemCreate) -> ItemResponse:
    """Create a new item (blog-style post)."""
    db_item: Any = Item.create(name=item.name, description=item.description, author=item.author)
    return _item_response(db_item)


@app.get("/items", response_model=list[ItemResponse])
async def list_items() -> list[ItemResponse]:
    """List all items, newest first."""
    items: Any = Item.select().order_by(Item.id.desc())
    return [_item_response(i) for i in items]


@app.get("/items/{item_id}", response_model=ItemResponse)
async def get_item(item_id: int) -> ItemResponse:
    """Get a single item."""
    item: Any = Item.get_or_none(Item.id == item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return _item_response(item)


@app.put("/items/{item_id}", response_model=ItemResponse)
async def update_item(
    item_id: int,
    update: ItemUpdate,
    x_username: str | None = Header(default=None),
    x_user_role: str | None = Header(default=None),
) -> ItemResponse:
    """Update a post. Allowed for the post's author or an admin."""
    item: Any = Item.get_or_none(Item.id == item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    if x_user_role != "admin" and x_username != item.author:
        raise HTTPException(status_code=403, detail="Only the author or an admin can edit this post")
    item.name = update.name
    item.description = update.description
    item.save()
    return _item_response(item)
