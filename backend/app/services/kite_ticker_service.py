"""
Kite Ticker Service - Real-time WebSocket Data
"""

from kiteconnect import KiteTicker
from app.core.config import settings
from loguru import logger
import asyncio
import json
from typing import Dict, List, Callable, Optional

class KiteTickerService:
    def __init__(self):
        self.api_key = settings.KITE_API_KEY
        self.access_token = settings.KITE_ACCESS_TOKEN
        self.kws: Optional[KiteTicker] = None
        self.subscribed_tokens: List[int] = []
        self.callbacks: List[Callable] = []
        self.is_connected = False
        
    def initialize(self):
        """Initialize KiteTicker connection"""
        if not self.access_token:
            logger.warning("Cannot initialize KiteTicker: No access token")
            return

        self.kws = KiteTicker(self.api_key, self.access_token)
        
        # Assign callbacks
        self.kws.on_ticks = self._on_ticks
        self.kws.on_connect = self._on_connect
        self.kws.on_close = self._on_close
        self.kws.on_error = self._on_error
        
    def connect(self, threaded=True):
        """Connect to Kite Ticker"""
        if not self.kws:
            self.initialize()
            
        if self.kws:
            logger.info("Connecting to Kite Ticker...")
            self.kws.connect(threaded=threaded)
            
    def subscribe(self, tokens: List[int]):
        """Subscribe to tokens"""
        if not self.kws or not self.is_connected:
            logger.warning("KiteTicker not connected, queuing subscription")
            self.subscribed_tokens.extend(tokens)
            return

        self.kws.subscribe(tokens)
        self.kws.set_mode(self.kws.MODE_FULL, tokens)
        self.subscribed_tokens.extend(tokens)
        logger.info(f"Subscribed to tokens: {tokens}")

    def add_callback(self, callback: Callable):
        """Add callback for tick data"""
        self.callbacks.append(callback)

    def _on_ticks(self, ws, ticks):
        """Handle incoming ticks"""
        # logger.debug(f"Received {len(ticks)} ticks")
        for callback in self.callbacks:
            try:
                # Run callback (might need to be scheduled if async)
                if asyncio.iscoroutinefunction(callback):
                    asyncio.create_task(callback(ticks))
                else:
                    callback(ticks)
            except Exception as e:
                logger.error(f"Error in ticker callback: {str(e)}")

    def _on_connect(self, ws, response):
        """Handle connection established"""
        self.is_connected = True
        logger.info("Connected to Kite Ticker")
        
        # Resubscribe to tokens
        if self.subscribed_tokens:
            self.kws.subscribe(self.subscribed_tokens)
            self.kws.set_mode(self.kws.MODE_FULL, self.subscribed_tokens)
            logger.info(f"Resubscribed to {len(self.subscribed_tokens)} tokens")

    def _on_close(self, ws, code, reason):
        """Handle connection closed"""
        self.is_connected = False
        logger.warning(f"Kite Ticker closed: {code} - {reason}")

    def _on_error(self, ws, code, reason):
        """Handle connection error"""
        logger.error(f"Kite Ticker error: {code} - {reason}")
