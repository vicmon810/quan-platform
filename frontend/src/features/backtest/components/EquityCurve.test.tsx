import {
  render,
  screen,
} from '@testing-library/react'

import {
  describe,
  expect,
  it,
  vi,
} from 'vitest'

import { EquityCurve } from './EquityCurve'


vi.mock('recharts', () => ({
  ResponsiveContainer: ({
    children,
  }: {
    children: React.ReactNode
  }) => (
    <div data-testid="responsive-container">
      {children}
    </div>
  ),

  LineChart: ({
    data,
    children,
  }: {
    data: unknown[]
    children: React.ReactNode
  }) => (
    <div
      data-testid="line-chart"
      data-point-count={data.length}
    >
      {children}
    </div>
  ),

  Line: () => (
    <div data-testid="equity-line" />
  ),

  XAxis: () => null,
  YAxis: () => null,
  CartesianGrid: () => null,
  Tooltip: () => null,
}))


describe('EquityCurve', () => {
  it('renders portfolio values as an equity curve', () => {
    const values = [
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
    ]

    render(
      <EquityCurve values={values} />,
    )

    expect(
      screen.getByRole('heading', {
        name: /equity curve/i,
      }),
    ).toBeInTheDocument()

    expect(
      screen.getByTestId('line-chart'),
    ).toHaveAttribute(
      'data-point-count',
      '2',
    )

    expect(
      screen.getByTestId('equity-line'),
    ).toBeInTheDocument()
  })
})