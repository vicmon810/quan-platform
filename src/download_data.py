import yfinance as yf 
from pathlib import Path

TICKERS = ["SPY", "QQQ", "AAPL", "MSFT"]
START = "2020-01-01"
END = "2025-01-01"

RAW_DIR = Path("data/raw")
RAW_DIR.mkdir(parents=True, exist_ok=True)

for ticker in TICKERS:
    print(f"Downloading {ticker}...")

    
    df = yf.download(ticker, start=START, end=END, auto_adjust=False)
    
    if isinstance(df.columns, object) and hasattr(df.columns, "get_level_values"):
        df.columns = df.columns.get_level_values(0)

    df = df.reset_index()

    df = df[["Date", "Open", "High", "Low", "Close", "Adj Close", "Volume"]]
    df.to_csv(RAW_DIR/f"{ticker}.csv", index=False)
    print(df.head())

print("Done")
