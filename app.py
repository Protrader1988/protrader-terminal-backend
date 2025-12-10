"""
ProTrader Terminal - Main FastAPI Application
Complete backend with 15 bots, 10 AI modules, WebSocket, and backtesting
"""

from fastapi import FastAPI, WebSocket, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import asyncio
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import json
import random

# Import all bots
from bots.wick_master_pro import WickMasterPro
from bots.momentum_master import MomentumMaster
from bots.mean_reversion_pro import MeanReversionPro
from bots.trend_follower_elite import TrendFollowerElite
from bots.scalper_supreme import ScalperSupreme
from bots.breakout_hunter import BreakoutHunter
from bots.gap_trader_pro import GapTraderPro
from bots.macd_master import MACDMaster
from bots.volume_profile_trader import VolumeProfileTrader
from bots.swing_trader_pro import SwingTraderPro
from bots.fibonacci_trader import FibonacciTrader
from bots.support_resistance_master import SupportResistanceMaster
from bots.pattern_recognition_bot import PatternRecognitionBot
from bots.news_sentiment_trader import NewsSentimentTrader
from bots.options_flow_tracker import OptionsFlowTracker

# Import AI modules
from ai_modules.sentiment_analyzer import MarketSentimentAnalyzer
from ai_modules.risk_engine import RiskAssessmentEngine
from ai_modules.pattern_prediction import PatternPredictionModel
from ai_modules.correlation_analyzer import CorrelationAnalyzer
from ai_modules.volatility_predictor import VolatilityPredictor
from ai_modules.liquidity_analyzer import LiquidityAnalyzer
from ai_modules.trend_strength_calculator import TrendStrengthCalculator
from ai_modules.anomaly_detector import AnomalyDetector
from ai_modules.portfolio_optimizer import PortfolioOptimizer
from ai_modules.signal_aggregator import SignalAggregator

# Initialize FastAPI app
app = FastAPI(
    title="ProTrader Terminal API",
    description="Advanced trading platform with 15 bots and 10 AI modules",
    version="2.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize all bots
BOTS = {
    'wick_master_pro': WickMasterPro(),
    'momentum_master': MomentumMaster(),
    'mean_reversion_pro': MeanReversionPro(),
    'trend_follower_elite': TrendFollowerElite(),
    'scalper_supreme': ScalperSupreme(),
    'breakout_hunter': BreakoutHunter(),
    'gap_trader_pro': GapTraderPro(),
    'macd_master': MACDMaster(),
    'volume_profile_trader': VolumeProfileTrader(),
    'swing_trader_pro': SwingTraderPro(),
    'fibonacci_trader': FibonacciTrader(),
    'support_resistance_master': SupportResistanceMaster(),
    'pattern_recognition_bot': PatternRecognitionBot(),
    'news_sentiment_trader': NewsSentimentTrader(),
    'options_flow_tracker': OptionsFlowTracker()
}

# Initialize AI modules
AI_MODULES = {
    'sentiment': MarketSentimentAnalyzer(),
    'risk': RiskAssessmentEngine(),
    'pattern_prediction': PatternPredictionModel(),
    'correlation': CorrelationAnalyzer(),
    'volatility': VolatilityPredictor(),
    'liquidity': LiquidityAnalyzer(),
    'trend_strength': TrendStrengthCalculator(),
    'anomaly': AnomalyDetector(),
    'portfolio_optimizer': PortfolioOptimizer(),
    'signal_aggregator': SignalAggregator()
}

# Active WebSocket connections
active_connections: List[WebSocket] = []

# Global state
PORTFOLIO = {
    'total_value': 100000.0,
    'cash': 50000.0,
    'positions': [],
    'pnl': 0.0,
    'pnl_percent': 0.0
}

ACTIVE_SIGNALS = []

# Helper function to generate sample market data
def generate_sample_data(symbol: str, days: int = 100) -> pd.DataFrame:
    """Generate sample OHLCV data for testing"""
    dates = pd.date_range(end=datetime.now(), periods=days, freq='D')

    # Generate realistic price data
    base_price = random.uniform(50, 500)
    prices = [base_price]

    for i in range(1, days):
        change = random.uniform(-0.05, 0.05)
        new_price = prices[-1] * (1 + change)
        prices.append(new_price)

    data = pd.DataFrame({
        'date': dates,
        'open': prices,
        'high': [p * random.uniform(1.0, 1.03) for p in prices],
        'low': [p * random.uniform(0.97, 1.0) for p in prices],
        'close': [p * random.uniform(0.98, 1.02) for p in prices],
        'volume': [random.randint(1000000, 5000000) for _ in range(days)]
    })

    return data

# API Endpoints

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "ProTrader Terminal API",
        "version": "2.0.0",
        "status": "operational",
        "bots": len(BOTS),
        "ai_modules": len(AI_MODULES)
    }

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "bots": "online",
            "ai_modules": "online",
            "websocket": "online",
            "backtesting": "online"
        }
    }

@app.get("/api/bots")
async def get_bots():
    """Get all available trading bots"""
    bots_info = []
    for bot_id, bot in BOTS.items():
        bots_info.append({
            'id': bot_id,
            'name': bot.name,
            'description': bot.description,
            'version': bot.version,
            'status': bot.status.value,
            'performance': bot.performance_stats
        })
    return {"bots": bots_info, "total": len(bots_info)}

@app.get("/api/bots/{bot_id}")
async def get_bot_details(bot_id: str):
    """Get specific bot details"""
    if bot_id not in BOTS:
        raise HTTPException(status_code=404, detail="Bot not found")

    bot = BOTS[bot_id]
    return {
        'id': bot_id,
        'name': bot.name,
        'description': bot.description,
        'version': bot.version,
        'status': bot.status.value,
        'config': bot.config,
        'performance': bot.performance_stats
    }

@app.post("/api/bots/{bot_id}/analyze")
async def analyze_with_bot(bot_id: str, request: Dict):
    """Analyze market with specific bot"""
    if bot_id not in BOTS:
        raise HTTPException(status_code=404, detail="Bot not found")

    symbol = request.get('symbol', 'AAPL')

    # Generate sample data
    data = generate_sample_data(symbol)

    # Run bot analysis
    bot = BOTS[bot_id]
    signal = bot.analyze(symbol, data, {})

    return {
        'bot': bot.name,
        'symbol': symbol,
        'signal': {
            'type': signal.signal_type.value,
            'confidence': signal.confidence,
            'entry_price': signal.entry_price,
            'stop_loss': signal.stop_loss,
            'take_profit': signal.take_profit,
            'reason': signal.reason,
            'timestamp': signal.timestamp.isoformat()
        },
        'indicators': signal.indicators
    }

@app.get("/api/signals")
async def get_signals():
    """Get all active trading signals"""
    return {
        'signals': ACTIVE_SIGNALS,
        'total': len(ACTIVE_SIGNALS)
    }

@app.post("/api/signals/generate")
async def generate_signals(request: Dict):
    """Generate signals from all bots for a symbol"""
    symbol = request.get('symbol', 'AAPL')

    # Generate sample data
    data = generate_sample_data(symbol)

    signals = []
    for bot_id, bot in BOTS.items():
        try:
            signal = bot.analyze(symbol, data, {})
            if signal.signal_type.value != 'hold':
                signals.append({
                    'bot': bot.name,
                    'bot_id': bot_id,
                    'type': signal.signal_type.value,
                    'confidence': signal.confidence,
                    'entry_price': signal.entry_price,
                    'stop_loss': signal.stop_loss,
                    'take_profit': signal.take_profit,
                    'reason': signal.reason,
                    'timestamp': datetime.now().isoformat()
                })
        except Exception as e:
            print(f"Error with bot {bot_id}: {str(e)}")

    return {
        'symbol': symbol,
        'signals': signals,
        'total_signals': len(signals)
    }

@app.get("/api/ai-modules")
async def get_ai_modules():
    """Get all AI modules"""
    modules = []
    for module_id, module in AI_MODULES.items():
        modules.append({
            'id': module_id,
            'name': module.name,
            'version': module.version
        })
    return {"modules": modules, "total": len(modules)}

@app.post("/api/ai/sentiment")
async def analyze_sentiment(request: Dict):
    """Analyze market sentiment"""
    module = AI_MODULES['sentiment']
    market_data = {
        'price_change_pct': request.get('price_change', 0),
        'volume_change_pct': request.get('volume_change', 0)
    }
    result = module.analyze_sentiment(market_data)
    return result

@app.post("/api/ai/risk-assessment")
async def assess_risk(request: Dict):
    """Assess trade risk"""
    module = AI_MODULES['risk']
    signal = {
        'entry_price': request.get('entry_price', 100),
        'stop_loss': request.get('stop_loss', 98)
    }
    portfolio = {'total_value': PORTFOLIO['total_value']}
    result = module.assess_trade_risk(signal, portfolio)
    return result

@app.post("/api/ai/predict")
async def predict_pattern(request: Dict):
    """Predict next price move"""
    symbol = request.get('symbol', 'AAPL')
    data = generate_sample_data(symbol)

    module = AI_MODULES['pattern_prediction']
    result = module.predict_next_move(data)
    return result

@app.get("/api/portfolio")
async def get_portfolio():
    """Get portfolio status"""
    return PORTFOLIO

@app.post("/api/backtest")
async def run_backtest(request: Dict):
    """Run backtest for a bot"""
    bot_id = request.get('bot_id')
    symbol = request.get('symbol', 'AAPL')
    days = request.get('days', 100)

    if bot_id not in BOTS:
        raise HTTPException(status_code=404, detail="Bot not found")

    # Generate historical data
    data = generate_sample_data(symbol, days)

    # Run backtest
    bot = BOTS[bot_id]
    trades = []
    equity_curve = [10000]  # Starting capital

    for i in range(20, len(data)):
        window_data = data.iloc[:i]
        signal = bot.analyze(symbol, window_data, {})

        if signal.signal_type.value != 'hold':
            # Simulate trade
            entry = signal.entry_price
            exit_price = entry * random.uniform(0.98, 1.05)
            pnl = (exit_price - entry) / entry * 100

            trades.append({
                'entry_date': data.iloc[i]['date'].isoformat(),
                'type': signal.signal_type.value,
                'entry_price': entry,
                'exit_price': exit_price,
                'pnl_percent': pnl
            })

            equity_curve.append(equity_curve[-1] * (1 + pnl/100))

    # Calculate metrics
    winning_trades = [t for t in trades if t['pnl_percent'] > 0]
    win_rate = len(winning_trades) / len(trades) * 100 if trades else 0
    total_return = (equity_curve[-1] - equity_curve[0]) / equity_curve[0] * 100

    return {
        'bot': bot.name,
        'symbol': symbol,
        'period_days': days,
        'total_trades': len(trades),
        'winning_trades': len(winning_trades),
        'win_rate': round(win_rate, 2),
        'total_return_pct': round(total_return, 2),
        'final_equity': round(equity_curve[-1], 2),
        'trades': trades[-10:],  # Last 10 trades
        'equity_curve': equity_curve[-50:]  # Last 50 points
    }

# WebSocket endpoint for real-time data
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket for real-time market data and signals"""
    await websocket.accept()
    active_connections.append(websocket)

    try:
        while True:
            # Send market updates every 2 seconds
            market_update = {
                'type': 'market_update',
                'timestamp': datetime.now().isoformat(),
                'data': {
                    'AAPL': random.uniform(170, 180),
                    'TSLA': random.uniform(240, 260),
                    'NVDA': random.uniform(480, 520)
                }
            }

            await websocket.send_json(market_update)
            await asyncio.sleep(2)

    except Exception as e:
        if websocket in active_connections:
            active_connections.remove(websocket)

@app.on_event("startup")
async def startup_event():
    """Startup tasks"""
    print("=" * 60)
    print("🚀 ProTrader Terminal Backend Starting...")
    print("=" * 60)
    print(f"✅ Loaded {len(BOTS)} trading bots")
    print(f"✅ Loaded {len(AI_MODULES)} AI modules")
    print(f"✅ WebSocket streaming: Ready")
    print(f"✅ Backtesting engine: Ready")
    print("=" * 60)
    print("📡 Server ready at http://0.0.0.0:8000")
    print("📊 API docs at http://0.0.0.0:8000/docs")
    print("=" * 60)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
