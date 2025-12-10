"""
Crypto Arbitrage Bot - Cross-exchange arbitrage opportunities
Exploits price differences across exchanges
"""

import pandas as pd
from typing import Dict, Tuple
from datetime import datetime
from bots.base_bot import BaseBot, TradingSignal, SignalType

class CryptoArbitrageBot(BaseBot):
    """Crypto arbitrage trading bot"""
    
    def __init__(self):
        super().__init__(
            name="Crypto Arbitrage Bot",
            description="Cross-exchange cryptocurrency arbitrage",
            version="1.0"
        )
        self.config = {
            'min_spread': 0.01,  # 1% minimum spread
            'max_trade_size': 50000,
            'exchanges': ['binance', 'coinbase', 'kraken']
        }
    
    def analyze(self, symbol: str, data: pd.DataFrame, market_data: Dict) -> TradingSignal:
        try:
            indicators = self.calculate_indicators(data)
            latest = data.iloc[-1]
            
            signal_type = SignalType.HOLD
            confidence = 0.0
            reason = "No arbitrage opportunity"
            
            # Check for arbitrage opportunities (simplified)
            spread = indicators.get('spread', 0)
            if spread > self.config['min_spread']:
                signal_type = SignalType.BUY
                confidence = 0.85
                reason = f"Arbitrage opportunity detected - {spread*100:.2f}% spread"
            
            if signal_type != SignalType.HOLD:
                entry_price = latest['close']
                stop_loss, take_profit = self.get_risk_parameters(symbol, entry_price, signal_type)
                return TradingSignal(signal_type, symbol, confidence, entry_price,
                                   stop_loss, take_profit, 0.0, datetime.now(), reason, indicators)
            
            return TradingSignal(SignalType.HOLD, symbol, 0.0, latest['close'],
                               0.0, 0.0, 0.0, datetime.now(), reason, indicators)
        except:
            return TradingSignal(SignalType.HOLD, symbol, 0.0, 0.0, 0.0, 0.0, 0.0, datetime.now(), "Error", {})
    
    def calculate_indicators(self, data: pd.DataFrame) -> Dict:
        # Simplified spread calculation
        high_low_spread = (data['high'].iloc[-1] - data['low'].iloc[-1]) / data['close'].iloc[-1]
        return {'spread': high_low_spread, 'price': data['close'].iloc[-1]}
    
    def validate_signal(self, signal: TradingSignal, market_data: Dict) -> bool:
        return signal.confidence >= 0.80
    
    def calculate_position_size(self, signal: TradingSignal, portfolio_value: float, risk_per_trade: float) -> float:
        return min(portfolio_value * 0.15, self.config['max_trade_size'])
    
    def get_risk_parameters(self, symbol: str, entry_price: float, signal_type: SignalType) -> Tuple[float, float]:
        stop_pct = 0.002  # 0.2% stop (tight for arbitrage)
        target_pct = 0.01  # 1% target
        if signal_type == SignalType.BUY:
            return (entry_price * (1 - stop_pct), entry_price * (1 + target_pct))
        return (entry_price * (1 + stop_pct), entry_price * (1 - target_pct))
    
    def get_best_market_conditions(self) -> list:
        return ["Crypto markets", "High volatility", "Multiple exchanges"]
    
    def get_asset_preferences(self) -> list:
        return ["crypto"]
