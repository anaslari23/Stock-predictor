from nsepython import *
import json

def test_index(symbol):
    print(f"\nTesting {symbol}...")
    try:
        # Try nse_quote (usually for indices)
        print("1. Trying nse_quote...")
        quote = nse_quote(symbol)
        print(json.dumps(quote, indent=2))
    except Exception as e:
        print(f"nse_quote failed: {e}")

    try:
        # Try nse_eq (usually for stocks)
        print("\n2. Trying nse_eq...")
        quote = nse_eq(symbol)
        print(json.dumps(quote, indent=2))
    except Exception as e:
        print(f"nse_eq failed: {e}")

    try:
        # Try nse_get_index_quote
        print("\n3. Trying nse_get_index_quote...")
        quote = nse_get_index_quote(symbol)
        print(json.dumps(quote, indent=2))
    except Exception as e:
        print(f"nse_get_index_quote failed: {e}")

test_index("NIFTY")
