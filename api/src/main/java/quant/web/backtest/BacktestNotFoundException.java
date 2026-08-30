package quant.web.backtest;

import java.util.UUID;

public class BacktestNotFoundException  extends RuntimeException{
    public BacktestNotFoundException(UUID publicId){
        super("Backtest not found:" + publicId);
    }
}
