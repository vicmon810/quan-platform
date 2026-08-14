import backtrader as bt


class PortfolioValueAnalyzer(bt.Analyzer):
    def start(self):
        self.values = []

    def next(self):
        portfolio_value = float(
            self.strategy.broker.getvalue()
        )

        gross_position_value = 0.0

        for data in self.strategy.datas:
            position = self.strategy.getposition(data)

            position_value = (
                float(position.size) * float(data.close[0])
            )

            gross_position_value += abs(position_value)

        # if portfolio_value > 0 :
        #     exposure = (
        #         gross_position_value / portfolio_value
        #     )
        # else: 
        #     exposure = 0.0
        exposure = (
            gross_position_value / portfolio_value 
            if portfolio_value > 0 
            else 0.0
        )
        
        self.values.append({
            "date": self.strategy.datetime.date(0),
            "value": portfolio_value,
            "exposure":exposure,
        })

    def get_analysis(self):
        return self.values