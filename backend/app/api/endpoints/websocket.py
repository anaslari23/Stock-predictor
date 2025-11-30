"""
WebSocket Endpoint for Real-time Price Streaming
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from loguru import logger
import asyncio
import json

router = APIRouter()

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket connected. Total connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        logger.info(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                pass

manager = ConnectionManager()

@router.websocket("/prices")
async def websocket_prices(websocket: WebSocket, symbol: str = "NIFTY50"):
    """
    WebSocket endpoint for real-time price streaming
    """
    await manager.connect(websocket)
    try:
        while True:
            # Simulate price updates (replace with real data source)
            import random
            price = 22000 + random.uniform(-100, 100)
            
            message = json.dumps({
                "symbol": symbol,
                "price": round(price, 2),
                "timestamp": asyncio.get_event_loop().time()
            })
            
            await manager.send_personal_message(message, websocket)
            await asyncio.sleep(2)  # Update every 2 seconds
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
        manager.disconnect(websocket)
