package quant.web.backtest;

import java.math.BigDecimal;




public record  BacktestMetrics 
    (BigDecimal finalValue,
    BigDecimal cumulativeReturn,
    BigDecimal cagr,
    BigDecimal maxDrawdown,
    BigDecimal dailySharp,
    BigDecimal calmar){

    }

