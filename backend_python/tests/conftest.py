"""
Pytest fixtures for runbooks_testing API tests.
"""

import os
import tempfile
from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

# Use a temp file for test database (not :memory: which creates new DB per connection)
_test_db_file = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
os.environ["RUNBOOKS_TESTING_DB_PATH"] = _test_db_file.name

from runbooks_testing_api.main import app
from runbooks_testing_api.models import Item, User, close_db, db, init_db


@pytest.fixture(autouse=True)
def setup_test_db() -> Iterator[None]:
    """Create fresh database tables for each test."""
    init_db()
    yield
    # Clean up data after each test
    User.delete().execute()
    Item.delete().execute()


@pytest.fixture
def client() -> Iterator[TestClient]:
    """Create a test client for the FastAPI app."""
    with TestClient(app) as c:
        yield c


@pytest.fixture
def sample_user() -> User:
    """Create a sample user for testing."""
    return User.create(username="testuser", email="test@example.com")


@pytest.fixture
def sample_item() -> Item:
    """Create a sample item for testing."""
    return Item.create(name="Test Item", description="A test item")
