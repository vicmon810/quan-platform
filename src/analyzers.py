import backtrader as bt


class PortfolioValueAnalyzer(bt.Analyzer):
    def start(self):
        self.values = []

    def next(self):
        self.values.append({
            "date": self.strategy.datas[0].datetime.date(0).isoformat(),
            "value": self.strategy.broker.getvalue(),
        })

    def get_analysis(self):
        return self.values