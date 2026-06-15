export type Category = "technical" | "behavioral" | "situational"
export type Difficulty = "basic" | "intermediate" | "advanced"

export interface Question {
  id: number
  category: Category
  difficulty: Difficulty
  question: string
  answer: string
}

export const categoryLabels: Record<Category, string> = {
  technical: "技术",
  behavioral: "行为",
  situational: "情境",
}

export const difficultyLabels: Record<Difficulty, string> = {
  basic: "基础",
  intermediate: "中级",
  advanced: "高级",
}

export const categoryStyles: Record<Category, string> = {
  technical: "bg-blue-100 text-blue-700 border-blue-200",
  behavioral: "bg-emerald-100 text-emerald-700 border-emerald-200",
  situational: "bg-violet-100 text-violet-700 border-violet-200",
}

export const difficultyStyles: Record<Difficulty, string> = {
  basic: "bg-slate-100 text-slate-600 border-slate-200",
  intermediate: "bg-orange-100 text-orange-700 border-orange-200",
  advanced: "bg-red-100 text-red-700 border-red-200",
}

export const questions: Question[] = [
  {
    id: 1,
    category: "technical",
    difficulty: "intermediate",
    question: "请解释 React 中的虚拟 DOM 是什么，它如何提升性能？",
    answer:
      "虚拟 DOM 是真实 DOM 的轻量级 JavaScript 表示。当状态变化时，React 先在虚拟 DOM 上进行计算，通过 Diff 算法找出最小变更集，再批量更新真实 DOM，从而减少昂贵的 DOM 操作，提升渲染性能。",
  },
  {
    id: 2,
    category: "behavioral",
    difficulty: "basic",
    question: "请讲述一次你与团队成员发生分歧的经历，你是如何处理的？",
    answer:
      "建议使用 STAR 法则（情境、任务、行动、结果）作答。重点说明你如何主动倾听对方观点、用数据或事实沟通、寻找共同目标并达成共识，最终对项目产生了积极影响。",
  },
  {
    id: 3,
    category: "situational",
    difficulty: "advanced",
    question: "如果项目临近上线却发现重大缺陷，你会如何决策？",
    answer:
      "首先评估缺陷的严重程度与影响范围，权衡修复成本与延期风险。及时向相关方透明沟通，提出可行方案（如热修复、回滚、灰度发布或延期），并基于数据和业务优先级做出决策，同时记录复盘以避免再次发生。",
  },
  {
    id: 4,
    category: "technical",
    difficulty: "basic",
    question: "什么是闭包（Closure）？请举一个使用场景。",
    answer:
      "闭包是指函数能够访问其词法作用域之外的变量，即使外部函数已执行完毕。常见场景包括：数据私有化、函数柯里化、以及在循环中保留每次迭代的状态（如事件处理器）。",
  },
  {
    id: 5,
    category: "technical",
    difficulty: "advanced",
    question: "如何设计一个支持高并发的短链接生成系统？",
    answer:
      "核心包括：使用发号器（如雪花算法或号段模式）生成唯一 ID 并转 62 进制作为短码；引入缓存（Redis）加速读取；数据库做分库分表；通过 CDN 与负载均衡应对流量；并考虑防刷、过期清理与统计分析。",
  },
  {
    id: 6,
    category: "behavioral",
    difficulty: "intermediate",
    question: "描述一个你主导并推动完成的项目，你扮演了什么角色？",
    answer:
      "说明项目背景与目标，你承担的具体职责（如规划、协调、技术决策），遇到的挑战与解决方式，以及量化的成果。强调领导力、责任心和跨团队协作能力。",
  },
  {
    id: 7,
    category: "situational",
    difficulty: "intermediate",
    question: "当你的任务优先级频繁变动时，你如何保证交付质量？",
    answer:
      "建立清晰的优先级评估机制，与利益相关方确认目标；将任务拆解并采用敏捷迭代；保留缓冲时间应对变化；通过自动化测试与持续集成保障质量；并定期同步进度，管理预期。",
  },
  {
    id: 8,
    category: "technical",
    difficulty: "intermediate",
    question: "请说明 HTTP 与 HTTPS 的区别，以及 HTTPS 的加密过程。",
    answer:
      "HTTPS 在 HTTP 基础上加入 TLS/SSL 加密。握手时服务器提供证书，客户端验证后协商对称密钥（结合非对称加密交换密钥），随后使用对称加密传输数据，保证机密性、完整性和身份认证。",
  },
  {
    id: 9,
    category: "behavioral",
    difficulty: "basic",
    question: "你如何看待失败？请分享一次失败的经历及收获。",
    answer:
      "展现成长型思维：客观描述失败的原因，承担相应责任，说明你从中学到了什么，以及后续如何改进并应用到工作中。重点在于反思能力与韧性。",
  },
  {
    id: 10,
    category: "situational",
    difficulty: "advanced",
    question: "如果你接手一个文档缺失、原作者已离职的遗留系统，你会怎么做？",
    answer:
      "先通过阅读代码、运行系统、查看日志和数据库理清核心流程；补充关键文档与测试；小步重构降低风险；与使用方沟通确认业务规则；并建立监控，逐步提升系统可维护性。",
  },
  {
    id: 11,
    category: "technical",
    difficulty: "basic",
    question: "什么是 RESTful API？它有哪些设计原则？",
    answer:
      "REST 是一种基于资源的架构风格。原则包括：使用名词表示资源、用 HTTP 方法表达操作（GET/POST/PUT/DELETE）、无状态、统一接口、合理使用状态码，以及通过 URL 层级表达资源关系。",
  },
  {
    id: 12,
    category: "behavioral",
    difficulty: "intermediate",
    question: "你如何在压力下保持高效工作？",
    answer:
      "说明你的压力管理方法：合理拆解任务、聚焦最高优先级、保持沟通寻求支持、适当休息调整状态，并用具体案例证明你能在高压下依然交付高质量结果。",
  },
]
