"""
Level 17: WebSockets
====================
Learn real-time bidirectional communication with WebSockets.

Concepts Covered:
    - WebSocket basics
    - Accepting connections
    - Sending and receiving messages
    - Connection management
    - Broadcasting to multiple clients
    - Chat room implementation
    - Handling disconnections
    - WebSocket with authentication

Run Command:
    uvicorn main:app --reload

Test:
    1. Open http://127.0.0.1:8000 in browser
    2. Or use the WebSocket endpoints at ws://127.0.0.1:8000/ws
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Query, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from typing import List, Dict, Optional
from datetime import datetime
import json

app = FastAPI(
    title="Task Manager API - Level 17",
    description="Learning WebSockets",
    version="17.0.0"
)


# ============================================================
# CONCEPT 1: Connection Manager
# ============================================================

class ConnectionManager:
    """
    Manages WebSocket connections
    
    Handles:
    - Active connections list
    - Adding/removing connections
    - Broadcasting messages
    - Room-based messaging
    """
    
    def __init__(self):
        # All active connections
        self.active_connections: List[WebSocket] = []
        
        # Connections by room/channel
        self.rooms: Dict[str, List[WebSocket]] = {}
        
        # User to connection mapping
        self.user_connections: Dict[str, WebSocket] = {}
    
    async def connect(self, websocket: WebSocket):
        """Accept and store a new connection"""
        await websocket.accept()
        self.active_connections.append(websocket)
    
    def disconnect(self, websocket: WebSocket):
        """Remove a connection"""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
    
    async def send_personal_message(self, message: str, websocket: WebSocket):
        """Send message to a specific client"""
        await websocket.send_text(message)
    
    async def broadcast(self, message: str):
        """Send message to ALL connected clients"""
        for connection in self.active_connections:
            await connection.send_text(message)
    
    # Room-based methods
    async def join_room(self, room: str, websocket: WebSocket):
        """Add connection to a room"""
        if room not in self.rooms:
            self.rooms[room] = []
        self.rooms[room].append(websocket)
    
    def leave_room(self, room: str, websocket: WebSocket):
        """Remove connection from a room"""
        if room in self.rooms and websocket in self.rooms[room]:
            self.rooms[room].remove(websocket)
            if not self.rooms[room]:
                del self.rooms[room]
    
    async def broadcast_to_room(self, room: str, message: str):
        """Send message to all clients in a room"""
        if room in self.rooms:
            for connection in self.rooms[room]:
                await connection.send_text(message)
    
    # User-based methods
    def register_user(self, username: str, websocket: WebSocket):
        """Register a user's connection"""
        self.user_connections[username] = websocket
    
    def unregister_user(self, username: str):
        """Unregister a user"""
        if username in self.user_connections:
            del self.user_connections[username]
    
    async def send_to_user(self, username: str, message: str):
        """Send message to a specific user"""
        if username in self.user_connections:
            await self.user_connections[username].send_text(message)


# Create global connection manager
manager = ConnectionManager()


# ============================================================
# CONCEPT 2: Basic WebSocket Endpoint
# ============================================================

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    Basic WebSocket endpoint
    
    - Accepts connection
    - Receives messages
    - Echoes them back
    - Handles disconnection
    
    Test with: wscat -c ws://localhost:8000/ws
    Or use the HTML page at http://localhost:8000
    """
    await manager.connect(websocket)
    
    try:
        while True:
            # Wait for message from client
            data = await websocket.receive_text()
            
            # Echo back to sender
            await manager.send_personal_message(
                f"You said: {data}",
                websocket
            )
            
            # Broadcast to all others
            await manager.broadcast(f"Someone said: {data}")
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast("A user disconnected")


# ============================================================
# CONCEPT 3: WebSocket with Path Parameter
# ============================================================

@app.websocket("/ws/{client_id}")
async def websocket_with_client_id(websocket: WebSocket, client_id: int):
    """
    WebSocket endpoint with path parameter
    
    Each client has a unique ID
    """
    await manager.connect(websocket)
    
    # Announce new connection
    await manager.broadcast(f"Client #{client_id} joined")
    
    try:
        while True:
            data = await websocket.receive_text()
            
            # Include client ID in messages
            message = f"Client #{client_id}: {data}"
            await manager.broadcast(message)
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast(f"Client #{client_id} left")


# ============================================================
# CONCEPT 4: Chat Room WebSocket
# ============================================================

@app.websocket("/ws/chat/{room}/{username}")
async def chat_room(
    websocket: WebSocket,
    room: str,
    username: str
):
    """
    Chat room WebSocket
    
    - Users join specific rooms
    - Messages only go to users in same room
    - Tracks usernames
    
    URL: ws://localhost:8000/ws/chat/{room}/{username}
    Example: ws://localhost:8000/ws/chat/general/john
    """
    await manager.connect(websocket)
    await manager.join_room(room, websocket)
    manager.register_user(username, websocket)
    
    # Announce join
    join_message = json.dumps({
        "type": "system",
        "message": f"{username} joined the room",
        "room": room,
        "timestamp": datetime.now().isoformat()
    })
    await manager.broadcast_to_room(room, join_message)
    
    try:
        while True:
            data = await websocket.receive_text()
            
            # Parse incoming message
            try:
                incoming = json.loads(data)
                message_text = incoming.get("message", data)
            except json.JSONDecodeError:
                message_text = data
            
            # Create chat message
            chat_message = json.dumps({
                "type": "message",
                "username": username,
                "message": message_text,
                "room": room,
                "timestamp": datetime.now().isoformat()
            })
            
            await manager.broadcast_to_room(room, chat_message)
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        manager.leave_room(room, websocket)
        manager.unregister_user(username)
        
        # Announce leave
        leave_message = json.dumps({
            "type": "system",
            "message": f"{username} left the room",
            "room": room,
            "timestamp": datetime.now().isoformat()
        })
        await manager.broadcast_to_room(room, leave_message)


# ============================================================
# CONCEPT 5: WebSocket with Query Parameters
# ============================================================

@app.websocket("/ws/auth")
async def websocket_with_auth(
    websocket: WebSocket,
    token: Optional[str] = Query(default=None)
):
    """
    WebSocket with authentication via query parameter
    
    URL: ws://localhost:8000/ws/auth?token=secret-token
    
    In production, validate JWT token here
    """
    # Validate token
    if token != "secret-token":
        await websocket.close(code=4001, reason="Invalid token")
        return
    
    await manager.connect(websocket)
    await manager.send_personal_message("Authenticated successfully!", websocket)
    
    try:
        while True:
            data = await websocket.receive_text()
            await manager.send_personal_message(f"Secure message: {data}", websocket)
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)


# ============================================================
# CONCEPT 6: JSON Message Protocol
# ============================================================

@app.websocket("/ws/json")
async def json_websocket(websocket: WebSocket):
    """
    WebSocket with JSON message protocol
    
    Expects messages like:
    {"action": "subscribe", "channel": "news"}
    {"action": "send", "channel": "news", "message": "Hello"}
    """
    await manager.connect(websocket)
    subscribed_channels: List[str] = []
    
    try:
        while True:
            data = await websocket.receive_json()
            
            action = data.get("action")
            
            if action == "subscribe":
                channel = data.get("channel")
                if channel:
                    subscribed_channels.append(channel)
                    await manager.join_room(channel, websocket)
                    await websocket.send_json({
                        "type": "subscribed",
                        "channel": channel
                    })
            
            elif action == "unsubscribe":
                channel = data.get("channel")
                if channel in subscribed_channels:
                    subscribed_channels.remove(channel)
                    manager.leave_room(channel, websocket)
                    await websocket.send_json({
                        "type": "unsubscribed",
                        "channel": channel
                    })
            
            elif action == "send":
                channel = data.get("channel")
                message = data.get("message")
                if channel and message:
                    broadcast_msg = json.dumps({
                        "type": "message",
                        "channel": channel,
                        "message": message,
                        "timestamp": datetime.now().isoformat()
                    })
                    await manager.broadcast_to_room(channel, broadcast_msg)
            
            elif action == "ping":
                await websocket.send_json({"type": "pong"})
            
            else:
                await websocket.send_json({
                    "type": "error",
                    "message": f"Unknown action: {action}"
                })
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        for channel in subscribed_channels:
            manager.leave_room(channel, websocket)


# ============================================================
# CONCEPT 7: Task Updates WebSocket
# ============================================================

# Simple task storage
tasks = {
    1: {"id": 1, "title": "Task 1", "status": "pending"},
    2: {"id": 2, "title": "Task 2", "status": "in_progress"},
}


@app.websocket("/ws/tasks")
async def task_updates(websocket: WebSocket):
    """
    Real-time task updates
    
    Clients receive updates when tasks change
    """
    await manager.connect(websocket)
    await manager.join_room("tasks", websocket)
    
    # Send current tasks on connect
    await websocket.send_json({
        "type": "initial",
        "tasks": list(tasks.values())
    })
    
    try:
        while True:
            data = await websocket.receive_json()
            
            action = data.get("action")
            
            if action == "update_status":
                task_id = data.get("task_id")
                new_status = data.get("status")
                
                if task_id in tasks:
                    tasks[task_id]["status"] = new_status
                    
                    # Broadcast update to all clients
                    update_msg = json.dumps({
                        "type": "task_updated",
                        "task": tasks[task_id]
                    })
                    await manager.broadcast_to_room("tasks", update_msg)
            
            elif action == "create":
                new_id = max(tasks.keys()) + 1
                tasks[new_id] = {
                    "id": new_id,
                    "title": data.get("title", f"Task {new_id}"),
                    "status": "pending"
                }
                
                create_msg = json.dumps({
                    "type": "task_created",
                    "task": tasks[new_id]
                })
                await manager.broadcast_to_room("tasks", create_msg)
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        manager.leave_room("tasks", websocket)


# ============================================================
# HTML Test Page
# ============================================================

@app.get("/", response_class=HTMLResponse)
async def get_test_page():
    """HTML page for testing WebSockets"""
    return """
<!DOCTYPE html>
<html>
<head>
    <title>WebSocket Test - Level 17</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; }
        h1 { color: #333; }
        .section { margin: 20px 0; padding: 20px; border: 1px solid #ddd; border-radius: 8px; }
        input, button { padding: 10px; margin: 5px; }
        input { width: 300px; }
        button { cursor: pointer; background: #007bff; color: white; border: none; border-radius: 4px; }
        button:hover { background: #0056b3; }
        #messages, #chatMessages { 
            height: 200px; overflow-y: auto; border: 1px solid #ccc; 
            padding: 10px; margin: 10px 0; background: #f9f9f9;
        }
        .message { padding: 5px 0; border-bottom: 1px solid #eee; }
        .system { color: #666; font-style: italic; }
        .status { padding: 5px 10px; border-radius: 4px; display: inline-block; }
        .connected { background: #d4edda; color: #155724; }
        .disconnected { background: #f8d7da; color: #721c24; }
    </style>
</head>
<body>
    <h1>🔌 Level 17: WebSocket Testing</h1>
    
    <!-- Basic WebSocket -->
    <div class="section">
        <h2>1. Basic WebSocket Echo</h2>
        <p>Status: <span id="status" class="status disconnected">Disconnected</span></p>
        <input type="text" id="messageInput" placeholder="Type a message...">
        <button onclick="sendMessage()">Send</button>
        <button onclick="connectWs()">Connect</button>
        <button onclick="disconnectWs()">Disconnect</button>
        <div id="messages"></div>
    </div>
    
    <!-- Chat Room -->
    <div class="section">
        <h2>2. Chat Room</h2>
        <p>Chat Status: <span id="chatStatus" class="status disconnected">Disconnected</span></p>
        <input type="text" id="username" placeholder="Username" value="user1">
        <input type="text" id="room" placeholder="Room" value="general">
        <button onclick="joinChat()">Join Room</button>
        <button onclick="leaveChat()">Leave</button>
        <br><br>
        <input type="text" id="chatInput" placeholder="Chat message...">
        <button onclick="sendChat()">Send</button>
        <div id="chatMessages"></div>
    </div>
    
    <!-- Connection Info -->
    <div class="section">
        <h2>3. WebSocket Endpoints</h2>
        <ul>
            <li><code>ws://localhost:8000/ws</code> - Basic echo</li>
            <li><code>ws://localhost:8000/ws/{client_id}</code> - With client ID</li>
            <li><code>ws://localhost:8000/ws/chat/{room}/{username}</code> - Chat room</li>
            <li><code>ws://localhost:8000/ws/auth?token=secret-token</code> - With auth</li>
            <li><code>ws://localhost:8000/ws/json</code> - JSON protocol</li>
            <li><code>ws://localhost:8000/ws/tasks</code> - Task updates</li>
        </ul>
    </div>

    <script>
        let ws = null;
        let chatWs = null;
        
        // Basic WebSocket
        function connectWs() {
            ws = new WebSocket("ws://localhost:8000/ws");
            
            ws.onopen = function() {
                document.getElementById("status").textContent = "Connected";
                document.getElementById("status").className = "status connected";
                addMessage("Connected to server", "system");
            };
            
            ws.onmessage = function(event) {
                addMessage(event.data);
            };
            
            ws.onclose = function() {
                document.getElementById("status").textContent = "Disconnected";
                document.getElementById("status").className = "status disconnected";
                addMessage("Disconnected from server", "system");
            };
        }
        
        function disconnectWs() {
            if (ws) ws.close();
        }
        
        function sendMessage() {
            const input = document.getElementById("messageInput");
            if (ws && input.value) {
                ws.send(input.value);
                input.value = "";
            }
        }
        
        function addMessage(msg, type = "") {
            const div = document.getElementById("messages");
            const p = document.createElement("p");
            p.className = "message " + type;
            p.textContent = msg;
            div.appendChild(p);
            div.scrollTop = div.scrollHeight;
        }
        
        // Chat Room
        function joinChat() {
            const username = document.getElementById("username").value;
            const room = document.getElementById("room").value;
            
            chatWs = new WebSocket(`ws://localhost:8000/ws/chat/${room}/${username}`);
            
            chatWs.onopen = function() {
                document.getElementById("chatStatus").textContent = "Connected to " + room;
                document.getElementById("chatStatus").className = "status connected";
            };
            
            chatWs.onmessage = function(event) {
                const data = JSON.parse(event.data);
                let msg = "";
                if (data.type === "system") {
                    msg = `[System] ${data.message}`;
                } else {
                    msg = `${data.username}: ${data.message}`;
                }
                addChatMessage(msg, data.type);
            };
            
            chatWs.onclose = function() {
                document.getElementById("chatStatus").textContent = "Disconnected";
                document.getElementById("chatStatus").className = "status disconnected";
            };
        }
        
        function leaveChat() {
            if (chatWs) chatWs.close();
        }
        
        function sendChat() {
            const input = document.getElementById("chatInput");
            if (chatWs && input.value) {
                chatWs.send(JSON.stringify({message: input.value}));
                input.value = "";
            }
        }
        
        function addChatMessage(msg, type = "") {
            const div = document.getElementById("chatMessages");
            const p = document.createElement("p");
            p.className = "message " + type;
            p.textContent = msg;
            div.appendChild(p);
            div.scrollTop = div.scrollHeight;
        }
        
        // Enter key handlers
        document.getElementById("messageInput").addEventListener("keypress", function(e) {
            if (e.key === "Enter") sendMessage();
        });
        document.getElementById("chatInput").addEventListener("keypress", function(e) {
            if (e.key === "Enter") sendChat();
        });
    </script>
</body>
</html>
    """


@app.get("/info")
def info():
    """API Information"""
    return {
        "message": "Level 17 - WebSockets",
        "concepts": [
            "WebSocket endpoint (@app.websocket)",
            "Connection manager",
            "Broadcasting messages",
            "Chat rooms",
            "JSON protocol",
            "Authentication with WebSockets"
        ],
        "endpoints": {
            "ws://localhost:8000/ws": "Basic echo",
            "ws://localhost:8000/ws/{id}": "With client ID",
            "ws://localhost:8000/ws/chat/{room}/{user}": "Chat room",
            "ws://localhost:8000/ws/auth?token=X": "Authenticated",
            "ws://localhost:8000/ws/json": "JSON protocol",
            "ws://localhost:8000/ws/tasks": "Task updates"
        },
        "test_page": "http://localhost:8000/"
    }
