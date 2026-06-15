"use client"

import { useEffect, useState } from "react"

interface SubScoreBarProps {
  label: string
  score: number
  delay?: number
}

export function SubScoreBar({ label, score, delay = 0 }: SubScoreBarProps) {
  const [width, setWidth] = useState(0)

  useEffect(() => {
    const timer = setTimeout(() => setWidth(score), 300 + delay)
    return () => clearTimeout(timer)
  }, [score, delay])

  return (
    <div className="flex flex-col gap-1.5">
      <div className="flex items-center justify-between text-sm">
        <span className="font-medium text-foreground">{label}</span>
        <span className="font-semibold text-primary tabular-nums">{score}%</span>
      </div>
      <div className="h-2.5 w-full overflow-hidden rounded-full bg-muted">
        <div
          className="h-full rounded-full bg-gradient-to-r from-primary to-accent transition-[width] duration-1000 ease-out"
          style={{ width: `${width}%` }}
        />
      </div>
    </div>
  )
}
