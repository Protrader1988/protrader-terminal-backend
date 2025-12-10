"""
Scalping Bot - High-frequency short-term trading
Quick in and out trades for small profits
"""

import pandas as pd
from typing import Dict, Tuple
from datetime import datetime
from bots.base_bot import BaseBot, TradingSignal, SignalType

class ScalpingBot(BaseBot):
    """Scalping bot for quick trades"""
    
    def __init__(self):
        super().__init__(
            name="Scalping Bot",
            description="High-frequency scalping strategy",
            version="1.0"
        )
        self.config = {
            'ema_fast': 5,
            'ema_slow': 15,
            'min_spread': 0.001,
            'target_profit': 0.005
        }
    
    def analyze(self, symbol: str, data: pd.DataFrame, market_data: Dict) -> TradingSignal:
        try:
            indicators = self.calculate_indicators(data)
            latest = data.iloc[-1]
            
            signal_type = SignalType.HOLD
            confidence = 0.0
            reason = "No scalp setup"
            
            if indicators['ema_fast'] > indicators['ema_slow'] and indicators['momentum'] > 0:
                signal_type = SignalType.BUY
                confidence = 0.70
                reason = "Fast EMA crossed above slow EMA with positive momentum"
            elif indicators['ema_fast'] < indicators['ema_slow'] and indicators['momentum'] < 0:
                signal_type = SignalType.SELL
                confidence = 0.70
                reason = "Fast EMA crossed below slow EMA with negative momentum"
            
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
        ema_fast = data['close'].ewm(span=self.config['ema_fast']).mean().iloc[-1]
        ema_slow = data['close'].ewm(span=self.config['ema_slow']).mean().iloc[-1]
        momentum = data['close'].pct_change(5).iloc[-1]
        
        return {'ema_fast': ema_fast, 'ema_slow': ema_slow, 'momentum': momentum, 'price': data['close'].iloc[-1]}
    
    def validate_signal(self, signal: TradingSignal, market_data: Dict) -> bool:
        return signal.confidence >= 0.65
    
    def calculate_position_size(self, signal: TradingSignal, portfolio_value: float, risk_per_trade: float) -> float:
        return min(portfolio_value * 0.10, 10000)  # Small positions for scalping
    
    def get_risk_parameters(self, symbol: str, entry_price: float, signal_type: SignalType) -> Tuple[float, float]:
        stop_pct = 0.005  # 0.5% stop
        target_pct = 0.01  # 1% target (2:1 RR)
        if signal_type == SignalType.BUY:
            return (entry_price * (1 - stop_pct), entry_price * (1 + target_pct))
        return (entry_price * (1 + stop_pct), entry_price * (1 - target_pct))
    
    def get_best_market_conditions(self) -> list:
        return ["High liquidity", "Tight spreads", "Active trading hours"]
