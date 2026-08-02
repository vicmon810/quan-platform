import backtrader as bt


class PortfolioValueAnalyzer(bt.Analyzer):
    def start(self):
        self.values = []

    def next(self):
        portfoli_value = float(
            self.strategy.broker.getvalue()
        )

        gross_position_value = 0.0

        for data in self.strategy.datas:
            position = self.strategy.getposition(data)

            position_value = (
                float(position.size) * float(data.close[0])
            )

            gross_position_value += abs(position_value)

        if portfoli_value > 0 :
            exposure = (
                gross_position_value / portfoli_value
            )
        else: 
            exposure = 0.0

        self.values.append({
            "data": self.strategy.datetime.date(0),
            "value": portfoli_value,
            "exposure":exposure,
        })

    def get_analysis(self):
        return self.values