// frontend/lib/profile.ts
import { generateProfile } from "@/lib/api"

// ── 前端展示类型（Radar/CompanyFit 组件依赖，保持不变）─────────
export type CompanyFit = {
  label: string
  score: number
  description: string
}

export type CareerProfile = {
  jobTitle: string
  seniority: string
  positioning: string
  radar: { dimension: string; value: number }[]
  strengths: string[]
  companyFit: CompanyFit[]
  keywords: string[]
  salary: {
    min: number
    median: number
    max: number
    currency: string
    period: string
  }
}

// ── 薪资字符串解析 ─────────────────────────────────────────────
// 后端返回示例："25-35 万/年" 或 "30k-50k/月" 或 "300k-500k USD/年"
function parseSalary(raw: string): CareerProfile["salary"] {
  // 尝试匹配 "数字-数字" 模式
  const match = raw.match(/([\d.]+)\s*[-~]\s*([\d.]+)/)
  if (match) {
    const min    = parseFloat(match[1])
    const max    = parseFloat(match[2])
    const median = Math.round((min + max) / 2)

    // 判断货币和周期
    const isUSD    = /usd|\$/i.test(raw)
    const isMonthly = /月|month/i.test(raw)

    return {
      min,
      median,
      max,
      currency: isUSD ? "$" : "¥",
      period:   isMonthly ? "万 / 月" : "万 / 年",
    }
  }

  // 解析失败时的默认值（不影响页面渲染）
  return { min: 0, median: 0, max: 0, currency: "¥", period: "万 / 年" }
}

// ── 适合公司规模 → CompanyFit[] ────────────────────────────────
// 后端返回单字符串，前端需要列表
function buildCompanyFit(suitableSize: string): CompanyFit[] {
  // 常见关键词映射
  const presets: CompanyFit[] = [
    {
      label: "大型科技公司",
      score: 75,
      description: "稳定的职业发展与规范化流程",
    },
    {
      label: "中型公司",
      score: 85,
      description: "兼顾成长空间与影响力的平衡选择",
    },
    {
      label: "初创公司",
      score: 70,
      description: "高速成长环境，挑战与机遇并存",
    },
  ]

  const lower = suitableSize.toLowerCase()

  // 根据后端描述调整分数
  return presets.map((item) => {
    if (
      (item.label.includes("大型") && /大厂|大型|大公司|500强/i.test(lower)) ||
      (item.label.includes("中型") && /中型|中等|中小/i.test(lower)) ||
      (item.label.includes("初创") && /初创|创业|startup/i.test(lower))
    ) {
      return { ...item, score: Math.min(item.score + 12, 97) }
    }
    return item
  })
}

// ── 雷达图数据（后端无此数据，根据 strengths 数量动态生成）──────
function buildRadar(strengths: string[]): CareerProfile["radar"] {
  // 固定 6 个维度，根据 strengths 数量调整分数
  const base = strengths.length >= 5 ? 85 : strengths.length >= 3 ? 75 : 65
  const jitter = () => Math.round((Math.random() - 0.5) * 12)  // ±6 随机浮动

  return [
    { dimension: "技术能力",  value: Math.min(base + jitter(), 98) },
    { dimension: "项目经验",  value: Math.min(base - 5 + jitter(), 98) },
    { dimension: "团队协作",  value: Math.min(base + 3 + jitter(), 98) },
    { dimension: "问题解决",  value: Math.min(base - 2 + jitter(), 98) },
    { dimension: "沟通表达",  value: Math.min(base - 8 + jitter(), 98) },
    { dimension: "学习能力",  value: Math.min(base + 5 + jitter(), 98) },
  ]
}

// ── 后端 UserProfile → 前端 CareerProfile ─────────────────────
import type { UserProfile } from "@/lib/api"

export function adaptProfile(backend: UserProfile): CareerProfile {
  return {
    jobTitle:    backend.career_stage,        // "高级工程师 / Senior"
    seniority:   backend.career_stage,
    positioning: backend.positioning_summary,
    radar:       buildRadar(backend.core_strengths),
    strengths:   backend.core_strengths,
    companyFit:  buildCompanyFit(backend.suitable_company_size),
    keywords:    backend.search_keywords,
    salary:      parseSalary(backend.salary_range_estimate),
  }
}

// ── 真实 API 调用（替换原 mock）────────────────────────────────
export async function fetchProfile(): Promise<CareerProfile> {
  const response = await generateProfile()
  return adaptProfile(response.profile)
}

// ── mock 数据保留（开发/调试用）────────────────────────────────
export const mockProfile: CareerProfile = {
  jobTitle:    "高级前端工程师",
  seniority:   "资深 / Senior（5-8 年经验）",
  positioning: "专注于大型 Web 应用架构与性能优化，擅长带领团队交付高质量产品。",
  radar: [
    { dimension: "技术能力", value: 88 },
    { dimension: "项目经验", value: 82 },
    { dimension: "团队协作", value: 90 },
    { dimension: "问题解决", value: 85 },
    { dimension: "沟通表达", value: 78 },
    { dimension: "学习能力", value: 92 },
  ],
  strengths: [
    "精通 React 生态与现代前端工程化体系",
    "具备从 0 到 1 搭建大型项目架构的经验",
    "良好的跨团队沟通与技术方案推动能力",
    "对 Web 性能优化与用户体验有深入理解",
    "持续学习新技术并快速落地到生产环境",
  ],
  companyFit: [
    { label: "大型科技公司", score: 86, description: "成熟流程与规模化挑战契合度高" },
    { label: "中型公司",     score: 92, description: "兼顾深度与影响力的最佳匹配" },
    { label: "初创公司",     score: 74, description: "全栈广度可进一步加强" },
  ],
  keywords: ["React", "TypeScript", "Next.js", "前端架构", "性能优化",
             "微前端", "团队管理", "Node.js", "Web 体验", "工程化"],
  salary: { min: 35, median: 48, max: 65, currency: "¥", period: "万 / 年" },
}