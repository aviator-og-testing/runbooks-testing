"""
Tests for runbooks_testing database models.
"""

import pytest

from runbooks_testing_api.models import Item, User


class TestUserModel:
    """Tests for the User model."""

    def test_create_user(self) -> None:
        """Should create a user with username and email."""
        user = User.create(username="alice", email="alice@example.com")
        assert user.username == "alice"
        assert user.email == "alice@example.com"
        assert user.id is not None

    def test_user_str_representation(self) -> None:
        """User string representation should show username."""
        user = User.create(username="bob", email="bob@example.com")
        assert str(user) == "User(bob)"

    def test_username_must_be_unique(self) -> None:
        """Should not allow duplicate usernames."""
        User.create(username="unique", email="first@example.com")
        with pytest.raises(Exception):
            User.create(username="unique", email="second@example.com")

    def test_email_must_be_unique(self) -> None:
        """Should not allow duplicate emails."""
        User.create(username="first", email="same@example.com")
        with pytest.raises(Exception):
            User.create(username="second", email="same@example.com")

    def test_created_at_is_set_automatically(self) -> None:
        """created_at should be set on creation."""
        user = User.create(username="timed", email="timed@example.com")
        assert user.created_at is not None


class TestItemModel:
    """Tests for the Item model."""

    def test_create_item_with_description(self) -> None:
        """Should create an item with name and description."""
        item = Item.create(name="Gadget", description="A fancy gadget")
        assert item.name == "Gadget"
        assert item.description == "A fancy gadget"

    def test_create_item_without_description(self) -> None:
        """Should allow creating items without description."""
        item = Item.create(name="Plain Item")
        assert item.name == "Plain Item"
        assert item.description is None

    def test_created_at_is_set_automatically(self) -> None:
        """created_at should be set on creation."""
        item = Item.create(name="Timed Item")
        assert item.created_at is not None
