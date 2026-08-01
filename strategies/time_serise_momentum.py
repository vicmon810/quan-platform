import backtrader as bt 

class TimeSeriseMomentum(bt.Strategy):
    """
    Desc: Time serise momentum strategy. Goes long when trailing return over the lookback window exceeds a 
    threshold, exits when it falls back below.
    Param: lookback (int): number of bars used to compute momentum
           threshold(float): minium trailing return required to enter
           target_percent(float): fraction of profolio value to allocate
    return: None
    """
    params = (
        ("lookback",126),
        ("threshold",0.1),
        ("target_percent", 0.95)
    )


    def __init__(self):
        """
        Desc: Initialze the momentum indicator as the percentage change between current close and 
        close `lookback` bars ago. 
        Param: None
        Return: None
        """
        self.momentum = (
            self.data.close / self.data.close(-self.params.lookback) -1
        )

        self.pending_order = None 
        self.signal_history = []

    def notify_order(self, order):
        """
        Desc: Callback invoked by backtrader whenever an order's status changes. Clears the pending order flag
        once the oder reaches a terminal state, so new oder can be placed.
        Param: order(bt.Order) the order whose status changed
        Return: None
        """
        if order.status in {
            order.Completed, 
            order.Canceled,
            order.Margin, 
            order.Rejected,
        }:

            self.pending_order = None 

    def next(self):
        """
        Desc: core strategy logic executed on each new bar. Skips action while an order is pending or 
        insufficient history exists. Enter a long position when momentum exceeds the threshold, exist when momentum
        falls back to or below it. 
        Param: None
        REturn: None
        """
        if self.pending_order is not None:
            return

        if len(self.data) <= self.params.lookback:
            return

        signal = float(self.momentum[0])
        self.signal_history.append(signal)

        if signal > self.params.threshold and not self.position:
            self.pending_order = self.order_target_percent(
                target=self.params.target_percent
            )
        elif signal <= self.params.threshold and self.position:
            self.pending_order = self.close()
        