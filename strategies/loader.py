import importlib

class StrategyAdapter:
    def __init__(self, impl, params=None):
        self.impl = impl
        self.params = params or {}

    def generate_signals(self, candles, symbol, timeframe):
        for fn in ("generate_signals","run","infer"):
            if hasattr(self.impl, fn):
                return getattr(self.impl, fn)(candles=candles, symbol=symbol, timeframe=timeframe, **self.params) or []
        if hasattr(self.impl, "predict_signals"):
            return self.impl.predict_signals(candles, symbol, timeframe, **self.params) or []
        raise RuntimeError("Strategy does not expose a supported entrypoint.")

def load_strategy(name: str, params=None) -> StrategyAdapter:
    mod = importlib.import_module(f"strategies.{name}")
    impl = getattr(mod, "Strategy", None)
    instance = impl(**(params or {})) if callable(impl) else mod
    return StrategyAdapter(instance, params)
