import backtrader as bt

class MovingAverageCross(bt.Strategy):
    params = (
        ("fast", 20),
        ("slow", 50),
    )

    def __init__(self):
        self.ma_fast = bt.ind.SMA(self.data.close, period=self.params.fast)
        self.ma_slow = bt.ind.SMA(self.data.close, period=self.params.slow)
        self.cross = bt.ind.CrossOver(self.ma_fast, self.ma_slow)

    def next(self):
        if not self.position:
            if self.cross > 0:
                self.buy()
        else:
            if self.cross < 0:
                self.sell()
    
class BuyAndHold(bt.Strategy):
    def next(self):
        if not self.position:
            self.buy