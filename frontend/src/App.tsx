import { BacktestPage } from "./features/backtest/BacktestPage"


function App() {
  return (
    <main className="min-h-screen">
      <div className="mx-auto max-w-6xl px-6 py-10">
        <header>
        <h1 className="text-3xl font-semibold">
          Quant Platform
        </h1>

        <p className="mt-2 text-slate-400">
          Backtest strategies against historical market data.
        </p>
        </header>

        <BacktestPage/>
      </div>
    </main>
  )
}

export default App