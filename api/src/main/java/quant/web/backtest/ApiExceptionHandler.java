package quant.web.backtest;


import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;

import quant.web.backtest.AssetNotFoundException;


@RestControllerAdvice
public class ApiExceptionHandler {
    @ExceptionHandler(AssetNotFoundException.class)
    public ResponseEntity<Void> handleAssetNotFound(
        AssetNotFoundException exception
    ){
        return ResponseEntity.notFound().build();
    }
}
