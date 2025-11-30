"""
Search Service - Yahoo Finance Stock Search with Caching
"""

import aiohttp
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from loguru import logger
import asyncio

class SearchService:
    def __init__(self):
        self.cache: Dict[str, tuple[List[Dict], datetime]] = {}
        self.cache_ttl = timedelta(minutes=15)
        self.yahoo_base_url = "https://query2.finance.yahoo.com/v1/finance/search"
        self.session: Optional[aiohttp.ClientSession] = None
        self.rate_limit_delay = 0.5  # seconds between requests
        self.last_request_time = 0
        logger.info("SearchService initialized with 15-minute cache")
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session"""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=10),
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
            )
        return self.session
    
    async def search(self, query: str) -> List[Dict[str, str]]:
        """
        Search for stocks using Yahoo Finance API
        Returns cached results if available and not expired
        """
        # Check cache first
        if query in self.cache:
            results, timestamp = self.cache[query]
            if datetime.now() - timestamp < self.cache_ttl:
                logger.info(f"Cache hit for query: {query}")
                return results
            else:
                logger.info(f"Cache expired for query: {query}")
                del self.cache[query]
        
        # Rate limiting
        await self._rate_limit()
        
        try:
            # Fetch from Yahoo Finance
            results = await self._fetch_from_yahoo(query)
            
            # Cache the results
            self.cache[query] = (results, datetime.now())
            logger.info(f"Cached {len(results)} results for query: {query}")
            
            return results
            
        except Exception as e:
            logger.error(f"Search error for '{query}': {str(e)}")
            # Return empty list on error
            return []
    
    async def _rate_limit(self):
        """Implement rate limiting to avoid overwhelming Yahoo Finance API"""
        current_time = asyncio.get_event_loop().time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.rate_limit_delay:
            await asyncio.sleep(self.rate_limit_delay - time_since_last)
        
        self.last_request_time = asyncio.get_event_loop().time()
    
    async def _fetch_from_yahoo(self, query: str) -> List[Dict[str, str]]:
        """
        Fetch search results from Yahoo Finance API
        """
        session = await self._get_session()
        
        params = {
            'q': query,
            'quotesCount': 10,
            'newsCount': 0,
            'enableFuzzyQuery': False,
            'quotesQueryId': 'tss_match_phrase_query'
        }
        
        try:
            async with session.get(self.yahoo_base_url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return self._parse_yahoo_response(data)
                elif response.status == 429:
                    logger.warning("Rate limit hit on Yahoo Finance API")
                    raise Exception("Rate limit exceeded")
                else:
                    logger.error(f"Yahoo Finance API error: {response.status}")
                    raise Exception(f"API returned status {response.status}")
                    
        except aiohttp.ClientError as e:
            logger.error(f"Network error: {str(e)}")
            raise Exception(f"Network error: {str(e)}")
    
    def _parse_yahoo_response(self, data: dict) -> List[Dict[str, str]]:
        """
        Parse Yahoo Finance API response
        Extract symbol and name from quotes
        """
        results = []
        
        try:
            quotes = data.get('quotes', [])
            
            for quote in quotes:
                # Filter for equity stocks only
                quote_type = quote.get('quoteType', '')
                if quote_type not in ['EQUITY', 'ETF', 'INDEX']:
                    continue
                
                symbol = quote.get('symbol', '')
                # Get long name or short name
                name = quote.get('longname') or quote.get('shortname') or symbol
                
                if symbol:
                    results.append({
                        'symbol': symbol,
                        'name': name,
                        'exchange': quote.get('exchange', ''),
                        'type': quote_type
                    })
            
            logger.info(f"Parsed {len(results)} results from Yahoo Finance")
            return results
            
        except Exception as e:
            logger.error(f"Error parsing Yahoo response: {str(e)}")
            return []
    
    def clear_cache(self):
        """Clear all cached results"""
        self.cache.clear()
        logger.info("Search cache cleared")
    
    def get_cache_stats(self) -> Dict:
        """Get cache statistics"""
        total_entries = len(self.cache)
        valid_entries = sum(
            1 for _, (_, timestamp) in self.cache.items()
            if datetime.now() - timestamp < self.cache_ttl
        )
        
        return {
            'total_entries': total_entries,
            'valid_entries': valid_entries,
            'expired_entries': total_entries - valid_entries,
            'cache_ttl_minutes': self.cache_ttl.total_seconds() / 60
        }
    
    async def close(self):
        """Close aiohttp session"""
        if self.session and not self.session.closed:
            await self.session.close()
            logger.info("SearchService session closed")
