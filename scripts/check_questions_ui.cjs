// Production-page regression with synthetic API responses only.
// Requires Playwright (available via NODE_PATH in the Codex workspace runtime).
const assert = require('node:assert/strict')
const fs = require('node:fs/promises')
const path = require('node:path')
const { chromium } = require('playwright')

const base = new URL(process.argv[2] || 'http://127.0.0.1:3168')
const output = path.resolve(process.argv[3] || 'test-results/questions-ui')
if (!['127.0.0.1', 'localhost'].includes(base.hostname)) throw new Error('Use a local production server')
const payload = { success: true, total: 2, questions: [
  { question_text: '合成技术题：缓存如何失效？', question_type: '技术深度', difficulty: '基础', reference_answer: '合成答案：更新输入后失效。', focus_area: '缓存', intent: '验证' },
  { question_text: '合成行为题：如何协作？', question_type: '行为面试', difficulty: '进阶', reference_answer: '合成答案：明确分工。', focus_area: '协作', intent: '验证' },
] }

async function main() {
  await fs.mkdir(output, { recursive: true })
  const browser = await chromium.launch({ channel: process.env.PLAYWRIGHT_CHANNEL || 'msedge', headless: true })
  const results = []
  try {
    for (const mode of ['cached', 'missing', 'plain404', 'server', 'network', 'plain502', 'null200', 'invalid200', 'retry', 'generateFailure']) {
      const context = await browser.newContext({ viewport: { width: 1280, height: 900 }, serviceWorkers: 'block' })
      const page = await context.newPage()
      const errors = []
      const calls = { cached: 0, generated: 0, unexpected: 0 }
      page.on('pageerror', e => errors.push(e.message))
      await context.route('**/*', async route => {
        const url = new URL(route.request().url())
        if (url.pathname.startsWith('/api/')) {
          if (url.pathname === '/api/session' && route.request().method() === 'POST') {
            return route.fulfill({ json: { success: true, idle_timeout_seconds: 1800 } })
          }
          if (url.pathname === '/api/questions/cached' && route.request().method() === 'GET') {
            calls.cached++
            if (mode === 'network') return route.abort('failed')
            if (mode === 'cached') return route.fulfill({ json: payload })
            if (mode === 'null200') return route.fulfill({ contentType: 'application/json', body: 'null' })
            if (mode === 'invalid200') return route.fulfill({ json: { success: true } })
            if (mode === 'plain404' || mode === 'plain502') return route.fulfill({ status: mode === 'plain404' ? 404 : 502, body: 'Non-JSON error' })
            return route.fulfill({ status: ['missing', 'generateFailure'].includes(mode) ? 404 : 500, json: { detail: '合成缓存错误' } })
          }
          if (url.pathname === '/api/questions/generate' && route.request().method() === 'POST') {
            calls.generated++
            if (mode === 'generateFailure' || (mode === 'retry' && calls.generated === 1)) return route.fulfill({ status: 500, json: { detail: '合成生成错误' } })
            return route.fulfill({ json: payload })
          }
          calls.unexpected++
          return route.abort()
        }
        if (url.origin === base.origin) return route.continue()
        calls.unexpected++
        return route.abort()
      })
      await page.goto(new URL('/questions', base).href)
      const source = page.getByRole('status')
      await source.waitFor()
      const initialLabel = mode === 'cached' ? '后端缓存' : ['missing', 'plain404'].includes(mode) ? '本次生成' : '固定示例，非个性化'
      assert.ok((await source.innerText()).includes(initialLabel), mode)
      assert.equal(calls.cached, 1, mode)
      assert.equal(calls.generated, ['missing', 'plain404', 'generateFailure'].includes(mode) ? 1 : 0, mode)
      if (['server', 'network', 'plain502', 'null200', 'invalid200', 'retry'].includes(mode)) await page.getByText(/读取缓存失败/).waitFor()
      if (mode === 'generateFailure') await page.getByText(/生成失败/).waitFor()
      if (mode === 'retry') {
        await page.getByRole('button', { name: '重新生成', exact: true }).click()
        await page.getByText(/生成失败/).waitFor()
        assert.ok((await source.innerText()).includes('固定示例'))
        await page.getByRole('button', { name: '重新生成', exact: true }).click()
        await page.getByText('题目来源：本次生成', { exact: true }).waitFor()
        assert.equal(calls.generated, 2)
        assert.equal(calls.cached, 1)
      }
      if (mode === 'cached') {
        await page.getByRole('button', { name: '查看参考答案', exact: true }).first().click()
        await page.getByRole('button', { name: '查看问题', exact: true }).first().waitFor()
        await page.getByRole('button', { name: '查看问题', exact: true }).first().click()
        await page.getByRole('button', { name: '收藏', exact: true }).first().click()
        await page.getByRole('button', { name: /仅看收藏/ }).click()
        assert.equal(await page.getByRole('button', { name: '查看参考答案', exact: true }).count(), 1)
        await page.getByRole('searchbox').fill('不匹配的合成词')
        await page.getByText('没有匹配的题目', { exact: true }).waitFor()
        assert.ok((await source.innerText()).includes('后端缓存'))
        await page.getByRole('searchbox').fill('')
        await page.getByRole('button', { name: /仅看收藏/ }).click()
        await page.getByRole('button', { name: '行为', exact: true }).click()
        assert.equal(await page.getByRole('button', { name: '查看参考答案', exact: true }).count(), 1)
        assert.ok((await source.innerText()).includes('后端缓存'))
        await page.reload()
        await source.waitFor()
        assert.ok((await source.innerText()).includes('后端缓存'))
        assert.equal(calls.cached, 2)
        assert.equal(calls.generated, 0)
        await page.screenshot({ path: path.join(output, 'cached-desktop.png'), fullPage: true })
        await page.getByRole('button', { name: '收藏', exact: true }).first().click()
        await page.getByRole('button', { name: '重新生成', exact: true }).click()
        await page.getByText('题目来源：本次生成', { exact: true }).waitFor()
        await page.getByRole('button', { name: '仅看收藏 (0)', exact: true }).waitFor()
        assert.equal(calls.generated, 1)
      }
      if (mode === 'server') {
        await page.setViewportSize({ width: 390, height: 844 })
        await page.getByRole('searchbox').fill('React')
        assert.ok((await source.innerText()).includes('固定示例'))
        await page.reload()
        await source.waitFor()
        assert.ok((await source.innerText()).includes('固定示例'))
        assert.equal(calls.cached, 2)
        assert.equal(calls.generated, 0)
        assert.ok(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth))
        await page.screenshot({ path: path.join(output, 'example-mobile.png'), fullPage: true })
      }
      assert.equal(calls.unexpected, 0, mode)
      assert.deepEqual(errors, [], mode)
      results.push({ mode, calls, pageErrors: errors, passed: true })
      await context.close()
    }
    await fs.writeFile(path.join(output, 'results.json'), JSON.stringify(results, null, 2))
    console.log(JSON.stringify(results))
  } finally {
    await browser.close()
  }
}

main().catch(error => { console.error(error); process.exitCode = 1 })
