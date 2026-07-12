"""Test yfinance download"""
import yfinance as yf
import pandas as pd

# Test single symbol
print("Testing single symbol download...")
try:
    data = yf.download("AAPL", period="6mo", interval="1d", progress=False, auto_adjust=True)
    print(f"Type: {type(data)}")
    print(f"Shape: {data.shape if hasattr(data, 'shape') else 'N/A'}")
    if isinstance(data, pd.DataFrame):
        print(f"Columns: {list(data.columns)}")
        print(f"Length: {len(data)}")
        if not data.empty:
            print(f"Close last: {data['Close'].iloc[-1] if 'Close' in data.columns else 'N/A'}")
            print("SUCCESS")
        else:
            print("EMPTY DATAFRAME")
    else:
        print(f"Data: {data}")
except Exception as e:
    print(f"Error: {e}")

# Test multiple with list
print("\nTesting multi-symbol download...")
try:
    data2 = yf.download(["AAPL", "MSFT"], period="6mo", interval="1d", progress=False, group_by="ticker")
    print(f"Type: {type(data2)}")
    if isinstance(data2, pd.DataFrame):
        print(f"Columns multi: {list(data2.columns)}")
        print(f"Shape: {data2.shape}")
    else:
        print(f"Data2: {data2}")
except Exception as e:
    print(f"Error: {e}")
