import pytest
from fastapi.testclient import TestClient
from ..main import app
import io

client = TestClient(app)

# Helper function to get auth token
def get_auth_token():
    login_data = {
        "username": "test@example.com",
        "password": "strongpassword123"
    }
    response = client.post("/api/v1/auth/token", data=login_data)
    return response.json()["access_token"]

@pytest.fixture
def auth_headers():
    token = get_auth_token()
    return {"Authorization": f"Bearer {token}"}

def test_read_user_me(auth_headers):
    response = client.get("/api/v1/users/me", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"
    assert "hashed_password" not in data

def test_read_user_me_no_token():
    response = client.get("/api/v1/users/me")
    assert response.status_code == 401

def test_update_user_me(auth_headers):
    update_data = {
        "full_name": "Updated Name",
        "bio": "Updated bio"
    }
    response = client.put("/api/v1/users/me", json=update_data, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["full_name"] == update_data["full_name"]
    assert data["bio"] == update_data["bio"]

def test_update_user_me_invalid_data(auth_headers):
    update_data = {
        "email": "invalid-email"  # Email should not be updateable
    }
    response = client.put("/api/v1/users/me", json=update_data, headers=auth_headers)
    assert response.status_code == 422

def test_upload_profile_photo(auth_headers):
    # Create a mock image file
    file_content = b"fake image content"
    file = io.BytesIO(file_content)
    
    response = client.post(
        "/api/v1/users/me/photo",
        files={"file": ("test.jpg", file, "image/jpeg")},
        headers=auth_headers
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Profile photo updated successfully"

def test_upload_profile_photo_no_file(auth_headers):
    response = client.post("/api/v1/users/me/photo", headers=auth_headers)
    assert response.status_code == 422

def test_update_preferences(auth_headers):
    preferences = {
        "max_distance": 50,
        "age_range": {"min": 18, "max": 35},
        "interested_in": ["female"],
        "show_me": True
    }
    response = client.put(
        "/api/v1/users/me/preferences",
        json=preferences,
        headers=auth_headers
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Preferences updated successfully"

def test_update_preferences_invalid_data(auth_headers):
    preferences = {
        "max_distance": -1  # Invalid distance
    }
    response = client.put(
        "/api/v1/users/me/preferences",
        json=preferences,
        headers=auth_headers
    )
    assert response.status_code == 422

def test_read_user(auth_headers):
    # First get our own user ID
    me_response = client.get("/api/v1/users/me", headers=auth_headers)
    user_id = me_response.json()["id"]
    
    response = client.get(f"/api/v1/users/{user_id}", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == user_id

def test_read_nonexistent_user(auth_headers):
    response = client.get("/api/v1/users/nonexistent-id", headers=auth_headers)
    assert response.status_code == 404
    assert response.json()["detail"] == "User not found" 