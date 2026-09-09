import {
  render,
  screen,
} from '@testing-library/react'

import {
  describe,
  expect,
  it,
} from 'vitest'

import { BacktestHeader } from './BacktestHeader'


describe('BacktestHeader', () => {
  it('shows the asset and capital progression', () => {
    render(
      <BacktestHeader
        symbol="AAPL"
        exchangeCode="NASDAQ"
        strategyName="BuyAndHold"
        status="COMPLETED"
        startDate="2020-01-01"
        endDate="2025-01-01"
        initialCash={10_000}
        finalValue={33_212.99564}
      />,
    )

    expect(
      screen.getByRole('heading', {
        name: 'AAPL',
      }),
    ).toBeInTheDocument()

    expect(
      screen.getByText(/NASDAQ/i),
    ).toBeInTheDocument()

    expect(
      screen.getByText('COMPLETED'),
    ).toBeInTheDocument()

    expect(
      screen.getByText('$10,000 → $33,212.996'),
    ).toBeInTheDocument()

    expect(
      screen.getByText(/Buy & Hold/i),
    ).toBeInTheDocument()

    expect(
      screen.getByText(/2020 — 2025/i),
    ).toBeInTheDocument()
  })
})