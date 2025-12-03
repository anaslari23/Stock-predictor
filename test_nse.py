from nsepython import *
import json

try:
    symbol = "TCS"
    print(f"Fetching data for {symbol}...")
    quote = nse_eq(symbol)
    
    # Print key price fields
    print("\n--- Price Info ---")
    if 'priceInfo' in quote:
        print(json.dumps(quote['priceInfo'], indent=2))
    else:
        print("No priceInfo found!")
        
    print("\n--- Metadata ---")
    if 'metadata' in quote:
        print(json.dumps(quote['metadata'], indent=2))
        
    print(f"\nLast Price: {quote.get('priceInfo', {}).get('lastPrice')}")
    print(f"Last Update Time: {quote.get('metadata', {}).get('lastUpdateTime')}")
    
except Exception as e:
    print(f"Error: {e}")
