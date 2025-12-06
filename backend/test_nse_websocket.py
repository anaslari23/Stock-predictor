"""
NSE WebSocket Client - Prototype
Attempts to connect to NSE's WebSocket and stream real-time data
"""

import websocket
import json
import time
from datetime import datetime

class NSEWebSocketClient:
    def __init__(self):
        self.ws_url = "wss://www.nseindia.com/"
        self.ws = None
        self.connected = False
        
    def on_message(self, ws, message):
        """Handle incoming WebSocket messages"""
        try:
            print(f"\n📨 Received message at {datetime.now().strftime('%H:%M:%S.%f')[:-3]}")
            print(f"   Raw: {message[:200]}...")  # First 200 chars
            
            # Try to parse as JSON
            try:
                data = json.loads(message)
                print(f"   JSON: {json.dumps(data, indent=2)[:500]}...")
            except:
                print(f"   Not JSON, raw text")
                
        except Exception as e:
            print(f"❌ Error processing message: {e}")
    
    def on_error(self, ws, error):
        """Handle WebSocket errors"""
        print(f"❌ WebSocket Error: {error}")
    
    def on_close(self, ws, close_status_code, close_msg):
        """Handle WebSocket close"""
        print(f"\n🔌 WebSocket Closed")
        print(f"   Status Code: {close_status_code}")
        print(f"   Message: {close_msg}")
        self.connected = False
    
    def on_open(self, ws):
        """Handle WebSocket open"""
        print("✅ WebSocket Connected!")
        self.connected = True
        
        # Try sending subscription messages
        # Common patterns for stock market WebSockets
        subscription_attempts = [
            # Pattern 1: Simple symbol subscription
            {"action": "subscribe", "symbols": ["TCS", "RELIANCE", "NIFTY 50"]},
            {"type": "subscribe", "symbols": ["TCS", "RELIANCE"]},
            {"cmd": "subscribe", "symbols": ["TCS"]},
            
            # Pattern 2: Channel-based subscription
            {"subscribe": ["stock.TCS", "index.NIFTY50"]},
            {"channels": ["market.stocks", "market.indices"]},
            
            # Pattern 3: Simple string messages
            "subscribe:TCS",
            "SUB:TCS,RELIANCE",
        ]
        
        print("\n📤 Attempting to send subscription messages...")
        for i, msg in enumerate(subscription_attempts, 1):
            try:
                if isinstance(msg, dict):
                    ws.send(json.dumps(msg))
                    print(f"   {i}. Sent JSON: {json.dumps(msg)[:100]}...")
                else:
                    ws.send(msg)
                    print(f"   {i}. Sent string: {msg}")
                time.sleep(0.5)  # Small delay between attempts
            except Exception as e:
                print(f"   {i}. Failed: {e}")
    
    def connect(self):
        """Connect to NSE WebSocket"""
        print("=" * 60)
        print("NSE WebSocket Client - Connecting...")
        print("=" * 60)
        print(f"URL: {self.ws_url}")
        print()
        
        # Set up WebSocket with headers
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Origin': 'https://www.nseindia.com',
            'Referer': 'https://www.nseindia.com/market-data/live-equity-market',
        }
        
        try:
            self.ws = websocket.WebSocketApp(
                self.ws_url,
                header=headers,
                on_open=self.on_open,
                on_message=self.on_message,
                on_error=self.on_error,
                on_close=self.on_close
            )
            
            # Run WebSocket (blocks until connection closes)
            self.ws.run_forever()
            
        except KeyboardInterrupt:
            print("\n\n⏹️  Stopped by user")
        except Exception as e:
            print(f"\n❌ Connection failed: {e}")

if __name__ == "__main__":
    client = NSEWebSocketClient()
    
    print("\n💡 This will attempt to connect to NSE's WebSocket")
    print("   Press Ctrl+C to stop\n")
    
    time.sleep(2)
    client.connect()
