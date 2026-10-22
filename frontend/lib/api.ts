// frontend/lib/api.ts
// 所有后端 API 调用的统一封装

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000"

// ─────────────────────────────────────────────────────────────
// 类型定义（与后端 api/schemas.py + models/schemas.py 对齐）
// ─────────────────────────────────────────────────────────────

export interface UploadResponse {
  success: boolean
  filename: string
  char_count: number
  preview: string
}

export interface UploadStatus {
  jd_uploaded: boolean
  resume_uploaded: boolean
  ready_to_analyze: boolean
  jd_char_count: number
  resume_char_count: number
}

// SSE 事件 step 的枚举
export type SSEStep =
  | "jd_start"
  | "jd_done"
  | "resume_start"
  | "resume_done"
  | "gap_start"
  | "complete"
  | "error"

export interface SSEEvent {
  step: SSEStep
  message: string
  data?: Record<string, unknown>
}

// GapAnalysis 对应 models/schemas.py 的 GapAnalysis
export interface GapAnalysis {
  matched_skills: string[]
  missing_skills: string[]
  skill_score: number
  experience_match: string
  experience_score: number
  education_match: string
  education_score: number
  project_relevance: string
  project_score: number
  strengths: string[]
  weaknesses: string[]
  recommendations: string[]
  overall_match_score: number
}

// Question 对应 models/schemas.py 的 Question
export interface Question {
  question_text: string
  question_type: "技术深度" | "项目经验" | "情景模拟" | "行为面试"
  difficulty: "基础" | "进阶" | "高级"
  focus_area: string
  intent: string
  reference_answer: string
}

export interface QuestionsResponse {
  success: boolean
  total: number
  questions: Question[]
}

// UserProfile 对应 api/schemas.py 的 UserProfile
export interface UserProfile {
  core_strengths: string[]
  suitable_company_size: string
  career_stage: string
  search_keywords: string[]
  positioning_summary: string
  salary_range_estimate: string
}

export interface ProfileResponse {
  success: boolean
  profile: UserProfile
}

// ─────────────────────────────────────────────────────────────
// 工具函数
// ─────────────────────────────────────────────────────────────

export class APIError extends Error {
  constructor(public readonly status: number, message: string) {
    super(message)
    this.name = "APIError"
  }
}

let sessionInitialization: Promise<void> | null = null

// Both first uploads await the same cookie response before sending their files.
async function ensureSession(): Promise<void> {
  if (!sessionInitialization) {
    const pending = fetch(`${API_BASE}/api/session`, {
      method: "POST", credentials: "include", cache: "no-store",
    }).then(async res => { await handleResponse(res) })
    sessionInitialization = pending
    void pending.catch(() => {
      if (sessionInitialization === pending) sessionInitialization = null
    })
  }
  await sessionInitialization
}

async function sessionFetch(path: string, options: RequestInit = {}): Promise<Response> {
  await ensureSession()
  return fetch(`${API_BASE}${path}`, { ...options, credentials: "include", cache: "no-store" })
}

async function handleResponse<T>(res: Response): Promise<T> {
  if (!res.ok) {
    if (res.status === 410) sessionInitialization = null
    // FastAPI 的错误格式是 { detail: string }
    const err = await res.json().catch(() => ({ detail: `HTTP ${res.status}` }))
    throw new APIError(
      res.status,
      typeof err?.detail === "string" ? err.detail : `HTTP ${res.status}`,
    )
  }
  return res.json() as Promise<T>
}

// ─────────────────────────────────────────────────────────────
// 上传接口
// ─────────────────────────────────────────────────────────────

export async function uploadJD(file: File): Promise<UploadResponse> {
  const form = new FormData()
  form.append("file", file)
  const res = await sessionFetch("/api/upload/jd", {
    method: "POST",
    body: form,
  })
  return handleResponse<UploadResponse>(res)
}

export async function uploadResume(file: File): Promise<UploadResponse> {
  const form = new FormData()
  form.append("file", file)
  const res = await sessionFetch("/api/upload/resume", {
    method: "POST",
    body: form,
  })
  return handleResponse<UploadResponse>(res)
}

export async function getUploadStatus(): Promise<UploadStatus> {
  const res = await sessionFetch("/api/upload/status")
  return handleResponse<UploadStatus>(res)
}

export async function clearSession(): Promise<void> {
  const res = await sessionFetch("/api/upload/clear", { method: "DELETE" })
  await handleResponse(res)
}

// ─────────────────────────────────────────────────────────────
// SSE 分析接口
// ─────────────────────────────────────────────────────────────

/**
 * 启动 SSE 流式分析
 * @returns 关闭函数，组件 unmount 时调用
 *
 * 用法：
 *   const close = startAnalysis(onEvent, onError)
 *   useEffect(() => close, [])
 */
export function startAnalysis(
  onEvent: (event: SSEEvent) => void,
  onError: (message: string) => void,
  forceNew = false,
): () => void {
  let closed = false
  let es: EventSource | null = null
  void (async () => {
    try {
      if (!forceNew) {
        try {
          const report = await getAnalysisResult()
          if (!closed) onEvent({ step: "complete", message: "已恢复本会话的分析报告", data: { ...report } })
          return
        } catch (err) {
          if (!(err instanceof APIError) || err.status !== 404) throw err
        }
      }
      const status = await getUploadStatus()
      if (!status.ready_to_analyze) throw new Error("请返回首页重新上传 JD 和简历")
      if (closed) return
      es = new EventSource(`${API_BASE}/api/analyze/stream`, { withCredentials: true })
      es.onmessage = (raw) => {
        if (closed) return
        try {
          const event = JSON.parse(raw.data) as SSEEvent
          if (event.step === "error" && event.data?.status === 410) sessionInitialization = null
          onEvent(event)
          if (event.step === "complete" || event.step === "error") {
            closed = true
            es?.close()
          }
        } catch {
          onError("解析服务器响应失败")
          closed = true
          es?.close()
        }
      }
      es.onerror = () => {
        if (closed || es?.readyState === EventSource.CLOSED) return
        onError("与分析服务的连接中断，请重试；资料过期时请返回首页重新上传")
        closed = true
        es?.close()
      }
    } catch (err) {
      if (!closed) onError(err instanceof Error ? err.message : "分析服务暂不可用，请稍后重试")
    }
  })()
  return () => { closed = true; es?.close() }
}

// 获取已缓存的分析结果（用于页面刷新恢复）
export async function getAnalysisResult(): Promise<GapAnalysis> {
  const res = await sessionFetch("/api/analyze/result")
  const body = await handleResponse<{ success: boolean; data: GapAnalysis }>(res)
  return body.data
}

// ─────────────────────────────────────────────────────────────
// 题目生成接口
// ─────────────────────────────────────────────────────────────

export async function generateQuestions(
  numQuestions = 10,
): Promise<QuestionsResponse> {
  const res = await sessionFetch("/api/questions/generate", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ num_questions: numQuestions }),
  })
  return handleResponse<QuestionsResponse>(res)
}

export async function getCachedQuestions(): Promise<QuestionsResponse> {
  const res = await sessionFetch("/api/questions/cached")
  return handleResponse<QuestionsResponse>(res)
}

// ─────────────────────────────────────────────────────────────
// 求职画像接口
// ─────────────────────────────────────────────────────────────

export async function generateProfile(): Promise<ProfileResponse> {
  const res = await sessionFetch("/api/profile/generate", {
    method: "POST",
  })
  return handleResponse<ProfileResponse>(res)
}

// ─────────────────────────────────────────────────────────────
// 健康检查
// ─────────────────────────────────────────────────────────────

export async function checkHealth(): Promise<boolean> {
  try {
    const res = await fetch(`${API_BASE}/api/health`)
    return res.ok
  } catch {
    return false
  }
}
