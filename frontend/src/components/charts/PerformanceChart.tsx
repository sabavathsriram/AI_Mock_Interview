import React from 'react'
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts'
import { cn } from '@/utils/cn'

export interface PerformanceDataPoint {
  name: string
  score: number
  maxScore?: number
}

interface PerformanceChartProps {
  data: PerformanceDataPoint[]
  className?: string
  height?: number
}

export const PerformanceChart: React.FC<PerformanceChartProps> = ({
  data,
  className,
  height = 300,
}) => {
  return (
    <div className={cn('w-full', className)}>
      <ResponsiveContainer width="100%" height={height}>
        <BarChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
          <XAxis dataKey="name" stroke="#6b7280" />
          <YAxis stroke="#6b7280" domain={[0, 100]} />
          <Tooltip
            contentStyle={{
              backgroundColor: '#fff',
              border: '1px solid #e5e7eb',
              borderRadius: '8px',
            }}
          />
          <Legend />
          <Bar dataKey="score" fill="#5b8bff" name="Your Score" />
          {data[0]?.maxScore && (
            <Bar dataKey="maxScore" fill="#e5e7eb" name="Max Score" />
          )}
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}

PerformanceChart.displayName = 'PerformanceChart'
