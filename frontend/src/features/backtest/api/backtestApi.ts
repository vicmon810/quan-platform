import type {
    CreateBacktestRequest,
    CreateBacktestResponse,
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