"use client"

import type { ReactNode } from "react"
import { cn } from "@/lib/utils"

interface ActionButtonProps {
  children: ReactNode
  onClick?: () => void
  disabled?: boolean
  icon?: ReactNode
}

export function ActionButton({ children, onClick, disabled, icon }: ActionButtonProps) {
  return (
    <button
      type="button"
      onClick={onClick}
      disabled={disabled}
      className={cn(
        "inline-flex items-center justify-center gap-2 rounded-xl px-8 py-3.5 text-base font-semibold text-primary-foreground transition-all duration-200",
        "bg-gradient-to-r from-primary to-accent shadow-lg shadow-primary/25",
        "hover:shadow-xl hover:shadow-primary/30 hover:-translate-y-0.5",
        "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2",
        "disabled:cursor-not-allowed disabled:opacity-40 disabled:shadow-none disabled:translate-y-0",
      )}
    >
      {icon}
      {children}
    </button>
  )
}
