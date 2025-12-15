# Level 17: WebSockets

## Learning Objectives
- Understand WebSocket vs HTTP
- Create WebSocket endpoints
- Manage connections
- Broadcast messages
- Implement chat rooms
- Handle disconnections
- Use JSON protocols
- Authenticate WebSocket connections

---

## Setup Instructions

```bash
cd level_17_websockets
pip install -r requirements.txt
uvicorn main:app --reload
```

**Test:** Open http://localhost:8000 in browser for interactive test page.

---

## WebSocket vs HTTP

| HTTP | WebSocket |
|------|-----------|
| Request-Response | Bidirectional |
| Client initiates | Either can send |
| Connection closes | Stays open |
| Polling for updates | Real-time push |
| Good for CRUD | Good for live data |

---

## Key Concepts

### 1. Basic WebSocket Endpoint
```python
from fastapi import WebSocket

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    # Accept connection
    await websocket.accept()
    
    while True:
        # Receive message
        data = await websocket.receive_text()
        
        # Send response
        await websocket.send_text(f"Echo: {data}")
```

### 2. Handling Disconnection
```python
from fastapi import WebSocketDisconnect

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"Echo: {data}")
    except WebSocketDisconnect:
        print("Client disconnected")
```

### 3. Connection Manager
```python
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
    
    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()
```

### 4. WebSocket with Path Parameters
```python
@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int):
    await manager.connect(websocket)
    await manager.broadcast(f"Client {client_id} joined")
    
    try:
        while True:
            data = await websocket.receive_text()
            await manager.broadcast(f"Client {client_id}: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
```

### 5. WebSocket with Query Parameters
```python
@app.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    token: str = Query(...)
):
    if token != "valid-token":
        await websocket.close(code=4001)
        return
    
    await websocket.accept()
    # ... handle messages
```

### 6. JSON Messages
```python
@app.websocket("/ws/json")
async def json_websocket(websocket: WebSocket):
    await websocket.accept()
    
    while True:
        # Receive JSON
        data = await websocket.receive_json()
        
        # Send JSON
        await websocket.send_json({
            "type": "response",
            "data": data
        })
```

### 7. Chat Room Pattern
```python
class ConnectionManager:
    def __init__(self):
        self.rooms: Dict[str, List[WebSocket]] = {}
    
    async def join_room(self, room: str, websocket: WebSocket):
        if room not in self.rooms:
            self.rooms[room] = []
        self.rooms[room].append(websocket)
    
    async def broadcast_to_room(self, room: str, message: str):
        if room in self.rooms:
            for connection in self.rooms[room]:
                await connection.send_text(message)
```

---

## WebSocket Endpoints

| Endpoint | Description |
|----------|-------------|
| `ws://localhost:8000/ws` | Basic echo |
| `ws://localhost:8000/ws/{client_id}` | With client ID |
| `ws://localhost:8000/ws/chat/{room}/{username}` | Chat room |
| `ws://localhost:8000/ws/auth?token=secret-token` | Authenticated |
| `ws://localhost:8000/ws/json` | JSON protocol |
| `ws://localhost:8000/ws/tasks` | Task updates |

---

## Testing WebSockets

### Option 1: Browser Console
```javascript
// Connect
const ws = new WebSocket("ws://localhost:8000/ws");

// Handle messages
ws.onmessage = (event) => console.log(event.data);

// Send message
ws.send("Hello!");

// Close
ws.close();
```

### Option 2: wscat (CLI)
```bash
# Install
npm install -g wscat

# Connect
wscat -c ws://localhost:8000/ws

# Type messages and press Enter
```

### Option 3: Python Client
```python
import asyncio
import websockets

async def test():
    async with websockets.connect("ws://localhost:8000/ws") as ws:
        await ws.send("Hello!")
        response = await ws.recv()
        print(response)

asyncio.run(test())
```

### Option 4: Test Page
Open http://localhost:8000 in your browser!

---

## Message Patterns

### Simple Text
```
Client: Hello
Server: Echo: Hello
```

### JSON Protocol
```json
// Client sends:
{"action": "subscribe", "channel": "news"}

// Server responds:
{"type": "subscribed", "channel": "news"}

// Client sends:
{"action": "send", "channel": "news", "message": "Hello"}

// All subscribers receive:
{"type": "message", "channel": "news", "message": "Hello"}
```

---

## Close Codes

| Code | Meaning |
|------|---------|
| 1000 | Normal closure |
| 1001 | Going away |
| 1002 | Protocol error |
| 1003 | Unsupported data |
| 1008 | Policy violation |
| 4001+ | Application-specific |

```python
await websocket.close(code=4001, reason="Invalid token")
```

---

## Connection Manager Methods

```python
# Basic
await manager.connect(websocket)
manager.disconnect(websocket)
await manager.send_personal_message(msg, websocket)
await manager.broadcast(msg)

# Room-based
await manager.join_room(room, websocket)
manager.leave_room(room, websocket)
await manager.broadcast_to_room(room, msg)

# User-based
manager.register_user(username, websocket)
manager.unregister_user(username)
await manager.send_to_user(username, msg)
```

---

## Exercises

### Exercise 1: Private Messaging
Extend the chat room to support private messages:
- `/pm username message` sends to specific user
- Only sender and recipient see the message

### Exercise 2: Typing Indicator
Add "user is typing..." feature:
- Send typing status when user starts typing
- Clear after 3 seconds of inactivity

### Exercise 3: Online Users List
- Track online users per room
- Broadcast updated list when users join/leave

### Exercise 4: Message History
- Store last 50 messages per room
- Send history to new users on join

---

## Best Practices

1. **Always handle disconnections** - Use try/except WebSocketDisconnect
2. **Use connection manager** - Don't store connections in global list
3. **Validate input** - Check message format before processing
4. **Authenticate early** - Reject invalid connections immediately
5. **Use JSON for complex data** - Easier to parse and extend
6. **Implement heartbeat** - Detect dead connections

---

## Common Issues

| Issue | Solution |
|-------|----------|
| Connection refused | Check server is running |
| Connection closes immediately | Check authentication |
| Messages not received | Check broadcast logic |
| Memory leak | Remove disconnected clients |

---

## What's Next?
**Level 18: Lifespan Events** - Learn application startup and shutdown events.
