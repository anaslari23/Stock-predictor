"""
Search Service - Indian Stock Search with Local Database
"""

from typing import List, Dict
from datetime import datetime, timedelta
from loguru import logger


class SearchService:
    def __init__(self):
        self.cache: Dict[str, tuple[List[Dict], datetime]] = {}
        self.cache_ttl = timedelta(minutes=15)
        logger.info("SearchService initialized with local Indian stock database")
        
        # Load stock database
        self.stocks = self._load_stock_database()
    
    def _load_stock_database(self) -> List[Dict[str, str]]:
        """Load local database of Indian stocks"""
        # NIFTY 50 + popular stocks
        stocks = [
            {'symbol': 'TCS', 'name': 'Tata Consultancy Services'},
            {'symbol': 'RELIANCE', 'name': 'Reliance Industries'},
            {'symbol': 'HDFCBANK', 'name': 'HDFC Bank'},
            {'symbol': 'INFY', 'name': 'Infosys'},
            {'symbol': 'ICICIBANK', 'name': 'ICICI Bank'},
            {'symbol': 'HINDUNILVR', 'name': 'Hindustan Unilever'},
            {'symbol': 'ITC', 'name': 'ITC Limited'},
            {'symbol': 'SBIN', 'name': 'State Bank of India'},
            {'symbol': 'BHARTIARTL', 'name': 'Bharti Airtel'},
            {'symbol': 'KOTAKBANK', 'name': 'Kotak Mahindra Bank'},
            {'symbol': 'LT', 'name': 'Larsen & Toubro'},
            {'symbol': 'AXISBANK', 'name': 'Axis Bank'},
            {'symbol': 'ASIANPAINT', 'name': 'Asian Paints'},
            {'symbol': 'MARUTI', 'name': 'Maruti Suzuki'},
            {'symbol': 'TITAN', 'name': 'Titan Company'},
            {'symbol': 'WIPRO', 'name': 'Wipro'},
            {'symbol': 'ULTRACEMCO', 'name': 'UltraTech Cement'},
            {'symbol': 'NESTLEIND', 'name': 'Nestle India'},
            {'symbol': 'BAJFINANCE', 'name': 'Bajaj Finance'},
            {'symbol': 'HCLTECH', 'name': 'HCL Technologies'},
            {'symbol': 'SUNPHARMA', 'name': 'Sun Pharmaceutical'},
            {'symbol': 'ONGC', 'name': 'Oil & Natural Gas Corporation'},
            {'symbol': 'NTPC', 'name': 'NTPC'},
            {'symbol': 'POWERGRID', 'name': 'Power Grid Corporation'},
            {'symbol': 'M&M', 'name': 'Mahindra & Mahindra'},
            {'symbol': 'TATAMOTORS', 'name': 'Tata Motors'},
            {'symbol': 'TATASTEEL', 'name': 'Tata Steel'},
            {'symbol': 'TECHM', 'name': 'Tech Mahindra'},
            {'symbol': 'INDUSINDBK', 'name': 'IndusInd Bank'},
            {'symbol': 'ADANIENT', 'name': 'Adani Enterprises'},
            {'symbol': 'ADANIPORTS', 'name': 'Adani Ports'},
            {'symbol': 'JSWSTEEL', 'name': 'JSW Steel'},
            {'symbol': 'DIVISLAB', 'name': 'Divi\'s Laboratories'},
            {'symbol': 'DRREDDY', 'name': 'Dr Reddy\'s Laboratories'},
            {'symbol': 'CIPLA', 'name': 'Cipla'},
            {'symbol': 'EICHERMOT', 'name': 'Eicher Motors'},
            {'symbol': 'GRASIM', 'name': 'Grasim Industries'},
            {'symbol': 'BRITANNIA', 'name': 'Britannia Industries'},
            {'symbol': 'HEROMOTOCO', 'name': 'Hero MotoCorp'},
            {'symbol': 'COALINDIA', 'name': 'Coal India'},
            {'symbol': 'BAJAJFINSV', 'name': 'Bajaj Finserv'},
            {'symbol': 'BPCL', 'name': 'Bharat Petroleum'},
            {'symbol': 'HINDALCO', 'name': 'Hindalco Industries'},
            {'symbol': 'APOLLOHOSP', 'name': 'Apollo Hospitals'},
            {'symbol': 'SHREECEM', 'name': 'Shree Cement'},
            {'symbol': 'VEDL', 'name': 'Vedanta'},
            {'symbol': 'UPL', 'name': 'UPL'},
            {'symbol': 'SBILIFE', 'name': 'SBI Life Insurance'},
            {'symbol': 'TATACONSUM', 'name': 'Tata Consumer Products'},
            {'symbol': 'BAJAJ-AUTO', 'name': 'Bajaj Auto'},
            # Indices
            {'symbol': 'NIFTY50', 'name': 'NIFTY 50 Index'},
            {'symbol': 'BANKNIFTY', 'name': 'Bank NIFTY Index'},
            {'symbol': 'NIFTYIT', 'name': 'NIFTY IT Index'},
        ]
        
        logger.info(f"Loaded {len(stocks)} stocks into local database")
        return stocks
    
    async def search(self, query: str) -> List[Dict[str, str]]:
        """
        Search for stocks in local database
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
        
        try:
            # Search in local database
            results = self._search_local(query)
            
            # Cache the results
            self.cache[query] = (results, datetime.now())
            logger.info(f"Cached {len(results)} results for query: {query}")
            
            return results
            
        except Exception as e:
            logger.error(f"Search error for '{query}': {str(e)}")
            return []
    
    def _search_local(self, query: str) -> List[Dict[str, str]]:
        """Search in local stock database"""
        query_lower = query.lower()
        results = []
        
        for stock in self.stocks:
            symbol_lower = stock['symbol'].lower()
            name_lower = stock['name'].lower()
            
            # Match symbol or name contains query
            if query_lower in symbol_lower or query_lower in name_lower:
                results.append({
                    'symbol': stock['symbol'],
                    'name': stock['name'],
                    'exchange': 'NSE',
                    'type': 'INDEX' if stock['symbol'] in ['NIFTY50', 'BANKNIFTY', 'NIFTYIT'] else 'EQUITY'
                })
        
        logger.info(f"Found {len(results)} matches for query: {query}")
        return results[:10]  # Limit to 10 results
    
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

