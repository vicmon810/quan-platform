import type {
  ChangeEvent,
} from 'react'

import type {
  AssetOption,
} from '../model/types'


interface AssetSelectorProps {
  assets: AssetOption[]
  selectedAsset: AssetOption
  onChange: (asset: AssetOption) => void
}

function getAssetKey(
  asset: AssetOption,
): string {
  return `${asset.exchangeCode}:${asset.symbol}`
}

export function AssetSelector({
  assets,
  selectedAsset,
  onChange,
}: AssetSelectorProps) {
  function handleChange(
    event: ChangeEvent<HTMLSelectElement>,
  ): void {
    const asset = assets.find(
      candidate =>
        getAssetKey(candidate)
        === event.target.value,
    )

    if (asset !== undefined) {
      onChange(asset)
    }
  }

  return (
    <label className="block">
      <span className="mb-2 block text-xs text-slate-500">
        Asset
      </span>

      <select
        aria-label="Asset"
        value={getAssetKey(selectedAsset)}
        onChange={handleChange}
        className="
          w-full
          rounded-md
          border
          border-slate-700
          bg-slate-950
          px-3
          py-2.5
          text-sm
          text-slate-100
          outline-none
          transition
          focus:border-slate-500
        "
      >
        {assets.map(asset => (
          <option
            key={getAssetKey(asset)}
            value={getAssetKey(asset)}
          >
            {asset.symbol}
            {' — '}
            {asset.name}
            {' · '}
            {asset.exchangeCode}
          </option>
        ))}
      </select>
    </label>
  )
}