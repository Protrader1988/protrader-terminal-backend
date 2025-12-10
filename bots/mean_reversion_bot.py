"""
Mean Reversion Bot - Trading oversold/overbought conditions
Capitalizes on price returning to average
"""

import pandas as pd
import numpy as np
from typing import Dict, Tuple
from datetime import datetime

from bots.base_bot import BaseBot, TradingSignal, SignalType

class MeanReversionBot(BaseBot):
    """Mean reversion trading bot"""
    
    def __init__(self):
        super().__init__(
            name="Mean Reversion Bot",
            description="Mean reversion and oversold/overbought trading",
            version="1.0"
        )
        
        self.config = {
            'bb_period': 20,
            'bb_std': 2.0,
            'rsi_period': 14,
            'rsi_oversold': 30,
            'rsi_overbought': 70,
            'min_confidence': 0.70
        }
    
    def analyze(self, symbol: str, data: pd.DataFrame, market_data: Dict) -> TradingSignal:
        """Analyze for mean reversion opportunities"""
        try:
            indicators = self.calculate_indicators(data)
            latest = data.iloc[-1]
            
            signal_type = SignalType.HOLD
            confidence = 0.0
            reason = "No mean reversion signal"
            
            # Oversold condition - potential buy
            if (latest['close'] < indicators['bb_lower'] and 
                indicators['rsi'] < self.config['rsi_oversold']):
                
                signal_type = SignalType.BUY
                confidence = 0.80
                reason = f"Oversold - RSI: {indicators['rsi']:.1f}, Below BB lower band"
            
            # Overbought condition - potential sell
            elif (latest['close'] > indicators['bb_upper'] and 
                  indicators['rsi'] > self.config['rsi_overbought']):
                
                signal_type = SignalType.SELL
                confidence = 0.80
                reason = f"Overbought - RSI: {indicators['rsi']:.1f}, Above BB upper band"
            
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
            
            return self._create_hold_signal(symbol, latest['close'], reason, indicators)
            
        except Exception as e:
            return self._create_hold_signal(symbol, 0.0, f"Error: {e}", {})
    
    def calculate_indicators(self, data: pd.DataFrame) -> Dict:
        """Calculate mean reversion indicators"""
        # Bollinger Bands
        sma = data['close'].rolling(window=self.config['bb_period']).mean()
        std = data['close'].rolling(window=self.config['bb_period']).std()
        bb_upper = sma + (std * self.config['bb_std'])
        bb_lower = sma - (std * self.config['bb_std'])
        
        # RSI
        delta = data['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=self.config['rsi_period']).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=self.config['rsi_period']).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        return {
            'bb_upper': bb_upper.iloc[-1],
            'bb_middle': sma.iloc[-1],
            'bb_lower': bb_lower.iloc[-1],
            'rsi': rsi.iloc[-1],
            'price': data['close'].iloc[-1]
        }
    
    def validate_signal(self, signal: TradingSignal, market_data: Dict) -> bool:
        return signal.confidence >= self.config['min_confidence']
    
    def calculate_position_size(self, signal: TradingSignal, portfolio_value: float, 
                               risk_per_trade: float) -> float:
        risk_amount = portfolio_value * risk_per_trade
        price_risk = abs(signal.entry_price - signal.stop_loss)
        if price_risk == 0:
            return 0.0
        shares = risk_amount / price_risk
        return min(shares * signal.entry_price, portfolio_value * 0.20)
    
    def get_risk_parameters(self, symbol: str, entry_price: float, 
                          signal_type: SignalType) -> Tuple[float, float]:
        stop_pct = 0.03  # 3%
        target_pct = 0.045  # 4.5% (1.5:1 RR)
        
        if signal_type == SignalType.BUY:
            return (entry_price * (1 - stop_pct), entry_price * (1 + target_pct))
        else:
            return (entry_price * (1 + stop_pct), entry_price * (1 - target_pct))
    
    def get_best_market_conditions(self) -> list:
        return ["Range-bound markets", "Low volatility", "Established support/resistance"]
    
    def _create_hold_signal(self, symbol, price, reason, indicators):
        return TradingSignal(
            signal_type=SignalType.HOLD,
            symbol=symbol,
            confidence=0.0,
            entry_price=price,
            stop_loss=0.0,
            take_profit=0.0,
            position_size=0.0,
            timestamp=datetime.now(),
            reason=reason,
            indicators=indicators
        )
