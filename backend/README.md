# Stock Predictor AI Backend

Production-ready FastAPI backend for AI-powered stock predictions with real-time WebSocket streaming.

## 🚀 Features

- **FastAPI** framework with async support
- **WebSocket** for real-time price streaming
- **CORS** configured for Flutter web/Android/iOS
- **Comprehensive error handling** and logging
- **Modular architecture** with services and routers
- **Pydantic** models for request/response validation
- **ML-ready** structure for model integration

## 📁 Project Structure

```
backend/
├── app/
│   ├── api/
│   │   ├── endpoints/
│   │   │   ├── predictions.py
│   │   │   ├── stocks.py
│   │   │   ├── screener.py
│   │   │   └── websocket.py
│   │   └── __init__.py
│   ├── core/
│   │   ├── config.py
│   │   └── logging_config.py
│   ├── models/
│   │   └── schemas.py
│   ├── services/
│   │   ├── prediction_service.py
│   │   ├── stock_service.py
│   │   └── screener_service.py
│   ├── ml/
│   │   └── models/
│   └── utils/
├── data/
├── logs/
├── tests/
├── main.py
├── run.py
├── requirements.txt
└── .env.example
```

## 🛠️ Installation

1. **Create virtual environment**:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Configure environment**:
```bash
cp .env.example .env
# Edit .env with your configuration
```

## 🏃 Running the Server

**Development mode** (with auto-reload):
```bash
python run.py
```

Or using uvicorn directly:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Production mode**:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

## 📡 API Endpoints

### Health Check
- `GET /` - Root endpoint
- `GET /health` - Detailed health check

### Predictions
- `GET /api/v1/predictions/predict/{symbol}` - Get AI prediction

### Stocks
- `GET /api/v1/stocks/search?q={query}` - Search stocks
- `GET /api/v1/stocks/price/{symbol}` - Get current price
- `GET /api/v1/stocks/ohlcv/{symbol}?timeframe=1D` - Get OHLCV data
- `GET /api/v1/stocks/details/{symbol}` - Get stock details

### Screener
- `GET /api/v1/screener?filter=bullish&page=1` - Get filtered stocks
- `GET /api/v1/screener/ai-picks` - Get AI recommendations

### WebSocket
- `WS /api/v1/ws/prices?symbol=TCS.NS` - Real-time price streaming

## 📚 API Documentation

Once the server is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🧪 Testing

```bash
pytest tests/
```

## 📝 TODO

- [ ] Integrate real ML model for predictions
- [ ] Connect to yfinance for live data
- [ ] Add authentication/authorization
- [ ] Implement caching (Redis)
- [ ] Add rate limiting
- [ ] Database integration for historical data
- [ ] Deploy to production server

## 📄 License

MIT License
