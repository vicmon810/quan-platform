package quant.web.backtest;

public class AssetNotFoundException extends RuntimeException {

    public AssetNotFoundException(
        String exchangeCode,
        String symbol
    ) {
        super(
            "Asset not found: "
                + exchangeCode
                + ":"
                + symbol
        );
    }
}