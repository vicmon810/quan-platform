package quant.web.backtest;

import  java.math.BigDecimal;
import java.time.LocalDate;
import java.util.UUID;

public record  BacktestSummary(
    UUID publicId,
    String status,
    String exchangeCode,
    String symbol,
    String strategyName,
    LocalDate startDate,
    LocalDate endDate, 
    BigDecimal initialCash,
    BacktestMetrics metrics
) {
    
}
