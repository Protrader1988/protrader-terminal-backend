"""
Momentum Bot - Breakout and Momentum Trading Strategy
Capitalizes on strong directional moves and breakouts
"""

import pandas as pd
import numpy as np
from typing import Dict, Tuple
from datetime import datetime

from bots.base_bot import BaseBot, TradingSignal, SignalType

class MomentumBot(BaseBot):
    """Momentum breakout trading bot"""
    
    def __init__(self):
        super().__init__(
            name="Momentum Bot",
            description="Breakout and momentum trading strategy",
            version="1.0"
        )
        
        self.config = {
            'momentum_period': 14,
            'breakout_period': 20,
            'volume_threshold': 1.5,
            'min_confidence': 0.65,
            'rsi_oversold': 30,
            'rsi_overbought': 70
        }
    
    def analyze(self, symbol: str, data: pd.DataFrame, market_data: Dict) -> TradingSignal:
        """Analyze for momentum opportunities"""
        try:
            indicators = self.calculate_indicators(data)
            latest = data.iloc[-1]
            
            signal_type = SignalType.HOLD
            confidence = 0.0
            reason = "No momentum signal"
            
            # Check for bullish breakout
            if (latest['close'] > indicators['resistance'] and 
                indicators['rsi'] < self.config['rsi_overbought'] and
                indicators['volume_ratio'] > self.config['volume_threshold']):
                
                signal_type = SignalType.BUY
                confidence = 0.75
                reason = f"Bullish breakout above ${indicators['resistance']:.2f}"
            
            # Check for bearish breakout
            elif (latest['close'] < indicators['support'] and 
                  indicators['rsi'] > self.config['rsi_oversold'] and
                  indicators['volume_ratio'] > self.config['volume_threshold']):
                
                signal_type = SignalType.SELL
                confidence = 0.75
                reason = f"Bearish breakdown below ${indicators['support']:.2f}"
            
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
        """Calculate momentum indicators"""
        period = self.config['breakout_period']
        
        # Calculate RSI
        delta = data['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        # Support/Resistance
        resistance = data['high'].rolling(window=period).max().iloc[-1]
        support = data['low'].rolling(window=period).min().iloc[-1]
        
        # Volume
        avg_volume = data['volume'].rolling(window=20).mean().iloc[-1]
        current_volume = data['volume'].iloc[-1]
        volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1.0
        
        return {
            'rsi': rsi.iloc[-1],
            'resistance': resistance,
            'support': support,
            'volume_ratio': volume_ratio,
            'price': data['close'].iloc[-1]
        }
    
    def validate_signal(self, signal: TradingSignal, market_data: Dict) -> bool:
        """Validate signal"""
        return signal.confidence >= self.config['min_confidence']
    
    def calculate_position_size(self, signal: TradingSignal, portfolio_value: float, 
                               risk_per_trade: float) -> float:
        """Calculate position size"""
        risk_amount = portfolio_value * risk_per_trade
        price_risk = abs(signal.entry_price - signal.stop_loss)
        if price_risk == 0:
            return 0.0
        shares = risk_amount / price_risk
        return min(shares * signal.entry_price, portfolio_value * 0.25)
    
    def get_risk_parameters(self, symbol: str, entry_price: float, 
                          signal_type: SignalType) -> Tuple[float, float]:
        """Calculate stop loss and take profit"""
        stop_pct = 0.025  # 2.5%
        target_pct = 0.05  # 5% (2:1 RR)
        
        if signal_type == SignalType.BUY:
            return (entry_price * (1 - stop_pct), entry_price * (1 + target_pct))
        else:
            return (entry_price * (1 + stop_pct), entry_price * (1 - target_pct))
    
    def get_best_market_conditions(self) -> list:
        return ["Trending markets", "High volume", "Clear breakouts"]
    
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
