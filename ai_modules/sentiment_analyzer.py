"""
Market Sentiment Analyzer - Analyzes overall market sentiment
"""

import pandas as pd
import numpy as np
from typing import Dict, List
from datetime import datetime

class MarketSentimentAnalyzer:
    """Analyzes market sentiment from multiple sources"""

    def __init__(self):
        self.name = "Market Sentiment Analyzer"
        self.version = "1.0"

    def analyze_sentiment(self, market_data: Dict) -> Dict:
        """
        Analyze market sentiment

        Returns:
            Dict with sentiment score (0-1) and analysis
        """
        # Simplified sentiment calculation
        price_momentum = market_data.get('price_change_pct', 0)
        volume_change = market_data.get('volume_change_pct', 0)

        # Calculate sentiment score
        sentiment_score = 0.5  # Neutral baseline

        if price_momentum > 2:
            sentiment_score += 0.2
        elif price_momentum < -2:
            sentiment_score -= 0.2

        if volume_change > 50:
            sentiment_score += 0.1

        sentiment_score = max(0, min(1, sentiment_score))

        return {
            'sentiment_score': sentiment_score,
            'sentiment_label': self._get_sentiment_label(sentiment_score),
            'price_momentum': price_momentum,
            'volume_change': volume_change,
            'timestamp': datetime.now().isoformat()
        }

    def _get_sentiment_label(self, score: float) -> str:
        if score >= 0.7:
            return "Very Bullish"
        elif score >= 0.6:
            return "Bullish"
        elif score >= 0.4:
            return "Neutral"
        elif score >= 0.3:
            return "Bearish"
        else:
            return "Very Bearish"
