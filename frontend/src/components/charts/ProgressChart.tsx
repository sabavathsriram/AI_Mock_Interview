import React from 'react'
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts'
import { cn } from '@/utils/cn'

export interface ProgressDataPoint {
  date: string
  score: number
}

interface ProgressChartProps {
  data: ProgressDataPoint[]
  className?: string
  height?: number
}

export const ProgressChart: React.FC<ProgressChartProps> = ({
  data,
  className,
  height = 300,
}) => {
  return (
    <div className={cn('w-full', className)}>
      <ResponsiveContainer width="100%" height={height}>
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
          <XAxis dataKey="date" stroke="#6b7280" />
          <YAxis stroke="#6b7280" domain={[0, 100]} />
          <Tooltip
            contentStyle={{
              backgroundColor: '#fff',
              border: '1px solid #e5e7eb',
              borderRadius: '8px',
            }}
          />
          <Legend />
          <Line
            type="monotone"
            dataKey="score"
            stroke="#5b8bff"
            strokeWidth={3}
            dot={{ fill: '#5b8bff', r: 5 }}
            activeDot={{ r: 7 }}
            name="Interview Score"
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}

ProgressChart.displayName = 'ProgressChart'
