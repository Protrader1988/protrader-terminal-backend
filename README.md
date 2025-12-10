# ProTrader Terminal Backend

Advanced trading platform backend with 15 trading bots, 10 AI modules, WebSocket streaming, and backtesting engine.

## 🚀 Features

### 15 Trading Bots
1. **WickMasterPro** - Wick rejection and reversal patterns
2. **MomentumMaster** - High-momentum breakout trading
3. **MeanReversionPro** - Statistical mean reversion
4. **TrendFollowerElite** - Multi-timeframe trend following
5. **ScalperSupreme** - High-frequency scalping
6. **BreakoutHunter** - Volatility breakout specialist
7. **GapTraderPro** - Gap fill trading
8. **MACDMaster** - MACD crossover system
9. **VolumeProfileTrader** - Volume-based trading
10. **SwingTraderPro** - Multi-day swing trades
11. **FibonacciTrader** - Fibonacci retracement levels
12. **SupportResistanceMaster** - Classic S/R trading
13. **PatternRecognitionBot** - Chart pattern detection
14. **NewsSentimentTrader** - Sentiment-driven trading
15. **OptionsFlowTracker** - Options flow analysis

### 10 AI Modules
1. Market Sentiment Analyzer
2. Risk Assessment Engine
3. Pattern Prediction Model
4. Correlation Analyzer
5. Volatility Predictor
6. Liquidity Analyzer
7. Trend Strength Calculator
8. Anomaly Detector
9. Portfolio Optimizer
10. Signal Aggregator

### Additional Features
- ✅ WebSocket streaming for real-time data
- ✅ Backtesting engine with performance metrics
- ✅ Portfolio management
- ✅ Risk assessment and position sizing
- ✅ RESTful API with 20+ endpoints
- ✅ CORS enabled for frontend integration

## 📦 Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Run the server
python app.py
```

## 🔌 API Endpoints

### Core Endpoints
- `GET /` - Root endpoint
- `GET /api/health` - Health check
- `GET /api/bots` - List all bots
- `GET /api/bots/{bot_id}` - Get bot details
- `POST /api/bots/{bot_id}/analyze` - Analyze with specific bot

### Signal Generation
- `GET /api/signals` - Get active signals
- `POST /api/signals/generate` - Generate signals for symbol

### AI Modules
- `GET /api/ai-modules` - List all AI modules
- `POST /api/ai/sentiment` - Analyze sentiment
- `POST /api/ai/risk-assessment` - Assess trade risk
- `POST /api/ai/predict` - Predict price movement

### Portfolio & Trading
- `GET /api/portfolio` - Get portfolio status
- `POST /api/backtest` - Run backtest

### WebSocket
- `WS /ws` - Real-time market data stream

## 🧪 Testing

```bash
# Run tests
pytest

# Test specific bot
curl http://localhost:8000/api/bots/wick_master_pro

# Generate signals
curl -X POST http://localhost:8000/api/signals/generate \
  -H "Content-Type: application/json" \
  -d '{"symbol": "AAPL"}'
```

## 📊 Usage Example

```python
import requests

# Get all bots
response = requests.get("http://localhost:8000/api/bots")
print(response.json())

# Analyze with WickMasterPro
response = requests.post(
    "http://localhost:8000/api/bots/wick_master_pro/analyze",
    json={"symbol": "AAPL"}
)
signal = response.json()
print(f"Signal: {signal['signal']['type']} - Confidence: {signal['signal']['confidence']}")

# Run backtest
response = requests.post(
    "http://localhost:8000/api/backtest",
    json={"bot_id": "wick_master_pro", "symbol": "AAPL", "days": 100}
)
results = response.json()
print(f"Win Rate: {results['win_rate']}% - Total Return: {results['total_return_pct']}%")
```

## 🏗️ Project Structure

```
protrader_backend/
├── app.py                      # Main FastAPI application
├── requirements.txt            # Python dependencies
├── bots/                       # Trading bots
│   ├── base_bot.py            # Base bot class
│   ├── wick_master_pro.py     # Bot 1
│   ├── momentum_master.py     # Bot 2
│   └── ...                    # Bots 3-15
├── ai_modules/                # AI modules
│   ├── sentiment_analyzer.py
│   ├── risk_engine.py
│   └── ...                    # Modules 3-10
└── README.md                  # This file
```

## 🔧 Configuration

Each bot has configurable parameters in its `config` dictionary:

```python
# Example: WickMasterPro config
{
    'min_wick_ratio': 2.5,
    'min_volume_spike': 1.3,
    'lookback_period': 20,
    'confidence_threshold': 0.7,
    'risk_reward_ratio': 2.0
}
```

## 📈 Performance Metrics

The backtesting engine provides:
- Total trades executed
- Win rate percentage
- Total return percentage
- Equity curve
- Individual trade details
- Risk-adjusted returns

## 🌐 Frontend Integration

This backend is designed to work with the ProTrader Terminal frontend. The frontend is already deployed at:
https://i7pav0yhg2.fellou.io/protrader-terminal-wickmasterpro-edition-icM7cDL_

## 🚦 Status

✅ **PRODUCTION READY**
- All 15 bots implemented and tested
- All 10 AI modules operational
- WebSocket streaming functional
- Backtesting engine working
- Full REST API available

## 📝 License

Proprietary - ProTrader Terminal

## 👥 Support

For issues or questions, contact the development team.
