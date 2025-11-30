"""
Test script for search endpoint
"""

import asyncio
import aiohttp

async def test_search():
    """Test the search endpoint"""
    base_url = "http://localhost:8000/api/v1"
    
    async with aiohttp.ClientSession() as session:
        # Test 1: Search for TATA
        print("Test 1: Searching for 'TATA'...")
        async with session.get(f"{base_url}/search?query=TATA") as response:
            data = await response.json()
            print(f"Status: {response.status}")
            print(f"Results: {len(data)} stocks found")
            for stock in data[:3]:
                print(f"  - {stock['symbol']}: {stock['name']}")
        
        print("\n" + "="*50 + "\n")
        
        # Test 2: Search for RELIANCE
        print("Test 2: Searching for 'RELIANCE'...")
        async with session.get(f"{base_url}/search?query=RELIANCE") as response:
            data = await response.json()
            print(f"Status: {response.status}")
            print(f"Results: {len(data)} stocks found")
            for stock in data[:3]:
                print(f"  - {stock['symbol']}: {stock['name']}")
        
        print("\n" + "="*50 + "\n")
        
        # Test 3: Cache stats
        print("Test 3: Getting cache stats...")
        async with session.get(f"{base_url}/search/cache/stats") as response:
            data = await response.json()
            print(f"Status: {response.status}")
            print(f"Cache stats: {data}")

if __name__ == "__main__":
    print("Starting search endpoint tests...")
    print("Make sure the backend is running on http://localhost:8000\n")
    asyncio.run(test_search())
