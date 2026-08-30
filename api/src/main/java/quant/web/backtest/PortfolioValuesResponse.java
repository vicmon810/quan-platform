package quant.web.backtest;

import java.util.List;
import java.util.UUID;

public record PortfolioValuesResponse 
    (UUID publicId,
    List<PortfolioValuePoint> values){
    }

