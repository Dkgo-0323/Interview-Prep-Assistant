import { APIError, type SSEEvent, type GapAnalysis, type QuestionsResponse } from "./api"

const BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000"
export const githubLoginURL = `${BASE}/api/auth/github/login`

export interface RecordSummary {
  id: string
  title: string
  revision: number
  created_at: string
  updated_at: string
}
export interface RecordDetail extends RecordSummary {
  inputs: { jd_text?: string; resume_text?: string }
  results: { gap?: GapAnalysis; questions?: { questions: QuestionsResponse["questions"] } }
}
export interface RecordTask {
  kind: "analysis" | "questions"
  revision: number
  attempt: string
  status: "running" | "completed" | "failed" | "interrupted"
  updated_at: string
}

// Account requests never initialize an anonymous session or retry mutations.
async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const res = await fetch(`${BASE}/api${path}`, { ...options, credentials: "include", cache: "no-store" })
  if (!res.ok) {
    const body = await res.json().catch(() => null)
    throw new APIError(res.status, typeof body?.detail === "string" ? body.detail : `HTTP ${res.status}`)
  }
  return (res.status === 204 ? undefined : await res.json()) as T
}
const json = (method: string, body: object): RequestInit => ({
  method, headers: { "Content-Type": "application/json" }, body: JSON.stringify(body),
})
const recordPath = (id: string) => `/records/${encodeURIComponent(id)}`
export const getAccount = (signal?: AbortSignal) => request<{ account_id: string }>("/auth/me", { signal })
export const logoutAccount = () => request<{ success: boolean }>("/auth/logout", { method: "POST" })
export const listRecords = (signal?: AbortSignal) => request<RecordSummary[]>("/records", { signal })
export const createRecord = (title: string) => request<RecordDetail>("/records", json("POST", { title }))
export const readRecord = (id: string, signal?: AbortSignal) => request<RecordDetail>(recordPath(id), { signal })
export const renameRecord = (id: string, title: string) => request<RecordDetail>(recordPath(id), json("PATCH", { title }))
export const deleteRecord = (id: string) => request<void>(recordPath(id), { method: "DELETE" })
export const readTasks = (id: string, signal?: AbortSignal) => request<RecordTask[]>(`${recordPath(id)}/tasks`, { signal })
export function uploadRecord(id: string, revision: number, kind: "jd" | "resume", file: File) {
  const body = new FormData()
  body.append("file", file)
  return request<RecordDetail>(`${recordPath(id)}/upload/${kind}?revision=${revision}`, { method: "POST", body })
}
export const clearRecordInputs = (id: string, revision: number) =>
  request<RecordDetail>(`${recordPath(id)}/inputs`, json("DELETE", { revision }))
export const generateRecordQuestions = (id: string, revision: number, count: number) =>
  request<QuestionsResponse>(`${recordPath(id)}/questions/generate`, json("POST", { revision, num_questions: count }))

// POST + fetch streaming: a read, reload or reconnect cannot start generation.
export async function analyzeRecord(id: string, revision: number, onEvent: (event: SSEEvent) => void, signal: AbortSignal) {
  const res = await fetch(`${BASE}/api${recordPath(id)}/analysis/stream`, {
    ...json("POST", { revision }), credentials: "include", cache: "no-store", signal,
  })
  if (!res.ok) {
    const body = await res.json().catch(() => null)
    throw new APIError(res.status, typeof body?.detail === "string" ? body.detail : `HTTP ${res.status}`)
  }
  if (!res.headers.get("content-type")?.includes("text/event-stream") || !res.body) throw new Error("分析响应格式无效")
  const reader = res.body.getReader()
  const decoder = new TextDecoder()
  let buffer = "", terminal = false
  function dispatch(frame: string) {
    const data = frame.split("\n").filter(line => line.startsWith("data:")).map(line => line.slice(5).trimStart()).join("\n")
    if (!data) return // comments/heartbeats
    const event = JSON.parse(data) as SSEEvent
    if (event.step === "error") throw new APIError(typeof event.data?.status === "number" ? event.data.status : 500, event.message)
    onEvent(event)
    if (event.step === "complete") terminal = true
  }
  try {
    while (!terminal) {
      const { done, value } = await reader.read()
      buffer += decoder.decode(value, { stream: !done })
      // Normalize only complete CRLF pairs; a chunk can end between CR and LF.
      buffer = buffer.replace(/\r\n/g, "\n")
      let end: number
      while (!terminal && (end = buffer.indexOf("\n\n")) >= 0) {
        const frame = buffer.slice(0, end)
        buffer = buffer.slice(end + 2)
        dispatch(frame)
      }
      if (buffer.length > 2_000_000) throw new Error("分析响应过大，请刷新记录")
      if (done) {
        if (!terminal) throw new Error("分析连接提前结束，请刷新任务状态后明确重试")
        break
      }
    }
  } finally {
    await reader.cancel().catch(() => {})
    reader.releaseLock()
  }
}
