import os
from fastapi import FastAPI
from dotenv import load_dotenv
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame
from datetime import datetime, timedelta

load_dotenv()

API_KEY = os.getenv("APCA_API_KEY_ID")
API_SECRET = os.getenv("APCA_API_SECRET_KEY")

client = StockHistoricalDataClient(API_KEY, API_SECRET)

app = FastAPI()

# Corrected get_candles function with TimeFrame usage
def get_candles(timeframe):
    end = datetime.utcnow()
    start = end - timedelta(days=30)
    
    # Request data for the given timeframe
    request = StockBarsRequest(
        symbol_or_symbols="SPY",
        timeframe=timeframe,
        start=start,
        end=end
    )
    
    # Fetch the stock bars and reset the index
    bars = client.get_stock_bars(request).df
    bars.reset_index(inplace=True)
    
    return bars.to_dict(orient="records")

@app.get("/spy/multi-resolution-ohlc")
def get_multi_resolution_ohlc():
    candles = {
        "5_min": get_candles(TimeFrame.Minute),  # 5-minute candles
        "15_min": get_candles(TimeFrame.Minute),  # 15-minute candles
        "30_min": get_candles(TimeFrame.Minute),  # 30-minute candles
        "1_hour": get_candles(TimeFrame.Hour)     # 1-hour candles
    }
    return {"symbol": "SPY", "candles": candles}


