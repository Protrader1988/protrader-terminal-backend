"""
News Sentinel Bot - News-driven trading strategy
Trades based on news sentiment and market reactions
"""

import pandas as pd
from typing import Dict, Tuple
from datetime import datetime
from bots.base_bot import BaseBot, TradingSignal, SignalType

class NewsSentinelBot(BaseBot):
    """News-driven trading bot"""
    
    def __init__(self):
        super().__init__(
            name="News Sentinel Bot",
            description="News sentiment and event-driven trading",
            version="1.0"
        )
        self.config = {
            'sentiment_threshold': 0.6,
            'volume_spike_threshold': 2.0,
            'news_impact_window': 30  # minutes
        }
    
    def analyze(self, symbol: str, data: pd.DataFrame, market_data: Dict) -> TradingSignal:
        try:
            indicators = self.calculate_indicators(data)
            latest = data.iloc[-1]
            
            signal_type = SignalType.HOLD
            confidence = 0.0
            reason = "No news catalyst"
            
            sentiment = market_data.get('news_sentiment', 0)
            volume_spike = indicators.get('volume_ratio', 1.0)
            
            # Positive news + volume spike
            if sentiment > self.config['sentiment_threshold'] and volume_spike > self.config['volume_spike_threshold']:
                signal_type = SignalType.BUY
                confidence = 0.75
                reason = f"Positive news sentiment ({sentiment:.2f}) with {volume_spike:.1f}x volume"
            
            # Negative news + volume spike
            elif sentiment < -self.config['sentiment_threshold'] and volume_spike > self.config['volume_spike_threshold']:
                signal_type = SignalType.SELL
                confidence = 0.75
                reason = f"Negative news sentiment ({sentiment:.2f}) with {volume_spike:.1f}x volume"
            
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
        avg_volume = data['volume'].rolling(window=20).mean().iloc[-1]
        current_volume = data['volume'].iloc[-1]
        volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1.0
        
        price_change = data['close'].pct_change(5).iloc[-1]
        
        return {
            'volume_ratio': volume_ratio,
            'price_change': price_change,
            'price': data['close'].iloc[-1]
        }
    
    def validate_signal(self, signal: TradingSignal, market_data: Dict) -> bool:
        return signal.confidence >= 0.70
    
    def calculate_position_size(self, signal: TradingSignal, portfolio_value: float, risk_per_trade: float) -> float:
        risk_amount = portfolio_value * risk_per_trade
        price_risk = abs(signal.entry_price - signal.stop_loss)
        if price_risk == 0:
            return 0.0
        shares = risk_amount / price_risk
        return min(shares * signal.entry_price, portfolio_value * 0.20)
    
    def get_risk_parameters(self, symbol: str, entry_price: float, signal_type: SignalType) -> Tuple[float, float]:
        stop_pct = 0.03  # 3% stop
        target_pct = 0.06  # 6% target (2:1 RR)
        if signal_type == SignalType.BUY:
            return (entry_price * (1 - stop_pct), entry_price * (1 + target_pct))
        return (entry_price * (1 + stop_pct), entry_price * (1 - target_pct))
    
    def get_best_market_conditions(self) -> list:
        return ["Earnings season", "Major news events", "High volatility"]
