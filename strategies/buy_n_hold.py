import backtrader as bt


class BuyAndHold(bt.Strategy):
    def next(self):
        if not self.position:
            self.order_target_percent(target=0.95)
            self.buy