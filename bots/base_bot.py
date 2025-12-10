from enum import Enum
from datetime import datetime
from typing import Dict, Optional
from dataclasses import dataclass

class SignalType(Enum):
    BUY = "buy"
    SELL = "sell"
    HOLD = "hold"

class BotStatus(Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    ERROR = "error"

@dataclass
class TradingSignal:
    signal_type: SignalType
    symbol: str
    confidence: float
    entry_price: float
    stop_loss: float
    take_profit: float
    position_size: float
    timestamp: datetime
    reason: str
    indicators: Dict
    metadata: Optional[Dict] = None

class BaseBot:
    def __init__(self, name: str, description: str, version: str):
        self.name = name
        self.description = description
        self.version = version
        self.last_signal_time = None
        self.status = BotStatus.ACTIVE
