import { BacktestForm } from './components/BacktestForm'
import { EquityCurve } from './components/EquityCurve'
import { MetricsPanel } from './components/MetricsPanel'
import { useBacktest } from './hooks/useBacktest'


export function BacktestPage() {
  const {
    status,
    summary,
    portfolioValues,
    submit,
  } = useBacktest()

  return (
    <section className="space-y-8">
      <div>
        <h2 className="text-2xl font-semibold">
          Run Backtest
        </h2>

        <p className="mt-2 text-sm text-slate-400">
          Test a strategy against historical market data.
        </p>
      </div>

      {portfolioValues.length > 0 && (
        <EquityCurve
          values={portfolioValues}
        />
      )}

      {summary?.metrics && (
        <MetricsPanel
          metrics={summary.metrics}
        />
      )}

      {status !== null && (
        <div className="text-sm text-slate-400">
          Status: {status}
        </div>
      )}

      <div className="max-w-xl">
        <BacktestForm
          onSubmit={submit}
        />
      </div>
    </section>
  )
}