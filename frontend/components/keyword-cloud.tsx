"use client"

import { useState } from "react"
import { Copy, Check } from "lucide-react"

export function KeywordCloud({ keywords }: { keywords: string[] }) {
  const [copied, setCopied] = useState(false)

  async function handleCopy() {
    try {
      await navigator.clipboard.writeText(keywords.join("、"))
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    } catch (err) {
      console.log("[v0] copy failed", err)
    }
  }

  return (
    <div className="flex flex-col gap-4">
      <div className="flex flex-wrap gap-2">
        {keywords.map((kw) => (
          <span
            key={kw}
            className="rounded-full border border-primary/20 bg-primary/5 px-3.5 py-1.5 text-sm font-medium text-primary"
          >
            {kw}
          </span>
        ))}
      </div>
      <button
        type="button"
        onClick={handleCopy}
        className="inline-flex w-full items-center justify-center gap-2 rounded-xl border border-border bg-card px-4 py-2.5 text-sm font-semibold text-foreground transition-colors hover:bg-secondary sm:w-auto"
      >
        {copied ? (
          <>
            <Check className="h-4 w-4 text-primary" />
            已复制
          </>
        ) : (
          <>
            <Copy className="h-4 w-4" />
            复制全部关键词
          </>
        )}
      </button>
    </div>
  )
}
