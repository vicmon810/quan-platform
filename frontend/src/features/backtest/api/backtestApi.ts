import type {
    CreateBacktestRequest,
    CreateBacktestResponse,
    BacktestSummary,
    PortfolioValueResponse
} from '../model/types'

export async function createBacktest(request:CreateBacktestRequest): 
Promise<CreateBacktestResponse> {
    const response = await fetch('/api/backtests', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
    })
    if (!response.ok){
        throw new Error(
            `Failed to create backtest: ${response.status}`
        )
    }
    return response.json() as Promise<CreateBacktestResponse>
}

export async function getBacktest(publicId:string):Promise<BacktestSummary> {
        
        const response = await fetch(
                `/api/backtests/${publicId}`
        )
        
        if (!response.ok){
            throw new Error(
                `Failed to get backtest: ${response.status}`
            )
        }
        return response.json() as Promise<BacktestSummary>
}


export async function getPortfolioValues(publicId:string):Promise<PortfolioValueResponse> {
    const response = await fetch(
        `/api/backtest/${publicId}/portfolio-values`,
    )

    if(!response.ok){
        throw new Error(
            `Failed to get portfolio values: ${response.status}`,
        )
    }

    return response.json() as Promise<PortfolioValueResponse>
}