// Uses the project's installed TypeScript compiler; no network or model calls.
const { test } = require('node:test')
const assert = require('node:assert/strict')
const { readFileSync } = require('node:fs')
const { join } = require('node:path')
const vm = require('node:vm')
const ts = require('../frontend/node_modules/typescript')

function client(fetch) {
  const source = readFileSync(join(__dirname, '../frontend/lib/api.ts'), 'utf8')
  const js = ts.transpileModule(source, {
    compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2022 },
  }).outputText
  const exports = {}
  vm.runInNewContext(js, {
    exports, fetch, Error, FormData,
    process: { env: { NEXT_PUBLIC_API_URL: 'https://offline.invalid' } },
  })
  return exports
}

test('cache 404 keeps status and API message as an Error', async () => {
  const api = client(async () => Response.json({ detail: '暂无题目' }, { status: 404 }))
  await assert.rejects(api.getCachedQuestions(), err =>
    err instanceof Error && err instanceof api.APIError && err.status === 404 && err.message === '暂无题目')
})

test('non-JSON server failure keeps HTTP 502', async () => {
  const api = client(async () => new Response('Bad gateway', { status: 502 }))
  await assert.rejects(api.getCachedQuestions(), err => err.status === 502 && err.message === 'HTTP 502')
})

test('shared upload status client retains string error detail', async () => {
  const api = client(async () => Response.json({ detail: '服务暂不可用' }, { status: 503 }))
  await assert.rejects(api.getUploadStatus(), err => err.status === 503 && err.message === '服务暂不可用')
})

test('validation detail arrays use a readable HTTP fallback', async () => {
  const api = client(async () => Response.json({ detail: [{ msg: 'required' }] }, { status: 422 }))
  await assert.rejects(api.generateQuestions(10), err => err.status === 422 && err.message === 'HTTP 422')
})

test('network errors are not misclassified as HTTP 404', async () => {
  const failure = new TypeError('offline')
  const api = client(async () => { throw failure })
  await assert.rejects(api.getCachedQuestions(), err => err === failure && !(err instanceof api.APIError))
})

test('successful responses keep their existing payload', async () => {
  const payload = { success: true, total: 0, questions: [] }
  const api = client(async () => Response.json(payload))
  assert.deepEqual(await api.getCachedQuestions(), payload)
})
