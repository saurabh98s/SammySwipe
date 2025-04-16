import pytest
from fastapi.testclient import TestClient
from ..main import app
from ..db.database import db
from ..core.config import get_settings
import os
import tempfile
import uuid

@pytest.fixture(scope="session")
def test_db():
    """Create a test database connection."""
    # Use the Neo4j instance running in Docker
    settings = get_settings()
    settings.NEO4J_URI = "bolt://neo4j:7687"
    settings.NEO4J_USER = "neo4j"
    settings.NEO4J_PASSWORD = "sammy_swipe_secret"
    
    yield db

@pytest.fixture(scope="session")
def test_client():
    """Create a test client."""
    return TestClient(app)

@pytest.fixture(scope="session")
def temp_media_dir():
    """Create a temporary directory for media files."""
    with tempfile.TemporaryDirectory() as temp_dir:
        settings = get_settings()
        settings.MEDIA_DIR = temp_dir
        yield temp_dir

@pytest.fixture(autouse=True)
def setup_test_environment(temp_media_dir):
    """Setup test environment before each test."""
    # Set environment variables for testing
    os.environ["TESTING"] = "1"
    os.environ["MEDIA_DIR"] = temp_media_dir
    os.environ["NEO4J_URI"] = "bolt://neo4j:7687"
    os.environ["NEO4J_USER"] = "neo4j"
    os.environ["NEO4J_PASSWORD"] = "sammy_swipe_secret"
    
    yield
    
    # Clean up environment variables
    os.environ.pop("TESTING", None)
    os.environ.pop("MEDIA_DIR", None)

@pytest.fixture
def test_user(test_db):
    """Create a test user with a unique email."""
    unique_id = str(uuid.uuid4())
    email = f"test_{unique_id}@example.com"
    username = f"testuser_{unique_id}"
    
    query = """
    CREATE (u:User {
        id: $id,
        email: $email,
        username: $username,
        full_name: 'Test User',
        hashed_password: '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LHHWxNHGRI.3.9Fk.',  # password: strongpassword123
        gender: 'male',
        birth_date: date('1990-01-01'),
        bio: 'Test bio',
        interests: ['reading', 'coding'],
        location: 'Test City',
        profile_photo: 'test_photo.jpg',
        created_at: datetime(),
        updated_at: datetime(),
        is_active: true,
        is_verified: true
    })
    RETURN u
    """
    result = test_db.execute_query(
        query,
        {
            "id": f"test-user-{unique_id}",
            "email": email,
            "username": username
        }
    )
    user_data = result[0]["u"]
    yield user_data
    
    # Clean up test user
    test_db.execute_query(
        "MATCH (u:User {id: $id}) DETACH DELETE u",
        {"id": user_data["id"]}
    )

@pytest.fixture
def test_user_token(test_client, test_user):
    """Get authentication token for test user."""
    response = test_client.post(
        "/api/v1/auth/token",
        data={
            "username": test_user["email"],
            "password": "strongpassword123"
        }
    )
    return response.json()["access_token"]

@pytest.fixture
def auth_headers(test_user_token):
    """Get authentication headers for test user."""
    return {"Authorization": f"Bearer {test_user_token}"} 