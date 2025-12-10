from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

def fetch_headlines(tickers):
    # Placeholder headlines; replace with your news API of choice.
    items = []
    for t in tickers:
        items.append({"ticker": t, "title": f"{t} rallies on strong demand", "summary": f"Analysts positive on {t} outlook."})
        items.append({"ticker": t, "title": f"{t} faces regulatory scrutiny", "summary": f"Short-term volatility for {t} expected."})
    return items

_analyzer = SentimentIntensityAnalyzer()

def simple_sentiment(text: str):
    s = _analyzer.polarity_scores(text or "")
    return {"compound": s["compound"], "pos": s["pos"], "neu": s["neu"], "neg": s["neg"]}
