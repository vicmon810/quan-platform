import { useState, useRef } from "react";

import { createBacktest, getBacktest, getPortfolioValues } from "../api/backtestApi";

import type {
    BacktestSummary,
    PortfolioValuePoint,
    BacktestStatus,
    CreateBacktestRequest
} from '../model/types';
//import { request } from "http";
const POLL_INTERVAL_MS = 1000

export function useBacktest() {
    const [publicId, setPublicId] = useState<string | null>(null)
    const [status, setStatus] = useState<BacktestStatus | null>(null)
    const [summary, setSummary] = useState<BacktestSummary | null>(null )
    const [portfolioValues, setPortfolioValues] = useState<PortfolioValuePoint[]>([])
    const timeRef = useRef<ReturnType<typeof setTimeout> | null>(null, )
    
    async function poll(id:string):Promise<void> {
        timeRef.current = setTimeout(
            async () => {
                const nextSummary = await getBacktest(id)
                setSummary(nextSummary)
                setStatus(nextSummary.status)

                if (nextSummary.status === 'PENDING' || nextSummary.status ==='RUNNING'){
                    await poll(id)
                    return
                }
                if(nextSummary.status ==='COMPLETED'){
                    const PortfolioValueResponse = await getPortfolioValues(id)
                    setPortfolioValues(PortfolioValueResponse.values,)
                }
            },
            POLL_INTERVAL_MS
        )
    }

    async function submit(request:CreateBacktestRequest): Promise<void> {
        const response = await createBacktest(request)

        setPublicId(response.publicId)
        setStatus(response.status)

        if(response.status==='PENDING' || response.status==='RUNNING'){
            await poll(response.publicId)
        }
    }

    return {publicId, status,summary, portfolioValues, submit}
}