# Backtest Persistence Adapter Design

## Goal

将 `extract_result()` 返回的 quant domain result 转换为
Persistence Layer 可以直接保存的 payload，同时保持 Engine 与数据库解耦。

## Input

`build_persistence_payload()` 接收：

- `result`
  - ticker
  - strategy
  - final_value
  - portfolio_values
  - performance metrics
  - strategy parameters
- `exchange_code`
- `display_name`
- `currency_code`
- `asset_type`
- `initial_cash`
- `strategy_version`
- `engine_version`

## Output

返回：

```python
{
    "asset": {...},
    "run": {...},
    "metrics": {...},
    "portfolio_values": [...]
}
```
## Asset

```python 
{
    "exchange_code": str,
    "symbol": str,
    "display_name": str,
    "currency_code": str,
    "asset_type": str,
}
```

## Run 
```python
{
    "strategy_name": str,
    "strategy_version": str,
    "start_date": date,
    "end_date": date,
    "initial_cash": Decimal,
    "parameters": dict,
    "engine_version": str,
}
```