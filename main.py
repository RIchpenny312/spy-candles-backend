import os
import logging
from fastapi import FastAPI, HTTPException
from dotenv import load_dotenv
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame
from datetime import datetime, timedelta

# Set up logging
logging.basicConfig(level=logging.DEBUG)

load_dotenv()

API_KEY = os.getenv("APCA_API_KEY_ID")
API_SECRET = os.getenv("APCA_API_SECRET_KEY")
client = StockHistoricalDataClient(API_KEY, API_SECRET)

app = FastAPI()

# Root endpoint for testing
@app.get("/")
def read_root():
    return {"message": "API is live and working!"}

# Function to get SPY candles
def get_candles(timeframe):
    try:
        end = datetime.utcnow()
        start = end - timedelta(days=30)
        
        logging.debug(f"Fetching candles from {start} to {end} for timeframe {timeframe}")

        request = StockBarsRequest(
            symbol_or_symbols="SPY",
            timeframe=timeframe,
            start=start,
            end=end
        )
        
        bars = client.get_stock_bars(request).df
        bars.reset_index(inplace=True)
        
        logging.debug(f"Fetched {len(bars)} candles")
        return bars.to_dict(orient="records")
    
    except Exception as e:
        logging.error(f"Error fetching candles: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")

# Endpoint to fetch multi-resolution candles
@app.get("/spy/multi-resolution-ohlc")
def get_multi_resolution_ohlc():
    try:
        logging.debug("Fetching candles for all timeframes")

        candles = {
            "5_min": get_candles(TimeFrame.Minute),
            "15_min": get_candles(TimeFrame.Minute),
            "30_min": get_candles(TimeFrame.Minute),
            "1_hour": get_candles(TimeFrame.Hour)
        }
        logging.debug("Fetched candles successfully")
        return {"symbol": "SPY", "candles": candles}
    
    except Exception as e:
        logging.error(f"Error in /spy/multi-resolution-ohlc route: {e}")
        raise HTTPException(status_code=500, detail="Internal server error fetching candles")
