import type { BacktestStatus } from "../model/types";

interface BacktestHeaderProps {
    symbol: string 
    exchangeCode: string 
    strategyName: string 
    status: BacktestStatus 
    startDate: string 
    endDate:string 
    initialCash: number
    finalValue: number
}   

// function formatMoney(value: number,):string {
//     return new Intl.NumberFormat(
//         'en-NZ',
//         {
//             style: 'currency',
//             currency: 'USD',
//             maximumFractionDigits: 3,
//         },
//     ).format(value)
// }


function formatMoney(value: number): string {
    return `$${value.toLocaleString(
        'en-NZ',
        {maximumFractionDigits:3,},
    )}`
}

function formatStrategyName(strategyName: string,):string {
    if (strategyName === 'BuyAndHold'){
        return 'Buy & Hold'
    }
    return strategyName
}

function getYear (date:string,):string {
    return date.slice(0,4)
}


export function BacktestHeader(
    {symbol, exchangeCode, strategyName,
        status, startDate, endDate,  initialCash, finalValue
    }: BacktestHeaderProps){
        return(
            <header className="space-y-5">
                <div className="flex items-start justify-between gap-6">
                    <h2 className="font-mono text-3xl font-semibold tracking-tight text-slate-100">
                        {symbol}
                    </h2>
                    <p className="mt-1 text-sm text-slate-500">
                        {exchangeCode}
                    </p>
                </div>

                <span className="font-mono text-xs tracking-wide text-slate-400">
                    {status}
                </span>

                <div>
                    <p className="font-mono text-2xl tracking-tight text-slate-100">
                        {formatMoney(initialCash)}
                        {' → '}
                        {formatMoney(finalValue)}
                    </p>
                    <p className="mt-2 text-sm text-slate-500">
                        {formatStrategyName(strategyName)}
                        {' . '}
                        {getYear(startDate)}
                        {' — '}
                        {getYear(endDate)}
                    </p>
                </div>
            </header>
        )
    }