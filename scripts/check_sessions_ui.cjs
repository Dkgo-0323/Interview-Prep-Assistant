// Real loopback HTTP/cookies/SSE with serve_offline_demo.py; no real provider.
const assert = require('node:assert/strict')
const fs = require('node:fs/promises')
const path = require('node:path')
const { chromium } = require('playwright')
const base = new URL(process.argv[2] || 'http://127.0.0.1:3168')
const output = path.resolve(process.argv[3] || 'test-results/sessions-ui')
if (!['localhost', '127.0.0.1'].includes(base.hostname)) throw new Error('Loopback pages only')
const fixtures = path.join(__dirname, '../tests/fixtures/workflow')

async function main() {
  await fs.mkdir(output, { recursive: true })
  const browser = await chromium.launch({ channel: process.env.PLAYWRIGHT_CHANNEL || 'msedge', headless: true })
  const results = []
  const errors = []
  const contexts = []
  const diagnostics = []
  async function visitor() {
    const context = await browser.newContext({ viewport: { width: 1280, height: 900 }, serviceWorkers: 'block' })
    contexts.push(context)
    await context.route('**/*', route => {
      const url = new URL(route.request().url())
      if (['localhost', '127.0.0.1'].includes(url.hostname)) return route.continue()
      errors.push('blocked nonlocal request')
      return route.abort()
    })
    const page = await context.newPage()
    page.setDefaultTimeout(10000)
    page.on('pageerror', error => errors.push(error.message))
    page.on('requestfailed', request => diagnostics.push({ path: new URL(request.url()).pathname, failure: request.failure()?.errorText }))
    page.on('response', response => {
      if (new URL(response.url()).pathname.startsWith('/api/')) diagnostics.push({ path: new URL(response.url()).pathname, status: response.status() })
    })
    const calls = { bootstrap: 0, stream: 0, generated: 0 }
    page.on('request', request => {
      const p = new URL(request.url()).pathname
      if (p === '/api/session') calls.bootstrap++
      if (p === '/api/analyze/stream') calls.stream++
      if (p === '/api/questions/generate') calls.generated++
    })
    return { context, page, calls }
  }
  async function uploadFiles(page) {
    await Promise.all([
      page.locator('input[type=file]').nth(0).setInputFiles(path.join(fixtures, 'jd.txt')),
      page.locator('input[type=file]').nth(1).setInputFiles(path.join(fixtures, 'resume.txt')),
    ])
    await page.getByRole('button', { name: '开始分析', exact: true }).waitFor()
    await page.waitForFunction(() => [...document.querySelectorAll('button')].some(button => button.textContent.includes('开始分析') && !button.disabled))
  }
  try {
    const a = await visitor()
    const b = await visitor()
    await a.page.goto(base.href)
    await uploadFiles(a.page)
    assert.equal(a.calls.bootstrap, 1)
    const aCookie = (await a.context.cookies()).find(cookie => cookie.name === 'interview_session')
    assert.ok(aCookie?.httpOnly)
    assert.ok(!(await a.page.evaluate(() => document.cookie)).includes('interview_session'))
    await a.page.reload()
    await a.page.waitForFunction(() => [...document.querySelectorAll('button')].some(button => button.textContent.includes('开始分析') && !button.disabled))
    await a.page.getByRole('button', { name: '开始分析', exact: true }).click()
    await a.page.getByRole('heading', { name: '你的匹配度分析报告', exact: true }).waitFor()
    assert.equal(a.calls.stream, 1)
    await a.page.reload()
    await a.page.getByRole('heading', { name: '你的匹配度分析报告', exact: true }).waitFor()
    assert.equal(a.calls.stream, 1, 'refresh must use cached report')
    results.push({ scenario: 'parallel upload, homepage/report refresh, HttpOnly cookie and real SSE', passed: true })
    await a.page.goto(new URL('/questions', base).href)
    await a.page.getByText('题目来源：本次生成', { exact: true }).waitFor()
    await a.page.reload()
    await a.page.getByText('题目来源：后端缓存', { exact: true }).waitFor()
    await a.page.screenshot({ path: path.join(output, 'session-questions.png'), fullPage: true })
    assert.equal(a.calls.generated, 1)
    await b.page.goto(new URL('/analyze', base).href)
    await b.page.getByText('请返回首页重新上传 JD 和简历', { exact: true }).waitFor()
    assert.equal(b.calls.stream, 0)
    const bCookie = (await b.context.cookies()).find(cookie => cookie.name === 'interview_session')
    assert.notEqual(aCookie.value, bCookie.value)
    results.push({ scenario: 'second visitor cannot read first visitor report or start model work', passed: true })
    const c = await visitor()
    await c.page.goto(new URL('/questions', base).href)
    await c.page.getByText(/容量已满/).waitFor()
    await c.page.getByText('题目来源：固定示例，非个性化', { exact: true }).waitFor()
    assert.equal(c.calls.generated, 0)
    results.push({ scenario: 'third visitor capacity rejection sends no generation', passed: true })
    await b.page.goto(base.href)
    await uploadFiles(b.page)
    await b.page.getByRole('button', { name: '开始分析', exact: true }).click()
    await b.page.getByRole('heading', { name: '你的匹配度分析报告', exact: true }).waitFor()
    await a.page.goto(base.href)
    await a.page.getByRole('button', { name: '清除本会话资料', exact: true }).click()
    await a.page.getByRole('alert').getByText('本会话资料已清除，请重新上传两个文件。', { exact: true }).waitFor()
    await a.page.goto(new URL('/analyze', base).href)
    await a.page.getByText('请返回首页重新上传 JD 和简历', { exact: true }).waitFor()
    await b.page.reload()
    await b.page.getByRole('heading', { name: '你的匹配度分析报告', exact: true }).waitFor()
    assert.equal(b.calls.stream, 1)
    results.push({ scenario: 'clear affects only current visitor', passed: true })
    await b.context.route('**/api/analyze/result', route => route.fulfill({ status: 410, json: { detail: '合成过期响应：会话已过期，请返回首页重新上传资料' } }))
    await b.page.reload()
    await b.page.getByText(/合成过期响应/).waitFor()
    await b.page.getByRole('heading', { name: '暂时无法完成分析', exact: true }).waitFor()
    assert.equal(await b.page.getByRole('link', { name: '返回首页重新上传', exact: true }).getAttribute('href'), '/')
    assert.equal(b.calls.stream, 1)
    await b.page.setViewportSize({ width: 390, height: 844 })
    assert.ok(await b.page.evaluate(() => document.documentElement.scrollWidth <= innerWidth))
    await b.page.screenshot({ path: path.join(output, 'session-expired-mobile.png'), fullPage: true })
    results.push({ scenario: 'intercepted 410 shows recovery without new SSE, mobile layout', passed: true })
    assert.deepEqual(errors, [])
    await fs.writeFile(path.join(output, 'results.json'), JSON.stringify({ results, pageErrors: errors, provider: 'synthetic-only', expiryUI: 'intercepted-410' }, null, 2))
    console.log(JSON.stringify(results))
  } catch (error) {
    for (let i = 0; i < contexts.length; i++) {
      const page = contexts[i].pages()[0]
      if (page) await page.screenshot({ path: path.join(output, `failure-${i}.png`), fullPage: true })
    }
    await fs.writeFile(path.join(output, 'failure.json'), JSON.stringify({ results, diagnostics, errors }, null, 2))
    console.error(JSON.stringify({ diagnostics, errors }))
    throw error
  } finally {
    for (const context of contexts) await context.close()
    await browser.close()
  }
}
main().catch(error => { console.error(error); process.exitCode = 1 })
