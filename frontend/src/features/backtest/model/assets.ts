export interface AssetOption {
  symbol: string
  name: string
  exchangeCode: string
}

export const DEFAULT_ASSETS: AssetOption[] = [
  {
    symbol: 'AAPL',
    name: 'Apple',
    exchangeCode: 'NASDAQ',
  },
  {
    symbol: 'MSFT',
    name: 'Microsoft',
    exchangeCode: 'NASDAQ',
  },
  {
    symbol: 'BHP',
    name: 'BHP',
    exchangeCode: 'ASX',
  },
]