from fastapi import FastAPI, HTTPException
from supabase import create_client

app = FastAPI()

url = "https://zxsfthlswqtofvkbidks.supabase.co"
key = "sb_publishable_KbYlYtwWVHRb938OigLkXQ_SnR9n9Lt"
supabase = create_client(url, key)

@app.get("/analyze/{symbol}")
async def analyze_stock(symbol: str):
    response = (
        supabase.table("stock_records")
        .select("*")
        .eq("ticker", symbol.upper())
        .order("created_at", desc=True)
        .limit(1)
        .execute()
    )

    if not response.data:
        raise HTTPException(status_code=404, detail=f"No data found for {symbol.upper()}")

    record = response.data[0]
    initial_p = float(record["initial_price"])
    final_p = float(record["final_price"])

    signal = "Bullish" if final_p > initial_p else "Bearish"

    return {
        "ticker": symbol.upper(),
        "analysis": {
            "start_price": initial_p,
            "current_price": final_p,
            "signal": signal,
            "source": "Internal Database"
        }
    }