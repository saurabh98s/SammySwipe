import pytest
from fastapi.testclient import TestClient
from datetime import date
from backend.main import app

client = TestClient(app)

def test_register_success():
    user_data = {
        "email": "test@example.com",
        "username": "testuser",
        "password": "strongpassword123",
        "full_name": "Test User",
        "gender": "male",
        "birth_date": str(date(1990, 1, 1)),
        "bio": "Test bio",
        "interests": ["reading", "coding"],
        "location": "Test City",
        "profile_photo": "test_photo.jpg"
    }
    response = client.post("/api/v1/auth/register", json=user_data)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == user_data["email"]
    assert data["username"] == user_data["username"]
    assert "hashed_password" not in data

def test_register_existing_user():
    user_data = {
        "email": "test@example.com",
        "username": "testuser2",
        "password": "strongpassword123",
        "full_name": "Test User",
        "gender": "male",
        "birth_date": str(date(1990, 1, 1)),
        "bio": "Test bio",
        "interests": ["reading", "coding"],
        "location": "Test City",
        "profile_photo": "test_photo.jpg"
    }
    response = client.post("/api/v1/auth/register", json=user_data)
    assert response.status_code == 400
    assert response.json()["detail"] == "User with this email already exists"

def test_register_invalid_data():
    user_data = {
        "email": "invalid-email",
        "username": "testuser",
        "password": "weak"
    }
    response = client.post("/api/v1/auth/register", json=user_data)
    assert response.status_code == 422

def test_login_success():
    login_data = {
        "username": "test@example.com",
        "password": "strongpassword123"
    }
    response = client.post("/api/v1/auth/token", data=login_data)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_invalid_credentials():
    login_data = {
        "username": "test@example.com",
        "password": "wrongpassword"
    }
    response = client.post("/api/v1/auth/token", data=login_data)
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect email or password"

def test_login_nonexistent_user():
    login_data = {
        "username": "nonexistent@example.com",
        "password": "password123"
    }
    response = client.post("/api/v1/auth/token", data=login_data)
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect email or password" 