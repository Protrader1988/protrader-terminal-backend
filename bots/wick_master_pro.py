"""
Wick Master Pro - Advanced Wick Reversal Trading Bot
Specializes in detecting rejection wicks and reversal patterns
"""

import pandas as pd
import numpy as np
from typing import Dict, Tuple
from datetime import datetime

from bots.base_bot import BaseBot, TradingSignal, SignalType, BotStatus

class WickMasterPro(BaseBot):
    """
    Wick Master Pro trading bot.
    
    Strategy:
    - Detects rejection wicks (long wicks with small bodies)
    - Identifies support/resistance levels
    - Trades reversals at key levels
    - Uses volume confirmation
    """
    
    def __init__(self):
        super().__init__(
            name="Wick Master Pro",
            description="Advanced wick rejection and reversal pattern detection bot",
            version="2.0"
        )
        
        # Strategy parameters
        self.config = {
            'min_wick_ratio': 2.5,  # Wick must be 2.5x body size
            'min_volume_spike': 1.3,  # 30% above average volume
            'lookback_period': 20,
            'confidence_threshold': 0.7,
            'risk_reward_ratio': 2.0
        }
    
    def analyze(self, symbol: str, data: pd.DataFrame, market_data: Dict) -> TradingSignal:
        """
        Analyze price data for wick reversal patterns
        
        Args:
            symbol: Trading symbol
            data: OHLCV DataFrame
            market_data: Additional market context
            
        Returns:
            TradingSignal with recommendation
        """
        try:
            # Calculate indicators
            indicators = self.calculate_indicators(data)
            
            # Get latest candle
            latest = data.iloc[-1]
            prev_candle = data.iloc[-2]
            
            # Detect wick patterns
            signal_type = SignalType.HOLD
            confidence = 0.0
            reason = "No clear signal"
            
            # Check for bullish rejection wick (at support)
            if self._is_bullish_rejection_wick(latest, indicators):
                signal_type = SignalType.BUY
                confidence = self._calculate_confidence(latest, indicators, 'bullish')
                reason = f"Bullish rejection wick detected at support ${latest['low']:.2f}"
            
            # Check for bearish rejection wick (at resistance)
            elif self._is_bearish_rejection_wick(latest, indicators):
                signal_type = SignalType.SELL
                confidence = self._calculate_confidence(latest, indicators, 'bearish')
                reason = f"Bearish rejection wick detected at resistance ${latest['high']:.2f}"
            
            # Calculate stop loss and take profit if signal found
            if signal_type != SignalType.HOLD:
                entry_price = latest['close']
                stop_loss, take_profit = self.get_risk_parameters(
                    symbol, entry_price, signal_type
                )
                
                # Create trading signal
                signal = TradingSignal(
                    signal_type=signal_type,
                    symbol=symbol,
                    confidence=confidence,
                    entry_price=entry_price,
                    stop_loss=stop_loss,
                    take_profit=take_profit,
                    position_size=0.0,  # Calculated by risk management
                    timestamp=datetime.now(),
                    reason=reason,
                    indicators=indicators,
                    metadata={
                        'bot': self.name,
                        'wick_ratio': indicators.get('wick_ratio', 0),
                        'volume_ratio': indicators.get('volume_ratio', 0)
                    }
                )
                
                self.last_signal_time = datetime.now()
                return signal
            
            # No signal - return HOLD
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
        """
        Calculate indicators for wick analysis
        
        Args:
            data: OHLCV DataFrame
            
        Returns:
            Dictionary of calculated indicators
        """
        latest = data.iloc[-1]
        
        # Calculate wick sizes
        body_size = abs(latest['close'] - latest['open'])
        upper_wick = latest['high'] - max(latest['open'], latest['close'])
        lower_wick = min(latest['open'], latest['close']) - latest['low']
        
        # Wick ratios
        upper_wick_ratio = upper_wick / body_size if body_size > 0 else 0
        lower_wick_ratio = lower_wick / body_size if body_size > 0 else 0
        
        # Volume analysis
        avg_volume = data['volume'].rolling(window=20).mean().iloc[-1]
        volume_ratio = latest['volume'] / avg_volume if avg_volume > 0 else 1.0
        
        # Support/Resistance levels
        lookback = self.config['lookback_period']
        recent_highs = data['high'].tail(lookback)
        recent_lows = data['low'].tail(lookback)
        
        resistance = recent_highs.max()
        support = recent_lows.min()
        
        # Calculate distance to key levels
        price = latest['close']
        dist_to_resistance = (resistance - price) / price * 100
        dist_to_support = (price - support) / price * 100
        
        return {
            'body_size': body_size,
            'upper_wick': upper_wick,
            'lower_wick': lower_wick,
            'upper_wick_ratio': upper_wick_ratio,
            'lower_wick_ratio': lower_wick_ratio,
            'wick_ratio': max(upper_wick_ratio, lower_wick_ratio),
            'volume_ratio': volume_ratio,
            'support': support,
            'resistance': resistance,
            'dist_to_support': dist_to_support,
            'dist_to_resistance': dist_to_resistance,
            'price': price
        }
    
    def _is_bullish_rejection_wick(self, candle, indicators: Dict) -> bool:
        """Check if candle shows bullish rejection pattern"""
        # Long lower wick (rejection of lower prices)
        lower_wick_ratio = indicators.get('lower_wick_ratio', 0)
        
        # Volume spike
        volume_ratio = indicators.get('volume_ratio', 1.0)
        
        # Near support level
        dist_to_support = indicators.get('dist_to_support', 100)
        
        # Bullish close (closed near high)
        body_position = (candle['close'] - candle['low']) / (candle['high'] - candle['low'])
        
        return (
            lower_wick_ratio >= self.config['min_wick_ratio'] and
            volume_ratio >= self.config['min_volume_spike'] and
            dist_to_support < 2.0 and  # Within 2% of support
            body_position > 0.6  # Closed in upper 40% of range
        )
    
    def _is_bearish_rejection_wick(self, candle, indicators: Dict) -> bool:
        """Check if candle shows bearish rejection pattern"""
        # Long upper wick (rejection of higher prices)
        upper_wick_ratio = indicators.get('upper_wick_ratio', 0)
        
        # Volume spike
        volume_ratio = indicators.get('volume_ratio', 1.0)
        
        # Near resistance level
        dist_to_resistance = indicators.get('dist_to_resistance', 100)
        
        # Bearish close (closed near low)
        body_position = (candle['close'] - candle['low']) / (candle['high'] - candle['low'])
        
        return (
            upper_wick_ratio >= self.config['min_wick_ratio'] and
            volume_ratio >= self.config['min_volume_spike'] and
            dist_to_resistance < 2.0 and  # Within 2% of resistance
            body_position < 0.4  # Closed in lower 40% of range
        )
    
    def _calculate_confidence(self, candle, indicators: Dict, direction: str) -> float:
        """Calculate confidence score for the signal"""
        confidence = 0.5  # Base confidence
        
        # Wick ratio contribution (max +0.2)
        wick_ratio = indicators.get('wick_ratio', 0)
        if wick_ratio > self.config['min_wick_ratio']:
            confidence += min(0.2, (wick_ratio - self.config['min_wick_ratio']) * 0.05)
        
        # Volume contribution (max +0.2)
        volume_ratio = indicators.get('volume_ratio', 1.0)
        if volume_ratio > self.config['min_volume_spike']:
            confidence += min(0.2, (volume_ratio - self.config['min_volume_spike']) * 0.1)
        
        # Level proximity contribution (max +0.1)
        if direction == 'bullish':
            dist = indicators.get('dist_to_support', 100)
        else:
            dist = indicators.get('dist_to_resistance', 100)
        
        if dist < 2.0:
            confidence += 0.1 * (1 - dist / 2.0)
        
        return min(confidence, 0.95)  # Cap at 95%
    
    def validate_signal(self, signal: TradingSignal, market_data: Dict) -> bool:
        """
        Validate trading signal before execution
        
        Args:
            signal: Generated trading signal
            market_data: Current market context
            
        Returns:
            True if valid, False otherwise
        """
        # Check confidence threshold
        if signal.confidence < self.config['confidence_threshold']:
            return False
        
        # Check if market is open
        if market_data.get('market_open', True) == False:
            return False
        
        # Check risk/reward ratio
        entry = signal.entry_price
        stop = signal.stop_loss
        target = signal.take_profit
        
        risk = abs(entry - stop)
        reward = abs(target - entry)
        
        if risk > 0:
            rr_ratio = reward / risk
            if rr_ratio < self.config['risk_reward_ratio']:
                return False
        
        return True
    
    def calculate_position_size(self, signal: TradingSignal, portfolio_value: float, 
                               risk_per_trade: float) -> float:
        """
        Calculate position size based on risk management
        
        Args:
            signal: Trading signal
            portfolio_value: Current portfolio value
            risk_per_trade: Risk per trade (0.01 = 1%)
            
        Returns:
            Position size in dollars
        """
        # Calculate risk amount
        risk_amount = portfolio_value * risk_per_trade
        
        # Calculate price distance to stop loss
        price_risk = abs(signal.entry_price - signal.stop_loss)
        
        if price_risk == 0:
            return 0.0
        
        # Position size = risk amount / price risk per share
        shares = risk_amount / price_risk
        position_size = shares * signal.entry_price
        
        # Cap at maximum position size (20% of portfolio)
        max_position = portfolio_value * 0.20
        position_size = min(position_size, max_position)
        
        return position_size
    
    def get_risk_parameters(self, symbol: str, entry_price: float, 
                          signal_type: SignalType) -> Tuple[float, float]:
        """
        Calculate stop loss and take profit levels
        
        Args:
            symbol: Trading symbol
            entry_price: Entry price
            signal_type: BUY or SELL
            
        Returns:
            Tuple of (stop_loss, take_profit)
        """
        # Use ATR-based stops (simplified: 2% stop, 4% target)
        stop_distance = entry_price * 0.02  # 2% stop loss
        target_distance = entry_price * 0.04  # 4% take profit (2:1 RR)
        
        if signal_type == SignalType.BUY:
            stop_loss = entry_price - stop_distance
            take_profit = entry_price + target_distance
        else:  # SELL
            stop_loss = entry_price + stop_distance
            take_profit = entry_price - target_distance
        
        return (stop_loss, take_profit)
    
    def get_best_market_conditions(self) -> list:
        """Get ideal market conditions for this bot"""
        return [
            "High volatility markets",
            "Clear support/resistance levels",
            "Strong trending markets with pullbacks",
            "Markets with above-average volume"
        ]
    
    def get_asset_preferences(self) -> list:
        """Get preferred asset types"""
        return ["stocks", "crypto", "forex"]
    
    def _create_error_signal(self, symbol: str, error: str) -> TradingSignal:
        """Create error signal"""
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
            indicators={},
            metadata={'error': error}
        )
