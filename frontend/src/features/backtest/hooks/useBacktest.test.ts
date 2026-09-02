import { act, renderHook } from '@testing-library/react'

import { beforeEach, describe, expect, it, vi } from 'vitest'

import { createBacktest, getBacktest, getPortfolioValues } from '../api/backtestApi'
import type { CreateBacktestRequest } from '../model/types'
import { useBacktest } from './useBacktest'

vi.mock('../api/backtestApi', () => ({
    createBacktest: vi.fn(),
    getBacktest: vi.fn(),
    getPortfolioValues: vi.fn()
}))

const createBacktestMock = vi.mocked(createBacktest)
const getBacktestMock = vi.mocked(getBacktest)
const getPortfolioValuesMock = vi.mocked(getPortfolioValues)

describe('useBacktest', () => {
    beforeEach(() => {
        vi.clearAllMocks()
        // 给所有测试一个默认返回值，避免漏 mock 时读取 undefined.values 报错
        getPortfolioValuesMock.mockResolvedValue({
            publicId: 'test-public-id',
            values: [],
        })
    })

    it('stores the created backtest id and status after submit', async () => {
        createBacktestMock.mockResolvedValue({
            publicId: 'test-public-id',
            status: 'PENDING'
        })

        const request: CreateBacktestRequest = {
            exchangeCode: 'NASDAQ',
            symbol: 'APAPL',
            strategyName: 'BuyAndHold',
            startYear: 2020,
            endYear: 2025,
            initialCash: 10_000,
            parameters: {},
        }

        const { result } = renderHook(() => useBacktest())

        await act(async () => {
            await result.current.submit(request)
        })

        expect(createBacktestMock).toHaveBeenCalledWith(request)
        expect(result.current.publicId).toBe('test-public-id')
        expect(result.current.status).toBe('PENDING')
    })

    it('polls until the backtest is completed', async () => {
        vi.useFakeTimers()

        createBacktestMock.mockResolvedValue({
            publicId: 'test-public-id',
            status: 'PENDING',
        })

        getBacktestMock
            .mockResolvedValueOnce({
                publicId: 'test-public-id',
                status: 'RUNNING',
                exchangeCode: 'NASDAQ',
                symbol: 'AAPL',
                strategyName: 'BuyAndHold',
                startDate: '2020-01-01',
                endDate: '2025-01-01',
                initialCash: 10_000,
                metrics: null,
            })
            .mockResolvedValueOnce({
                publicId: 'test-public-id',
                status: 'COMPLETED',
                exchangeCode: 'NASDAQ',
                symbol: 'AAPL',
                strategyName: 'BuyAndHold',
                startDate: '2020-01-01',
                endDate: '2025-01-01',
                initialCash: 10_000,
                metrics: {
                    finalValue: 19_000,
                    cumulativeReturn: 0.9,
                    cagr: 0.13,
                    maxDrawdown: 0.3,
                    dailySharpe: 0.75,
                    calmar: 0.43,
                },
            })

        const request: CreateBacktestRequest = {
            exchangeCode: 'NASDAQ',
            symbol: 'AAPL',
            strategyName: 'BuyAndHold',
            startYear: 2020,
            endYear: 2025,
            initialCash: 10_000,
            parameters: {},
        }

        const { result } = renderHook(() => useBacktest())

        await act(async () => {
            await result.current.submit(request)
        })

        await act(async () => {
            await vi.advanceTimersByTimeAsync(1000)
        })

        expect(result.current.status).toBe('RUNNING')

        await act(async () => {
            await vi.advanceTimersByTimeAsync(1000)
        })

        expect(result.current.status).toBe('COMPLETED')
        expect(getBacktestMock).toHaveBeenCalledTimes(2)

        vi.useRealTimers()
    })

    it('loads portfolio values when the backtest completes', async () => {
        vi.useFakeTimers()

        createBacktestMock.mockResolvedValue({
            publicId: 'test-public-id',
            status: 'PENDING',
        })

        getBacktestMock.mockResolvedValue({
            publicId: 'test-public-id',
            status: 'COMPLETED',
            exchangeCode: 'NASDAQ',
            symbol: 'AAPL',
            strategyName: 'BuyAndHold',
            startDate: '2020-01-01',
            endDate: '2025-01-01',
            initialCash: 10_000,
            metrics: {
                finalValue: 19_000,
                cumulativeReturn: 0.9,
                cagr: 0.13,
                maxDrawdown: 0.3,
                dailySharpe: 0.75,
                calmar: 0.43,
            },
        })

        getPortfolioValuesMock.mockResolvedValue({
            publicId: 'test-public-id',
            values: [
                {
                    date: '2020-01-02',
                    value: 10_000,
                    marketExposure: 0,
                    drawdown: 0,
                },
                {
                    date: '2020-01-03',
                    value: 10_100,
                    marketExposure: 0.95,
                    drawdown: 0.01,
                },
            ],
        })

        const request: CreateBacktestRequest = {
            exchangeCode: 'NASDAQ',
            symbol: 'AAPL',
            strategyName: 'BuyAndHold',
            startYear: 2020,
            endYear: 2025,
            initialCash: 10_000,
            parameters: {},
        }

        const { result } = renderHook(() => useBacktest())

        await act(async () => {
            await result.current.submit(request)
        })

        await act(async () => {
            await vi.advanceTimersByTimeAsync(1000)
        })

        expect(getBacktestMock).toHaveBeenCalledWith('test-public-id')
        expect(result.current.status).toBe('COMPLETED')

        expect(getPortfolioValuesMock).toHaveBeenCalledWith('test-public-id')

        expect(result.current.portfolioValues).toEqual([
            {
                date: '2020-01-02',
                value: 10_000,
                marketExposure: 0,
                drawdown: 0,
            },
            {
                date: '2020-01-03',
                value: 10_100,
                marketExposure: 0.95,
                drawdown: 0.01,
            },
        ])

        vi.useRealTimers()
    })
})