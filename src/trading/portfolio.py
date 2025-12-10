class Portfolio:
    def __init__(self, cash=10000.0):
        self.cash=cash; self.pos=0.0; self.last=0.0
    def on_signal(self, s):
        px = s.get("price", self.last)
        if s["side"]=="buy" and self.cash>0:
            qty = self.cash/px; self.pos += qty; self.cash -= qty*px; self.last=px
        elif s["side"]=="sell" and self.pos>0:
            self.cash += self.pos*px; self.pos=0.0; self.last=px
    def nav(self, price): return self.cash + self.pos*price
