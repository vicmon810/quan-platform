import {
  render,
  screen,
} from '@testing-library/react'

import {
  describe,
  expect,
  it,
} from 'vitest'

import { MetricsPanel } from './MetricsPanel'


describe('MetricsPanel', () => {
  it('shows the main backtest metrics in readable form', () => {
    render(
      <MetricsPanel
        metrics={{
          finalValue: 19_061.99,
          cumulativeReturn: 0.9062,
          cagr: 0.1378,
          maxDrawdown: 0.3171,
          dailySharpe: 0.75,
          calmar: 0.43,
        }}
      />,
    )

    expect(
      screen.getByText('Total return'),
    ).toBeInTheDocument()

    expect(
      screen.getByText('+90.62%'),
    ).toBeInTheDocument()

    expect(
      screen.getByText('CAGR'),
    ).toBeInTheDocument()

    expect(
      screen.getByText('13.78%'),
    ).toBeInTheDocument()

    expect(
      screen.getByText('Max drawdown'),
    ).toBeInTheDocument()

    expect(
      screen.getByText('-31.71%'),
    ).toBeInTheDocument()

    expect(
      screen.getByText('Sharpe'),
    ).toBeInTheDocument()

    expect(
      screen.getByText('0.75'),
    ).toBeInTheDocument()
  })
})