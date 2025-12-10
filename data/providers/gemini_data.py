import os, requests
BASE=os.getenv("GEMINI_BASE_URL","https://api.sandbox.gemini.com")
_TF={"1m":"1m","5m":"5m","15m":"15m","30m":"30m","1h":"1hr","6h":"6hr","1d":"1day","1D":"1day"}
def get_bars(symbol, timeframe, start=None, end=None):
    sym=symbol.replace("/","").lower(); tf=_TF.get(timeframe,timeframe)
    r=requests.get(f"{BASE}/v2/candles/{sym}/{tf}", timeout=15)
    if not r.ok: return []
    raw=list(reversed(r.json() or [])) # newest-last
    return [{"t":int(ts),"o":float(o),"h":float(h),"l":float(l),"c":float(c),"v":float(v)} for ts,o,h,l,c,v in raw]
