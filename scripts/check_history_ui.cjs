// Production Next page + intercepted synthetic account API. No OAuth/model/DB.
const assert = require('node:assert/strict')
const fs = require('node:fs/promises')
const path = require('node:path')
const { chromium } = require('playwright')
const base = new URL(process.argv[2] || 'http://127.0.0.1:3168')
const output = path.resolve(process.argv[3] || 'test-results/history-ui')
if (!['127.0.0.1', 'localhost'].includes(base.hostname)) throw new Error('Loopback only')
const gap = JSON.parse(require('node:fs').readFileSync(path.join(__dirname, '../tests/fixtures/workflow/llm_responses.json'))).GapAnalysis
const question = { question_text: '合成题：怎样避免旧结果写回？', question_type: '技术深度', difficulty: '基础', focus_area: '版本', intent: '隔离', reference_answer: '合成答案：核对记录版本和任务编号。' }
async function main() {
  await fs.mkdir(output, { recursive: true })
  const browser = await chromium.launch({ channel: process.env.PLAYWRIGHT_CHANNEL || 'msedge', headless: true })
  const rows = new Map(), tasks = new Map(), errors = [], results = []
  const calls = { analysis: 0, questions: 0, anonymous: 0 }
  let sequence = 0, unavailable = false, busyResponse = false, streamFailure = false, holdRead = null
  let releasePending
  const contexts = []
  function fresh(title) { const id = `00000000-0000-4000-8000-${String(++sequence).padStart(12, '0')}`; const row = { id, title, revision: 0, inputs: {}, results: {}, created_at: '2026-10-28T06:00:00Z', updated_at: '2026-10-28T06:00:00Z' }; rows.set(id, row); return row }
  async function device(owner = 'same-account', width = 1280) {
    const context = await browser.newContext({ viewport: { width, height: 900 }, serviceWorkers: 'block' })
    contexts.push(context)
    const state = { owner, loggedIn: true }
    const page = await context.newPage()
    page.setDefaultTimeout(10000)
    page.on('pageerror', e => errors.push(e.message))
    await context.route('**/*', async route => {
      const req = route.request(), url = new URL(req.url()), p = url.pathname, method = req.method()
      if (!p.startsWith('/api/')) {
        if (url.origin === base.origin) return route.continue()
        errors.push(`nonlocal: ${url.origin}`); return route.abort()
      }
      const reply = (json, status = 200) => route.fulfill({ json: structuredClone(json), status })
      if (p === '/api/session' || p.startsWith('/api/upload/') || p.startsWith('/api/analyze/') || p === '/api/questions/generate') { calls.anonymous++; return reply({}, 500) }
      if (unavailable) return reply({ detail: '账号登录尚未配置' }, 503)
      if (p === '/api/auth/logout') { state.loggedIn = false; return reply({ success: true }) }
      if (!state.loggedIn) return reply({ detail: '请先登录GitHub账号' }, 401)
      if (p === '/api/auth/me') return reply({ account_id: state.owner })
      if (p === '/api/records') {
        if (method === 'GET') return reply(state.owner === 'same-account' ? [...rows.values()].map(({ inputs, results, ...r }) => r) : [])
        const data = req.postDataJSON()
        if (rows.size >= 20) return reply({ detail: '历史记录已达20份，请先删除' }, 409)
        return reply(fresh(data.title), 201)
      }
      const [id, ...rest] = p.slice('/api/records/'.length).split('/'), suffix = rest.join('/')
      const row = rows.get(id)
      if (!row || state.owner !== 'same-account') return reply({ detail: '记录不存在' }, 404)
      if (!suffix) {
        if (method === 'GET' && holdRead?.id === id) { const snapshot = structuredClone(row); const pending = holdRead; holdRead = null; await pending.wait; return reply(snapshot) }
        if (method === 'GET') return reply(row)
        if (method === 'PATCH') { row.title = req.postDataJSON().title; return reply(row) }
        if (method === 'DELETE') { rows.delete(id); tasks.delete(id); return route.fulfill({ status: 204 }) }
      }
      if (suffix === 'tasks') return reply(tasks.get(id) || [])
      const data = suffix.startsWith('upload/') ? { revision: Number(url.searchParams.get('revision')) } : req.postDataJSON()
      if (data.revision !== row.revision) return reply({ detail: '资料版本已变化，请刷新记录后重试' }, 409)
      if (suffix.startsWith('upload/')) {
        row.inputs[`${rest[1]}_text`] = '合成文本，仅用于浏览器验收，非真实简历。'
        row.revision++; row.results = {}; tasks.delete(id); return reply(row)
      }
      if (suffix === 'inputs') { row.inputs = {}; row.results = {}; row.revision++; tasks.delete(id); return reply(row) }
      if (suffix === 'analysis/stream') {
        calls.analysis++
        if (busyResponse || streamFailure) return route.fulfill({ contentType: 'text/event-stream', body: `data: ${JSON.stringify({ step: 'error', message: busyResponse ? '任务仍在运行' : '合成分析失败', data: { status: busyResponse ? 409 : 500 } })}\n\n` })
        row.results = { gap }; tasks.set(id, [{ kind: 'analysis', revision: row.revision, status: 'completed' }])
        return route.fulfill({ contentType: 'text/event-stream', body: `data: {"step":"jd_start","message":"合成进度"}\n\ndata: ${JSON.stringify({ step: 'complete', message: '分析完成', data: gap })}\n\n` })
      }
      if (suffix === 'questions/generate') { calls.questions++; row.results.questions = { questions: [question] }; tasks.set(id, [...(tasks.get(id) || []), { kind: 'questions', revision: row.revision, status: 'completed' }]); return reply({ success: true, total: 1, questions: [question] }) }
      errors.push(`unexpected: ${method} ${p}`); return reply({}, 500)
    })
    return { page, context, state }
  }
  try {
    const a = await device(), b = await device()
    await a.page.goto(new URL('/history', base).href)
    await a.page.getByLabel('新记录名称').fill('Python后端准备')
    await a.page.getByRole('button', { name: '创建记录', exact: true }).click()
    await a.page.getByRole('heading', { name: 'Python后端准备', exact: true }).waitFor()
    const id = [...rows.keys()][0]
    for (const label of ['上传记录JD', '上传记录简历']) {
      await a.page.getByLabel(label, { exact: true }).setInputFiles({ name: 'synthetic.txt', mimeType: 'text/plain', buffer: Buffer.from('合成资料，浏览器验收专用，无真实简历。') })
      await a.page.getByText(label === '上传记录JD' ? /资料版本 1/ : /资料版本 2/).waitFor()
    }
    await a.page.getByRole('button', { name: '开始分析当前资料', exact: true }).click()
    await a.page.getByRole('heading', { name: '已保存的匹配报告', exact: true }).waitFor()
    await a.page.getByRole('button', { name: '生成本记录题目', exact: true }).click()
    await a.page.getByText('已保存的个性化题库（1题）', { exact: true }).waitFor()
    await a.page.locator('summary').click()
    await a.page.getByText(question.reference_answer, { exact: true }).waitFor()
    results.push('命名创建→两次有版本上传→明确POST分析→题库与参考回答')
    await b.page.goto(new URL(`/history?record=${id}`, base).href)
    await b.page.getByText('已保存的个性化题库（1题）', { exact: true }).waitFor()
    await a.page.reload()
    await a.page.getByText('已保存的个性化题库（1题）', { exact: true }).waitFor()
    assert.deepEqual(calls, { analysis: 1, questions: 1, anonymous: 0 })
    results.push('同账号独立浏览器恢复；刷新不生成、不进入匿名接口')
    await a.page.getByLabel('记录名称', { exact: true }).fill('已改名的准备')
    await a.page.getByRole('button', { name: '保存名称', exact: true }).click()
    await a.page.getByRole('heading', { name: '已改名的准备', exact: true }).waitFor()
    await b.page.getByRole('button', { name: '刷新当前记录', exact: true }).click()
    await b.page.getByRole('heading', { name: '已改名的准备', exact: true }).waitFor()
    assert.equal(rows.get(id).revision, 2)
    // Other device changes input while A still holds revision2.
    rows.get(id).revision++; rows.get(id).results = {}
    await a.page.getByRole('button', { name: '重新分析当前资料', exact: true }).click()
    await a.page.getByRole('alert').filter({ hasText: '资料版本已变化' }).first().waitFor()
    assert.equal(calls.analysis, 1)
    await a.page.getByRole('button', { name: '刷新当前记录', exact: true }).click()
    await a.page.getByText(/资料版本 3/).waitFor()
    assert.equal(await a.page.getByRole('heading', { name: '已保存的匹配报告', exact: true }).count(), 0)
    results.push('改名不变版本；跨设备旧版本409清除旧展示、明确刷新后恢复')
    for (const mode of ['busy', 'failure']) {
      busyResponse = mode === 'busy'; streamFailure = mode === 'failure'
      await a.page.getByRole('button', { name: '开始分析当前资料', exact: true }).click()
      await a.page.getByRole('alert').filter({ hasText: busyResponse ? '任务仍在运行' : '合成分析失败' }).first().waitFor()
      const before = calls.analysis
      await a.page.getByRole('button', { name: '刷新当前记录', exact: true }).click()
      await a.page.getByText(/资料版本 3/).waitFor()
      assert.equal(calls.analysis, before)
    }
    busyResponse = streamFailure = false
    tasks.set(id, [{ kind: 'analysis', revision: 3, status: 'interrupted' }])
    rows.get(id).results = { gap }
    await a.page.getByRole('button', { name: '刷新当前记录', exact: true }).click()
    await a.page.getByText(/报告任务：已中断/).waitFor()
    await a.page.getByText(/这是本资料版本上次成功保存的报告/).waitFor()
    results.push('HTTP200内SSE409/500失败不重发；中断与上次成功报告明确标注')
    const other = fresh('第二份独立记录')
    await a.page.getByRole('button', { name: '刷新历史', exact: true }).click()
    await a.page.getByRole('button', { name: other.title, exact: true }).waitFor()
    let release; holdRead = { id, wait: new Promise(resolve => { release = resolve; releasePending = resolve }) }
    await a.page.getByRole('button', { name: '刷新当前记录', exact: true }).click()
    await a.page.getByRole('button', { name: other.title, exact: true }).click()
    await a.page.getByRole('heading', { name: other.title, exact: true }).waitFor()
    release()
    await a.page.waitForTimeout(150)
    assert.equal(await a.page.getByRole('heading', { name: '已保存的匹配报告', exact: true }).count(), 0)
    assert.equal(await a.page.locator('summary').count(), 0)
    results.push('切换记录后晚到旧响应不串报告/题库')
    await a.page.getByRole('button', { name: '删除此记录', exact: true }).click()
    await a.page.getByRole('button', { name: '取消删除', exact: true }).click()
    assert.ok(rows.has(other.id))
    await a.page.getByRole('button', { name: '删除此记录', exact: true }).click()
    await a.page.getByRole('button', { name: '确认永久删除', exact: true }).click()
    await a.page.getByText('选择一份记录，继续上传、分析与面试题练习。').waitFor()
    assert.ok(!rows.has(other.id))
    while (rows.size < 20) fresh(`占位${rows.size}`)
    await a.page.getByRole('button', { name: '刷新历史', exact: true }).click()
    await a.page.getByText(/已达20份/).waitFor()
    assert.ok(await a.page.getByRole('button', { name: '创建记录', exact: true }).isDisabled())
    assert.ok(rows.has(id))
    results.push('删除须二次确认、取消保留；20份上限不淘汰')
    const c = await device('other-account')
    await c.page.goto(new URL(`/history?record=${id}`, base).href)
    await c.page.getByRole('alert').filter({ hasText: '记录不存在' }).first().waitFor()
    assert.equal(await c.page.getByRole('heading', { name: '已保存的匹配报告', exact: true }).count(), 0)
    a.state.loggedIn = false
    await a.page.getByRole('button', { name: '刷新历史', exact: true }).click()
    await a.page.getByRole('link', { name: '使用 GitHub 登录', exact: true }).waitFor()
    assert.equal(await a.page.getByLabel('当前准备记录').count(), 0)
    assert.equal(b.state.loggedIn, true)
    await b.page.getByRole('button', { name: '退出本设备', exact: true }).click()
    await b.page.getByRole('link', { name: '使用 GitHub 登录', exact: true }).waitFor()
    results.push('另一账号404、过期清屏、退出本设备')
    unavailable = true
    const mobile = await device('same-account', 390)
    await mobile.page.goto(new URL('/history', base).href)
    await mobile.page.getByRole('alert').filter({ hasText: '账号登录尚未配置' }).waitFor()
    assert.ok(await mobile.page.evaluate(() => document.documentElement.scrollWidth <= innerWidth))
    await mobile.page.screenshot({ path: path.join(output, 'unconfigured-mobile.png'), fullPage: true })
    unavailable = false
    await mobile.page.getByRole('button', { name: '重新检查登录状态', exact: true }).click()
    await mobile.page.getByRole('button', { name: rows.get(id).title, exact: true }).click()
    await mobile.page.getByRole('heading', { name: '已保存的匹配报告', exact: true }).waitFor()
    assert.ok(await mobile.page.evaluate(() => document.documentElement.scrollWidth <= innerWidth))
    await mobile.page.screenshot({ path: path.join(output, 'record-mobile.png'), fullPage: true })
    await mobile.page.setViewportSize({ width: 1280, height: 900 })
    await mobile.page.screenshot({ path: path.join(output, 'record-desktop.png'), fullPage: true })
    results.push('未配置503可恢复；390px与桌面页面无横向溢出')
    assert.equal(calls.anonymous, 0); assert.deepEqual(errors, [])
    await fs.writeFile(path.join(output, 'results.json'), JSON.stringify({ results, calls, errors, boundary: 'All account APIs intercepted; no real OAuth, parsers, DB or model' }, null, 2))
    console.log(JSON.stringify({ passed: results.length, results, calls, errors }))
  } catch (err) {
    for (const c of contexts) for (const p of c.pages()) console.error('PAGE DIAGNOSTIC', p.url(), (await p.locator('body').innerText()).slice(0, 3000))
    throw err
  } finally { releasePending?.(); for (const c of contexts) await c.close(); await browser.close() }
}
main().catch(e => { console.error(e); process.exitCode = 1 })
