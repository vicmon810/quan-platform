import { afterEach, describe, expect, it, vi } from 'vitest'

import { createBacktest } from '../api/backtestApi'//'backtestApi'
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