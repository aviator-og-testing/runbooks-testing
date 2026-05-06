"""
Tests for runbooks_testing API endpoints.
"""

from fastapi.testclient import TestClient

from runbooks_testing_api.models import Item, User


class TestHealthEndpoints:
    """Tests for health check endpoints."""

    def test_root_returns_hello_world(self, client: TestClient) -> None:
        """GET / should return hello world message."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Hello World"
        assert data["status"] == "ok"

    def test_hello_with_name(self, client: TestClient) -> None:
        """GET /hello/{name} should return personalized greeting."""
        response = client.get("/hello/Alice")
        assert response.status_code == 200
        assert response.json()["message"] == "Hello Alice"


class TestUserEndpoints:
    """Tests for user CRUD endpoints."""

    def test_create_user(self, client: TestClient) -> None:
        """POST /users should create a new user."""
        response = client.post(
            "/users",
            json={"username": "newuser", "email": "new@example.com"},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["username"] == "newuser"
        assert data["email"] == "new@example.com"
        assert "id" in data

    def test_create_duplicate_user_fails(self, client: TestClient, sample_user: User) -> None:
        """POST /users with existing username should fail."""
        response = client.post(
            "/users",
            json={"username": sample_user.username, "email": "other@example.com"},
        )
        assert response.status_code == 400

    def test_list_users_empty(self, client: TestClient) -> None:
        """GET /users should return empty list when no users exist."""
        response = client.get("/users")
        assert response.status_code == 200
        assert response.json() == []

    def test_list_users_with_data(self, client: TestClient, sample_user: User) -> None:
        """GET /users should return list of users."""
        response = client.get("/users")
        assert response.status_code == 200
        users = response.json()
        assert len(users) == 1
        assert users[0]["username"] == sample_user.username

    def test_get_user_by_id(self, client: TestClient, sample_user: User) -> None:
        """GET /users/{id} should return specific user."""
        response = client.get(f"/users/{sample_user.id}")
        assert response.status_code == 200
        assert response.json()["username"] == sample_user.username

    def test_get_nonexistent_user(self, client: TestClient) -> None:
        """GET /users/{id} should return 404 for unknown user."""
        response = client.get("/users/99999")
        assert response.status_code == 404


class TestItemEndpoints:
    """Tests for item CRUD endpoints."""

    def test_create_item(self, client: TestClient) -> None:
        """POST /items should create a new item."""
        response = client.post(
            "/items",
            json={"name": "Widget", "description": "A useful widget"},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Widget"
        assert data["description"] == "A useful widget"

    def test_create_item_without_description(self, client: TestClient) -> None:
        """POST /items should allow items without description."""
        response = client.post("/items", json={"name": "Simple Item"})
        assert response.status_code == 201
        assert response.json()["description"] is None

    def test_list_items(self, client: TestClient, sample_item: Item) -> None:
        """GET /items should return list of items."""
        response = client.get("/items")
        assert response.status_code == 200
        items = response.json()
        assert len(items) == 1
        assert items[0]["name"] == sample_item.name
