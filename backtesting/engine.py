from strategies.loader import load_strategy
from data.providers.alpaca_data import get_bars as stocks_bars
from data.providers.gemini_data import get_bars as crypto_bars
from src.trading.metrics import evaluate_signals

def fetch(symbol, timeframe, start=None, end=None):
    return crypto_bars(symbol, timeframe, start, end) if "/" in symbol else stocks_bars(symbol, timeframe, start, end)

def run(strategy: str, symbol: str, timeframe: str, start=None, end=None, params=None, initial_cash=10000.0):
    candles = fetch(symbol, timeframe, start, end)
    strat = load_strategy(strategy, params or {})
    signals = strat.generate_signals(candles=candles, symbol=symbol, timeframe=timeframe)
    summary = evaluate_signals(candles, signals, initial_cash=initial_cash)
    return {"signals": signals, "summary": summary}
