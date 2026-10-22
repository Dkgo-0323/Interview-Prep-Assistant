// Uses the project's installed TypeScript compiler; no network or model calls.
const { test } = require('node:test')
const assert = require('node:assert/strict')
const { readFileSync } = require('node:fs')
const { join } = require('node:path')
const vm = require('node:vm')
const ts = require('../frontend/node_modules/typescript')

function client(fetch, extras = {}) {
  const source = readFileSync(join(__dirname, '../frontend/lib/api.ts'), 'utf8')
  const js = ts.transpileModule(source, {
    compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2022 },
  }).outputText
  const exports = {}
  vm.runInNewContext(js, {
    exports, Error, FormData,
    EventSource: extras.EventSource,
    fetch: (url, options) => url.endsWith('/api/session')
      ? (extras.initialize ? extras.initialize(url, options) : Promise.resolve(Response.json({ success: true })))
      : fetch(url, options),
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

test('concurrent first requests share bootstrap and always include cookies', async () => {
  let release
  let boots = 0
  const calls = []
  const api = client(async (url, options) => {
    calls.push(url)
    assert.equal(options.credentials, 'include')
    assert.equal(options.cache, 'no-store')
    return Response.json({ success: true })
  }, { initialize: async (url, options) => {
    boots++
    assert.equal(options.credentials, 'include')
    await new Promise(resolve => { release = resolve })
    return Response.json({ success: true })
  } })
  const first = api.getUploadStatus()
  const second = api.getCachedQuestions()
  assert.equal(boots, 1)
  assert.equal(calls.length, 0)
  release()
  await Promise.all([first, second])
  assert.equal(calls.length, 2)
})

test('expired session fails once without replaying work and can initialize on explicit retry', async () => {
  let boots = 0
  let requests = 0
  const api = client(async () => {
    requests++
    return requests === 1 ? Response.json({ detail: '会话过期，请重新上传' }, { status: 410 }) : Response.json({ success: true })
  }, { initialize: async () => { boots++; return Response.json({ success: true }) } })
  await assert.rejects(api.getUploadStatus(), err => err.status === 410)
  assert.equal(requests, 1)
  await api.getUploadStatus()
  assert.equal(boots, 2)
})

test('capacity failure does not send uploads or other dependent requests', async () => {
  let calls = 0
  const api = client(async () => { calls++; throw new Error('unexpected') }, {
    initialize: async () => Response.json({ detail: '容量已满' }, { status: 503 }),
  })
  await assert.rejects(api.getUploadStatus(), err => err.status === 503 && err.message === '容量已满')
  assert.equal(calls, 0)
})

test('clear reports failure instead of claiming a successful reset', async () => {
  const api = client(async () => Response.json({ detail: '清除失败' }, { status: 503 }))
  await assert.rejects(api.clearSession(), err => err.status === 503)
})

test('refresh restores report without opening SSE; failed cache never starts analysis', async () => {
  for (const status of [200, 503]) {
    const streams = []
    const events = []
    const errors = []
    const api = client(async () => status === 200 ? Response.json({ success: true, data: { overall_match_score: 77 } }) : Response.json({ detail: '缓存读取失败' }, { status }), {
      EventSource: class { constructor(...args) { streams.push(args) } },
    })
    const close = api.startAnalysis(event => events.push(event), error => errors.push(error))
    await new Promise(resolve => setImmediate(resolve))
    close()
    assert.equal(streams.length, 0)
    assert.equal(events.length, status === 200 ? 1 : 0)
    assert.equal(errors.length, status === 200 ? 0 : 1)
  }
})

test('SSE uses credentials, terminal errors close it, unmount cancels preflight', async () => {
  const streams = []
  class Stream {
    static CLOSED = 2
    constructor(url, options) { this.options = options; streams.push(this) }
    close() { this.closed = true }
  }
  const api = client(async url => url.endsWith('/result')
    ? Response.json({ detail: 'none' }, { status: 404 })
    : Response.json({ ready_to_analyze: true }), { EventSource: Stream })
  const events = []
  const close = api.startAnalysis(event => events.push(event), error => assert.fail(error))
  await new Promise(resolve => setImmediate(resolve))
  assert.equal(streams.length, 1)
  assert.equal(streams[0].options.withCredentials, true)
  streams[0].onmessage({ data: JSON.stringify({ step: 'error', message: '旧结果作废', data: { status: 409 } }) })
  assert.equal(events[0].step, 'error')
  assert.equal(streams[0].closed, true)
  close()
  const cancel = api.startAnalysis(() => assert.fail('unmounted event'), error => assert.fail(error))
  cancel()
  await new Promise(resolve => setImmediate(resolve))
  assert.equal(streams.length, 1)
})
