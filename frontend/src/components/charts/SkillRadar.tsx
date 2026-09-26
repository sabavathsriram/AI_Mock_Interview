import React from 'react'
import {
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
  Legend,
  Tooltip,
  ResponsiveContainer,
} from 'recharts'
import { cn } from '@/utils/cn'

export interface RadarDataPoint {
  name: string
  value: number
}

interface SkillRadarProps {
  data: RadarDataPoint[]
  className?: string
  height?: number
}

export const SkillRadar: React.FC<SkillRadarProps> = ({ data, className, height = 300 }) => {
  return (
    <div className={cn('w-full', className)}>
      <ResponsiveContainer width="100%" height={height}>
        <RadarChart data={data}>
          <PolarGrid stroke="#e5e7eb" />
          <PolarAngleAxis dataKey="name" stroke="#6b7280" />
          <PolarRadiusAxis angle={90} domain={[0, 100]} stroke="#6b7280" />
          <Radar
            name="Skill Level"
            dataKey="value"
            stroke="#5b8bff"
            fill="#5b8bff"
            fillOpacity={0.6}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: '#fff',
              border: '1px solid #e5e7eb',
              borderRadius: '8px',
            }}
          />
          <Legend />
        </RadarChart>
      </ResponsiveContainer>
    </div>
  )
}

SkillRadar.displayName = 'SkillRadar'
