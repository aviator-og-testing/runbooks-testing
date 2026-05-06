"""
Database models for runbooks_testing.

Uses Peewee ORM with SQLite for lightweight persistence.
Schema migrations are handled manually for now - see docs/migrations.md
for the recommended workflow.
"""

import os
from datetime import datetime
from typing import ClassVar

from peewee import (
    DateTimeField,
    Model,
    SqliteDatabase,
    TextField,
)

# Database path can be overridden via environment variable for testing
DATABASE_PATH: str = os.getenv("RUNBOOKS_TESTING_DB_PATH", "runbooks_testing.db")
db: SqliteDatabase = SqliteDatabase(DATABASE_PATH)


class BaseModel(Model):
    """Base model that all other models inherit from."""

    class Meta:
        database = db


class User(BaseModel):
    """
    Represents a user in the system.

    Note: In production, you'd want to add proper password hashing
    and potentially move to a more robust auth system.
    """

    username: ClassVar[TextField] = TextField(unique=True)
    email: ClassVar[TextField] = TextField(unique=True)
    created_at: ClassVar[DateTimeField] = DateTimeField(default=datetime.now)

    def __str__(self) -> str:
        return f"User({self.username})"


class Item(BaseModel):
    """
    Generic item model for demonstration purposes.

    This would typically be replaced with domain-specific models
    based on your application's requirements.
    """

    name: ClassVar[TextField] = TextField()
    description: ClassVar[TextField] = TextField(null=True)
    created_at: ClassVar[DateTimeField] = DateTimeField(default=datetime.now)


def init_db() -> None:
    """Initialize the database and create tables if they don't exist."""
    db.connect(reuse_if_open=True)
    db.create_tables([User, Item], safe=True)


def close_db() -> None:
    """Close the database connection."""
    if not db.is_closed():
        db.close()
