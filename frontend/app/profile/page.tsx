import Link from "next/link"
import { ArrowLeft, ArrowRight, BookOpen, FileSearch, Sparkles } from "lucide-react"

export default function ProfilePage() {
  return (
    <main className="min-h-svh bg-gradient-to-b from-secondary/40 via-background to-background">
      <div className="mx-auto w-full max-w-5xl px-4 py-10 sm:px-6">
        <header className="mb-8 flex flex-col gap-2">
          <Link
            href="/"
            className="mb-2 inline-flex w-fit items-center gap-1.5 text-sm text-muted-foreground transition-colors hover:text-foreground"
          >
            <ArrowLeft aria-hidden="true" className="h-4 w-4" />
            返回首页
          </Link>
          <h1 className="text-2xl font-bold text-foreground sm:text-3xl">求职画像</h1>
          <p className="text-sm text-muted-foreground">此功能尚未开放，暂未提供真实的求职画像分析。</p>
        </header>

        <section
          aria-labelledby="profile-unavailable-title"
          className="rounded-2xl border border-border bg-card p-6 shadow-sm sm:p-10"
        >
          <span className="mb-5 flex h-14 w-14 items-center justify-center rounded-2xl bg-primary/10 text-primary">
            <Sparkles aria-hidden="true" className="h-7 w-7" />
          </span>
          <h2 id="profile-unavailable-title" className="text-xl font-semibold text-foreground">
            画像功能尚未开放
          </h2>
          <p className="mt-3 max-w-2xl text-sm leading-relaxed text-muted-foreground">
            当前不会生成能力评分、公司匹配度或薪资预估。你可以前往岗位匹配分析，了解简历与目标职位的差距，或进入题库准备面试。
          </p>

          <nav aria-label="继续准备面试" className="mt-7 flex flex-col gap-3 sm:flex-row">
            <Link
              href="/analyze"
              prefetch={false}
              className="inline-flex items-center justify-center gap-2 rounded-xl bg-primary px-5 py-3 text-sm font-semibold text-primary-foreground transition-opacity hover:opacity-90"
            >
              <FileSearch aria-hidden="true" className="h-4 w-4" />
              前往岗位匹配分析
              <ArrowRight aria-hidden="true" className="h-4 w-4" />
            </Link>
            <Link
              href="/questions"
              prefetch={false}
              className="inline-flex items-center justify-center gap-2 rounded-xl border border-border bg-background px-5 py-3 text-sm font-semibold text-foreground transition-colors hover:bg-secondary"
            >
              <BookOpen aria-hidden="true" className="h-4 w-4" />
              前往面试题库
            </Link>
          </nav>
          <p className="mt-4 text-xs leading-relaxed text-muted-foreground">
            首次使用请先在首页上传 JD 和简历，再完成岗位匹配分析。
          </p>
        </section>
      </div>
    </main>
  )
}
