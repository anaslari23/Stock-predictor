from nsepython import *
import json

try:
    symbol = "TCS"
    print(f"Fetching data for {symbol}...")
    quote = nse_eq(symbol)
    print(json.dumps(quote, indent=2))
    
    price = quote['priceInfo']['lastPrice']
    print(f"\nLast Price: {price}")
    
except Exception as e:
    print(f"Error: {e}")
