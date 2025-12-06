"""
NSE WebSocket Discovery Script
This script helps identify NSE's WebSocket endpoint by analyzing network traffic
"""

import requests
from bs4 import BeautifulSoup
import json
import re

def discover_nse_websocket():
    """
    Attempt to discover NSE WebSocket endpoint by inspecting their website
    """
    print("🔍 Discovering NSE WebSocket endpoint...")
    
    # NSE live market page
    url = "https://www.nseindia.com/market-data/live-equity-market"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
    }
    
    try:
        # Get the page
        print(f"📡 Fetching {url}...")
        session = requests.Session()
        response = session.get(url, headers=headers, timeout=10)
        
        print(f"✓ Status: {response.status_code}")
        
        # Look for WebSocket URLs in the HTML/JavaScript
        content = response.text
        
        # Common WebSocket URL patterns
        ws_patterns = [
            r'wss?://[^\s"\'<>]+',  # Any WebSocket URL
            r'socket[^\s"\'<>]*',    # Socket-related URLs
            r'stream[^\s"\'<>]*',    # Stream-related URLs
        ]
        
        found_urls = set()
        for pattern in ws_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            found_urls.update(matches)
        
        if found_urls:
            print(f"\n✓ Found {len(found_urls)} potential WebSocket URLs:")
            for url in sorted(found_urls):
                print(f"  - {url}")
        else:
            print("\n⚠️  No WebSocket URLs found in HTML")
        
        # Look for JavaScript files that might contain WebSocket logic
        soup = BeautifulSoup(content, 'html.parser')
        scripts = soup.find_all('script', src=True)
        
        print(f"\n📜 Found {len(scripts)} external JavaScript files")
        print("   (These might contain WebSocket initialization code)")
        
        for script in scripts[:5]:  # Show first 5
            print(f"  - {script['src']}")
        
        # Try to find API endpoints
        api_patterns = [
            r'/api/[^\s"\'<>]+',
            r'/ws/[^\s"\'<>]+',
            r'/socket/[^\s"\'<>]+',
        ]
        
        api_urls = set()
        for pattern in api_patterns:
            matches = re.findall(pattern, content)
            api_urls.update(matches)
        
        if api_urls:
            print(f"\n✓ Found {len(api_urls)} API endpoints:")
            for url in sorted(api_urls):
                print(f"  - {url}")
        
        return {
            'websocket_urls': list(found_urls),
            'api_endpoints': list(api_urls),
            'script_files': [s['src'] for s in scripts]
        }
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

if __name__ == "__main__":
    print("=" * 60)
    print("NSE WebSocket Discovery Tool")
    print("=" * 60)
    print()
    
    result = discover_nse_websocket()
    
    if result:
        print("\n" + "=" * 60)
        print("💡 Next Steps:")
        print("=" * 60)
        print("1. Inspect the JavaScript files to find WebSocket initialization")
        print("2. Use browser DevTools Network tab to capture live WebSocket traffic")
        print("3. Analyze the WebSocket message format")
        print("4. Implement the WebSocket client based on findings")
