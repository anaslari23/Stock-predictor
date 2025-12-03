import yfinance as yf

def test_yfinance(symbol):
    print(f"Testing {symbol}...")
    ticker = yf.Ticker(symbol)
    info = ticker.info
    
    # Try different price fields
    price = info.get('currentPrice') or info.get('regularMarketPrice') or info.get('previousClose')
    print(f"Price: {price}")
    print(f"Previous Close: {info.get('previousClose')}")
    
test_yfinance("^NSEI")
