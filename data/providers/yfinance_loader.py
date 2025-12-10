import yfinance as yf

def get_bars(symbol: str, timeframe: str, start=None, end=None):
    # timeframe map: 1m/5m/15m/30m/1h/1d -> yfinance intervals where possible
    tf_map = {"1m":"1m","5m":"5m","15m":"15m","30m":"30m","1h":"60m","1d":"1d"}
    interval = tf_map.get(timeframe, "1d")
    df = yf.download(symbol, period="60d", interval=interval, progress=False)
    out = []
    for ts, row in df.iterrows():
        out.append({"t": int(ts.timestamp()*1000), "o": float(row["Open"]), "h": float(row["High"]),
                    "l": float(row["Low"]), "c": float(row["Close"]), "v": float(row["Volume"])})
    return out
