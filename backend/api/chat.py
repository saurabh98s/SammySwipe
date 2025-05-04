from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect, Body
from typing import Any, List, Dict
from ..models.user import UserInDB
from ..services.auth import get_current_active_user
from ..db.database import db
from datetime import datetime, timedelta
import json
import random
from pydantic import BaseModel

router = APIRouter()

# Store active websocket connections
active_connections: Dict[str, WebSocket] = {}

class MessageContent(BaseModel):
    content: str

@router.websocket("/ws/chat/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    await websocket.accept()
    active_connections[user_id] = websocket
    
    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            # Store message in database
            query = """
            MATCH (sender:User {id: $sender_id}), (receiver:User {id: $receiver_id})
            CREATE (sender)-[r:SENT {
                content: $content,
                sent_at: datetime(),
                read: false
            }]->(receiver)
            RETURN r
            """
            
            db.execute_query(
                query,
                {
                    "sender_id": user_id,
                    "receiver_id": message_data["receiver_id"],
                    "content": message_data["content"]
                }
            )
            
            # Send message to receiver if online
            if message_data["receiver_id"] in active_connections:
                receiver_ws = active_connections[message_data["receiver_id"]]
                await receiver_ws.send_text(data)
                
    except WebSocketDisconnect:
        del active_connections[user_id]

@router.get("/chat/{user_id}/history")
async def get_chat_history(
    user_id: str,
    current_user: UserInDB = Depends(get_current_active_user),
) -> Any:
    # Verify users are matched
    query = """
    MATCH (u1:User {id: $current_user_id})-[r:MATCHED]-(u2:User {id: $user_id})
    WHERE r.status = 'accepted'
    RETURN r
    """
    
    result = db.execute_query(
        query,
        {
            "current_user_id": current_user.id,
            "user_id": user_id
        }
    )
    
    if not result:
        raise HTTPException(
            status_code=403,
            detail="You can only chat with matched users"
        )
    
    # Get chat history
    query = """
    MATCH (sender:User)-[r:SENT]->(receiver:User)
    WHERE (sender.id = $user1_id AND receiver.id = $user2_id)
    OR (sender.id = $user2_id AND receiver.id = $user1_id)
    RETURN sender.id as sender_id, r.content as content, r.sent_at as sent_at, r.read as read
    ORDER BY r.sent_at DESC
    LIMIT 100
    """
    
    messages = db.execute_query(
        query,
        {
            "user1_id": current_user.id,
            "user2_id": user_id
        }
    )
    
    return messages

@router.put("/chat/{user_id}/mark-read")
async def mark_messages_as_read(
    user_id: str,
    current_user: UserInDB = Depends(get_current_active_user),
) -> Any:
    query = """
    MATCH (sender:User {id: $sender_id})-[r:SENT]->(receiver:User {id: $receiver_id})
    WHERE r.read = false
    SET r.read = true, r.read_at = datetime()
    RETURN count(r) as updated
    """
    
    result = db.execute_query(
        query,
        {
            "sender_id": user_id,
            "receiver_id": current_user.id
        }
    )
    
    return {"messages_marked_read": result[0]["updated"]}

@router.get("/{user_id}/history", tags=["chat"])
async def get_chat_history(user_id: str, current_user: UserInDB = Depends(get_current_active_user)) -> List[Dict[str, Any]]:
    """
    Get chat history with a specific user
    """
    # This would normally query the database for chat history
    # For demonstration, we'll generate some sample data
    
    # Generate timestamps over the last 2 days
    now = datetime.now()
    timestamps = []
    for i in range(random.randint(3, 15)):
        hours_ago = random.randint(1, 48)
        timestamps.append(now - timedelta(hours=hours_ago))
    
    # Sort chronologically
    timestamps.sort()
    
    # Sample message content
    sample_messages = [
        "Hey there!",
        "How's it going?",
        "Nice to match with you!",
        "What are your plans for the weekend?",
        "Have you seen that new movie?",
        "I love your profile pic!",
        "What kind of music do you like?",
        "Do you enjoy traveling?",
        "What's your favorite food?",
        "I'm really enjoying our conversation!",
        "Would you like to grab coffee sometime?",
        "That's interesting!",
        "Tell me more about yourself",
        "I'm a big fan of hiking too!"
    ]
    
    messages = []
    for i, timestamp in enumerate(timestamps):
        sender_id = user_id if random.random() > 0.5 else current_user.id
        messages.append({
            "id": f"msg_{i}",
            "sender_id": sender_id,
            "content": random.choice(sample_messages),
            "timestamp": timestamp.isoformat(),
            "is_read": True if timestamp < now - timedelta(hours=1) else False
        })
    
    return messages

@router.post("/{user_id}", tags=["chat"])
async def send_message(
    user_id: str, 
    message: MessageContent, 
    current_user: UserInDB = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """
    Send a message to a specific user
    """
    # This would normally save the message to the database
    # For demonstration, we'll just echo back the message
    
    return {
        "id": f"msg_{random.randint(1000, 9999)}",
        "sender_id": current_user.id,
        "content": message.content,
        "timestamp": datetime.now().isoformat(),
        "is_read": False
    } 