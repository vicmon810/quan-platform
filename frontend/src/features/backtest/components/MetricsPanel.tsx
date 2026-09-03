import type {
  BacktestMetrics,
} from '../model/types'


interface MetricsPanelProps {
  metrics: BacktestMetrics
}

function formatPercent(
  value: number,
  showPositiveSign = false,
): string {
  const percent = value * 100

  const prefix =
    showPositiveSign && percent > 0
      ? '+'
      : ''

  return `${prefix}${percent.toFixed(2)}%`
}

function formatRatio(
  value: number | null,
): string {
  if (value === null) {
    return '—'
  }

  return value.toFixed(2)
}

export function MetricsPanel({
  metrics,
}: MetricsPanelProps) {
  return (
    <section
      aria-label="Backtest metrics"
      className="
        grid
        grid-cols-2
        border-y
        border-slate-800
        md:grid-cols-4
      "
    >
      <Metric
        label="Total return"
        value={formatPercent(
          metrics.cumulativeReturn,
          true,
        )}
        description="Growth over the full period"
      />

      <Metric
        label="CAGR"
        value={formatPercent(metrics.cagr)}
        description="Average annual growth"
      />

      <Metric
        label="Max drawdown"
        value={`-${formatPercent(
          Math.abs(metrics.maxDrawdown),
        )}`}
        description="Largest peak-to-trough fall"
      />

      <Metric
        label="Sharpe"
        value={formatRatio(
          metrics.dailySharpe,
        )}
        description="Return relative to volatility"
      />
    </section>
  )
}

interface MetricProps {
  label: string
  value: string
  description: string
}

function Metric({
  label,
  value,
  description,
}: MetricProps) {
  return (
    <div className="py-5 pr-6">
      <p className="text-xs text-slate-500">
        {label}
      </p>

      <p className="mt-2 font-mono text-xl font-medium tracking-tight text-slate-100">
        {value}
      </p>

      <p className="mt-1 text-xs leading-5 text-slate-500">
        {description}
      </p>
    </div>
  )
}