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
        """GET /items should return paginated list of items with defaults."""
        response = client.get("/items")
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 1
        assert data["items"][0]["name"] == sample_item.name
        assert data["total_count"] == 1
        assert data["page"] == 1
        assert data["page_size"] == 20

    def test_list_items_with_custom_page_size(self, client: TestClient) -> None:
        """GET /items?page=1&page_size=2 should return only 2 items with full total_count."""
        for i in range(5):
            Item.create(name=f"Item {i}", description=None)
        response = client.get("/items?page=1&page_size=2")
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 2
        assert data["total_count"] == 5
        assert data["page"] == 1
        assert data["page_size"] == 2

    def test_list_items_partial_last_page(self, client: TestClient) -> None:
        """GET /items should return remaining items on the last partial page."""
        for i in range(5):
            Item.create(name=f"Item {i}", description=None)
        response = client.get("/items?page=3&page_size=2")
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 1
        assert data["total_count"] == 5
        assert data["page"] == 3
        assert data["page_size"] == 2

    def test_list_items_empty(self, client: TestClient) -> None:
        """GET /items should return empty list with metadata when no items exist."""
        response = client.get("/items?page=1&page_size=10")
        assert response.status_code == 200
        data = response.json()
        assert data["items"] == []
        assert data["total_count"] == 0
        assert data["page"] == 1
        assert data["page_size"] == 10

    def test_list_items_page_beyond_total(self, client: TestClient) -> None:
        """GET /items with a page beyond total results should return empty items."""
        for i in range(3):
            Item.create(name=f"Item {i}", description=None)
        response = client.get("/items?page=5&page_size=2")
        assert response.status_code == 200
        data = response.json()
        assert data["items"] == []
        assert data["total_count"] == 3
        assert data["page"] == 5
        assert data["page_size"] == 2

    def test_list_items_page_size_zero_rejected(self, client: TestClient) -> None:
        """GET /items?page_size=0 should return HTTP 422."""
        response = client.get("/items?page_size=0")
        assert response.status_code == 422

    def test_list_items_page_zero_rejected(self, client: TestClient) -> None:
        """GET /items?page=0 should return HTTP 422."""
        response = client.get("/items?page=0")
        assert response.status_code == 422

    def test_list_items_sort_by_name_ascending(self, client: TestClient) -> None:
        """GET /items?sort_by=name should order items by name ascending."""
        Item.create(name="Charlie", description=None)
        Item.create(name="Alpha", description=None)
        Item.create(name="Bravo", description=None)
        response = client.get("/items?sort_by=name")
        assert response.status_code == 200
        names = [item["name"] for item in response.json()["items"]]
        assert names == ["Alpha", "Bravo", "Charlie"]

    def test_list_items_default_sort_by_created_at_desc(self, client: TestClient) -> None:
        """GET /items should order by created_at descending by default."""
        from datetime import datetime, timedelta

        base = datetime(2026, 1, 1, 12, 0, 0)
        Item.create(name="oldest", description=None, created_at=base)
        Item.create(name="middle", description=None, created_at=base + timedelta(hours=1))
        Item.create(name="newest", description=None, created_at=base + timedelta(hours=2))
        response = client.get("/items")
        assert response.status_code == 200
        names = [item["name"] for item in response.json()["items"]]
        assert names == ["newest", "middle", "oldest"]

    def test_list_items_invalid_sort_by_rejected(self, client: TestClient) -> None:
        """GET /items with an invalid sort_by value should return HTTP 422."""
        response = client.get("/items?sort_by=description")
        assert response.status_code == 422
