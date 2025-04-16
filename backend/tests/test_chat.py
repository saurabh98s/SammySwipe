import pytest
from fastapi.testclient import TestClient
from fastapi.websockets import WebSocket
from ..main import app
import json
import asyncio

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
def matched_user_id(auth_headers):
    # Get a matched user
    response = client.get("/api/v1/matches/my-matches", headers=auth_headers)
    if response.status_code == 200 and len(response.json()) > 0:
        return response.json()[0]["id"]
    
    # If no matches exist, create one
    response = client.get("/api/v1/matches/recommendations", headers=auth_headers)
    if response.status_code == 200 and len(response.json()) > 0:
        user_to_match = response.json()[0]
        client.post(
            f"/api/v1/matches/{user_to_match['id']}",
            headers=auth_headers
        )
        client.put(
            f"/api/v1/matches/{user_to_match['id']}/accept",
            headers=auth_headers
        )
        return user_to_match["id"]
    
    return None

def test_get_chat_history_matched_user(auth_headers, matched_user_id):
    if matched_user_id:
        response = client.get(f"/api/v1/chat/{matched_user_id}/history", headers=auth_headers)
        assert response.status_code == 200
        messages = response.json()
        assert isinstance(messages, list)
        if len(messages) > 0:
            assert "sender_id" in messages[0]
            assert "content" in messages[0]
            assert "sent_at" in messages[0]
            assert "read" in messages[0]

def test_get_chat_history_unmatched_user(auth_headers):
    response = client.get("/api/v1/chat/unmatched-user-id/history", headers=auth_headers)
    assert response.status_code == 403
    assert response.json()["detail"] == "You can only chat with matched users"

def test_mark_messages_as_read(auth_headers, matched_user_id):
    if matched_user_id:
        response = client.put(
            f"/api/v1/chat/{matched_user_id}/mark-read",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "messages_marked_read" in data
        assert isinstance(data["messages_marked_read"], int)

def test_websocket_chat():
    with client.websocket_connect(f"/api/v1/ws/chat/test-user-1") as websocket1:
        with client.websocket_connect(f"/api/v1/ws/chat/test-user-2") as websocket2:
            # Send message from user 1 to user 2
            message = {
                "receiver_id": "test-user-2",
                "content": "Hello, user 2!"
            }
            websocket1.send_text(json.dumps(message))
            
            # Receive message on user 2's connection
            data = websocket2.receive_text()
            received_message = json.loads(data)
            assert received_message["content"] == "Hello, user 2!"
            assert received_message["receiver_id"] == "test-user-2"

def test_websocket_disconnect():
    with client.websocket_connect(f"/api/v1/ws/chat/test-user") as websocket:
        # Test successful connection
        assert websocket.client.application.state.active_connections["test-user"]
        
    # Test disconnection (context manager handles the disconnect)
    assert "test-user" not in websocket.client.application.state.active_connections

@pytest.mark.asyncio
async def test_websocket_multiple_messages():
    async with client.websocket_connect(f"/api/v1/ws/chat/sender") as websocket1:
        async with client.websocket_connect(f"/api/v1/ws/chat/receiver") as websocket2:
            # Send multiple messages
            messages = [
                {"receiver_id": "receiver", "content": f"Message {i}"}
                for i in range(3)
            ]
            
            for message in messages:
                await websocket1.send_text(json.dumps(message))
                
                # Verify each message is received
                data = await websocket2.receive_text()
                received = json.loads(data)
                assert received["content"] == message["content"]
                assert received["receiver_id"] == "receiver" 