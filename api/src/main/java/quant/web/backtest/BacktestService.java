package quant.web.backtest;


import java.math.BigDecimal;
import java.time.LocalDate;
import java.util.Map;
import java.util.UUID;
import java.util.List;


import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
public class BacktestService {
    private static final String STRATEGY_VERSION = "1.0.0";
    private final BacktestRepository repository;


    public BacktestService(BacktestRepository repository){
        this.repository = repository;
    }

    @Transactional
    public UUID createBacktest(
        String exchangeCode,
        String symbol,
        String strategyName,
        int startYear,
        int endYear,
        BigDecimal initialCash,
        Map<String, Object> parameters
    ){
        long assetId = repository.findAssetId(exchangeCode, symbol).orElseThrow(
            () -> new AssetNotFoundException(exchangeCode, symbol)
        );

        LocalDate startDate = LocalDate.of(startYear,1,1);
        LocalDate endDate = LocalDate.of(endYear,1,1);

        return repository.createPendingRun(
            assetId,
            strategyName,
            STRATEGY_VERSION,
            startDate,
            endDate,
            initialCash,
            parameters
        );
    }

    public BacktestSummary getBacktest(UUID publicId){
        return repository
                .findSummaryByPublicId(publicId)    
                .orElseThrow(
                    () -> new BacktestNotFoundException(
                        publicId
                    )
                );
    }

    public List<PortfolioValuePoint> getPortfolioValues(UUID publicId){
        repository.findSummaryByPublicId(publicId)
        .orElseThrow( 
            () ->  new BacktestNotFoundException(publicId)
        );
        return repository.findPortfolioValuesByPublicId(publicId);
    }
}
