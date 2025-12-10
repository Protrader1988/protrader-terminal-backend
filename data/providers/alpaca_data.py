import os, requests, datetime as dt
DATA_BASE=os.getenv("ALPACA_DATA_BASE","https://data.alpaca.markets")
ALPACA_KEY=os.getenv("ALPACA_API_KEY",""); ALPACA_SECRET=os.getenv("ALPACA_SECRET_KEY","")
_TF={"1m":"1Min","5m":"5Min","15m":"15Min","30m":"30Min","1h":"1Hour","1d":"1Day","1D":"1Day"}
def _iso(x): 
    if isinstance(x,(int,float)): return dt.datetime.utcfromtimestamp(x/1000).isoformat()
    return str(x)
def get_bars(symbol, timeframe, start=None, end=None):
    tf=_TF.get(timeframe,timeframe); url=f"{DATA_BASE}/v2/stocks/{symbol.upper()}/bars"
    params={"timeframe":tf}; 
    if start: params["start"]=_iso(start)
    if end: params["end"]=_iso(end)
    s=requests.Session(); s.headers.update({"APCA-API-KEY-ID":ALPACA_KEY,"APCA-API-SECRET-KEY":ALPACA_SECRET})
    r=s.get(url,params=params,timeout=20); 
    if not r.ok: return []
    bars=r.json().get("bars",[]); out=[]
    for b in bars:
        ts=b["t"].replace("Z",""); epoch=int(dt.datetime.fromisoformat(ts).timestamp()*1000)
        out.append({"t":epoch,"o":float(b["o"]),"h":float(b["h"]),"l":float(b["l"]),"c":float(b["c"]),"v":float(b["v"])})
    return out
