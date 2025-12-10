"""
Grid Trading Bot - Automated grid trading strategy
Places buy and sell orders at predetermined intervals
"""

import pandas as pd
from typing import Dict, Tuple
from datetime import datetime
from bots.base_bot import BaseBot, TradingSignal, SignalType

class GridTradingBot(BaseBot):
    """Grid trading strategy bot"""
    
    def __init__(self):
        super().__init__(
            name="Grid Trading Bot",
            description="Automated grid trading with multiple levels",
            version="1.0"
        )
        self.config = {
            'grid_levels': 10,
            'grid_spacing': 0.02,  # 2% between levels
            'base_size': 1000,
            'range_detection_period': 50
        }
        self.grid_levels_cache = {}
    
    def analyze(self, symbol: str, data: pd.DataFrame, market_data: Dict) -> TradingSignal:
        try:
            indicators = self.calculate_indicators(data)
            latest = data.iloc[-1]
            current_price = latest['close']
            
            signal_type = SignalType.HOLD
            confidence = 0.0
            reason = "Grid levels maintained"
            
            # Check if price hit grid levels
            range_size = indicators['range_high'] - indicators['range_low']
            position_in_range = (current_price - indicators['range_low']) / range_size
            
            # Buy near bottom of range
            if position_in_range < 0.3:
                signal_type = SignalType.BUY
                confidence = 0.70
                reason = f"Price in lower 30% of range (${current_price:.2f})"
            
            # Sell near top of range
            elif position_in_range > 0.7:
                signal_type = SignalType.SELL
                confidence = 0.70
                reason = f"Price in upper 30% of range (${current_price:.2f})"
            
            if signal_type != SignalType.HOLD:
                entry_price = current_price
                stop_loss, take_profit = self.get_risk_parameters(symbol, entry_price, signal_type)
                return TradingSignal(signal_type, symbol, confidence, entry_price,
                                   stop_loss, take_profit, 0.0, datetime.now(), reason, indicators)
            
            return TradingSignal(SignalType.HOLD, symbol, 0.0, current_price,
                               0.0, 0.0, 0.0, datetime.now(), reason, indicators)
        except:
            return TradingSignal(SignalType.HOLD, symbol, 0.0, 0.0, 0.0, 0.0, 0.0, datetime.now(), "Error", {})
    
    def calculate_indicators(self, data: pd.DataFrame) -> Dict:
        period = self.config['range_detection_period']
        
        range_high = data['high'].rolling(window=period).max().iloc[-1]
        range_low = data['low'].rolling(window=period).min().iloc[-1]
        range_middle = (range_high + range_low) / 2
        
        return {
            'range_high': range_high,
            'range_low': range_low,
            'range_middle': range_middle,
            'price': data['close'].iloc[-1]
        }
    
    def validate_signal(self, signal: TradingSignal, market_data: Dict) -> bool:
        return signal.confidence >= 0.65
    
    def calculate_position_size(self, signal: TradingSignal, portfolio_value: float, risk_per_trade: float) -> float:
        # Grid trading uses fixed size per level
        return min(self.config['base_size'], portfolio_value * 0.10)
    
    def get_risk_parameters(self, symbol: str, entry_price: float, signal_type: SignalType) -> Tuple[float, float]:
        grid_spacing = self.config['grid_spacing']
        
        if signal_type == SignalType.BUY:
            stop_loss = entry_price * (1 - grid_spacing * 2)
            take_profit = entry_price * (1 + grid_spacing)
        else:
            stop_loss = entry_price * (1 + grid_spacing * 2)
            take_profit = entry_price * (1 - grid_spacing)
        
        return (stop_loss, take_profit)
    
    def get_best_market_conditions(self) -> list:
        return ["Range-bound markets", "Low volatility", "Sideways trends"]
