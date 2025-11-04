"""Test health check endpoint"""


def test_health_check(client):
    """Test health check endpoint returns 200"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_root_endpoint(client):
    """Test root endpoint returns welcome message"""
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()
    assert "version" in response.json()
