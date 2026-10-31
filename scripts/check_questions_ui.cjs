// Browser regression: every API response is synthetic; real Qwen is never used.
const assert = require('node:assert/strict')
const fs = require('node:fs/promises')
const path = require('node:path')
const { chromium } = require('playwright')
const base = new URL(process.argv[2] || 'http://127.0.0.1:3168')
const output = path.resolve(process.argv[3] || 'test-results/questions-ui')
if (!['127.0.0.1', 'localhost'].includes(base.hostname)) throw new Error('Loopback only')
const payload = { total: 2, questions: [
  { question_text: '合成技术题：缓存如何失效？', question_type: '技术深度', difficulty: '基础', reference_answer: '合成答案：更新输入后失效。', focus_area: '缓存', intent: '验证' },
  { question_text: '合成行为题：如何协作？', question_type: '行为面试', difficulty: '进阶', reference_answer: '合成答案：明确分工。', focus_area: '协作', intent: '验证' },
] }
const gap = JSON.parse(require('node:fs').readFileSync(path.join(__dirname, '../tests/fixtures/workflow/llm_responses.json'))).GapAnalysis
async function main() {
  await fs.mkdir(output, { recursive: true })
  const browser = await chromium.launch({ channel: process.env.PLAYWRIGHT_CHANNEL || 'msedge' })
  const results = []
  try {
    for (const mode of ['cached', 'missing', 'plain404', 'server', 'network', 'plain502', 'null200', 'invalid200', 'generateFailure', 'busy']) {
      const context = await browser.newContext({ serviceWorkers: 'block', viewport: { width: 1280, height: 900 } })
      const page = await context.newPage(), calls = { cached: 0, generated: 0, unexpected: 0 }, errors = []
      let saved = mode === 'cached'
      page.on('pageerror', error => errors.push(error.message))
      page.setDefaultTimeout(10000)
      await context.route('**/*', async route => {
        const url = new URL(route.request().url())
        if (url.pathname === '/api/session') return route.fulfill({ json: { success: true } })
        if (url.pathname === '/api/analyze/result') return route.fulfill({ json: { success: true, data: gap } })
        if (url.pathname === '/api/questions/cached') {
          calls.cached++
          if (saved) return route.fulfill({ json: payload })
          if (mode === 'network') return route.abort()
          if (mode === 'null200') return route.fulfill({ contentType: 'application/json', body: 'null' })
          if (mode === 'invalid200') return route.fulfill({ json: { success: true } })
          const status = mode === 'plain502' ? 502 : mode === 'server' ? 500 : 404
          return route.fulfill({ status, contentType: mode.startsWith('plain') ? 'text/plain' : 'application/json', body: mode.startsWith('plain') ? 'synthetic error' : JSON.stringify({ detail: '合成缓存错误' }) })
        }
        if (url.pathname === '/api/questions/generate') {
          calls.generated++
          await new Promise(resolve => setTimeout(resolve, 400))
          if (mode === 'busy' || mode === 'generateFailure') return route.fulfill({ status: mode === 'busy' ? 409 : 500, json: { detail: '合成生成错误' } })
          saved = true
          return route.fulfill({ json: payload })
        }
        if (url.pathname.startsWith('/api/') || url.origin !== base.origin) { calls.unexpected++; return route.abort() }
        return route.continue()
      })
      await page.goto(new URL('/questions', base).href)
      const empty = ['missing', 'plain404', 'generateFailure', 'busy'].includes(mode)
      if (mode === 'cached') await page.getByText('题目来源：后端缓存', { exact: true }).waitFor()
      else if (empty) await page.getByText('尚未生成面试题', { exact: true }).waitFor()
      else await page.getByText(/读取缓存失败/).waitFor()
      assert.ok(calls.cached >= 1, mode + ': cache endpoint exercised')
      assert.equal(calls.generated, 0, mode + ': page entry must be read-only')
      assert.equal(await page.getByText('题目来源：固定示例，非个性化', { exact: true }).count(), 0)
      if (empty) {
        await page.getByRole('button', { name: '生成10道面试题', exact: true }).click()
        await page.getByText('正在生成面试题…', { exact: true }).waitFor()
        if (mode === 'generateFailure') {
          await page.getByText(/生成失败/).waitFor()
          await page.getByRole('button', { name: '检查生成结果', exact: true }).click()
          await page.getByText('尚未生成面试题', { exact: true }).waitFor()
        } else if (mode === 'busy') {
          await page.getByText(/题目任务仍在处理中/).waitFor()
          await page.getByRole('button', { name: '检查生成结果', exact: true }).click()
          await page.getByText(/题目任务仍在处理中/).waitFor()
          assert.equal(calls.generated, 1)
          saved = true // Simulate the original task finishing, not another POST.
          await page.getByRole('button', { name: '检查生成结果', exact: true }).click()
          await page.getByText('题目来源：后端缓存', { exact: true }).waitFor()
        } else await page.getByText('题目来源：本次生成', { exact: true }).waitFor()
        assert.equal(calls.generated, 1, mode + ': exactly one explicit generation')
      }
      if (mode === 'cached') {
        await page.getByRole('button', { name: '查看参考答案', exact: true }).first().click()
        await page.getByRole('button', { name: '查看问题', exact: true }).first().click()
        await page.getByRole('button', { name: '收藏', exact: true }).first().click()
        await page.getByRole('button', { name: /仅看收藏/ }).click()
        await page.getByRole('searchbox').fill('不匹配的合成词')
        await page.getByText('没有匹配的题目', { exact: true }).waitFor()
        await page.reload()
        await page.getByText('题目来源：后端缓存', { exact: true }).waitFor()
        assert.equal(calls.generated, 0)
        await page.screenshot({ path: path.join(output, 'cached-desktop.png'), fullPage: true, animations: 'disabled' })
      }
      if (mode === 'server') {
        await page.setViewportSize({ width: 390, height: 844 })
        await page.getByRole('button', { name: '查看示例题（非个性化）', exact: true }).click()
        await page.getByText('题目来源：固定示例，非个性化', { exact: true }).waitFor()
        assert.equal(calls.generated, 0)
        assert.equal(await page.evaluate(() => document.documentElement.scrollWidth > innerWidth), false)
        await page.screenshot({ path: path.join(output, 'example-mobile.png'), fullPage: true, animations: 'disabled' })
      }
      if (mode === 'missing') {
        await page.goto(new URL('/analyze', base).href)
        await page.getByRole('link', { name: '进入面试题库 →', exact: true }).waitFor()
        assert.equal(await page.getByRole('link', { name: '重新上传资料', exact: true }).count(), 1)
        assert.equal(await page.getByText('查看求职画像', { exact: true }).count(), 0)
        assert.equal(await page.getByText('开始面试题练习', { exact: true }).count(), 0)
        await page.screenshot({ path: path.join(output, 'analysis-actions.png'), fullPage: true, animations: 'disabled' })
      }
      assert.equal(calls.unexpected, 0)
      assert.deepEqual(errors, [])
      results.push({ mode, calls, errors })
      await context.close()
    }
    await fs.writeFile(path.join(output, 'results.json'), JSON.stringify(results, null, 2))
    console.log(JSON.stringify(results))
  } finally { await browser.close() }
}
main().catch(error => { console.error(error); process.exit(1) })
