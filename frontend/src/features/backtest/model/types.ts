export type BacktestStatus =
| 'PENDING'
| 'RUNNING'
| 'COMPLETED'
| 'FAILED'

export interface CreateBacktestRequest{
    exchangeCode:string
    symbol:string
    strategyName: string 
    startYear: number 
    endYear:number
    initialCash:number
    parameters: Record<string, unknown>
}

export interface CreateBacktestResponse{
    publicId:string 
    status: BacktestStatus
}

export interface BacktestMetrics {
    finalValue: number
    cumulativeReturn: number
    cagr: number
    maxDrawdown: number
    dailySharpe: number | null 
    calmar: number | null
}

export interface BacktestSummary{
    publicId:string 
    status: BacktestStatus 
    exchagneCode: string 
    symbol: string
    strategyName: string 
    stratDate:string 
    endDate: string 
    initialCash: number 
    metrics: BacktestMetrics | null
}