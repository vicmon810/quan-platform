import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it, vi } from 'vitest'

import * as backtestApi from './api/backtestApi'
import { BacktestPage } from './BacktestPage'

describe('BacktestPage', () => {
  it('shows pending status after submitting a backtest', async () => {
    const user = userEvent.setup()

    vi.spyOn(
      backtestApi,
      'createBacktest',
    ).mockResolvedValue({
      publicId: 'test-public-id',
      status: 'PENDING',
    })

    render(<BacktestPage />)

    await user.click(
      screen.getByRole('button', {
        name: /run backtest/i,
      }),
    )

    expect(
      await screen.findByText(/status:\s*pending/i),
    ).toBeInTheDocument()
  })
})