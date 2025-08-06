from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import json
import asyncio
from typing import List, Dict, Any
import logging
from agents.chat_agent import ChatAgent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="LangGraph Chat Application", version="1.0.0")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"Client connected. Total connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        logger.info(f"Client disconnected. Total connections: {len(self.active_connections)}")

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception as e:
                logger.error(f"Error broadcasting message: {e}")

manager = ConnectionManager()

@app.get("/", response_class=HTMLResponse)
async def get_chat_page():
    with open("static/index.html", "r") as f:
        return HTMLResponse(content=f.read())

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            # Initialize chat agent
            chat_agent = ChatAgent(client_id=client_id)

            # Process message through chat agent
            response = await chat_agent.process_message(
                message_data.get("message", ""),
                client_id
            )
            
            # Send response back to client with interactive support
            response_data = {
                "type": "response",
                "message": response["message"],
                "tools_used": response.get("tools_used", []),
                "timestamp": response.get("timestamp"),
                "interactive": response.get("interactive", False)
            }
            
            # Add interactive-specific fields
            if response.get("interactive"):
                response_data.update({
                    "tool_execution": response.get("tool_execution", [])
                })
            
            await manager.send_personal_message(
                json.dumps(response_data),
                websocket
            )
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)

@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "Chat application is running"}

@app.get("/tools")
async def get_tools():
    """Get information about available tools"""
    return {
        "tools": chat_agent.get_tools_info(),
        "agent_name": chat_agent.name
    }

@app.post("/clear-history/{client_id}")
async def clear_conversation_history(client_id: str):
    """Clear conversation history for a specific client"""
    chat_agent.clear_conversation_history(client_id)
    return {"message": "Conversation history cleared"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=443, 
        ssl_keyfile="key.pem", 
        ssl_certfile="cert.pem"
    ) 