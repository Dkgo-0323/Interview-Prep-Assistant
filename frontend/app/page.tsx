"use client"

import { useState, useCallback } from "react"
import { useRouter } from "next/navigation"
import { Briefcase, FileUser, Sparkles, ArrowRight, AlertCircle } from "lucide-react"
import { FileUploadZone } from "@/components/file-upload-zone"
import { ActionButton } from "@/components/action-button"
import { uploadJD, uploadResume } from "@/lib/api"

// 文件上传状态接口
interface FileUploadState {
  file: File | null
  uploading: boolean
  uploaded: boolean  // 上传成功标记
  charCount: number
  error: string
}

const initState = (): FileUploadState => ({
  file: null,
  uploading: false,
  uploaded: false,
  charCount: 0,
  error: "",
})

export default function Home() {
  const router = useRouter()
  const [jd, setJd] = useState<FileUploadState>(initState())
  const [resume, setResume] = useState<FileUploadState>(initState())

  // 两个文件都上传成功才能开始
  const canStart = jd.uploaded && resume.uploaded

  // 文件变更处理 %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
  const handleFileChange = useCallback(
    (type: "jd" | "resume") =>
      async (file: File | null) => {
        const setter = type === "jd" ? setJd : setResume

        // 文件被移除时重置状态
        if (!file) {
          setter(initState())
          return
        }

        // 1. 设置上传中状态 + loading
        setter((prev) => ({
          ...prev,
          file,
          uploading: true,
          uploaded: false,
          error: "",
        }))

        try {
          // 2. 执行上传请求
          const result =
            type === "jd" ? await uploadJD(file) : await uploadResume(file)

          // 3. 上传成功，保存字符数
          setter((prev) => ({
            ...prev,
            uploading: false,
            uploaded: true,
            charCount: result.char_count,
          }))
        } catch (err) {
          // 4. 失败，保留文件供重试
          setter((prev) => ({
            ...prev,
            uploading: false,
            uploaded: false,
            error: err instanceof Error ? err.message : "上传失败，请重试",
          }))
        }
      },
    [],
  )

  function handleStart() {
    router.push("/analyze")
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-secondary via-background to-accent/10 font-sans">
      <main className="mx-auto flex w-full max-w-5xl flex-col items-center gap-10 px-6 py-16">
        {/* 标题区 */}
        <header className="flex flex-col items-center gap-4 text-center">
          <div className="flex items-center gap-2 rounded-full border border-border bg-card px-4 py-1.5 text-sm font-medium text-primary shadow-sm">
            <Sparkles className="h-4 w-4" />
            Interview Prep Assistant
          </div>
          <h1 className="text-balance text-4xl font-bold tracking-tight text-foreground sm:text-5xl">
            职位匹配智能助手
          </h1>
          <p className="max-w-xl text-pretty text-lg leading-relaxed text-muted-foreground">
            上传职位描述和简历，我们将分析匹配度、生成面试题，助你高效准备面试。
          </p>
        </header>

        {/* 上传区 */}
        <div className="grid w-full gap-6 md:grid-cols-2">
          <div className="flex flex-col gap-2">
            <FileUploadZone
              title="职位描述"
              description="Job Description"
              icon={<Briefcase className="h-5 w-5" />}
              file={jd.file}
              onFileChange={handleFileChange("jd")}
              // 上传中禁止更换
              disabled={jd.uploading}
            />
            {/* 反馈区 */}
            <UploadFeedback state={jd} />
          </div>

          <div className="flex flex-col gap-2">
            <FileUploadZone
              title="个人简历"
              description="Resume"
              icon={<FileUser className="h-5 w-5" />}
              file={resume.file}
              onFileChange={handleFileChange("resume")}
              disabled={resume.uploading}
            />
            <UploadFeedback state={resume} />
          </div>
        </div>

        {/* 开始按钮 */}
        <div className="flex flex-col items-center gap-3">
          <ActionButton
            disabled={!canStart}
            onClick={handleStart}
            icon={<ArrowRight className="h-5 w-5" />}
          >
            开始分析
          </ActionButton>
          {!canStart && (
            <p className="text-sm text-muted-foreground">
              {jd.uploading || resume.uploading
                ? "正在上传文件..."
                : "请上传两个文件后开始分析"}
            </p>
          )}
        </div>
      </main>
    </div>
  )
}

// 上传反馈组件 %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
function UploadFeedback({ state }: { state: FileUploadState }) {
  if (state.uploading) {
    return (
      <p className="flex items-center gap-1.5 text-xs text-muted-foreground">
        <span className="inline-block h-3 w-3 animate-spin rounded-full border-2 border-primary border-t-transparent" />
        正在上传...
      </p>
    )
  }
  if (state.error) {
    return (
      <p className="flex items-center gap-1.5 text-xs text-destructive">
        <AlertCircle className="h-3 w-3" />
        {state.error}
      </p>
    )
  }
  if (state.uploaded) {
    return (
      <p className="text-xs text-green-600">
        ✓ 上传成功，共 {state.charCount.toLocaleString()} 字
      </p>
    )
  }
  return null
}
