"""
AI Screener Service - Run predictions on multiple stocks with filtering
"""

import asyncio
from typing import List, Dict
from loguru import logger
from app.ml.predictor import Predictor
from app.services.ohlcv_service import OHLCVService
import pandas as pd

class AIScreenerService:
    def __init__(self):
        self.predictor = Predictor()
        self.ohlcv_service = OHLCVService()
        
        # Top 200 stocks (NIFTY 50 + FNO + popular stocks)
        self.stock_universe = [
            # NIFTY 50
            'RELIANCE.NS', 'TCS.NS', 'HDFCBANK.NS', 'INFY.NS', 'ICICIBANK.NS',
            'HINDUNILVR.NS', 'ITC.NS', 'SBIN.NS', 'BHARTIARTL.NS', 'KOTAKBANK.NS',
            'LT.NS', 'AXISBANK.NS', 'ASIANPAINT.NS', 'MARUTI.NS', 'SUNPHARMA.NS',
            'TITAN.NS', 'BAJFINANCE.NS', 'ULTRACEMCO.NS', 'NESTLEIND.NS', 'WIPRO.NS',
            'HCLTECH.NS', 'TECHM.NS', 'POWERGRID.NS', 'NTPC.NS', 'ONGC.NS',
            'TATAMOTORS.NS', 'M&M.NS', 'TATASTEEL.NS', 'ADANIPORTS.NS', 'JSWSTEEL.NS',
            'INDUSINDBK.NS', 'BAJAJFINSV.NS', 'HINDALCO.NS', 'COALINDIA.NS', 'GRASIM.NS',
            'BRITANNIA.NS', 'DIVISLAB.NS', 'DRREDDY.NS', 'CIPLA.NS', 'EICHERMOT.NS',
            'HEROMOTOCO.NS', 'SHREECEM.NS', 'UPL.NS', 'TATACONSUM.NS', 'APOLLOHOSP.NS',
            'BAJAJ-AUTO.NS', 'SBILIFE.NS', 'HDFCLIFE.NS', 'BPCL.NS', 'IOC.NS',
            
            # Additional FNO stocks
            'BANKBARODA.NS', 'PNB.NS', 'CANBK.NS', 'VEDL.NS', 'SAIL.NS',
            'NMDC.NS', 'RECLTD.NS', 'PFC.NS', 'IRCTC.NS', 'ZOMATO.NS',
            'PAYTM.NS', 'NYKAA.NS', 'ADANIENT.NS', 'ADANIGREEN.NS', 'GODREJCP.NS',
            'DABUR.NS', 'MARICO.NS', 'PIDILITIND.NS', 'BERGEPAINT.NS', 'HAVELLS.NS',
            'VOLTAS.NS', 'WHIRLPOOL.NS', 'DIXON.NS', 'AMBER.NS', 'MPHASIS.NS',
            'LTIM.NS', 'PERSISTENT.NS', 'COFORGE.NS', 'MINDTREE.NS', 'OFSS.NS',
        ]
        
        logger.info(f"AIScreenerService initialized with {len(self.stock_universe)} stocks")
    
    async def screen_stocks(self, filter_type: str, max_results: int = 50) -> List[Dict]:
        """
        Screen stocks based on AI predictions and filters
        """
        logger.info(f"Starting AI screener with filter: {filter_type}")
        
        # Run predictions on all stocks in parallel
        predictions = await self._run_predictions_parallel()
        
        # Apply filter
        filtered = self._apply_filter(predictions, filter_type)
        
        # Sort by confidence/probability
        sorted_results = sorted(filtered, key=lambda x: x['confidence'], reverse=True)
        
        # Limit results
        results = sorted_results[:max_results]
        
        logger.info(f"Screener found {len(results)} matches for filter: {filter_type}")
        return results
    
    async def _run_predictions_parallel(self) -> List[Dict]:
        """
        Run predictions on all stocks in parallel
        """
        logger.info(f"Running predictions on {len(self.stock_universe)} stocks...")
        
        # Create tasks for all stocks
        tasks = [self._predict_single_stock(symbol) for symbol in self.stock_universe]
        
        # Run in parallel with limited concurrency
        semaphore = asyncio.Semaphore(10)  # Max 10 concurrent predictions
        
        async def bounded_predict(task):
            async with semaphore:
                return await task
        
        results = await asyncio.gather(*[bounded_predict(task) for task in tasks], return_exceptions=True)
        
        # Filter out errors
        valid_results = [r for r in results if isinstance(r, dict) and r is not None]
        
        logger.info(f"Completed {len(valid_results)} predictions successfully")
        return valid_results
    
    async def _predict_single_stock(self, symbol: str) -> Dict:
        """
        Run prediction for a single stock
        """
        try:
            # Fetch OHLCV data (6 months)
            ohlcv_data = await self.ohlcv_service.get_ohlcv(symbol, "6mo")
            
            if not ohlcv_data or not ohlcv_data.get('candles'):
                logger.warning(f"No data for {symbol}")
                return None
            
            # Convert to DataFrame
            candles = ohlcv_data['candles']
            df = pd.DataFrame(candles)
            df['time'] = pd.to_datetime(df['t'])
            df = df.set_index('time')
            df = df.rename(columns={'o': 'open', 'h': 'high', 'l': 'low', 'c': 'close', 'v': 'volume'})
            df = df[['open', 'high', 'low', 'close', 'volume']]
            
            # Run prediction
            prediction = await self.predictor.predict(df, symbol)
            
            # Add technical indicators for filtering
            last_candle = candles[-1]
            prediction['rsi'] = last_candle.get('rsi', 50)
            prediction['macd'] = last_candle.get('macd', 0)
            prediction['price'] = last_candle.get('c', 0)
            prediction['change_percent'] = ((last_candle.get('c', 0) - candles[-2].get('c', 0)) / candles[-2].get('c', 1)) * 100 if len(candles) > 1 else 0
            
            return prediction
            
        except Exception as e:
            logger.error(f"Error predicting {symbol}: {str(e)}")
            return None
    
    def _apply_filter(self, predictions: List[Dict], filter_type: str) -> List[Dict]:
        """
        Apply filter criteria to predictions
        """
        if filter_type == "high_confidence":
            # High confidence UP predictions (p_up > 0.7)
            return [p for p in predictions if p['prediction'] == 'UP' and p['probability'] > 0.7]
        
        elif filter_type == "bearish":
            # Strong bearish signals (p_up < 0.3)
            return [p for p in predictions if p['prediction'] == 'DOWN' and p['probability'] < 0.3]
        
        elif filter_type == "trending":
            # Trending with AI alignment (positive MACD + UP prediction)
            return [p for p in predictions 
                   if p['prediction'] == 'UP' 
                   and p.get('macd', 0) > 0 
                   and p['probability'] > 0.6]
        
        elif filter_type == "oversold_up":
            # Oversold with UP prediction (RSI < 30 + p_up > 0.55)
            return [p for p in predictions 
                   if p.get('rsi', 50) < 30 
                   and p['prediction'] == 'UP' 
                   and p['probability'] > 0.55]
        
        elif filter_type == "all":
            # Return all with minimum confidence
            return [p for p in predictions if p['confidence'] > 0.6]
        
        else:
            logger.warning(f"Unknown filter type: {filter_type}, returning all")
            return predictions
