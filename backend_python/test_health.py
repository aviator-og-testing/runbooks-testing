"""Quick test for the /health endpoint"""

from datetime import datetime

from fastapi.testclient import TestClient

from runbooks_testing_api.main import app

client = TestClient(app)

response = client.get("/health")
print(f"Status code: {response.status_code}")
print(f"Response: {response.json()}")

# Verify structure
data = response.json()
assert "status" in data
assert "service" in data
assert "timestamp" in data
assert data["status"] == "ok"
assert data["service"] == "runbooks_testing_api"

# Verify timestamp is valid ISO 8601
datetime.fromisoformat(data["timestamp"])

print("All checks passed!")
