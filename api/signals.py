from flask import Blueprint, request, jsonify
from data.providers.alpaca_data import get_bars as stocks_bars
from data.providers.gemini_data import get_bars as crypto_bars
from strategies.loader import load_strategy

bp = Blueprint("signals", __name__)

def fetch_bars(symbol, timeframe, start=None, end=None):
    return crypto_bars(symbol, timeframe, start, end) if "/" in symbol else stocks_bars(symbol, timeframe, start, end)

@bp.post("/run")
def run_signals():
    payload = request.get_json(force=True)
    symbol = payload.get("symbol","AAPL")
    timeframe = payload.get("timeframe","1h")
    strategy = payload.get("strategy","wick_master_pro")
    params = payload.get("params", {})

    candles = fetch_bars(symbol, timeframe, payload.get("start"), payload.get("end"))
    strat = load_strategy(strategy, params)
    signals = strat.generate_signals(candles=candles, symbol=symbol, timeframe=timeframe)
    return jsonify({"symbol": symbol, "timeframe": timeframe, "count": len(signals), "signals": signals})
