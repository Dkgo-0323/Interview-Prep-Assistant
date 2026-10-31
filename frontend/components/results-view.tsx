"use client"

import { CheckCircle2, AlertTriangle, Lightbulb } from "lucide-react"
import { ScoreCircle } from "@/components/score-circle"
import { SubScoreBar } from "@/components/sub-score-bar"

export interface AnalysisResult {
  overall: number
  subScores: { label: string; score: number }[]
  strengths: string[]
  improvements: string[]
  tips: string[]
}

export function ResultsView({ result }: { result: AnalysisResult }) {
  return (
    <div className="flex w-full flex-col gap-6 duration-700 animate-in fade-in slide-in-from-bottom-4">
      {/* Score overview */}
      <div className="grid gap-6 rounded-2xl border border-border bg-card p-6 shadow-sm md:grid-cols-[auto_1fr] md:items-center md:gap-10">
        <div className="flex justify-center">
          <ScoreCircle score={result.overall} />
        </div>
        <div className="flex flex-col gap-4">
          {result.subScores.map((s, i) => (
            <SubScoreBar key={s.label} label={s.label} score={s.score} delay={i * 150} />
          ))}
        </div>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        {/* Strengths */}
        <section className="flex flex-col gap-3 rounded-2xl border border-border bg-card p-6 shadow-sm">
          <h2 className="flex items-center gap-2 text-lg font-semibold text-foreground">
            <CheckCircle2 className="h-5 w-5 text-emerald-600" />
            核心优势
          </h2>
          <ul className="flex flex-col gap-2.5">
            {result.strengths.map((item) => (
              <li
                key={item}
                className="flex items-start gap-2 rounded-lg border border-emerald-200 bg-emerald-50 p-3 text-sm leading-relaxed text-emerald-900"
              >
                <CheckCircle2 className="mt-0.5 h-4 w-4 shrink-0 text-emerald-600" />
                {item}
              </li>
            ))}
          </ul>
        </section>

        {/* Improvements */}
        <section className="flex flex-col gap-3 rounded-2xl border border-border bg-card p-6 shadow-sm">
          <h2 className="flex items-center gap-2 text-lg font-semibold text-foreground">
            <AlertTriangle className="h-5 w-5 text-amber-600" />
            待提升项
          </h2>
          <ul className="flex flex-col gap-2.5">
            {result.improvements.map((item) => (
              <li
                key={item}
                className="flex items-start gap-2 rounded-lg border border-amber-200 bg-amber-50 p-3 text-sm leading-relaxed text-amber-900"
              >
                <AlertTriangle className="mt-0.5 h-4 w-4 shrink-0 text-amber-600" />
                {item}
              </li>
            ))}
          </ul>
        </section>
      </div>

      {/* Interview tips */}
      <section className="flex flex-col gap-3 rounded-2xl border border-primary/20 bg-primary/5 p-6">
        <h2 className="flex items-center gap-2 text-lg font-semibold text-foreground">
          <Lightbulb className="h-5 w-5 text-primary" />
          面试准备建议
        </h2>
        <ul className="flex flex-col gap-2.5">
          {result.tips.map((tip, i) => (
            <li key={tip} className="flex items-start gap-3 text-sm leading-relaxed text-foreground">
              <span className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-primary text-xs font-semibold text-primary-foreground">
                {i + 1}
              </span>
              {tip}
            </li>
          ))}
        </ul>
      </section>


    </div>
  )
}
