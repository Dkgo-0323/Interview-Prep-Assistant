"use client"

import { useState } from "react"
import { Star, RotateCcw } from "lucide-react"
import {
  type Question,
  categoryLabels,
  difficultyLabels,
  categoryStyles,
  difficultyStyles,
} from "@/lib/questions"
import { cn } from "@/lib/utils"

interface FlashcardProps {
  question: Question
  index: number
  total: number
  bookmarked: boolean
  onToggleBookmark: () => void
}

export function Flashcard({ question, index, total, bookmarked, onToggleBookmark }: FlashcardProps) {
  const [flipped, setFlipped] = useState(false)

  function handleBookmark(e: React.MouseEvent) {
    e.stopPropagation()
    onToggleBookmark()
  }

  return (
    <div className="h-72" style={{ perspective: "1200px" }}>
      <button
        type="button"
        onClick={() => setFlipped((f) => !f)}
        aria-label={flipped ? "查看问题" : "查看参考答案"}
        className="relative h-full w-full rounded-2xl text-left transition-transform duration-500"
        style={{
          transformStyle: "preserve-3d",
          transform: flipped ? "rotateY(180deg)" : "rotateY(0deg)",
        }}
      >
        {/* Front */}
        <div
          className="absolute inset-0 flex flex-col gap-4 rounded-2xl border border-border bg-card p-5 shadow-sm"
          style={{ backfaceVisibility: "hidden", WebkitBackfaceVisibility: "hidden" }}
        >
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-muted-foreground">
              {index + 1} / {total}
            </span>
            <div className="flex items-center gap-2">
              <span
                className={cn(
                  "rounded-full border px-2.5 py-0.5 text-xs font-medium",
                  categoryStyles[question.category],
                )}
              >
                {categoryLabels[question.category]}
              </span>
              <span
                className={cn(
                  "rounded-full border px-2.5 py-0.5 text-xs font-medium",
                  difficultyStyles[question.difficulty],
                )}
              >
                {difficultyLabels[question.difficulty]}
              </span>
              <span
                onClick={handleBookmark}
                role="button"
                tabIndex={0}
                aria-label={bookmarked ? "取消收藏" : "收藏"}
                onKeyDown={(e) => {
                  if (e.key === "Enter" || e.key === " ") {
                    e.preventDefault()
                    e.stopPropagation()
                    onToggleBookmark()
                  }
                }}
                className="rounded-full p-1 text-muted-foreground transition-colors hover:text-amber-500"
              >
                <Star className={cn("h-4 w-4", bookmarked && "fill-amber-400 text-amber-400")} />
              </span>
            </div>
          </div>
          <p className="flex-1 text-pretty text-base font-medium leading-relaxed text-foreground">
            {question.question}
          </p>
          <span className="inline-flex w-fit items-center gap-1.5 rounded-lg bg-primary/10 px-3 py-1.5 text-sm font-semibold text-primary">
            <RotateCcw className="h-3.5 w-3.5" />
            点击查看答案
          </span>
        </div>

        {/* Back */}
        <div
          className="absolute inset-0 flex flex-col gap-3 overflow-auto rounded-2xl border border-primary/30 bg-primary/5 p-5 shadow-sm"
          style={{
            backfaceVisibility: "hidden",
            WebkitBackfaceVisibility: "hidden",
            transform: "rotateY(180deg)",
          }}
        >
          <span className="text-xs font-semibold uppercase tracking-wide text-primary">参考答案</span>
          <p className="flex-1 text-pretty text-sm leading-relaxed text-foreground">{question.answer}</p>
          <span className="inline-flex w-fit items-center gap-1.5 text-sm font-medium text-muted-foreground">
            <RotateCcw className="h-3.5 w-3.5" />
            点击返回问题
          </span>
        </div>
      </button>
    </div>
  )
}
