import { Suspense } from "react"
import { HistoryWorkspace } from "@/components/history-workspace"

export default function HistoryPage() {
  return <Suspense fallback={<p className="p-8">正在读取历史入口…</p>}><HistoryWorkspace /></Suspense>
}
