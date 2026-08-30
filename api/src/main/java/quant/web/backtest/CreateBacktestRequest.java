package quant.web.backtest;

import java.math.BigDecimal;
import java.util.Map;

import jakarta.validation.constraints.AssertTrue;
import jakarta.validation.constraints.Positive;
import jakarta.validation.constraints.NotBlank;

public record CreateBacktestRequest(
    @NotBlank(message = "exchangeCode must not be blank")
    String exchangeCode,
    @NotBlank(message = "symbol must not be blank")
    String symbol,
    @NotBlank(message = "strategyName must not be blank")
    String strategyName,
    int startYear,
    int endYear,
    @Positive(message = "initialCash must be positive")
    BigDecimal initialCash,
    Map<String, Object> parameters
){
    @AssertTrue(message = "startYear must before endYear")
    // @AssertTrue(message = "startYear must be before endYear")
    public boolean isYearRangeValid() {
        return  endYear > startYear;
    }

    
}

// public class CreateBacktestRequest {
    
// }
