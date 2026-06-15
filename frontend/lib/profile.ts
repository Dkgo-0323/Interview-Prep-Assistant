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

// 模拟 API 返回的求职画像数据
export const mockProfile: CareerProfile = {
  jobTitle: "高级前端工程师",
  seniority: "资深 / Senior（5-8 年经验）",
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
    { label: "中型公司", score: 92, description: "兼顾深度与影响力的最佳匹配" },
    { label: "初创公司", score: 74, description: "全栈广度可进一步加强" },
  ],
  keywords: [
    "React",
    "TypeScript",
    "Next.js",
    "前端架构",
    "性能优化",
    "微前端",
    "团队管理",
    "Node.js",
    "Web 体验",
    "工程化",
  ],
  salary: {
    min: 35,
    median: 48,
    max: 65,
    currency: "¥",
    period: "万 / 年",
  },
}

// 模拟异步获取（含可控延迟）
export function fetchProfile(): Promise<CareerProfile> {
  return new Promise((resolve) => {
    setTimeout(() => resolve(mockProfile), 1400)
  })
}
