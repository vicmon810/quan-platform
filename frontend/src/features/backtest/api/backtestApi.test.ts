import { afterEach, describe, expect, it, vi } from 'vitest'

import { createBacktest, getBacktest, getPortfolioValues } from '../api/backtestApi'//'backtestApi'
// import { error } from 'console'

describe('createBacktest', () => {
  afterEach(() => {
    vi.restoreAllMocks()
  })

  it('posts the backtest request and returns the created job', async () => {
    const fetchMock = vi
      .spyOn(globalThis, 'fetch')
      .mockResolvedValue(
        new Response(
          JSON.stringify({
            publicId: 'test-public-id',
            status: 'PENDING',
          }),
          {
            status: 202,
            headers: {
              'Content-Type': 'application/json',
            },
          },
        ),
      )

    const request = {
      exchangeCode: 'NASDAQ',
      symbol: 'AAPL',
      strategyName: 'BuyAndHold',
      startYear: 2020,
      endYear: 2025,
      initialCash: 10_000,
      parameters: {},
    }

    const result = await createBacktest(request)

    expect(fetchMock).toHaveBeenCalledWith(
      '/api/backtests',
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
      },
    )

    expect(result).toEqual({
      publicId: 'test-public-id',
      status: 'PENDING',
    })
  })
})

it('throws when the API returns a non-success status', async() => {
    vi
    .spyOn(globalThis, 'fetch')
    .mockResolvedValue(
        new Response(
            JSON.stringify(
                {
                    error: 'Bad Request',
                }
            ),
            {
                status:400,
                headers: {
                    'Content-Type': 'application/json',
                },
            },
        ),
    )

    const request = {
        exchangeCode: 'NASDAQ',
        symbol:'APPL',
        strategyName: 'BuyAndHold',
        startYear: 2025,
        endYear:2020,
        initialCash: 10_000,
        parameters:{},
    }

    await expect(
        createBacktest(request),
    ).rejects.toThrow(
        'Failed to create backtest: 400',
    )
})

it('gets a backtest summary by public id', async () => {
  const fetchMock = vi
    .spyOn(globalThis, 'fetch')
    .mockResolvedValue(
      new Response(
        JSON.stringify({
          publicId: 'test-public-id',
          status: 'COMPLETED',
          exchangeCode: 'NASDAQ',
          symbol: 'AAPL',
          strategyName: 'BuyAndHold',
          startDate: '2020-01-01',
          endDate: '2025-01-01',
          initialCash: 10000,
          metrics: {
            finalValue: 19061.99,
            cumulativeReturn: 0.906199,
            cagr: 0.137816,
            maxDrawdown: 0.317141,
            dailySharpe: 0.753998,
            calmar: 0.434558,
          },
        }),
        {
          status: 200,
          headers: {
            'Content-Type': 'application/json',
          },
        },
      ),
    )

  const result =
    await getBacktest('test-public-id')

  expect(fetchMock).toHaveBeenCalledWith(
    '/api/backtests/test-public-id',
  )

  expect(result).toEqual({
    publicId: 'test-public-id',
    status: 'COMPLETED',
    exchangeCode: 'NASDAQ',
    symbol: 'AAPL',
    strategyName: 'BuyAndHold',
    startDate: '2020-01-01',
    endDate: '2025-01-01',
    initialCash: 10000,
    metrics: {
      finalValue: 19061.99,
      cumulativeReturn: 0.906199,
      cagr: 0.137816,
      maxDrawdown: 0.317141,
      dailySharpe: 0.753998,
      calmar: 0.434558,
    },
  })
})

it('gets portflio values by public id', async() => {
    const fetchMock = vi.
    spyOn(globalThis, 'fetch')
    .mockResolvedValue(
        new Response(
            JSON.stringify({
                publicId: 'test-public-id',
                values: [
                    {
                        date:'2020-01-02',
                        value:10000,
                        marketExposure:0,
                        drawdown:0,
                    },
                    {
                        date: '2020-01-03',
                        value:10100,
                        marketExposure: 0.95,
                        drawdown: 0.01,
                    },
                ],
            }),
            {
                status:200,
                headers:{
                    'Content-Type': 'application.json',
                },
            },
        ),
    )
    const result = await getPortfolioValues('test-public-id')
    expect(fetchMock).toHaveBeenCalledWith(
        '/api/backtests/test-public-id/portfolio-values',
    )

    expect(result.values).toHaveLength(2)
    expect(result.values[0]).toEqual({
        date: '2020-01-02',
        value:10000,
        marketExposure:0,
        drawdown:0,
    })
})