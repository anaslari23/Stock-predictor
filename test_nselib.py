from nselib import capital_market
import json

def test_nselib(symbol):
    print(f"Testing {symbol} with nselib...")
    try:
        data = capital_market.nifty50_equity_list()
        # Filter for NIFTY 50 index data if available, or just check if it works
        print("Nifty 50 equity list fetched successfully.")
        # print(data.head())
        
        # Try to get index quote
        # nselib doesn't have a direct "get_index_quote" but let's check documentation/methods
        # Usually it's for historical data.
        
        # Let's try to get live quote for a stock to see if it works
        quote = capital_market.price_volume_and_delivery_position_data(symbol='TCS', from_date='03-12-2025', to_date='03-12-2025')
        print(quote)
        
    except Exception as e:
        print(f"nselib failed: {e}")

test_nselib("NIFTY 50")
