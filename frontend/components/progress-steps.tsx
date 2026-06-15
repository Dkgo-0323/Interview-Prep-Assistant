"use client"

import { Check, Loader2 } from "lucide-react"
import { cn } from "@/lib/utils"
import type { ReactNode } from "react"

export type StepStatus = "pending" | "active" | "done"

export interface Step {
  id: string
  label: string
  icon: ReactNode
}

interface ProgressStepsProps {
  steps: Step[]
  current: number
}

export function ProgressSteps({ steps, current }: ProgressStepsProps) {
  return (
    <ol className="flex w-full flex-col gap-3 sm:flex-row sm:items-stretch sm:gap-4">
      {steps.map((step, index) => {
        const status: StepStatus = index < current ? "done" : index === current ? "active" : "pending"

        return (
          <li
            key={step.id}
            className={cn(
              "flex flex-1 items-center gap-3 rounded-xl border p-4 transition-all duration-500",
              status === "done" && "border-primary/30 bg-primary/5",
              status === "active" && "border-accent/40 bg-accent/10 shadow-sm",
              status === "pending" && "border-border bg-card opacity-60",
            )}
          >
            <div
              className={cn(
                "flex h-10 w-10 shrink-0 items-center justify-center rounded-full transition-colors duration-500",
                status === "done" && "bg-primary text-primary-foreground",
                status === "active" && "bg-accent text-accent-foreground",
                status === "pending" && "bg-muted text-muted-foreground",
              )}
            >
              {status === "done" ? (
                <Check className="h-5 w-5" />
              ) : status === "active" ? (
                <Loader2 className="h-5 w-5 animate-spin" />
              ) : (
                step.icon
              )}
            </div>
            <div className="flex flex-col">
              <span className="text-xs font-medium text-muted-foreground">步骤 {index + 1}</span>
              <span className="text-sm font-semibold text-foreground">{step.label}</span>
            </div>
          </li>
        )
      })}
    </ol>
  )
}
