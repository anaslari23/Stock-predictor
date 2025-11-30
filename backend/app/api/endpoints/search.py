"""
Search API Endpoint
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List
from app.models.schemas import SearchResult
from app.services.search_service import SearchService
from loguru import logger

router = APIRouter()
search_service = SearchService()

@router.get("/search", response_model=List[SearchResult])
async def search_stocks(
    query: str = Query(..., min_length=1, max_length=50, description="Search query")
):
    """
    Search for stocks by symbol or name
    
    - **query**: Search term (e.g., "TATA", "Apple", "RELIANCE")
    - Returns list of matching stocks with symbol and name
    - Results are cached for 15 minutes
    - Rate limited to prevent API abuse
    
    Example: GET /search?query=TATA
    """
    try:
        if len(query.strip()) == 0:
            raise HTTPException(status_code=400, detail="Query cannot be empty")
        
        logger.info(f"Search request for: {query}")
        results = await search_service.search(query.strip())
        
        logger.info(f"Returning {len(results)} results for: {query}")
        return results
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Search endpoint error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Search service temporarily unavailable"
        )

@router.get("/search/cache/stats")
async def get_cache_stats():
    """
    Get search cache statistics (admin endpoint)
    """
    try:
        stats = search_service.get_cache_stats()
        return stats
    except Exception as e:
        logger.error(f"Cache stats error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/search/cache/clear")
async def clear_cache():
    """
    Clear search cache (admin endpoint)
    """
    try:
        search_service.clear_cache()
        return {"message": "Cache cleared successfully"}
    except Exception as e:
        logger.error(f"Cache clear error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
