import yfinance as yf
from supabase import create_client
from datetime import datetime, timedelta

url = "https://zxsfthlswqtofvkbidks.supabase.co"
key = "sb_publishable_KbYlYtwWVHRb938OigLkXQ_SnR9n9Lt"

supabase = create_client(url, key)


def ingest_stock_data(symbol: str):
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)

    ticker = yf.Ticker(symbol)
    df = ticker.history(start=start_date, end=end_date)

    if not df.empty:
        initial_price = float(df["Close"].iloc[0])
        final_price = float(df["Close"].iloc[-1])

        data = {
            "ticker": symbol.upper(),
            "initial_price": round(initial_price, 2),
            "final_price": round(final_price, 2),
        }

        supabase.table("stock_records").insert(data).execute()
        print(f"Successfully inserted {symbol.upper()}")
    else:
        print(f"No data found for {symbol}")


ingest_stock_data("AAPL")
ingest_stock_data("TSLA")