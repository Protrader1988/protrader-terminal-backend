"""
Fibonacci Retracement Trader - Fibonacci level trading
"""

import pandas as pd
import numpy as np
from typing import Dict, Tuple
from datetime import datetime
from bots.base_bot import BaseBot, TradingSignal, SignalType, BotStatus

class FibonacciTrader(BaseBot):
    """Trades bounces and rejections at Fibonacci levels"""

    def __init__(self):
        super().__init__(
            name="Fibonacci Trader",
            description="Fibonacci retracement level trading",
            version="1.0"
        )
        self.config = {
            'lookback': 50,
            'fib_tolerance': 0.005,
            'key_levels': [0.236, 0.382, 0.500, 0.618, 0.786]
        }

    def analyze(self, symbol: str, data: pd.DataFrame, market_data: Dict) -> TradingSignal:
        try:
            indicators = self.calculate_indicators(data)
            latest = data.iloc[-1]

            signal_type = SignalType.HOLD
            confidence = 0.0
            reason = "No Fibonacci signal"

            at_fib_level = indicators['at_fib_level']
            fib_level = indicators['fib_level']
            trend = indicators['trend']

            if at_fib_level:
                if trend == 'uptrend' and fib_level in [0.382, 0.500, 0.618]:
                    signal_type = SignalType.BUY
                    confidence = 0.77
                    reason = f"Fib {fib_level} retracement in uptrend"
                elif trend == 'downtrend' and fib_level in [0.382, 0.500, 0.618]:
                    signal_type = SignalType.SELL
                    confidence = 0.77
                    reason = f"Fib {fib_level} retracement in downtrend"

            if signal_type != SignalType.HOLD:
                entry_price = latest['close']
                stop_loss, take_profit = self.get_risk_parameters(symbol, entry_price, signal_type)

                return TradingSignal(
                    signal_type=signal_type,
                    symbol=symbol,
                    confidence=confidence,
                    entry_price=entry_price,
                    stop_loss=stop_loss,
                    take_profit=take_profit,
                    position_size=0.0,
                    timestamp=datetime.now(),
                    reason=reason,
                    indicators=indicators
                )

            return TradingSignal(
                signal_type=SignalType.HOLD,
                symbol=symbol,
                confidence=0.0,
                entry_price=latest['close'],
                stop_loss=0.0,
                take_profit=0.0,
                position_size=0.0,
                timestamp=datetime.now(),
                reason=reason,
                indicators=indicators
            )
        except Exception as e:
            return self._create_error_signal(symbol, str(e))

    def calculate_indicators(self, data: pd.DataFrame) -> Dict:
        recent = data.tail(self.config['lookback'])
        high = recent['high'].max()
        low = recent['low'].min()
        current_price = data['close'].iloc[-1]

        diff = high - low
        fib_levels = {level: high - (diff * level) for level in self.config['key_levels']}

        at_fib_level = False
        fib_level = None
        for level, price in fib_levels.items():
            if abs(current_price - price) / current_price < self.config['fib_tolerance']:
                at_fib_level = True
                fib_level = level
                break

        sma_20 = data['close'].rolling(window=20).mean().iloc[-1]
        trend = 'uptrend' if current_price > sma_20 else 'downtrend'

        return {
            'at_fib_level': at_fib_level,
            'fib_level': fib_level,
            'trend': trend,
            'fib_levels': fib_levels,
            'price': current_price
        }

    def validate_signal(self, signal: TradingSignal, market_data: Dict) -> bool:
        return signal.confidence > 0.70

    def get_risk_parameters(self, symbol: str, entry_price: float, signal_type: SignalType) -> Tuple[float, float]:
        stop_distance = entry_price * 0.025
        target_distance = entry_price * 0.07

        if signal_type == SignalType.BUY:
            return (entry_price - stop_distance, entry_price + target_distance)
        else:
            return (entry_price + stop_distance, entry_price - target_distance)

    def _create_error_signal(self, symbol: str, error: str) -> TradingSignal:
        return TradingSignal(
            signal_type=SignalType.HOLD,
            symbol=symbol,
            confidence=0.0,
            entry_price=0.0,
            stop_loss=0.0,
            take_profit=0.0,
            position_size=0.0,
            timestamp=datetime.now(),
            reason=f"Error: {error}",
            indicators={}
        )
