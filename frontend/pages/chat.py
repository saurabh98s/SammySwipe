import streamlit as st
import requests
import json
from datetime import datetime
import websockets
import asyncio
import threading
from queue import Queue

# API Configuration
API_URL = "http://localhost:8000/api/v1"
WS_URL = "ws://localhost:8000/api/v1/ws"

def init_chat_state():
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "ws_queue" not in st.session_state:
        st.session_state.ws_queue = Queue()

async def connect_websocket(user_id: str, queue: Queue):
    uri = f"{WS_URL}/chat/{user_id}"
    async with websockets.connect(uri) as websocket:
        while True:
            try:
                # Check for outgoing messages
                if not queue.empty():
                    message = queue.get()
                    await websocket.send(json.dumps(message))
                
                # Check for incoming messages
                message = await websocket.recv()
                data = json.loads(message)
                st.session_state.messages.append(data)
                st.experimental_rerun()
                
            except websockets.exceptions.ConnectionClosed:
                break

def websocket_thread(user_id: str, queue: Queue):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(connect_websocket(user_id, queue))

def chat_page():
    st.title("SammySwipe - Chat")
    
    # Get matched users
    headers = {"Authorization": f"Bearer {st.session_state.token}"}
    response = requests.get(f"{API_URL}/matches/my-matches", headers=headers)
    
    if response.status_code == 200:
        matches = response.json()
        
        # Select user to chat with
        selected_user = st.selectbox(
            "Select a match to chat with",
            options=matches,
            format_func=lambda x: x["full_name"]
        )
        
        if selected_user:
            # Start WebSocket connection in a separate thread
            if "ws_thread" not in st.session_state:
                st.session_state.ws_thread = threading.Thread(
                    target=websocket_thread,
                    args=(st.session_state.user["id"], st.session_state.ws_queue),
                    daemon=True
                )
                st.session_state.ws_thread.start()
            
            # Get chat history
            response = requests.get(
                f"{API_URL}/chat/{selected_user['id']}/history",
                headers=headers
            )
            
            if response.status_code == 200:
                messages = response.json()
                
                # Display messages
                for msg in messages:
                    is_user = msg["sender_id"] == st.session_state.user["id"]
                    
                    with st.container():
                        if is_user:
                            st.write(f"You: {msg['content']}")
                        else:
                            st.write(f"{selected_user['full_name']}: {msg['content']}")
                        
                        st.caption(
                            f"Sent at: {datetime.fromisoformat(msg['sent_at']).strftime('%Y-%m-%d %H:%M:%S')}"
                        )
                
                # Send message
                with st.form("chat_form"):
                    message = st.text_input("Type your message")
                    send = st.form_submit_button("Send")
                    
                    if send and message:
                        # Add message to queue for WebSocket
                        st.session_state.ws_queue.put({
                            "receiver_id": selected_user["id"],
                            "content": message
                        })
                        
                        # Clear input
                        st.experimental_rerun()
    else:
        st.info("You don't have any matches yet. Start swiping to find matches!")

def main():
    init_chat_state()
    chat_page()

if __name__ == "__main__":
    main() 