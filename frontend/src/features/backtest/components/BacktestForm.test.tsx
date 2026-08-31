import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it, vi } from 'vitest'

import { BacktestForm } from './BacktestForm'

describe('BacktestForm', () => {
  it('submits the entered backtest request', async () => {
    const user = userEvent.setup()
    const onSubmit = vi.fn()

    render(
      <BacktestForm onSubmit={onSubmit} />,
    )

    await user.clear(
      screen.getByLabelText(/exchange/i),
    )
    await user.type(
      screen.getByLabelText(/exchange/i),
      'NASDAQ',
    )

    await user.clear(
      screen.getByLabelText(/symbol/i),
    )
    await user.type(
      screen.getByLabelText(/symbol/i),
      'AAPL',
    )

    await user.clear(
      screen.getByLabelText(/start year/i),
    )
    await user.type(
      screen.getByLabelText(/start year/i),
      '2020',
    )

    await user.clear(
      screen.getByLabelText(/end year/i),
    )
    await user.type(
      screen.getByLabelText(/end year/i),
      '2025',
    )

    await user.clear(
      screen.getByLabelText(/initial cash/i),
    )
    await user.type(
      screen.getByLabelText(/initial cash/i),
      '10000',
    )

    await user.click(
      screen.getByRole('button', {
        name: /run backtest/i,
      }),
    )

    expect(onSubmit).toHaveBeenCalledWith({
      exchangeCode: 'NASDAQ',
      symbol: 'AAPL',
      strategyName: 'BuyAndHold',
      startYear: 2020,
      endYear: 2025,
      initialCash: 10_000,
      parameters: {},
    })
  })
})