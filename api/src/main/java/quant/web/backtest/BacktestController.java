package quant.web.backtest;

import java.util.UUID;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import jakarta.validation.Valid;
// import jakarta.validation.Valid;
@RestController
@RequestMapping("/api/backtests")
public class BacktestController {
    private final BacktestService service;

    public BacktestController(BacktestService service){
        this.service = service;
    }

    @PostMapping
    public ResponseEntity<CreateBacktestResponse> createBacktest
    (@Valid @RequestBody CreateBacktestRequest request){
        UUID publicId = service.createBacktest(
             request.exchangeCode(),
             request.symbol(), 
             request.strategyName(),
             request.startYear(),
             request.endYear(), 
             request.initialCash(), 
             request.parameters()
        );

        CreateBacktestResponse response = new CreateBacktestResponse(publicId,"PENDING");
        return ResponseEntity.accepted().body(response);
    }
}
