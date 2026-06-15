import { Info } from "lucide-react"
import type { CareerProfile } from "@/lib/profile"

export function SalaryRange({ salary }: { salary: CareerProfile["salary"] }) {
  const { min, median, max, currency, period } = salary
  // 中位数在区间内的百分比位置
  const medianPct = ((median - min) / (max - min)) * 100

  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-end justify-between">
        <div>
          <p className="text-xs text-muted-foreground">最低</p>
          <p className="text-lg font-bold text-foreground">
            {currency}
            {min}
          </p>
        </div>
        <div className="text-center">
          <p className="text-xs text-primary">预估中位数</p>
          <p className="text-2xl font-bold text-primary">
            {currency}
            {median}
          </p>
        </div>
        <div className="text-right">
          <p className="text-xs text-muted-foreground">最高</p>
          <p className="text-lg font-bold text-foreground">
            {currency}
            {max}
          </p>
        </div>
      </div>

      <div className="relative pt-3">
        <div className="h-2.5 w-full rounded-full bg-secondary">
          <div className="h-full w-full rounded-full bg-primary/30" />
        </div>
        {/* 中位数标记 */}
        <div
          className="absolute top-0 flex -translate-x-1/2 flex-col items-center"
          style={{ left: `${medianPct}%` }}
        >
          <span className="h-5 w-5 rounded-full border-4 border-background bg-primary shadow" />
        </div>
      </div>

      <p className="text-center text-xs text-muted-foreground">
        单位：{currency}
        {period}
      </p>

      <div className="flex items-start gap-2 rounded-xl bg-secondary/60 p-3">
        <Info className="mt-0.5 h-4 w-4 shrink-0 text-muted-foreground" />
        <p className="text-xs leading-relaxed text-muted-foreground text-pretty">
          以上薪资范围为基于市场数据的估算，仅供参考，实际薪酬受地区、公司规模、个人表现等多种因素影响。
        </p>
      </div>
    </div>
  )
}
