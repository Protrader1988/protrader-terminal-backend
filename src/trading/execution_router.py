from brokers.alpaca_client import AlpacaClient
from brokers.gemini_client import GeminiClient

class ExecutionRouter:
    def __init__(self): 
        self.alpaca=AlpacaClient(); self.gemini=GeminiClient()
    @staticmethod
    def asset_type(symbol:str)->str:
        s=symbol.lower(); return "crypto" if "/" in s or s.endswith(("usd","usdt","btc","eth")) else "stock"
    def submit(self, side, symbol, qty, order_type="market", price=None):
        if self.asset_type(symbol)=="crypto":
            return self.gemini.submit_order(side, symbol, qty, order_type, price)
        return self.alpaca.submit_order(side, symbol, qty, order_type, "gtc", limit_price=price)
