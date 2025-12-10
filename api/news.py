from flask import Blueprint, request, jsonify
from data.providers.news_providers import fetch_headlines, simple_sentiment

bp = Blueprint("news", __name__)

@bp.get("/headlines")
def headlines():
    tickers = request.args.get("tickers","AAPL,MSFT,BTC-USD,ETH-USD").split(",")
    items = fetch_headlines([t.strip() for t in tickers if t.strip()])
    for it in items:
        it["sentiment"] = simple_sentiment(it.get("title","")+it.get("summary",""))
    return jsonify({"count": len(items), "items": items})
