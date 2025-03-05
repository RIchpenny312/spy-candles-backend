import os
from fastapi import FastAPI
from dotenv import load_dotenv
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame
from datetime import datetime, timedelta
import uvicorn

load_dotenv()

API_KEY = os.getenv("APCA_API_KEY_ID")
API_SECRET = os.getenv("APCA_API_SECRET_KEY")

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
        "5_min": get_candles(TimeFrame.Minute),
        "15_min": get_candles(TimeFrame.Minute),
        "30_min": get_candles(TimeFrame.Minute),
        "1_hour": get_candles(TimeFrame.Hour)
    }
    return {"symbol": "SPY", "candles": candles}

# Bind the app to the correct port
if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))  # Use the $PORT environment variable or default to 8000
    uvicorn.run(app, host="0.0.0.0", port=port)
