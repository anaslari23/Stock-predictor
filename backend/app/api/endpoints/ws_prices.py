"""
WebSocket Prices Endpoint - Real-time price streaming
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from loguru import logger
import asyncio
import json
from datetime import datetime
from app.services.price_service import PriceService

router = APIRouter()
price_service = PriceService()

class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[WebSocket, dict] = {}
        logger.info("WebSocket ConnectionManager initialized")

    async def connect(self, websocket: WebSocket, symbol: str):
        """Accept WebSocket connection and store symbol"""
        await websocket.accept()
        self.active_connections[websocket] = {
            'symbol': symbol,
            'last_heartbeat': datetime.now()
        }
        logger.info(f"WebSocket connected for {symbol}. Total connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        """Remove WebSocket connection"""
        if websocket in self.active_connections:
            symbol = self.active_connections[websocket]['symbol']
            del self.active_connections[websocket]
            logger.info(f"WebSocket disconnected for {symbol}. Total connections: {len(self.active_connections)}")

    async def send_message(self, websocket: WebSocket, message: dict):
        """Send JSON message to client"""
        try:
            await websocket.send_json(message)
        except Exception as e:
            logger.error(f"Error sending message: {str(e)}")
            self.disconnect(websocket)

    async def send_heartbeat(self, websocket: WebSocket):
        """Send heartbeat ping"""
        try:
            await websocket.send_json({
                'type': 'heartbeat',
                'timestamp': datetime.now().isoformat()
            })
            self.active_connections[websocket]['last_heartbeat'] = datetime.now()
        except Exception as e:
            logger.error(f"Heartbeat failed: {str(e)}")
            self.disconnect(websocket)

manager = ConnectionManager()

@router.websocket("/prices")
async def websocket_prices(websocket: WebSocket):
    """
    WebSocket endpoint for real-time price streaming
    
    **Client sends:**
    ```json
    {"symbol": "TCS.NS"}
    ```
    
    **Server sends every 2 seconds:**
    ```json
    {
        "type": "price_update",
        "symbol": "TCS.NS",
        "price": 3841.60,
        "change": 25.30,
        "changePercent": 1.42,
        "timestamp": "2025-01-20T15:30:00"
    }
    ```
    
    **Heartbeat (every 30 seconds):**
    ```json
    {
        "type": "heartbeat",
        "timestamp": "2025-01-20T15:30:00"
    }
    ```
    
    **Features:**
    - Real-time price updates every 2 seconds
    - Automatic heartbeat every 30 seconds
    - Graceful reconnection support
    - Error handling with disconnect
    """
    
    symbol = None
    
    try:
        # Wait for initial message with symbol
        data = await websocket.receive_json()
        symbol = data.get('symbol')
        
        if not symbol:
            await websocket.send_json({
                'type': 'error',
                'message': 'Symbol is required'
            })
            await websocket.close()
            return
        
        # Connect and store symbol
        await manager.connect(websocket, symbol)
        
        # Send initial connection confirmation
        await websocket.send_json({
            'type': 'connected',
            'symbol': symbol,
            'message': f'Connected to price stream for {symbol}',
            'timestamp': datetime.now().isoformat()
        })
        
        # Start price streaming and heartbeat tasks
        price_task = asyncio.create_task(stream_prices(websocket, symbol))
        heartbeat_task = asyncio.create_task(send_heartbeats(websocket))
        
        # Wait for client messages (for reconnect or symbol change)
        try:
            while True:
                data = await websocket.receive_json()
                
                # Handle symbol change
                if 'symbol' in data:
                    new_symbol = data['symbol']
                    logger.info(f"Symbol changed from {symbol} to {new_symbol}")
                    symbol = new_symbol
                    manager.active_connections[websocket]['symbol'] = new_symbol
                    
                    # Cancel and restart price task with new symbol
                    price_task.cancel()
                    price_task = asyncio.create_task(stream_prices(websocket, new_symbol))
                    
                    await websocket.send_json({
                        'type': 'symbol_changed',
                        'symbol': new_symbol,
                        'timestamp': datetime.now().isoformat()
                    })
                
        except WebSocketDisconnect:
            logger.info(f"Client disconnected for {symbol}")
        finally:
            # Cancel tasks
            price_task.cancel()
            heartbeat_task.cancel()
            manager.disconnect(websocket)
            
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected during handshake")
        if symbol:
            manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}", exc_info=True)
        if symbol:
            manager.disconnect(websocket)
        try:
            await websocket.send_json({
                'type': 'error',
                'message': str(e),
                'timestamp': datetime.now().isoformat()
            })
        except:
            pass

# Global Kite Ticker Service instance (lazy loaded)
kite_ticker_service = None

async def get_kite_ticker_service():
    global kite_ticker_service
    if kite_ticker_service is None:
        from app.services.kite_ticker_service import KiteTickerService
        kite_ticker_service = KiteTickerService()
        # Start connection in background if token exists
        if kite_ticker_service.access_token:
            kite_ticker_service.connect(threaded=True)
    return kite_ticker_service

async def stream_prices(websocket: WebSocket, symbol: str):
    """
    Stream price updates every 2 seconds (or real-time with Kite)
    """
    try:
        # Try to use Kite Ticker first
        kite_service = await get_kite_ticker_service()
        
        if kite_service and kite_service.is_connected:
            # TODO: Implement real-time subscription logic here
            # For now, we'll stick to the polling fallback but log that Kite is available
            logger.info(f"Kite Ticker connected, but using polling fallback for {symbol} (Implementation pending)")
            
        while True:
            # Get current price
            price_data = await price_service.get_price(symbol)
            
            # Send update
            await manager.send_message(websocket, {
                'type': 'price_update',
                'symbol': price_data['symbol'],
                'price': price_data['lastPrice'],
                'change': price_data['change'],
                'changePercent': price_data['changePercent'],
                'timestamp': price_data['timestamp'],
                'source': price_data['source']
            })
            
            # Wait 2 seconds
            await asyncio.sleep(2)
            
    except asyncio.CancelledError:
        logger.info(f"Price streaming cancelled for {symbol}")
    except Exception as e:
        logger.error(f"Error streaming prices for {symbol}: {str(e)}")

async def send_heartbeats(websocket: WebSocket):
    """
    Send heartbeat every 30 seconds
    """
    try:
        while True:
            await asyncio.sleep(30)
            await manager.send_heartbeat(websocket)
            
    except asyncio.CancelledError:
        logger.info("Heartbeat task cancelled")
    except Exception as e:
        logger.error(f"Heartbeat error: {str(e)}")
