"use client"

import { useRef, useState, type ReactNode } from "react"
import { UploadCloud } from "lucide-react"
import { cn } from "@/lib/utils"
import { FilePreview } from "@/components/file-preview"

const ACCEPTED = ".pdf,.docx,.txt"

interface FileUploadZoneProps {
  title: string
  description: string
  icon: ReactNode
  file: File | null
  onFileChange: (file: File | null) => void
}

export function FileUploadZone({ title, description, icon, file, onFileChange }: FileUploadZoneProps) {
  const inputRef = useRef<HTMLInputElement>(null)
  const [isDragging, setIsDragging] = useState(false)

  function handleDrop(e: React.DragEvent) {
    e.preventDefault()
    setIsDragging(false)
    const dropped = e.dataTransfer.files?.[0]
    if (dropped) onFileChange(dropped)
  }

  function handlePreview() {
    if (!file) return
    const url = URL.createObjectURL(file)
    window.open(url, "_blank", "noopener,noreferrer")
  }

  return (
    <div className="flex flex-col gap-4 rounded-2xl border border-border bg-card p-6 shadow-sm">
      <div className="flex items-center gap-3">
        <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10 text-primary">
          {icon}
        </div>
        <div>
          <h2 className="text-base font-semibold text-foreground">{title}</h2>
          <p className="text-xs text-muted-foreground">{description}</p>
        </div>
      </div>

      {file ? (
        <FilePreview file={file} onRemove={() => onFileChange(null)} onPreview={handlePreview} />
      ) : (
        <button
          type="button"
          onClick={() => inputRef.current?.click()}
          onDragOver={(e) => {
            e.preventDefault()
            setIsDragging(true)
          }}
          onDragLeave={() => setIsDragging(false)}
          onDrop={handleDrop}
          className={cn(
            "flex min-h-48 flex-col items-center justify-center gap-3 rounded-xl border-2 border-dashed p-8 text-center transition-colors",
            isDragging
              ? "border-primary bg-primary/5"
              : "border-border bg-secondary/30 hover:border-primary/50 hover:bg-secondary/60",
          )}
        >
          <div className="flex h-14 w-14 items-center justify-center rounded-full bg-primary/10 text-primary">
            <UploadCloud className="h-7 w-7" />
          </div>
          <div className="space-y-1">
            <p className="text-sm font-medium text-foreground">
              拖拽文件到此处，或 <span className="text-primary">点击上传</span>
            </p>
            <p className="text-xs text-muted-foreground">支持 PDF / DOCX / TXT 格式</p>
          </div>
        </button>
      )}

      <input
        ref={inputRef}
        type="file"
        accept={ACCEPTED}
        className="hidden"
        onChange={(e) => onFileChange(e.target.files?.[0] ?? null)}
      />
    </div>
  )
}
