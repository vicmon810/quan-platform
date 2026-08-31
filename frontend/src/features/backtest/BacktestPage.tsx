import {  useState } from "react";

import { createBacktest} from './api/backtestApi'
import { BacktestForm } from "./components/BacktestForm";

import type { 
    BacktestStatus,
    CreateBacktestRequest
} from "./model/types";

export function BacktestPage() {
    const [status, setStatus] = useState<BacktestStatus | null>(null)
    
    async function handleSubmit(request:CreateBacktestRequest) {
        const response = await createBacktest(request)

        setStatus(response.status)
    }

    return(
        <section className="space-y-8">
            <div>
                <h2 className="text-2xl font-semibold">
                Run Backtest
                </h2>
                <p className="mt-2 text-sm text-slate-400">
                    Test a strategy against historyical market data.
                </p>
            </div>

            <div className="max-w-xl">
                <BacktestForm onSubmit={handleSubmit}/>
            </div>
            {status !== null &&(
                <div className="rounded-lg border border-slate-800 bg-slate-900 p-4">
                        <p className="text-sm text-slate-300">
                            Status: {status}
                        </p>
                </div>
            )}
        </section>
    )
}