def drawdown(equity_curve):
    peak = -1e9; dd = 0.0
    for v in equity_curve:
        if v > peak: peak = v
        dd = min(dd, (v/peak - 1.0) if peak>0 else 0.0)
    return dd
