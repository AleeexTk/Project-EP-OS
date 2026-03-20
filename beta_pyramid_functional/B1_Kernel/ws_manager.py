import asyncio
import logging
from typing import List
from fastapi import WebSocket

logger = logging.getLogger("ws_manager")

class ConnectionManager:
    """Unified WebSocket Connection Manager for EvoPyramid API endpoints."""
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.debug(f"Client connected. Active: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            logger.debug(f"Client disconnected. Active: {len(self.active_connections)}")

    async def broadcast(self, message: dict):
        """Send JSON message to all active connected clients."""
        for connection in list(self.active_connections):
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.warning(f"Failed to broadcast to client: {e}")
                if connection in self.active_connections:
                    self.active_connections.remove(connection)

# Global singleton
manager = ConnectionManager()
