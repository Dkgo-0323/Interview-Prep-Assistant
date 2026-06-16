// frontend/lib/questions.ts
// ── 原有类型（保持不变，Flashcard 和 FilterBar 依赖这些）────────
export type Category = "technical" | "behavioral" | "situational"
export type Difficulty = "basic" | "intermediate" | "advanced"

export interface Question {
  id: number
  category: Category
  difficulty: Difficulty
  question: string
  answer: string
  // 扩展字段：保存后端原始数据，用于展示 focus_area / intent
  focusArea?: string
  intent?: string
}

export const categoryLabels: Record<Category, string> = {
  technical:   "技术",
  behavioral:  "行为",
  situational: "情境",
}

export const difficultyLabels: Record<Difficulty, string> = {
  basic:        "基础",
  intermediate: "中级",
  advanced:     "高级",
}

export const categoryStyles: Record<Category, string> = {
  technical:   "bg-blue-100 text-blue-700 border-blue-200",
  behavioral:  "bg-emerald-100 text-emerald-700 border-emerald-200",
  situational: "bg-violet-100 text-violet-700 border-violet-200",
}

export const difficultyStyles: Record<Difficulty, string> = {
  basic:        "bg-slate-100 text-slate-600 border-slate-200",
  intermediate: "bg-orange-100 text-orange-700 border-orange-200",
  advanced:     "bg-red-100 text-red-700 border-red-200",
}

// ── 后端字段 → 前端类型的映射表 ──────────────────────────────────
// 后端 question_type: "技术深度" | "项目经验" | "情景模拟" | "行为面试"
const BACKEND_TYPE_MAP: Record<string, Category> = {
  "技术深度": "technical",
  "项目经验": "technical",   // 项目经验归入技术类
  "情景模拟": "situational",
  "行为面试": "behavioral",
}

// 后端 difficulty: "基础" | "进阶" | "高级"
const BACKEND_DIFF_MAP: Record<string, Difficulty> = {
  "基础": "basic",
  "进阶": "intermediate",
  "高级": "advanced",
}

// 后端单题数据结构（与 api/schemas.py + models/schemas.py 对齐）
export interface BackendQuestion {
  question_text: string
  question_type: string
  difficulty: string
  focus_area: string
  intent: string
  reference_answer: string
}

/**
 * 把后端返回的题目列表转换为前端 Question[] 格式
 * 供 questions/page.tsx 调用
 */
export function mapBackendQuestions(backendList: BackendQuestion[]): Question[] {
  return backendList.map((q, index) => ({
    id:         index + 1,
    category:   BACKEND_TYPE_MAP[q.question_type]  ?? "technical",
    difficulty: BACKEND_DIFF_MAP[q.difficulty]     ?? "basic",
    question:   q.question_text,
    answer:     q.reference_answer,
    focusArea:  q.focus_area,
    intent:     q.intent,
  }))
}

// ── 原有 mock 数据（保留，作为后端失败时的兜底）─────────────────
export const questions: Question[] = [
  {
    id: 1,
    category: "technical",
    difficulty: "intermediate",
    question: "请解释 React 中的虚拟 DOM 是什么，它如何提升性能？",
    answer: "虚拟 DOM 是真实 DOM 的轻量级 JavaScript 表示。当状态变化时，React 先在虚拟 DOM 上进行计算，通过 Diff 算法找出最小变更集，再批量更新真实 DOM，从而减少昂贵的 DOM 操作，提升渲染性能。",
  },
  {
    id: 2,
    category: "behavioral",
    difficulty: "basic",
    question: "请讲述一次你与团队成员发生分歧的经历，你是如何处理的？",
    answer: "建议使用 STAR 法则（情境、任务、行动、结果）作答。重点说明你如何主动倾听对方观点、用数据或事实沟通、寻找共同目标并达成共识，最终对项目产生了积极影响。",
  },
  {
    id: 3,
    category: "situational",
    difficulty: "advanced",
    question: "如果项目临近上线却发现重大缺陷，你会如何决策？",
    answer: "首先评估缺陷的严重程度与影响范围，权衡修复成本与延期风险。及时向相关方透明沟通，提出可行方案（如热修复、回滚、灰度发布或延期），并基于数据和业务优先级做出决策，同时记录复盘以避免再次发生。",
  },
]