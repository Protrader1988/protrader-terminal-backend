"""
Risk Assessment Engine - Portfolio risk analysis
"""

import pandas as pd
import numpy as np
from typing import Dict, List

class RiskAssessmentEngine:
    """Assesses portfolio and trade risk"""

    def __init__(self):
        self.name = "Risk Assessment Engine"
        self.version = "1.0"

    def assess_trade_risk(self, signal: Dict, portfolio: Dict) -> Dict:
        """
        Assess risk for a potential trade

        Returns:
            Risk assessment with score and recommendations
        """
        entry_price = signal.get('entry_price', 0)
        stop_loss = signal.get('stop_loss', 0)
        portfolio_value = portfolio.get('total_value', 100000)

        # Calculate risk metrics
        risk_per_trade = abs(entry_price - stop_loss) / entry_price if entry_price > 0 else 0
        risk_amount = portfolio_value * 0.02  # 2% risk per trade

        position_size = risk_amount / (abs(entry_price - stop_loss)) if abs(entry_price - stop_loss) > 0 else 0
        position_size = min(position_size * entry_price, portfolio_value * 0.2)  # Max 20% per position

        risk_score = self._calculate_risk_score(risk_per_trade, position_size, portfolio_value)

        return {
            'risk_score': risk_score,
            'risk_level': self._get_risk_level(risk_score),
            'position_size': position_size,
            'risk_per_trade_pct': risk_per_trade * 100,
            'recommended_size': position_size,
            'max_loss': abs(entry_price - stop_loss) * (position_size / entry_price) if entry_price > 0 else 0
        }

    def _calculate_risk_score(self, risk_pct: float, position: float, portfolio: float) -> float:
        score = 50  # Baseline

        if risk_pct > 0.05:  # >5% risk
            score += 30
        elif risk_pct > 0.03:
            score += 20

        position_pct = (position / portfolio) * 100 if portfolio > 0 else 0
        if position_pct > 15:
            score += 20

        return min(100, score)

    def _get_risk_level(self, score: float) -> str:
        if score >= 70:
            return "High Risk"
        elif score >= 40:
            return "Medium Risk"
        else:
            return "Low Risk"
