import time, yaml
from strategies.loader import load_strategy
from data.providers.alpaca_data import get_bars as stocks_bars
from data.providers.gemini_data import get_bars as crypto_bars
from src.trading.execution_router import ExecutionRouter

def fetch(symbol, timeframe):
    return crypto_bars(symbol, timeframe) if "/" in symbol else stocks_bars(symbol, timeframe)

def main():
    with open("config/strategies.yaml","r") as f:
        cfg = yaml.safe_load(f)

    uni = cfg.get("universe", [])
    strategies = [s for s in cfg.get("strategies", []) if s.get("enabled",True)]
    router = ExecutionRouter()

    print("Paper trader running…")
    while True:
        for s in strategies:
            name=s["name"]; tf=s.get("timeframe","1h"); params=s.get("params",{}); qty=float(s.get("paper_qty",0.001))
            strat = load_strategy(name, params)
            for sym in uni:
                candles = fetch(sym, tf)
                if not candles: 
                    print(f"[{name}] no candles for {sym}/{tf}"); continue
                signals = strat.generate_signals(candles=candles, symbol=sym, timeframe=tf)
                for sig in signals[-3:]:  # act on last few signals only
                    side=sig.get("side"); px=sig.get("price") or candles[-1]["c"]
                    if side in ("buy","sell"):
                        resp = router.submit(side, sym, qty, order_type="market", price=None)
                        print("EXEC", name, sym, side, qty, "->", resp.get("status"))
        time.sleep(60)

if __name__=="__main__":
    main()
