import { useState } from "react";

import type { CreateBacktestRequest } from "../model/types";
// import { input } from "@testing-library/user-event/dist/cjs/event/input.js";

interface BacktestFormProps {
    onSubmit: (
        request: CreateBacktestRequest,
    ) => void 
}

export function BacktestForm({onSubmit,}: BacktestFormProps){
    const [exchangeCode, setExchangeCode] = useState('NASDAQ')
    const [symbol, setSymbol] = useState('AAPL')
    const [startYear, setStartYear] = useState(2020)
    const [endYear, setEndYear] = useState(2025)
    const [initialCash, setInitialCash] = useState(10_000)

    function handleSubmit(
        event: React.FormEvent<HTMLFormElement>,
    ){
        event.preventDefault()
        onSubmit(
            {
                exchangeCode,
                symbol,
                strategyName:'BuyAndHold',
                startYear,
                endYear,
                initialCash,
                parameters:{},
            }
        )
    }

    return(
        <form 
        onSubmit={handleSubmit} 
        className="space-y-5">
            <div>
                <label htmlFor="exchange" className="mb-2 block test-sm font-medium">
                    Exchange
                </label>

                <input id="exchange" value={exchangeCode} onChange={
                    (event) => setExchangeCode(event?.target.value)
                } 
                className="w-full rounded-lg border border-slate-700 bg-slate-900 px-3 py-2"/>
            </div>

            <div>
                <label htmlFor="symbol" className="mb-2 block text-sm font-medium">
                    Symbol
                </label>
                <input id="symbol" value={symbol} 
                onChange={(event) => setSymbol(event?.target.value)}
                className="w-full rounded-lg border border-slate-700 bg-slate-900 px-3 py-2"/>
            </div>

            <div>
                <label htmlFor="start-year"
                className="mb-2 block text-sm font-medium">
                    Start Year
                </label>
                <input
                    id="start-year" type="number" value={startYear}
                    onChange={(event)=> setStartYear(Number(event?.target.value), )}
                    className="w-full rounded-lg border border-slate-700 bg-slate-900 px-3 py-2"
                />
            </div>

            <div>
                <label htmlFor="end-year" className="mb-2 block text-sm font-medium">
                    End Year 
                </label>
                <input
                    id="end-year"
                    type="number"
                    value={endYear}
                    onChange={(event) => setEndYear(Number(event?.target.value),)}
                    className="w-full rounded-lg border border-slate-700 bg-slate-900 px-3 py-2"
                />
            </div>

            <div>
                <label htmlFor="initial-cash" className="mb-2 block text-sm font-medium">
                    Initial cash
                </label>
                <input
                    id="initial-cash"
                    type="number"
                    value={initialCash}
                    onChange = {(event) => setInitialCash(Number(event.target.value),)}
                    className="w-full rounded-lg border border-slate-700 bg-slate-900 px-3 py-2"
                />
            </div>

            <button type="submit"
            className="w-full rounded-lg bg-slate-100 px-4 py-2 font-medium text-slate-950 hover:bg-white">
            Run Backtest
            </button>
        </form>
    )


}