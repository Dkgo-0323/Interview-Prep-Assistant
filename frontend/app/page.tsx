"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { Briefcase, FileUser, Sparkles, ArrowRight } from "lucide-react"
import { FileUploadZone } from "@/components/file-upload-zone"
import { ActionButton } from "@/components/action-button"

export default function Home() {
  const router = useRouter()
  const [jobDescription, setJobDescription] = useState<File | null>(null)
  const [resume, setResume] = useState<File | null>(null)

  const canStart = Boolean(jobDescription && resume)

  function handleStart() {
    router.push("/analyze")
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-secondary via-background to-accent/10 font-sans">
      <main className="mx-auto flex w-full max-w-5xl flex-col items-center gap-10 px-6 py-16">
        <header className="flex flex-col items-center gap-4 text-center">
          <div className="flex items-center gap-2 rounded-full border border-border bg-card px-4 py-1.5 text-sm font-medium text-primary shadow-sm">
            <Sparkles className="h-4 w-4" />
            Interview Prep Assistant
          </div>
          <h1 className="text-balance text-4xl font-bold tracking-tight text-foreground sm:text-5xl">
            上传文件，开始面试准备
          </h1>
          <p className="max-w-xl text-pretty text-lg leading-relaxed text-muted-foreground">
            上传职位描述和你的简历，我们将分析匹配度并为你生成针对性的面试问题。
          </p>
        </header>

        <div className="grid w-full gap-6 md:grid-cols-2">
          <FileUploadZone
            title="上传职位描述"
            description="Job Description"
            icon={<Briefcase className="h-5 w-5" />}
            file={jobDescription}
            onFileChange={setJobDescription}
          />
          <FileUploadZone
            title="上传简历"
            description="Resume"
            icon={<FileUser className="h-5 w-5" />}
            file={resume}
            onFileChange={setResume}
          />
        </div>

        <div className="flex flex-col items-center gap-3">
          <ActionButton disabled={!canStart} onClick={handleStart} icon={<ArrowRight className="h-5 w-5" />}>
            开始分析
          </ActionButton>
          {!canStart && (
            <p className="text-sm text-muted-foreground">请先上传两份文件后再开始分析</p>
          )}
        </div>
      </main>
    </div>
  )
}