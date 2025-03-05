import os
from fastapi import FastAPI
from dotenv import load_dotenv
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame
from datetime import datetime, timedelta

load_dotenv()

API_KEY = os.getenv("AKI6HOG3BKCHHAKLAJUY")
API_SECRET = os.getenv("t2drfGDtSnB2KH3OyYdBU01QmITWn4YXLMi3ihzs")

client = StockHistoricalDataClient(API_KEY, API_SECRET)

app = FastAPI()

def get_candles(timeframe):
    end = datetime.utcnow()
    start = end - timedelta(days=30)
    
    request = StockBarsRequest(
        symbol_or_symbols="SPY",
        timeframe=timeframe,
        start=start,
        end=end
    )
    
    bars = client.get_stock_bars(request).df
    bars.reset_index(inplace=True)
    
    return bars.to_dict(orient="records")

@app.get("/spy/multi-resolution-ohlc")
def get_multi_resolution_ohlc():
    candles = {
        "5_min": get_candles(TimeFrame.Minute * 5),
        "15_min": get_candles(TimeFrame.Minute * 15),
        "30_min": get_candles(TimeFrame.Minute * 30),
        "1_hour": get_candles(TimeFrame.Hour)
    }
    return {"symbol": "SPY", "candles": candles}
