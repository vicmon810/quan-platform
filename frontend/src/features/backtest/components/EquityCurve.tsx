import {
    CartesianGrid,

    Line, 
    LineChart,
    ResponsiveContainer,
    Tooltip,
    XAxis,
    YAxis
} from 'recharts'

import type {
    PortfolioValuePoint
} from '../model/types'

interface EquityCurveProps{
    values: PortfolioValuePoint[]
}

export function EquityCurve({values,}:EquityCurveProps){
    return (
        <section className='rounded-lg border border-slate-800 bg-slate-900 p-5'>
            <h3 className='mb-4 text-lg font-semibold'>
                Equity Curve 
            </h3>
            <div className='h-80 w-full'>
                <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={values}>
                        <CartesianGrid
                            strokeDasharray="3 3"/>

                            <XAxis 
                                dataKey="date"
                                minTickGap={32}
                            />
                            <YAxis
                                domain={['auto','auto']}
                            />
                            <Tooltip />
                            <Line 
                                type="monotone"
                                dataKey="value"
                                dot={false}
                                isAnimationActive={false}
                            />
                    </LineChart>
                </ResponsiveContainer>
            </div>
        </section>
    )
}