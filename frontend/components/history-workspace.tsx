"use client"

import { useCallback, useEffect, useRef, useState } from "react"
import { useSearchParams } from "next/navigation"
import { APIError } from "@/lib/api"
import * as api from "@/lib/history-api"
import { ScoreCircle } from "@/components/score-circle"

const button = "rounded-lg border border-border px-4 py-2 text-sm hover:bg-secondary disabled:opacity-50 disabled:cursor-not-allowed"
const input = "w-full min-w-0 rounded-lg border border-border bg-background px-3 py-2"
const message = (error: unknown) => error instanceof Error ? error.message : "请求失败，请刷新后重试"
const statuses = { running: "进行中", completed: "已完成", failed: "失败，可明确重试", interrupted: "已中断，可明确重试" }

export function HistoryWorkspace() {
  const selectRecord = (id?: string) => window.history.replaceState(null, "", id ? `/history?record=${encodeURIComponent(id)}` : "/history")
  const selected = useSearchParams().get("record")
  const [account, setAccount] = useState<string | null>(null)
  const [records, setRecords] = useState<api.RecordSummary[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState("")
  const [busy, setBusy] = useState(false)
  const [title, setTitle] = useState("")
  const epoch = useRef(0)
  const expire = useCallback((err: unknown) => {
    setError(message(err))
    if (err instanceof APIError && err.status === 401) {
      epoch.current++
      setAccount(null)
      setRecords([])
      setLoading(false)
    }
  }, [])
  const refresh = useCallback(async () => {
    const version = ++epoch.current
    try {
      const identity = await api.getAccount()
      const rows = await api.listRecords()
      if (version !== epoch.current) return
      setAccount(identity.account_id)
      setRecords(rows)
    } catch (err) { if (version === epoch.current) expire(err) }
    finally { if (version === epoch.current) setLoading(false) }
  }, [expire])
  useEffect(() => {
    const generation = epoch
    const version = ++generation.current
    void api.getAccount().then(async identity => ({ identity, rows: await api.listRecords() })).then(({ identity, rows }) => {
      if (version !== generation.current) return
      setAccount(identity.account_id); setRecords(rows)
    }).catch(err => { if (version === generation.current) expire(err) })
      .finally(() => { if (version === generation.current) setLoading(false) })
    return () => { generation.current++ }
  }, [expire])
  async function create(event: React.FormEvent) {
    event.preventDefault()
    if (busy) return
    setBusy(true); setError("")
    try {
      const row = await api.createRecord(title.trim())
      setRecords(rows => [row, ...rows]); setTitle("")
      selectRecord(row.id)
    } catch (err) { expire(err) }
    finally { setBusy(false) }
  }
  async function logout() {
    setBusy(true); setError("")
    // Invalidate pending reads before revoking the cookie.
    epoch.current++
    try {
      await api.logoutAccount()
      setAccount(null); setRecords([]); selectRecord()
    } catch (err) { expire(err) }
    finally { setBusy(false); setLoading(false) }
  }
  return <main className="mx-auto flex max-w-6xl flex-col gap-6 px-4 py-10 sm:px-6">
    <div className="flex flex-wrap items-center justify-between gap-4">
      <div><h1 className="text-3xl font-bold">我的准备记录</h1><p className="mt-2 text-muted-foreground">用 GitHub 登录，在不同设备继续同一份准备。</p></div>
      {account && <button className={button} disabled={busy} onClick={logout}>退出本设备</button>}
    </div>
    <p className="text-sm text-muted-foreground">每账号最多20份；仅保存解析文本、报告和题库，不长期保留原始文件。匿名上传不会自动转入账号。</p>
    {error && <p role="alert" className="rounded-lg border border-amber-300 p-4 text-amber-800">{error}</p>}
    {loading ? <p role="status">正在读取账号与历史…</p> : !account ? <div className="flex flex-wrap items-center gap-4 rounded-xl border p-6">
      <a className={button} href={api.githubLoginURL}>使用 GitHub 登录</a>
      <button className={button} onClick={() => { setLoading(true); setError(""); void refresh() }}>重新检查登录状态</button>
      <p className="text-sm text-muted-foreground">服务未配置时账号功能不可用；可继续使用首页匿名演示。</p>
    </div> : <div className="grid items-start gap-6 md:grid-cols-[260px_minmax(0,1fr)]">
      <aside className="min-w-0 space-y-4 rounded-xl border p-4">
        <h2 className="font-semibold">历史列表（{records.length}/20）</h2>
        <button className={button} disabled={busy} onClick={() => { setLoading(true); setError(""); void refresh() }}>刷新历史</button>
        <form className="space-y-2" onSubmit={create}>
          <label htmlFor="new-title" className="text-sm">新记录名称</label>
          <input id="new-title" className={input} maxLength={100} required value={title} onChange={e => setTitle(e.target.value)} />
          <button className={button} disabled={busy || records.length >= 20 || !title.trim()}>创建记录</button>
        </form>
        {records.length >= 20 && <p className="text-sm">已达20份，请先删除不需要的记录，不会自动淘汰。</p>}
        {!records.length && <p className="text-sm text-muted-foreground">还没有记录，请先命名创建。</p>}
        <ul className="space-y-2">{records.map(row => <li key={row.id}><button className={`${button} w-full break-all text-left ${selected === row.id ? "bg-primary/10" : ""}`} aria-pressed={selected === row.id} disabled={busy} onClick={() => selectRecord(row.id)}>{row.title}</button></li>)}</ul>
      </aside>
      {selected ? <RecordWorkspace key={`${account}:${selected}`} id={selected} onError={expire} onChanged={row => setRecords(rows => rows.map(old => old.id === row.id ? row : old))} onDeleted={() => {
        setRecords(rows => rows.filter(row => row.id !== selected)); selectRecord()
      }} /> : <p className="rounded-xl border p-6">选择一份记录，继续上传、分析与面试题练习。</p>}
    </div>}
  </main>
}

function RecordWorkspace({ id, onError, onChanged, onDeleted }: {
  id: string; onError: (error: unknown) => void; onChanged: (row: api.RecordDetail) => void; onDeleted: () => void
}) {
  const [row, setRow] = useState<api.RecordDetail | null>(null)
  const [tasks, setTasks] = useState<api.RecordTask[]>([])
  const [title, setTitle] = useState("")
  const [error, setError] = useState("")
  const [busy, setBusy] = useState(false)
  const [progress, setProgress] = useState("")
  const [confirmDelete, setConfirmDelete] = useState(false)
  const [count, setCount] = useState(10)
  const alive = useRef(true)
  const controller = useRef<AbortController | null>(null)
  // Event handlers capture this record instance; unmount prevents late responses
  // from replacing a newly selected record, including A -> B -> A navigation.
  async function load(signal?: AbortSignal) {
    const [next, statuses] = await Promise.all([api.readRecord(id, signal), api.readTasks(id, signal)])
    if (!alive.current || signal?.aborted) return
    setRow(next); setTitle(next.title); setTasks(statuses)
  }
  useEffect(() => {
    alive.current = true
    const initial = new AbortController()
    void load(initial.signal).catch(err => {
      if (!initial.signal.aborted) { setError(message(err)); onError(err) }
    })
    return () => { alive.current = false; initial.abort(); controller.current?.abort() }
    // The id is fixed by the parent's key; callbacks must not restart reads.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [id])
  async function action(work: () => Promise<unknown>) {
    if (busy) return
    setBusy(true); setError(""); setProgress("")
    try { await work() }
    catch (err) {
      if (alive.current) {
        setError(message(err)); onError(err)
        // Drop potentially stale input/results on conflict, deleted record or
        // uncertain transport outcome; explicit refresh is always read-only.
        setRow(null); setTasks([])
      }
    } finally { if (alive.current) setBusy(false) }
  }
  async function apply(next: api.RecordDetail) {
    if (!alive.current) return
    setRow(next); setTitle(next.title); onChanged(next)
    setTasks(await api.readTasks(id))
  }
  async function upload(kind: "jd" | "resume", file?: File) {
    if (!file || !row) return
    await action(async () => {
      if (file.size > 10 * 1024 * 1024 || !/\.(pdf|docx|txt)$/i.test(file.name)) throw new Error("请选择10MB以内的PDF、DOCX或TXT文件")
      await apply(await api.uploadRecord(id, row.revision, kind, file))
    })
  }
  const running = tasks.some(task => task.status === "running")
  const gap = row?.results.gap
  const questions = row?.results.questions?.questions ?? []
  return <section className="min-w-0 space-y-5 rounded-xl border p-5" aria-label="当前准备记录">
    <div className="flex flex-wrap gap-3"><button className={button} disabled={busy} onClick={() => void action(() => load())}>刷新当前记录</button><span role="status" className="self-center text-sm">{busy ? "请求进行中…" : progress}</span></div>
    {error && <p role="alert" className="break-words text-amber-800">{error}。请刷新当前记录确认状态，系统不会自动重发生成请求。</p>}
    {!row ? <p>尚未读取记录，或记录已不可用。请刷新确认。</p> : <>
      <h2 className="break-all text-xl font-semibold">{row.title}</h2>
      <p className="text-sm text-muted-foreground">资料版本 {row.revision} · 刷新只读取已保存内容</p>
      <form className="flex flex-wrap items-end gap-2" onSubmit={event => { event.preventDefault(); void action(async () => apply(await api.renameRecord(id, title.trim()))) }}>
        <label className="min-w-0 flex-1 text-sm">记录名称<input className={input} value={title} maxLength={100} required onChange={e => setTitle(e.target.value)} /></label>
        <button className={button} disabled={busy || !title.trim()}>保存名称</button>
      </form>
      <div className="grid gap-4 lg:grid-cols-2">{(["jd", "resume"] as const).map(kind => <label className="min-w-0 space-y-2 rounded-lg border p-4" key={kind}>
        <span className="block font-medium">{kind === "jd" ? "职位描述 JD" : "简历"}</span>
        <span className="block text-sm">{row.inputs[`${kind}_text`] ? `已保存 ${row.inputs[`${kind}_text`]!.length} 字符` : "尚未上传"}</span>
        <input aria-label={kind === "jd" ? "上传记录JD" : "上传记录简历"} className="w-full min-w-0 text-sm" type="file" accept=".pdf,.docx,.txt" disabled={busy} onChange={e => { const file = e.target.files?.[0]; e.target.value = ""; void upload(kind, file) }} />
      </label>)}</div>
      <p className="text-sm text-muted-foreground">重新上传或清空会使已有报告、题库和旧任务失效。跨设备版本冲突时请刷新后再操作。</p>
      <ul className="text-sm">{tasks.map(task => <li key={task.kind}>{task.kind === "analysis" ? "报告任务" : "题库任务"}：{statuses[task.status]}（资料版本 {task.revision}）</li>)}</ul>
      {running && <p className="text-sm">任务仍在进行；可刷新查看状态。页面不会自动重连、生成或排队。</p>}
      <div className="flex flex-wrap gap-3">
        <button className={button} disabled={busy || running || !row.inputs.jd_text || !row.inputs.resume_text} onClick={() => void action(async () => {
          controller.current = new AbortController()
          await api.analyzeRecord(id, row.revision, event => { if (alive.current) setProgress(event.message) }, controller.current.signal)
          await load()
        })}>{gap ? "重新分析当前资料" : "开始分析当前资料"}</button>
        <button className={button} disabled={busy} onClick={() => { if (window.confirm("清空本记录的解析文本、报告和题库？")) void action(async () => apply(await api.clearRecordInputs(id, row.revision))) }}>清空本记录资料</button>
      </div>
      {gap && <div className="space-y-4 rounded-lg border p-4">
        <h3 className="text-lg font-semibold">已保存的匹配报告</h3>
        <p className="text-sm text-muted-foreground">这是本资料版本上次成功保存的报告；任务进行中、失败或中断不表示它已更新。</p>
        <ScoreCircle score={gap.overall_match_score} />
        <p>技能 {gap.skill_score} · 经验 {gap.experience_score} · 教育 {gap.education_score} · 项目 {gap.project_score}</p>
        {[["优势", gap.strengths], ["待提升", gap.weaknesses], ["建议", gap.recommendations]].map(([label, items]) => <div key={label as string}><h4 className="font-medium">{label}</h4><ul className="list-inside list-disc space-y-1 text-sm">{(items as string[]).map((item, i) => <li key={i}>{item}</li>)}</ul></div>)}
      </div>}
      <div className="flex flex-wrap items-center gap-3">
        <label className="text-sm">题目数量 <select className={button} value={count} onChange={e => setCount(Number(e.target.value))}>{[10, 20, 30, 40, 50].map(n => <option key={n}>{n}</option>)}</select></label>
        <button className={button} disabled={busy || running || !gap} onClick={() => void action(async () => { await api.generateRecordQuestions(id, row.revision, count); await load() })}>{questions.length ? "重新生成本记录题目" : "生成本记录题目"}</button>
      </div>
      {!!questions.length && <div className="space-y-3"><h3 className="font-semibold">已保存的个性化题库（{questions.length}题）</h3><p className="text-sm text-muted-foreground">本资料版本上次成功保存的题目，结合上方任务状态查看；展开可阅读参考回答。</p>{questions.map((q, i) => <details className="rounded-lg border p-4" key={`${row.revision}:${i}:${q.question_text}`}><summary className="cursor-pointer break-words">{i + 1}. {q.question_text} · {q.difficulty}</summary><p className="mt-3 whitespace-pre-wrap break-words text-sm">{q.reference_answer}</p><p className="mt-2 text-xs text-muted-foreground">{q.question_type} · 考察点：{q.focus_area} · {q.intent}</p></details>)}</div>}
      <div className="border-t pt-4">{confirmDelete ? <div className="flex flex-wrap items-center gap-3"><p>永久删除本记录及其报告、题库？</p><button className={button} disabled={busy} onClick={() => void action(async () => { await api.deleteRecord(id); if (alive.current) onDeleted() })}>确认永久删除</button><button className={button} disabled={busy} onClick={() => setConfirmDelete(false)}>取消删除</button></div> : <button className={button} disabled={busy} onClick={() => setConfirmDelete(true)}>删除此记录</button>}</div>
    </>}
  </section>
}
