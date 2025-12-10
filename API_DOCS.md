# ProTrader Terminal API Documentation

## Base URL
```
http://localhost:8000
```

## Authentication
Currently no authentication required (add JWT if needed)

## Endpoints

### 1. Health Check
**GET** `/api/health`

Response:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00",
  "services": {
    "bots": "online",
    "ai_modules": "online",
    "websocket": "online",
    "backtesting": "online"
  }
}
```

### 2. List All Bots
**GET** `/api/bots`

Response:
```json
{
  "bots": [
    {
      "id": "wick_master_pro",
      "name": "Wick Master Pro",
      "description": "Advanced wick rejection trading",
      "version": "2.0",
      "status": "active",
      "performance": {
        "total_signals": 0,
        "winning_signals": 0,
        "total_pnl": 0.0
      }
    }
  ],
  "total": 15
}
```

### 3. Analyze with Bot
**POST** `/api/bots/{bot_id}/analyze`

Request:
```json
{
  "symbol": "AAPL"
}
```

Response:
```json
{
  "bot": "Wick Master Pro",
  "symbol": "AAPL",
  "signal": {
    "type": "buy",
    "confidence": 0.85,
    "entry_price": 175.50,
    "stop_loss": 172.00,
    "take_profit": 182.00,
    "reason": "Bullish rejection wick at support",
    "timestamp": "2024-01-01T12:00:00"
  },
  "indicators": {
    "wick_ratio": 3.2,
    "volume_ratio": 1.5
  }
}
```

### 4. Generate Signals
**POST** `/api/signals/generate`

Request:
```json
{
  "symbol": "AAPL"
}
```

Response:
```json
{
  "symbol": "AAPL",
  "signals": [
    {
      "bot": "Wick Master Pro",
      "bot_id": "wick_master_pro",
      "type": "buy",
      "confidence": 0.85,
      "entry_price": 175.50,
      "stop_loss": 172.00,
      "take_profit": 182.00,
      "reason": "Bullish rejection wick",
      "timestamp": "2024-01-01T12:00:00"
    }
  ],
  "total_signals": 3
}
```

### 5. Run Backtest
**POST** `/api/backtest`

Request:
```json
{
  "bot_id": "wick_master_pro",
  "symbol": "AAPL",
  "days": 100
}
```

Response:
```json
{
  "bot": "Wick Master Pro",
  "symbol": "AAPL",
  "period_days": 100,
  "total_trades": 45,
  "winning_trades": 28,
  "win_rate": 62.22,
  "total_return_pct": 23.5,
  "final_equity": 12350.00,
  "trades": [...],
  "equity_curve": [...]
}
```

### 6. WebSocket Connection
**WS** `/ws`

Receive real-time market updates:
```json
{
  "type": "market_update",
  "timestamp": "2024-01-01T12:00:00",
  "data": {
    "AAPL": 175.50,
    "TSLA": 245.30,
    "NVDA": 495.20
  }
}
```

## Error Responses

All errors follow this format:
```json
{
  "detail": "Error message here"
}
```

Common status codes:
- `200` - Success
- `404` - Bot/Resource not found
- `422` - Validation error
- `500` - Internal server error
