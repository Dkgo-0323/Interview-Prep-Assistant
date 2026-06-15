"use client"

import { Search } from "lucide-react"
import { type Category, type Difficulty, categoryLabels, difficultyLabels } from "@/lib/questions"
import { cn } from "@/lib/utils"

export type CategoryFilter = Category | "all"
export type DifficultyFilter = Difficulty | "all"

interface FilterBarProps {
  category: CategoryFilter
  difficulty: DifficultyFilter
  search: string
  onCategoryChange: (c: CategoryFilter) => void
  onDifficultyChange: (d: DifficultyFilter) => void
  onSearchChange: (s: string) => void
}

const categoryOptions: { value: CategoryFilter; label: string }[] = [
  { value: "all", label: "全部" },
  { value: "technical", label: categoryLabels.technical },
  { value: "behavioral", label: categoryLabels.behavioral },
  { value: "situational", label: categoryLabels.situational },
]

const difficultyOptions: { value: DifficultyFilter; label: string }[] = [
  { value: "all", label: "全部" },
  { value: "basic", label: difficultyLabels.basic },
  { value: "intermediate", label: difficultyLabels.intermediate },
  { value: "advanced", label: difficultyLabels.advanced },
]

function Pill({
  active,
  onClick,
  children,
}: {
  active: boolean
  onClick: () => void
  children: React.ReactNode
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={cn(
        "rounded-full px-3.5 py-1.5 text-sm font-medium transition-colors",
        active
          ? "bg-primary text-primary-foreground"
          : "bg-secondary text-secondary-foreground hover:bg-secondary/70",
      )}
    >
      {children}
    </button>
  )
}

export function QuestionFilterBar({
  category,
  difficulty,
  search,
  onCategoryChange,
  onDifficultyChange,
  onSearchChange,
}: FilterBarProps) {
  return (
    <div className="flex flex-col gap-4 rounded-2xl border border-border bg-card p-5 shadow-sm">
      <div className="relative">
        <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
        <input
          type="search"
          value={search}
          onChange={(e) => onSearchChange(e.target.value)}
          placeholder="搜索面试题..."
          className="w-full rounded-xl border border-border bg-background py-2.5 pl-10 pr-4 text-sm text-foreground outline-none transition-colors focus:border-primary focus:ring-2 focus:ring-primary/20"
        />
      </div>
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:gap-6">
        <div className="flex flex-wrap items-center gap-2">
          <span className="text-xs font-semibold text-muted-foreground">类别</span>
          {categoryOptions.map((o) => (
            <Pill key={o.value} active={category === o.value} onClick={() => onCategoryChange(o.value)}>
              {o.label}
            </Pill>
          ))}
        </div>
        <div className="flex flex-wrap items-center gap-2">
          <span className="text-xs font-semibold text-muted-foreground">难度</span>
          {difficultyOptions.map((o) => (
            <Pill key={o.value} active={difficulty === o.value} onClick={() => onDifficultyChange(o.value)}>
              {o.label}
            </Pill>
          ))}
        </div>
      </div>
    </div>
  )
}
