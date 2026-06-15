"use client"

import { PolarAngleAxis, PolarGrid, Radar, RadarChart } from "recharts"
import { ChartContainer, ChartTooltip, ChartTooltipContent } from "@/components/ui/chart"

type RadarPoint = { dimension: string; value: number }

export function StrengthsRadar({ data }: { data: RadarPoint[] }) {
  return (
    <ChartContainer
        config={{
        value: { label: "能力评分", color: "var(--primary)" },
      }}
      className="mx-auto aspect-square max-h-72 w-full"
    >
      <RadarChart data={data} outerRadius="72%">
        <ChartTooltip cursor={false} content={<ChartTooltipContent />} />
        <PolarGrid stroke="var(--border)" />
        <PolarAngleAxis
          dataKey="dimension"
          tick={{ fill: "var(--muted-foreground)", fontSize: 12 }}
        />
        <Radar
          dataKey="value"
          fill="var(--color-value)"
          fillOpacity={0.35}
          stroke="var(--color-value)"
          strokeWidth={2}
          dot={{ r: 3, fillOpacity: 1 }}
        />
      </RadarChart>
    </ChartContainer>
  )
}
