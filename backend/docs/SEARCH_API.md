# Search API Endpoint

## Overview
Production-ready stock search endpoint using Yahoo Finance API with caching and rate limiting.

## Endpoint

```
GET /api/v1/search?query={query}
```

## Features

✅ **Yahoo Finance Integration** - Real-time stock search
✅ **15-Minute Caching** - Reduces API calls and improves performance
✅ **Rate Limiting** - 0.5s delay between requests to Yahoo Finance
✅ **Error Handling** - Graceful fallback on API failures
✅ **Type Filtering** - Returns only EQUITY, ETF, and INDEX securities
✅ **Comprehensive Logging** - All requests and errors logged

## Request

**Query Parameters:**
- `query` (required): Search term (1-50 characters)

**Example:**
```bash
curl "http://localhost:8000/api/v1/search?query=TATA"
```

## Response

**Success (200):**
```json
[
  {
    "symbol": "TCS.NS",
    "name": "Tata Consultancy Services",
    "exchange": "NSI",
    "type": "EQUITY"
  },
  {
    "symbol": "TATAMOTORS.NS",
    "name": "Tata Motors Limited",
    "exchange": "NSI",
    "type": "EQUITY"
  }
]
```

**Error (400):**
```json
{
  "detail": "Query cannot be empty"
}
```

**Error (500):**
```json
{
  "detail": "Search service temporarily unavailable"
}
```

## Admin Endpoints

### Get Cache Stats
```
GET /api/v1/search/cache/stats
```

Response:
```json
{
  "total_entries": 5,
  "valid_entries": 3,
  "expired_entries": 2,
  "cache_ttl_minutes": 15
}
```

### Clear Cache
```
POST /api/v1/search/cache/clear
```

Response:
```json
{
  "message": "Cache cleared successfully"
}
```

## Implementation Details

### Caching Strategy
- Results cached in-memory for 15 minutes
- Cache key: search query string
- Automatic expiration after TTL
- Cache hit/miss logged

### Rate Limiting
- 0.5 second delay between Yahoo Finance API requests
- Prevents rate limit errors (429)
- Configurable in `SearchService`

### Error Handling
1. **Network Errors**: Returns empty list, logs error
2. **Rate Limit (429)**: Raises exception, logged
3. **API Errors**: Returns empty list, logs status
4. **Parse Errors**: Returns empty list, logs error

## Testing

Run the test script:
```bash
cd backend
python tests/test_search.py
```

## Files Modified

1. **app/services/search_service.py** - Core search logic
2. **app/api/endpoints/search.py** - API endpoint
3. **app/models/schemas.py** - SearchResult model
4. **app/api/__init__.py** - Router registration

## Configuration

Adjust in `app/services/search_service.py`:
```python
self.cache_ttl = timedelta(minutes=15)  # Cache duration
self.rate_limit_delay = 0.5  # Seconds between requests
```

## Production Considerations

- [ ] Add Redis for distributed caching
- [ ] Implement request rate limiting per IP
- [ ] Add authentication for admin endpoints
- [ ] Monitor Yahoo Finance API usage
- [ ] Consider backup search providers
