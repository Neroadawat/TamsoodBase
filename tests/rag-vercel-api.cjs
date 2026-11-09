const assert = require('node:assert/strict');
const { EventEmitter } = require('node:events');
const handler = require('../api/rag/ask.js');
const { retrieve, parseGeminiAnswer, isReleaseReady, callGemini, previewRateAllowed,
  isCorpusOverviewQuestion, corpusOverview } = handler._internals;

const functionalUnit = retrieve('FAME functional unit 1000 MJ');
assert.ok(functionalUnit.length > 0, 'preview corpus query should retrieve relevant evidence');
assert.equal(functionalUnit[0].id, 'fame-functional-unit');
assert.ok(functionalUnit[0].attribution.includes('Permpool'));
assert.equal(functionalUnit[0].licence, 'CC BY 4.0');
assert.deepEqual(retrieve('วิธีปลูกกล้วยไม้ในกระถาง'), [], 'out-of-scope query should abstain');
assert.equal(isCorpusOverviewQuestion('แชตนี้ทำอะไรได้บ้าง'), true);
assert.equal(isCorpusOverviewQuestion('ในระบบมีข้อมูลอะไรบ้าง'), true);
assert.equal(isCorpusOverviewQuestion('แชตนี้มีข้อมูลเรื่องอะไรบ้าง?'), true);
assert.equal(isCorpusOverviewQuestion('ถามเรื่องหน่วยหน้าที่ 1000 MJ'), false,
  'specific evidence questions must continue through retrieval and Gemini');
const overview = corpusOverview();
assert.equal(overview.hits.length, 6, 'overview should enumerate the complete Preview corpus');
assert.equal(overview.summary.source_ids.length, 6);
assert.match(overview.summary.text, /ไม่ใช่คลังข้อมูลทั้งหมดของโครงการ/);

const accepted = parseGeminiAnswer({ candidates: [{ content: { parts: [{ text: JSON.stringify({
  answer: 'ตัวอย่างคำตอบจากหลักฐาน', source_ids: [functionalUnit[0].id],
}) }] } }] }, new Set(functionalUnit.map(hit => hit.id)));
assert.deepEqual(accepted.source_ids, [functionalUnit[0].id]);
assert.throws(() => parseGeminiAnswer({ candidates: [{ content: { parts: [{ text: JSON.stringify({
  answer: 'มีอ้างอิง', source_ids: ['not-in-evidence'],
}) }] } }] }, new Set(functionalUnit.map(hit => hit.id))));
assert.equal(isReleaseReady({}), false, 'missing release configuration must stay closed');
assert.equal(isReleaseReady({ VERCEL_ENV: 'development', TAMSOOD_RAG_PUBLIC_ENABLED: 'true' }), false,
  'non-production deployments must not enter the Production release gate');
assert.equal(isReleaseReady({
  VERCEL_ENV: 'preview',
  TAMSOOD_RAG_PREVIEW_ENABLED: 'false',
  TAMSOOD_RAG_PUBLIC_ENABLED: 'true',
  TAMSOOD_GEMINI_DATA_PROCESSING_ACCEPTED: 'true',
  TAMSOOD_RAG_RIGHTS_CLEARANCE_REF: 'test-only',
  TAMSOOD_RAG_RATE_LIMIT_POLICY_ID: 'test-only',
  TAMSOOD_RAG_PRIVACY_REVIEW_REF: 'test-only',
  TAMSOOD_RAG_UAT_REF: 'test-only',
  TAMSOOD_RAG_PUBLIC_ORIGIN: 'https://example.org',
  GEMINI_API_KEY: 'test-only',
}), false, 'Preview must not fall through to the Production release gate');
assert.equal(isReleaseReady({
  VERCEL_ENV: 'preview',
  VERCEL_URL: 'tamsoodbase-git-feature-neroadawats-projects.vercel.app',
  TAMSOOD_RAG_PREVIEW_ENABLED: 'true',
  TAMSOOD_GEMINI_DATA_PROCESSING_ACCEPTED: 'true',
  GEMINI_API_KEY: 'test-only',
}), true, 'preview needs explicit flags, an API key, and the reviewed narrow corpus');

for (let i = 0; i < 2048; i++) {
  assert.equal(previewRateAllowed({ headers: { 'x-forwarded-for': `client-${i}` } }, 1000), true);
}
assert.equal(previewRateAllowed({ headers: { 'x-forwarded-for': 'client-overflow' } }, 1000), false,
  'preview rate buckets must have a fixed memory bound');
assert.equal(previewRateAllowed({ headers: { 'x-forwarded-for': 'client-after-expiry' } }, 61_001), true,
  'expired preview buckets should be pruned when the table is full');

function mockResponse() {
  return {
    headers: {},
    setHeader(name, value) { this.headers[name.toLowerCase()] = value; },
    end(body) { this.body = body; this.writableEnded = true; },
  };
}

async function testRouteStaysClosed() {
  const req = new EventEmitter();
  req.method = 'POST';
  req.headers = { origin: 'https://tamsoodbase.vercel.app', 'content-type': 'application/json' };
  const res = mockResponse();
  await handler(req, res);
  assert.equal(res.statusCode, 503);
  assert.match(res.body, /not available/);
}

async function testGeminiRequestKeepsKeyOutOfUrlAndChecksCitationIds() {
  let seen;
  const answer = await callGemini('คำถาม', [functionalUnit[0]], { GEMINI_API_KEY: 'fake-test-key' }, async (url, options) => {
    seen = { url: String(url), options };
    return {
      ok: true,
      headers: { get: () => '120' },
      text: async () => JSON.stringify({ candidates: [{ content: { parts: [{ text: JSON.stringify({
        answer: 'คำตอบตัวอย่าง', source_ids: [functionalUnit[0].id],
      }) }] } }] }),
    };
  });
  assert.equal(answer.source_ids[0], functionalUnit[0].id);
  assert.equal(seen.url.includes('fake-test-key'), false);
  assert.equal(seen.options.headers['x-goog-api-key'], 'fake-test-key');
  assert.equal(seen.options.body.includes('not-in-evidence'), false);
}

async function testCorpusOverviewRouteDoesNotNeedGemini() {
  const names = ['VERCEL_ENV', 'VERCEL_URL', 'TAMSOOD_RAG_PREVIEW_ENABLED',
    'TAMSOOD_GEMINI_DATA_PROCESSING_ACCEPTED', 'GEMINI_API_KEY'];
  const previousEnv = Object.fromEntries(names.map(name => [name, process.env[name]]));
  const oldFetch = global.fetch;
  let fetchCalled = false;
  Object.assign(process.env, {
    VERCEL_ENV: 'preview',
    VERCEL_URL: 'tamsoodbase-git-feature-neroadawats-projects.vercel.app',
    TAMSOOD_RAG_PREVIEW_ENABLED: 'true',
    TAMSOOD_GEMINI_DATA_PROCESSING_ACCEPTED: 'true',
    GEMINI_API_KEY: 'test-only',
  });
  global.fetch = async () => { fetchCalled = true; throw new Error('unexpected Gemini call'); };
  try {
    const body = Buffer.from(JSON.stringify({ question: 'ในระบบมีข้อมูลอะไรบ้าง' }));
    const req = new EventEmitter();
    req.method = 'POST';
    req.headers = {
      origin: `https://${process.env.VERCEL_URL}`,
      'content-type': 'application/json',
      'content-length': String(body.length),
      'x-forwarded-for': 'overview-test-client',
    };
    const res = mockResponse();
    const pending = handler(req, res);
    req.emit('data', body);
    req.emit('end');
    await pending;
    const payload = JSON.parse(res.body);
    assert.equal(res.statusCode, 200);
    assert.equal(payload.hits.length, 6);
    assert.equal(payload.summary.source_ids.length, 6);
    assert.match(payload.summary.text, /ไม่มีสถิติ NSO/);
    assert.equal(fetchCalled, false, 'overview should be answered from the local corpus catalog');
  } finally {
    global.fetch = oldFetch;
    for (const name of names) {
      if (previousEnv[name] === undefined) delete process.env[name];
      else process.env[name] = previousEnv[name];
    }
  }
}

Promise.all([testRouteStaysClosed(), testGeminiRequestKeepsKeyOutOfUrlAndChecksCitationIds(), testCorpusOverviewRouteDoesNotNeedGemini()])
  .then(() => console.log('Vercel RAG checks passed (Gemini request contract works; public route stays closed).'));
