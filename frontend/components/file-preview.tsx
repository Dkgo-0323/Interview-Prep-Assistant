"use client"

import { FileText, Eye, Trash2 } from "lucide-react"

interface FilePreviewProps {
  file: File
  onRemove: () => void
  onPreview: () => void
}

function formatSize(bytes: number) {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}

export function FilePreview({ file, onRemove, onPreview }: FilePreviewProps) {
  return (
    <div className="flex items-center gap-4 rounded-xl border border-border bg-secondary/50 p-4">
      <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-lg bg-gradient-to-br from-primary to-accent text-primary-foreground">
        <FileText className="h-6 w-6" />
      </div>
      <div className="min-w-0 flex-1">
        <p className="truncate text-sm font-medium text-foreground">{file.name}</p>
        <p className="text-xs text-muted-foreground">{formatSize(file.size)}</p>
      </div>
      <div className="flex shrink-0 items-center gap-1">
        <button
          type="button"
          onClick={onPreview}
          aria-label="预览文件"
          className="flex h-9 w-9 items-center justify-center rounded-lg text-muted-foreground transition-colors hover:bg-background hover:text-primary"
        >
          <Eye className="h-4 w-4" />
        </button>
        <button
          type="button"
          onClick={onRemove}
          aria-label="删除文件"
          className="flex h-9 w-9 items-center justify-center rounded-lg text-muted-foreground transition-colors hover:bg-background hover:text-destructive"
        >
          <Trash2 className="h-4 w-4" />
        </button>
      </div>
    </div>
  )
}
