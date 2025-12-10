from flask import Blueprint, request, jsonify
from api.signals import fetch_bars
from strategies.loader import load_strategy
from src.trading.metrics import evaluate_signals

bp = Blueprint("backtest", __name__)

@bp.post("/")
def backtest():
    p = request.get_json(force=True)
    symbol = p.get("symbol","AAPL")
    timeframe = p.get("timeframe","1h")
    strategy = p.get("strategy","wick_master_pro")
    params = p.get("params", {})
    start, end = p.get("start"), p.get("end")
    candles = fetch_bars(symbol, timeframe, start, end)
    strat = load_strategy(strategy, params)
    signals = strat.generate_signals(candles=candles, symbol=symbol, timeframe=timeframe)
    report = evaluate_signals(candles, signals, initial_cash=p.get("initial_cash",10000))
    return jsonify({"symbol": symbol, "timeframe": timeframe, "summary": report})
