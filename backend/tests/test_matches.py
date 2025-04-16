import pytest
from fastapi.testclient import TestClient
from ..main import app

client = TestClient(app)

@pytest.fixture
def auth_headers():
    login_data = {
        "username": "test@example.com",
        "password": "strongpassword123"
    }
    response = client.post("/api/v1/auth/token", data=login_data)
    return {"Authorization": f"Bearer {response.json()['access_token']}"}

@pytest.fixture
def user_preferences(auth_headers):
    # Set up user preferences first
    preferences = {
        "max_distance": 50,
        "age_range": {"min": 18, "max": 35},
        "interested_in": ["female"],
        "show_me": True
    }
    client.put(
        "/api/v1/users/me/preferences",
        json=preferences,
        headers=auth_headers
    )
    return preferences

def test_get_match_recommendations_no_preferences(auth_headers):
    # Clear preferences first (if any)
    preferences = {
        "max_distance": None,
        "age_range": None,
        "interested_in": None,
        "show_me": False
    }
    client.put(
        "/api/v1/users/me/preferences",
        json=preferences,
        headers=auth_headers
    )
    
    response = client.get("/api/v1/matches/recommendations", headers=auth_headers)
    assert response.status_code == 400
    assert response.json()["detail"] == "Please set your matching preferences first"

def test_get_match_recommendations(auth_headers, user_preferences):
    response = client.get("/api/v1/matches/recommendations", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    if len(data) > 0:
        assert "id" in data[0]
        assert "email" in data[0]
        assert "hashed_password" not in data[0]

def test_create_match(auth_headers):
    # First get a recommendation
    response = client.get("/api/v1/matches/recommendations", headers=auth_headers)
    if response.status_code == 200 and len(response.json()) > 0:
        user_to_match = response.json()[0]
        
        response = client.post(
            f"/api/v1/matches/{user_to_match['id']}",
            headers=auth_headers
        )
        assert response.status_code == 200
        assert response.json()["message"] == "Match created successfully"
        
        # Try to create same match again
        response = client.post(
            f"/api/v1/matches/{user_to_match['id']}",
            headers=auth_headers
        )
        assert response.status_code == 400
        assert response.json()["detail"] == "Match already exists"

def test_create_match_nonexistent_user(auth_headers):
    response = client.post(
        "/api/v1/matches/nonexistent-id",
        headers=auth_headers
    )
    assert response.status_code == 400

def test_accept_match(auth_headers):
    # First create a match
    response = client.get("/api/v1/matches/recommendations", headers=auth_headers)
    if response.status_code == 200 and len(response.json()) > 0:
        user_to_match = response.json()[0]
        
        client.post(
            f"/api/v1/matches/{user_to_match['id']}",
            headers=auth_headers
        )
        
        response = client.put(
            f"/api/v1/matches/{user_to_match['id']}/accept",
            headers=auth_headers
        )
        assert response.status_code == 200
        assert response.json()["message"] == "Match accepted successfully"

def test_reject_match(auth_headers):
    # First create a match
    response = client.get("/api/v1/matches/recommendations", headers=auth_headers)
    if response.status_code == 200 and len(response.json()) > 0:
        user_to_match = response.json()[0]
        
        client.post(
            f"/api/v1/matches/{user_to_match['id']}",
            headers=auth_headers
        )
        
        response = client.put(
            f"/api/v1/matches/{user_to_match['id']}/reject",
            headers=auth_headers
        )
        assert response.status_code == 200
        assert response.json()["message"] == "Match rejected successfully"

def test_get_my_matches(auth_headers):
    response = client.get("/api/v1/matches/my-matches", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    if len(data) > 0:
        assert "id" in data[0]
        assert "email" in data[0]
        assert "match_score" in data[0]
        assert "hashed_password" not in data[0] 