const { test } = require('node:test')
const assert = require('node:assert/strict')
const { readFileSync } = require('node:fs')
const vm = require('node:vm')
const ts = require('../frontend/node_modules/typescript')
class APIError extends Error { constructor(status, message) { super(message); this.status = status } }
function client(fetch) {
  const exports = {}
  vm.runInNewContext(ts.transpileModule(readFileSync(require('node:path').join(__dirname, '../frontend/lib/history-api.ts'), 'utf8'), {
    compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2022 },
  }).outputText, { exports, require: () => ({ APIError }), fetch, Error, FormData, TextDecoder,
    process: { env: { NEXT_PUBLIC_API_URL: 'https://offline.invalid' } } })
  return exports
}
test('account CRUD carries cookies and no-store, no anonymous bootstrap, no owner field', async () => {
  const calls = []
  const api = client(async (url, options) => {
    calls.push({ path: new URL(url).pathname, ...options })
    return options.method === 'DELETE' ? new Response(null, { status: 204 }) : Response.json({ id: 'one' })
  })
  await api.getAccount(); await api.listRecords(); await api.createRecord('岗位')
  await api.readRecord('one'); await api.renameRecord('one', '新名'); await api.readTasks('one')
  assert.equal(await api.deleteRecord('one'), undefined)
  await api.logoutAccount()
  assert.equal(calls.length, 8)
  assert.ok(calls.every(c => c.credentials === 'include' && c.cache === 'no-store' && !c.path.includes('/session')))
  assert.equal(calls[2].body, JSON.stringify({ title: '岗位' }))
  assert.equal(calls[4].method, 'PATCH')
})
test('upload, clear, generation bind record and explicit revision, never retry 409', async () => {
  const calls = []
  const api = client(async (url, options) => {
    calls.push({ url, ...options })
    return Response.json({ detail: '版本冲突' }, { status: 409 })
  })
  await assert.rejects(api.uploadRecord('a/b', 7, 'jd', new Blob(['synthetic'])), e => e.status === 409)
  await assert.rejects(api.clearRecordInputs('one', 7), e => e.status === 409)
  await assert.rejects(api.generateRecordQuestions('one', 7, 20), e => e.status === 409)
  assert.equal(calls.length, 3)
  assert.ok(calls[0].url.endsWith('/records/a%2Fb/upload/jd?revision=7'))
  assert.equal(calls[1].body, '{"revision":7}')
  assert.equal(calls[2].body, '{"revision":7,"num_questions":20}')
})
test('HTTP auth/storage/nonJSON failures preserve status without automatic login or retry', async () => {
  for (const status of [401, 404, 503]) {
    let count = 0
    const api = client(async () => { count++; return new Response('failure', { status }) })
    await assert.rejects(api.readRecord('one'), e => e.status === status && e.message === `HTTP ${status}`)
    assert.equal(count, 1)
  }
})
test('POST SSE decodes byte-split Chinese, split CRLF, heartbeats and terminal complete', async () => {
  const bytes = new TextEncoder().encode(': ping\r\n\r\ndata: {"step":"jd_start","message":"开始"}\r\n\r\ndata: {"step":"complete","message":"完成","data":{}}\r\n\r\n')
  let calls = 0
  const api = client(async (url, options) => {
    calls++
    assert.ok(url.endsWith('/records/one/analysis/stream'))
    assert.equal(options.method, 'POST'); assert.equal(options.body, '{"revision":3}')
    return new Response(new ReadableStream({ start(c) { for (const b of bytes) c.enqueue(new Uint8Array([b])); c.close() } }), { headers: { 'Content-Type': 'text/event-stream' } })
  })
  const events = []
  await api.analyzeRecord('one', 3, e => events.push(e), new AbortController().signal)
  assert.deepEqual(events.map(e => e.message), ['开始', '完成'])
  assert.equal(calls, 1)
})
test('SSE errors after HTTP200 keep status, early EOF and malformed data do not succeed', async () => {
  for (const [data, expected] of [
    ['data: {"step":"error","message":"busy","data":{"status":409}}\n\n', 'busy'],
    ['data: {"step":"jd_start","message":"working"}\n\n', '提前结束'],
    ['data: broken\n\n', 'JSON'],
  ]) {
    let calls = 0
    const api = client(async () => { calls++; return new Response(data, { headers: { 'Content-Type': 'text/event-stream' } }) })
    await assert.rejects(api.analyzeRecord('one', 1, () => {}, new AbortController().signal), e => e.message.includes(expected))
    assert.equal(calls, 1)
  }
})
test('stream transport cancellation signal and HTTP401 do not reconnect', async () => {
  const controller = new AbortController()
  let calls = 0
  const api = client(async (url, options) => {
    calls++; assert.equal(options.signal, controller.signal)
    return Response.json({ detail: 'expired' }, { status: 401 })
  })
  await assert.rejects(api.analyzeRecord('one', 0, () => assert.fail(), controller.signal), e => e.status === 401)
  assert.equal(calls, 1)
})
