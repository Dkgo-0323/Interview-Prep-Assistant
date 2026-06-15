"use client"

import { useMemo, useState } from "react"
import Link from "next/link"
import { ArrowLeft, BookOpen, Star } from "lucide-react"
import { questions } from "@/lib/questions"
import { Flashcard } from "@/components/flashcard"
import {
  QuestionFilterBar,
  type CategoryFilter,
  type DifficultyFilter,
} from "@/components/question-filter-bar"

const PAGE_SIZE = 10

export default function QuestionsPage() {
  const [category, setCategory] = useState<CategoryFilter>("all")
  const [difficulty, setDifficulty] = useState<DifficultyFilter>("all")
  const [search, setSearch] = useState("")
  const [visible, setVisible] = useState(PAGE_SIZE)
  const [bookmarks, setBookmarks] = useState<Set<number>>(new Set())
  const [onlyBookmarked, setOnlyBookmarked] = useState(false)

  const filtered = useMemo(() => {
    return questions.filter((q) => {
      if (category !== "all" && q.category !== category) return false
      if (difficulty !== "all" && q.difficulty !== difficulty) return false
      if (onlyBookmarked && !bookmarks.has(q.id)) return false
      if (search.trim() && !q.question.toLowerCase().includes(search.trim().toLowerCase())) return false
      return true
    })
  }, [category, difficulty, search, onlyBookmarked, bookmarks])

  const shown = filtered.slice(0, visible)

  function toggleBookmark(id: number) {
    setBookmarks((prev) => {
      const next = new Set(prev)
      if (next.has(id)) next.delete(id)
      else next.add(id)
      return next
    })
  }

  return (
    <main className="min-h-svh bg-gradient-to-b from-secondary/40 to-background">
      <div className="mx-auto flex w-full max-w-5xl flex-col gap-6 px-4 py-10 md:py-14">
        <header className="flex flex-col gap-4">
          <Link
            href="/analyze"
            className="inline-flex w-fit items-center gap-1.5 text-sm font-medium text-muted-foreground transition-colors hover:text-foreground"
          >
            <ArrowLeft className="h-4 w-4" />
            返回分析报告
          </Link>
          <div className="flex flex-col gap-2">
            <div className="flex items-center gap-2.5">
              <span className="flex h-10 w-10 items-center justify-center rounded-xl bg-primary text-primary-foreground">
                <BookOpen className="h-5 w-5" />
              </span>
              <h1 className="text-2xl font-semibold tracking-tight text-foreground md:text-3xl">面试题练习</h1>
            </div>
            <p className="text-pretty text-sm leading-relaxed text-muted-foreground">
              点击卡片翻转查看参考答案，使用筛选与搜索快速定位，收藏重点题目反复练习。
            </p>
          </div>
        </header>

        <QuestionFilterBar
          category={category}
          difficulty={difficulty}
          search={search}
          onCategoryChange={(c) => {
            setCategory(c)
            setVisible(PAGE_SIZE)
          }}
          onDifficultyChange={(d) => {
            setDifficulty(d)
            setVisible(PAGE_SIZE)
          }}
          onSearchChange={(s) => {
            setSearch(s)
            setVisible(PAGE_SIZE)
          }}
        />

        <div className="flex items-center justify-between">
          <p className="text-sm text-muted-foreground">
            共 <span className="font-semibold text-foreground">{filtered.length}</span> 道题目
          </p>
          <button
            type="button"
            onClick={() => {
              setOnlyBookmarked((v) => !v)
              setVisible(PAGE_SIZE)
            }}
            className={`inline-flex items-center gap-1.5 rounded-full border px-3.5 py-1.5 text-sm font-medium transition-colors ${
              onlyBookmarked
                ? "border-amber-300 bg-amber-50 text-amber-700"
                : "border-border bg-card text-muted-foreground hover:text-foreground"
            }`}
          >
            <Star className={`h-4 w-4 ${onlyBookmarked ? "fill-amber-400 text-amber-400" : ""}`} />
            仅看收藏 ({bookmarks.size})
          </button>
        </div>

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
            <p className="text-sm font-medium text-foreground">没有匹配的题目</p>
            <p className="text-sm text-muted-foreground">试试调整筛选条件或搜索关键词</p>
          </div>
        )}

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
      </div>
    </main>
  )
}
