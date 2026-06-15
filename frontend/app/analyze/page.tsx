"use client"

import { useEffect, useState } from "react"
import { Briefcase, FileUser, Gauge, Sparkles, AlertCircle, RotateCcw } from "lucide-react"
import Link from "next/link"
import { ProgressSteps, type Step } from "@/components/progress-steps"
import { ResultsView, type AnalysisResult } from "@/components/results-view"

const steps: Step[] = [
  { id: "jd", label: "分析职位描述", icon: <Briefcase className="h-5 w-5" /> },
  { id: "resume", label: "分析简历", icon: <FileUser className="h-5 w-5" /> },
  { id: "score", label: "计算匹配分数", icon: <Gauge className="h-5 w-5" /> },
]

const mockResult: AnalysisResult = {
  overall: 82,
  subScores: [
    { label: "技能匹配", score: 88 },
    { label: "经验匹配", score: 76 },
    { label: "教育背景", score: 90 },
    { label: "文化契合", score: 74 },
  ],
  strengths: [
    "扎实的前端工程能力，与岗位的核心技术栈高度吻合",
    "拥有从 0 到 1 主导产品落地的完整经验",
    "教育背景与岗位要求完全匹配",
    "具备良好的跨团队协作与沟通记录",
  ],
  improvements: [
    "缺少大规模分布式系统的实战经验",
    "团队管理与带人经验描述较为薄弱",
    "可补充更多可量化的业务成果数据",
  ],
  tips: [
    "准备 2-3 个 STAR 结构的项目案例，突出你主导落地的成果",
    "针对分布式系统相关问题，提前梳理你的学习路径与思考",
    "用具体数字量化过往贡献，例如性能提升、效率改进的百分比",
    "研究目标公司的产品与文化，准备有针对性的反向提问",
  ],
}

type Phase = "analyzing" | "done" | "error"

export default function AnalyzePage() {
  const [current, setCurrent] = useState(0)
  const [phase, setPhase] = useState<Phase>("analyzing")

  useEffect(() => {
    if (phase !== "analyzing") return

    const timers: ReturnType<typeof setTimeout>[] = []
    timers.push(setTimeout(() => setCurrent(1), 1200))
    timers.push(setTimeout(() => setCurrent(2), 2400))
    timers.push(setTimeout(() => setCurrent(3), 3600))
    timers.push(setTimeout(() => setPhase("done"), 4000))

    return () => timers.forEach(clearTimeout)
  }, [phase])

  function retry() {
    setCurrent(0)
    setPhase("analyzing")
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-secondary via-background to-accent/10 font-sans">
      <main className="mx-auto flex w-full max-w-3xl flex-col gap-8 px-6 py-16">
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
              : "请稍候，我们正在对比职位描述与你的简历。"}
          </p>
        </header>

        {phase !== "error" && <ProgressSteps steps={steps} current={current} />}

        {phase === "done" && <ResultsView result={mockResult} />}

        {phase === "error" && (
          <div className="flex flex-col items-center gap-4 rounded-2xl border border-destructive/30 bg-destructive/5 p-8 text-center">
            <AlertCircle className="h-10 w-10 text-destructive" />
            <p className="text-foreground">分析过程出现问题，请重试。</p>
            <button
              type="button"
              onClick={retry}
              className="inline-flex items-center gap-2 rounded-xl bg-primary px-6 py-3 text-sm font-semibold text-primary-foreground transition-colors hover:opacity-90"
            >
              <RotateCcw className="h-4 w-4" />
              重新分析
            </button>
          </div>
        )}

        {phase === "analyzing" && (
          <p className="text-center text-sm text-muted-foreground">
            <Link href="/" className="underline-offset-4 hover:underline">
              取消并返回
            </Link>
          </p>
        )}
      </main>
    </div>
  )
}
