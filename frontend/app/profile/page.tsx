"use client"

import { useState } from "react"
import Link from "next/link"
import {
  Sparkles,
  BadgeCheck,
  Award,
  Target,
  Building2,
  Tags,
  Wallet,
  Loader2,
  AlertCircle,
  ArrowLeft,
  RefreshCw,
} from "lucide-react"
import { fetchProfile, type CareerProfile } from "@/lib/profile"
import { StrengthsRadar } from "@/components/strengths-radar"
import { CompanyFit } from "@/components/company-fit"
import { KeywordCloud } from "@/components/keyword-cloud"
import { SalaryRange } from "@/components/salary-range"

type Status = "idle" | "loading" | "success" | "error"

function SectionCard({
  icon: Icon,
  title,
  children,
  className = "",
}: {
  icon: React.ElementType
  title: string
  children: React.ReactNode
  className?: string
}) {
  return (
    <section className={`rounded-2xl border border-border bg-card p-6 shadow-sm ${className}`}>
      <h2 className="mb-5 flex items-center gap-2 text-base font-semibold text-foreground">
        <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary/10 text-primary">
          <Icon className="h-4 w-4" />
        </span>
        {title}
      </h2>
      {children}
    </section>
  )
}

export default function ProfilePage() {
  const [status, setStatus] = useState<Status>("idle")
  const [profile, setProfile] = useState<CareerProfile | null>(null)

  async function handleGenerate() {
    setStatus("loading")
    try {
      const data = await fetchProfile()
      setProfile(data)
      setStatus("success")
    } catch (err) {
      console.log("[v0] generate profile failed", err)
      setStatus("error")
    }
  }

  return (
    <main className="min-h-svh bg-gradient-to-b from-secondary/40 via-background to-background">
      <div className="mx-auto w-full max-w-5xl px-4 py-10 sm:px-6">
        {/* Header */}
        <div className="mb-8 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div className="flex flex-col gap-1">
            <Link
              href="/"
              className="inline-flex w-fit items-center gap-1.5 text-sm text-muted-foreground transition-colors hover:text-foreground"
            >
              <ArrowLeft className="h-4 w-4" />
              返回首页
            </Link>
            <h1 className="text-2xl font-bold text-foreground text-balance sm:text-3xl">求职画像</h1>
            <p className="text-sm text-muted-foreground text-pretty">
              基于你的简历与目标职位，生成专业的求职定位与能力分析。
            </p>
          </div>
          <button
            type="button"
            onClick={handleGenerate}
            disabled={status === "loading"}
            className="inline-flex shrink-0 items-center justify-center gap-2 rounded-xl bg-primary px-5 py-3 text-sm font-semibold text-primary-foreground transition-opacity hover:opacity-90 disabled:cursor-not-allowed disabled:opacity-60"
          >
            {status === "loading" ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin" />
                生成中...
              </>
            ) : (
              <>
                <Sparkles className="h-4 w-4" />
                {status === "success" ? "重新生成" : "生成画像"}
              </>
            )}
          </button>
        </div>

        {/* Idle */}
        {status === "idle" && (
          <div className="flex flex-col items-center justify-center gap-3 rounded-2xl border border-dashed border-border bg-card/50 py-20 text-center">
            <span className="flex h-14 w-14 items-center justify-center rounded-2xl bg-primary/10 text-primary">
              <Sparkles className="h-7 w-7" />
            </span>
            <p className="text-base font-semibold text-foreground">还没有生成画像</p>
            <p className="max-w-sm text-sm text-muted-foreground text-pretty">
              点击右上角「生成画像」，我们将为你分析求职定位、核心优势与薪资区间。
            </p>
          </div>
        )}

        {/* Loading */}
        {status === "loading" && (
          <div className="flex flex-col items-center justify-center gap-3 rounded-2xl border border-border bg-card py-20 text-center">
            <Loader2 className="h-8 w-8 animate-spin text-primary" />
            <p className="text-sm font-medium text-foreground">正在生成你的求职画像...</p>
            <p className="text-xs text-muted-foreground">分析能力维度与市场数据中</p>
          </div>
        )}

        {/* Error */}
        {status === "error" && (
          <div className="flex flex-col items-center justify-center gap-3 rounded-2xl border border-destructive/30 bg-destructive/5 py-20 text-center">
            <AlertCircle className="h-8 w-8 text-destructive" />
            <p className="text-sm font-semibold text-foreground">生成失败</p>
            <p className="max-w-sm text-sm text-muted-foreground text-pretty">
              获取画像数据时出现问题，请稍后重试。
            </p>
            <button
              type="button"
              onClick={handleGenerate}
              className="mt-1 inline-flex items-center gap-2 rounded-xl border border-border bg-card px-4 py-2 text-sm font-semibold text-foreground transition-colors hover:bg-secondary"
            >
              <RefreshCw className="h-4 w-4" />
              重试
            </button>
          </div>
        )}

        {/* Success */}
        {status === "success" && profile && (
          <div className="flex flex-col gap-6">
            {/* Profile summary */}
            <section className="rounded-2xl border border-primary/20 bg-gradient-to-br from-primary/10 via-accent/5 to-card p-6 shadow-sm sm:p-8">
              <h2 className="text-2xl font-bold text-foreground text-balance sm:text-3xl">
                {profile.jobTitle}
              </h2>
              <p className="mt-2 inline-flex items-center gap-1.5 rounded-full bg-card px-3 py-1 text-sm font-medium text-primary">
                <BadgeCheck className="h-4 w-4" />
                {profile.seniority}
              </p>
              <p className="mt-4 max-w-2xl text-sm leading-relaxed text-muted-foreground text-pretty">
                {profile.positioning}
              </p>
            </section>

            {/* Core strengths: radar + list */}
            <SectionCard icon={Award} title="核心优势">
              <div className="grid gap-6 lg:grid-cols-2 lg:items-center">
                <StrengthsRadar data={profile.radar} />
                <ul className="flex flex-col gap-3">
                  {profile.strengths.map((s) => (
                    <li key={s} className="flex items-start gap-2.5 text-sm text-foreground">
                      <Target className="mt-0.5 h-4 w-4 shrink-0 text-primary" />
                      <span className="leading-relaxed text-pretty">{s}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </SectionCard>

            {/* Company fit */}
            <SectionCard icon={Building2} title="公司类型匹配度">
              <CompanyFit items={profile.companyFit} />
            </SectionCard>

            <div className="grid gap-6 lg:grid-cols-2">
              {/* Keywords */}
              <SectionCard icon={Tags} title="推荐求职关键词">
                <KeywordCloud keywords={profile.keywords} />
              </SectionCard>

              {/* Salary */}
              <SectionCard icon={Wallet} title="薪资区间预估">
                <SalaryRange salary={profile.salary} />
              </SectionCard>
            </div>
          </div>
        )}
      </div>
    </main>
  )
}
