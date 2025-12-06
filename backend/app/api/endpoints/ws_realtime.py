"""
WebSocket endpoint for streaming real-time prices to Flutter app
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Set
import asyncio
import json
from loguru import logger
from app.services.nse_realtime_service import get_realtime_service

router = APIRouter()

# Track active WebSocket connections
active_connections: Set[WebSocket] = set()


@router.websocket("/ws/prices")
async def websocket_prices(websocket: WebSocket):
    """
    WebSocket endpoint for streaming real-time prices
    Client sends: {"action": "subscribe", "symbols": ["TCS", "RELIANCE"]}
    Server sends: {"symbol": "TCS", "lastPrice": 3180.5, ...}
    """
    await websocket.accept()
    active_connections.add(websocket)
    
    subscribed_symbols: Set[str] = set()
    realtime_service = get_realtime_service()
    
    logger.info(f"WebSocket client connected. Total connections: {len(active_connections)}")
    
    try:
        # Start the real-time service if not already running
        if not realtime_service.is_running:
            await realtime_service.start()
        
        # Send initial connection success message
        await websocket.send_json({
            "type": "connected",
            "message": "Real-time price stream connected"
        })
        
        # Handle incoming messages and stream prices
        while True:
            try:
                # Check for incoming messages (non-blocking)
                message = await asyncio.wait_for(
                    websocket.receive_text(),
                    timeout=0.5
                )
                
                # Parse subscription request
                try:
                    data = json.loads(message)
                    action = data.get('action')
                    symbols = data.get('symbols', [])
                    
                    if action == 'subscribe':
                        for symbol in symbols:
                            clean_symbol = symbol.replace('.NS', '').upper()
                            subscribed_symbols.add(clean_symbol)
                            realtime_service.subscribe(clean_symbol)
                        
                        await websocket.send_json({
                            "type": "subscribed",
                            "symbols": list(subscribed_symbols)
                        })
                        logger.info(f"Client subscribed to: {symbols}")
                    
                    elif action == 'unsubscribe':
                        for symbol in symbols:
                            clean_symbol = symbol.replace('.NS', '').upper()
                            subscribed_symbols.discard(clean_symbol)
                            realtime_service.unsubscribe(clean_symbol)
                        
                        await websocket.send_json({
                            "type": "unsubscribed",
                            "symbols": symbols
                        })
                
                except json.JSONDecodeError:
                    await websocket.send_json({
                        "type": "error",
                        "message": "Invalid JSON"
                    })
            
            except asyncio.TimeoutError:
                # No message received, send price updates
                if subscribed_symbols:
                    updates = []
                    for symbol in subscribed_symbols:
                        price_data = realtime_service.get_latest_price(symbol)
                        if price_data:
                            updates.append(price_data)
                    
                    if updates:
                        await websocket.send_json({
                            "type": "price_update",
                            "data": updates
                        })
    
    except WebSocketDisconnect:
        logger.info("WebSocket client disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        # Cleanup
        active_connections.discard(websocket)
        for symbol in subscribed_symbols:
            realtime_service.unsubscribe(symbol)
        
        logger.info(f"WebSocket client cleaned up. Remaining connections: {len(active_connections)}")
        
        # Stop service if no more connections
        if not active_connections and realtime_service.is_running:
            await realtime_service.stop()


@router.get("/ws/status")
async def websocket_status():
    """Get WebSocket service status"""
    realtime_service = get_realtime_service()
    return {
        "active_connections": len(active_connections),
        "service_running": realtime_service.is_running,
        "subscribed_symbols": list(realtime_service.subscribed_symbols),
        "cached_prices": len(realtime_service.latest_prices)
    }
