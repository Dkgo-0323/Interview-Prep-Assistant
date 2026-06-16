// frontend/app/analyze/page.tsx
"use client"

import { useEffect, useRef, useState } from "react"
import { Briefcase, FileUser, Gauge, Sparkles, AlertCircle, RotateCcw } from "lucide-react"
import Link from "next/link"
import { ProgressSteps, type Step } from "@/components/progress-steps"
import { ResultsView, type AnalysisResult } from "@/components/results-view"
import { startAnalysis, type SSEEvent, type GapAnalysis } from "@/lib/api"

// ── 步骤配置（id 与 SSE step 对应）──────────────────────────────
const STEPS: Step[] = [
  { id: "jd",     label: "分析职位描述", icon: <Briefcase className="h-5 w-5" /> },
  { id: "resume", label: "分析简历",     icon: <FileUser  className="h-5 w-5" /> },
  { id: "score",  label: "计算匹配分数", icon: <Gauge     className="h-5 w-5" /> },
]

// SSE step → 步骤索引（current 传给 ProgressSteps）
const STEP_INDEX: Partial<Record<string, number>> = {
  jd_start:     0,
  jd_done:      1,   // jd 完成，resume 开始前
  resume_start: 1,
  resume_done:  2,
  gap_start:    2,
  complete:     3,   // 全部完成
}

// ── GapAnalysis → AnalysisResult 映射 ─────────────────────────
// ResultsView 需要的格式 vs. 后端返回的 GapAnalysis 字段
function toAnalysisResult(gap: GapAnalysis): AnalysisResult {
  return {
    overall: gap.overall_match_score,
    subScores: [
      { label: "技能匹配", score: gap.skill_score },
      { label: "经验匹配", score: gap.experience_score },
      { label: "教育背景", score: gap.education_score },
      { label: "项目相关", score: gap.project_score },
    ],
    strengths:    gap.strengths,
    improvements: gap.weaknesses,
    tips:         gap.recommendations,
  }
}

type Phase = "idle" | "analyzing" | "done" | "error"

export default function AnalyzePage() {
  const [phase, setPhase]         = useState<Phase>("idle")
  const [current, setCurrent]     = useState(0)
  const [statusMsg, setStatusMsg] = useState("")
  const [result, setResult]       = useState<AnalysisResult | null>(null)
  const [errorMsg, setErrorMsg]   = useState("")

  // 保存 SSE 关闭函数，组件卸载时清理
  const closeRef = useRef<(() => void) | null>(null)

  // ── SSE 事件处理 ───────────────────────────────────────────
  const handleEvent = (event: SSEEvent) => {
    const idx = STEP_INDEX[event.step]
    if (idx !== undefined) setCurrent(idx)

    setStatusMsg(event.message)

    if (event.step === "complete" && event.data) {
      const gap = event.data as unknown as GapAnalysis
      setResult(toAnalysisResult(gap))
      setPhase("done")
    }

    if (event.step === "error") {
      setErrorMsg(event.message)
      setPhase("error")
    }
  }

  const handleError = (msg: string) => {
    setErrorMsg(msg)
    setPhase("error")
  }

  // ── 启动分析 ───────────────────────────────────────────────
  function startAnalyzing() {
    setCurrent(0)
    setStatusMsg("")
    setResult(null)
    setErrorMsg("")
    setPhase("analyzing")

    closeRef.current = startAnalysis(handleEvent, handleError)
  }

  // 页面加载时自动开始（与原版行为一致）
  useEffect(() => {
    startAnalyzing()
    return () => closeRef.current?.()
  }, []) // eslint-disable-line react-hooks/exhaustive-deps

  // ── 渲染 ───────────────────────────────────────────────────
  return (
    <div className="min-h-screen bg-gradient-to-br from-secondary via-background to-accent/10 font-sans">
      <main className="mx-auto flex w-full max-w-3xl flex-col gap-8 px-6 py-16">

        {/* 标题 */}
        <header className="flex flex-col items-center gap-3 text-center">
          <div className="flex items-center gap-2 rounded-full border border-border bg-card px-4 py-1.5 text-sm font-medium text-primary shadow-sm">
            <Sparkles className="h-4 w-4" />
            分析结果
          </div>
          <h1 className="text-balance text-3xl font-bold tracking-tight text-foreground sm:text-4xl">
            {phase === "done" ? "你的匹配度分析报告" : "正在分析中…"}
          </h1>
          <p className="max-w-lg text-pretty leading-relaxed text-muted-foreground">
            {phase === "done"
              ? "以下是基于职位描述与简历生成的匹配度评估和面试准备建议。"
              : statusMsg || "请稍候，我们正在对比职位描述与你的简历。"}
          </p>
        </header>

        {/* 进度步骤（分析中 + 完成时都显示）*/}
        {phase !== "error" && (
          <ProgressSteps steps={STEPS} current={current} />
        )}

        {/* 分析结果 */}
        {phase === "done" && result && (
          <ResultsView result={result} />
        )}

        {/* 错误状态 */}
        {phase === "error" && (
          <div className="flex flex-col items-center gap-4 rounded-2xl border border-destructive/30 bg-destructive/5 p-8 text-center">
            <AlertCircle className="h-10 w-10 text-destructive" />
            <p className="text-foreground">
              {errorMsg || "分析过程出现问题，请重试。"}
            </p>
            <button
              type="button"
              onClick={startAnalyzing}
              className="inline-flex items-center gap-2 rounded-xl bg-primary px-6 py-3 text-sm font-semibold text-primary-foreground transition-colors hover:opacity-90"
            >
              <RotateCcw className="h-4 w-4" />
              重新分析
            </button>
          </div>
        )}

        {/* 取消链接 */}
        {phase === "analyzing" && (
          <p className="text-center text-sm text-muted-foreground">
            <Link href="/" className="underline-offset-4 hover:underline">
              取消并返回
            </Link>
          </p>
        )}

        {/* 分析完成后的操作按钮 */}
        {phase === "done" && (
          <div className="flex flex-col gap-3 sm:flex-row sm:justify-center">
            <Link
              href="/questions"
              className="inline-flex items-center justify-center gap-2 rounded-xl bg-primary px-8 py-3 text-sm font-semibold text-primary-foreground transition-opacity hover:opacity-90"
            >
              生成面试题 →
            </Link>
            <Link
              href="/profile"
              className="inline-flex items-center justify-center gap-2 rounded-xl border border-border bg-card px-8 py-3 text-sm font-semibold text-foreground transition-colors hover:bg-secondary"
            >
              查看求职画像
            </Link>
          </div>
        )}
      </main>
    </div>
  )
}