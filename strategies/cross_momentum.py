import backtrader as bt

class CrossSectionalMomentum(bt.Strategy):
    params = (
        ("lookback", 126), # in past 126 days
        ("threshold", 0.15), # increase 15%
    )

    def __init__(self):
        self.momentum = (
            self.data.close/
            self.data.close(-self.params.lookback)
        ) - 1

    def next(self):
        if len(self.data) < self.params.lookback:
            return
    
        if not self.position:
            if self.momentum[0] > self.params.threshold:
                self.order_target_percent(0.95)

        else :
            if self.momentum[0] < self.params.threshold:
                self.close()
