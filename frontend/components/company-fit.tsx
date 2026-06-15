import { Building2, Building, Rocket } from "lucide-react"
import type { CompanyFit as CompanyFitType } from "@/lib/profile"

const ICONS = [Building2, Building, Rocket]

export function CompanyFit({ items }: { items: CompanyFitType[] }) {
  return (
    <div className="grid gap-4 sm:grid-cols-3">
      {items.map((item, i) => {
        const Icon = ICONS[i % ICONS.length]
        return (
          <div
            key={item.label}
            className="flex flex-col gap-3 rounded-2xl border border-border bg-card p-5 shadow-sm"
          >
            <div className="flex items-center gap-2">
              <span className="flex h-9 w-9 items-center justify-center rounded-lg bg-primary/10 text-primary">
                <Icon className="h-5 w-5" />
              </span>
              <span className="text-sm font-semibold text-foreground text-balance">{item.label}</span>
            </div>
            <div className="flex items-baseline gap-1">
              <span className="text-3xl font-bold text-foreground">{item.score}</span>
              <span className="text-sm text-muted-foreground">/ 100</span>
            </div>
            <div className="h-2.5 w-full overflow-hidden rounded-full bg-secondary">
              <div
                className="h-full rounded-full bg-primary transition-[width] duration-700 ease-out"
                style={{ width: `${item.score}%` }}
              />
            </div>
            <p className="text-xs leading-relaxed text-muted-foreground text-pretty">{item.description}</p>
          </div>
        )
      })}
    </div>
  )
}
