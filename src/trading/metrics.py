def evaluate_signals(candles, signals, initial_cash=10000.0):
    cash = initial_cash; pos = 0.0; last_price = candles[-1]["c"] if candles else 0.0
    for s in signals:
        px = float(s.get("price", last_price))
        if s["side"] == "buy" and cash > 0:
            qty = cash / px
            pos += qty; cash -= qty*px
        elif s["side"] == "sell" and pos > 0:
            cash += pos*px; pos = 0.0
    nav = cash + pos*last_price
    return {"initial": initial_cash, "final": round(nav,2), "return_pct": round((nav/initial_cash-1)*100, 2)}
