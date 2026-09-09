import {
  render,
  screen,
} from '@testing-library/react'

import userEvent from '@testing-library/user-event'

import {
  describe,
  expect,
  it,
  vi,
} from 'vitest'

import { AssetSelector } from './AssetSelector'


const assets = [
  {
    symbol: 'AAPL',
    name: 'Apple',
    exchangeCode: 'NASDAQ',
  },
  {
    symbol: 'MSFT',
    name: 'Microsoft',
    exchangeCode: 'NASDAQ',
  },
  {
    symbol: 'BHP',
    name: 'BHP',
    exchangeCode: 'ASX',
  },
]


describe('AssetSelector', () => {
  it('shows the selected asset in readable form', () => {
    render(
      <AssetSelector
        assets={assets}
        selectedAsset={assets[0]}
        onChange={() => {}}
      />,
    )

    expect(
      screen.getByLabelText('Asset'),
    ).toHaveValue('NASDAQ:AAPL')

    expect(
      screen.getByRole('option', {
        name: 'AAPL — Apple · NASDAQ',
      }),
    ).toBeInTheDocument()
  })

  it('returns the selected asset', async () => {
    const user = userEvent.setup()
    const onChange = vi.fn()

    render(
      <AssetSelector
        assets={assets}
        selectedAsset={assets[0]}
        onChange={onChange}
      />,
    )

    await user.selectOptions(
      screen.getByLabelText('Asset'),
      'NASDAQ:MSFT',
    )

    expect(onChange).toHaveBeenCalledWith(
      assets[1],
    )
  })
})