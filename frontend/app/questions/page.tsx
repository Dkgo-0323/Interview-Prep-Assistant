// frontend/app/questions/page.tsx
"use client"

import { useEffect, useMemo, useState } from "react"
import Link from "next/link"
import {
  ArrowLeft, BookOpen, Star, Loader2, AlertCircle, RefreshCw,
} from "lucide-react"
import {
  questions as fallbackQuestions,   // mock 兜底数据
  mapBackendQuestions,
  type Question,
} from "@/lib/questions"
import { APIError, generateQuestions, getCachedQuestions } from "@/lib/api"
import { Flashcard } from "@/components/flashcard"
import {
  QuestionFilterBar,
  type CategoryFilter,
  type DifficultyFilter,
} from "@/components/question-filter-bar"

const PAGE_SIZE = 10

type LoadStatus = "idle" | "loading" | "success" | "error"
type QuestionSource = "cached" | "generated" | "example"

const SOURCE_LABELS: Record<QuestionSource, { title: string; description: string }> = {
  cached: { title: "后端缓存", description: "当前匿名会话已有的生成结果；闲置过期或服务重启后需重新上传分析。" },
  generated: { title: "本次生成", description: "基于服务端现有岗位分析结果生成。" },
  example: { title: "固定示例，非个性化", description: "仅用于体验题库，不基于本次上传的简历或职位描述。" },
}

export default function QuestionsPage() {
  // ── 数据状态 ───────────────────────────────────────────────
  const [allQuestions, setAllQuestions] = useState<Question[]>([])
  const [loadStatus, setLoadStatus]     = useState<LoadStatus>("loading")
  const [errorMsg, setErrorMsg]         = useState("")
  const [source, setSource] = useState<QuestionSource | null>(null)
  const [requestKind, setRequestKind] = useState<"cached" | "generated">("cached")
  const [numToGenerate, setNumToGenerate] = useState(10)

  // ── 筛选 & UI 状态 ─────────────────────────────────────────
  const [category, setCategory]         = useState<CategoryFilter>("all")
  const [difficulty, setDifficulty]     = useState<DifficultyFilter>("all")
  const [search, setSearch]             = useState("")
  const [visible, setVisible]           = useState(PAGE_SIZE)
  const [bookmarks, setBookmarks]       = useState<Set<number>>(new Set())
  const [onlyBookmarked, setOnlyBookmarked] = useState(false)

  // ── 加载题目（优先读缓存，没有再生成）─────────────────────
  async function fetchQuestions(forceNew = false) {
    let operation: "cached" | "generated" = forceNew ? "generated" : "cached"
    try {
      let response
      let shouldGenerate = forceNew

      if (!forceNew) {
        // 先尝试拿缓存
        try {
          response = await getCachedQuestions()
        } catch (err) {
          // 只有 404 表示无缓存；网络/服务错误不能悄悄触发模型生成。
          if (!(err instanceof APIError) || err.status !== 404) throw err
          shouldGenerate = true
        }
      }

      // 没有缓存 或 强制重新生成
      if (shouldGenerate) {
        operation = "generated"
        setRequestKind("generated")
        response = await generateQuestions(numToGenerate)
      }

      if (!response) throw new Error("题目响应无效")
      const mapped = mapBackendQuestions(response.questions)
      setAllQuestions(mapped)
      setSource(operation)
      setBookmarks(new Set())
      setLoadStatus("success")
      setVisible(PAGE_SIZE)   // 重置分页
    } catch (err) {
      const msg = err instanceof Error ? err.message : "题目加载失败"

      // 降级：用 mock 数据，至少能看到页面
      setAllQuestions(fallbackQuestions)
      setSource("example")
      setBookmarks(new Set())
      setErrorMsg(`${operation === "cached" ? "读取缓存失败" : "生成失败"}：${msg}`)
      setLoadStatus("error")
    }
  }

  // 页面挂载时自动加载
  function loadQuestions(forceNew = false) {
    setLoadStatus("loading")
    setSource(null)
    setRequestKind(forceNew ? "generated" : "cached")
    setErrorMsg("")
    void fetchQuestions(forceNew)
  }

  useEffect(() => {
    async function loadInitialQuestions() {
      await Promise.resolve()
      await fetchQuestions()
    }

    void loadInitialQuestions()
  }, []) // eslint-disable-line react-hooks/exhaustive-deps -- initialize once; later generation is user-triggered.

  // ── 筛选逻辑 ───────────────────────────────────────────────
  const filtered = useMemo(() => {
    return allQuestions.filter((q) => {
      if (category !== "all"   && q.category   !== category)   return false
      if (difficulty !== "all" && q.difficulty !== difficulty) return false
      if (onlyBookmarked && !bookmarks.has(q.id))              return false
      if (
        search.trim() &&
        !q.question.toLowerCase().includes(search.trim().toLowerCase())
      ) return false
      return true
    })
  }, [allQuestions, category, difficulty, search, onlyBookmarked, bookmarks])

  const shown = filtered.slice(0, visible)

  function toggleBookmark(id: number) {
    setBookmarks((prev) => {
      const next = new Set(prev)
      if (next.has(id)) {
        next.delete(id)
      } else {
        next.add(id)
      }
      return next
    })
  }

  function resetFilters() {
    setCategory("all")
    setDifficulty("all")
    setSearch("")
    setVisible(PAGE_SIZE)
  }

  // ── 渲染 ───────────────────────────────────────────────────
  return (
    <main className="min-h-svh bg-gradient-to-b from-secondary/40 to-background">
      <div className="mx-auto flex w-full max-w-5xl flex-col gap-6 px-4 py-10 md:py-14">

        {/* 页头 */}
        <header className="flex flex-col gap-4">
          <Link
            href="/analyze"
            className="inline-flex w-fit items-center gap-1.5 text-sm font-medium text-muted-foreground transition-colors hover:text-foreground"
          >
            <ArrowLeft className="h-4 w-4" />
            返回分析报告
          </Link>

          <div className="flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
            <div className="flex flex-col gap-2">
              <div className="flex items-center gap-2.5">
                <span className="flex h-10 w-10 items-center justify-center rounded-xl bg-primary text-primary-foreground">
                  <BookOpen className="h-5 w-5" />
                </span>
                <h1 className="text-2xl font-semibold tracking-tight text-foreground md:text-3xl">
                  面试题练习
                </h1>
              </div>
              <p className="text-pretty text-sm leading-relaxed text-muted-foreground">
                点击卡片翻转查看参考答案，使用筛选与搜索快速定位，收藏重点题目反复练习。
              </p>
            </div>

            {/* 重新生成控制区 */}
            {loadStatus === "success" && (
              <div className="flex items-center gap-2 self-start sm:self-auto">
                <select
                  value={numToGenerate}
                  onChange={(e) => setNumToGenerate(Number(e.target.value))}
                  className="rounded-lg border border-border bg-card px-3 py-2 text-sm text-foreground outline-none focus:border-primary"
                >
                  {[10, 15, 20, 30].map((n) => (
                    <option key={n} value={n}>{n} 道题</option>
                  ))}
                </select>
                <button
                  type="button"
                  onClick={() => loadQuestions(true)}
                  className="inline-flex items-center gap-1.5 rounded-lg border border-border bg-card px-3 py-2 text-sm font-medium text-foreground transition-colors hover:bg-secondary"
                >
                  <RefreshCw className="h-4 w-4" />
                  重新生成
                </button>
              </div>
            )}
          </div>
        </header>

        {/* ── 加载中 ── */}
        {loadStatus === "loading" && (
          <div className="flex flex-col items-center justify-center gap-3 rounded-2xl border border-border bg-card py-20 text-center">
            <Loader2 className="h-8 w-8 animate-spin text-primary" />
            <p className="text-sm font-medium text-foreground">
              {requestKind === "cached" ? "正在读取题目缓存…" : "正在生成面试题…"}
            </p>
            <p className="text-xs text-muted-foreground">
              {requestKind === "cached" ? "缓存不存在时将根据已有分析生成题目" : "基于现有岗位分析，请稍候"}
            </p>
          </div>
        )}

        {/* ── 错误提示（降级显示 mock 数据）── */}
        {loadStatus === "error" && (
          <div className="flex items-start gap-3 rounded-xl border border-destructive/30 bg-destructive/5 p-4">
            <AlertCircle className="mt-0.5 h-4 w-4 shrink-0 text-destructive" />
            <div className="flex-1 text-sm">
              <span className="text-muted-foreground">{errorMsg}</span>
              <span className="ml-1 text-muted-foreground">（以下为示例题目）</span>
            </div>
            <button
              type="button"
              onClick={() => loadQuestions(true)}
              className="shrink-0 text-sm font-medium text-primary hover:underline"
            >
              重新生成
            </button>
          </div>
        )}

        {/* ── 题目内容区（加载完成后显示）── */}
        {(loadStatus === "success" || loadStatus === "error") && (
          <>
            {source && (
              <div role="status" className="rounded-xl border border-border bg-card px-4 py-3 text-sm">
                <p className="font-semibold text-foreground">题目来源：{SOURCE_LABELS[source].title}</p>
                <p className="mt-1 text-muted-foreground">{SOURCE_LABELS[source].description}</p>
              </div>
            )}

            {/* 筛选栏 */}
            <QuestionFilterBar
              category={category}
              difficulty={difficulty}
              search={search}
              onCategoryChange={(c) => { setCategory(c); setVisible(PAGE_SIZE) }}
              onDifficultyChange={(d) => { setDifficulty(d); setVisible(PAGE_SIZE) }}
              onSearchChange={(s) => { setSearch(s); setVisible(PAGE_SIZE) }}
            />

            {/* 统计 + 收藏切换 */}
            <div className="flex items-center justify-between">
              <p className="text-sm text-muted-foreground">
                共{" "}
                <span className="font-semibold text-foreground">
                  {filtered.length}
                </span>{" "}
                道题目
                {loadStatus === "success" && (
                  <span className="ml-1 text-xs">
                    （共 {allQuestions.length} 题）
                  </span>
                )}
              </p>
              <button
                type="button"
                onClick={() => { setOnlyBookmarked((v) => !v); setVisible(PAGE_SIZE) }}
                className={`inline-flex items-center gap-1.5 rounded-full border px-3.5 py-1.5 text-sm font-medium transition-colors ${
                  onlyBookmarked
                    ? "border-amber-300 bg-amber-50 text-amber-700"
                    : "border-border bg-card text-muted-foreground hover:text-foreground"
                }`}
              >
                <Star
                  className={`h-4 w-4 ${onlyBookmarked ? "fill-amber-400 text-amber-400" : ""}`}
                />
                仅看收藏 ({bookmarks.size})
              </button>
            </div>

            {/* 题目卡片网格 */}
            {shown.length > 0 ? (
              <div className="grid gap-5 md:grid-cols-2">
                {shown.map((q, i) => (
                  <Flashcard
                    key={q.id}
                    question={q}
                    index={i}
                    total={filtered.length}
                    bookmarked={bookmarks.has(q.id)}
                    onToggleBookmark={() => toggleBookmark(q.id)}
                  />
                ))}
              </div>
            ) : (
              <div className="flex flex-col items-center gap-2 rounded-2xl border border-dashed border-border bg-card py-16 text-center">
                <p className="text-sm font-medium text-foreground">
                  没有匹配的题目
                </p>
                <p className="text-sm text-muted-foreground">
                  试试调整筛选条件或搜索关键词
                </p>
                <button
                  type="button"
                  onClick={resetFilters}
                  className="mt-2 text-sm font-medium text-primary hover:underline"
                >
                  清除筛选
                </button>
              </div>
            )}

            {/* 加载更多 */}
            {visible < filtered.length && (
              <div className="flex justify-center pt-2">
                <button
                  type="button"
                  onClick={() => setVisible((v) => v + PAGE_SIZE)}
                  className="rounded-xl bg-primary px-6 py-3 text-sm font-semibold text-primary-foreground transition-opacity hover:opacity-90"
                >
                  加载更多题目
                </button>
              </div>
            )}
          </>
        )}
      </div>
    </main>
  )
}
