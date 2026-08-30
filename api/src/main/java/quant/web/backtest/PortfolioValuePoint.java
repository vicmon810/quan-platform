package quant.web.backtest;

import java.math.BigDecimal;
import java.time.LocalDate;

public record PortfolioValuePoint (LocalDate date,
    BigDecimal value,
    BigDecimal marketExposure,
    BigDecimal drawdown){
    
}
