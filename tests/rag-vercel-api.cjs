const assert = require('node:assert/strict');
const { EventEmitter } = require('node:events');
const handler = require('../api/rag/ask.js');
const { retrieve, parseGeminiAnswer, isReleaseReady, callGemini } = handler._internals;

const functionalUnit = retrieve('FAME functional unit 1000 MJ');
assert.ok(functionalUnit.length > 0, 'preview corpus query should retrieve relevant evidence');
assert.equal(functionalUnit[0].id, 'fame-functional-unit');
assert.ok(functionalUnit[0].attribution.includes('Permpool'));
assert.equal(functionalUnit[0].licence, 'CC BY 4.0');
assert.deepEqual(retrieve('วิธีปลูกกล้วยไม้ในกระถาง'), [], 'out-of-scope query should abstain');

const accepted = parseGeminiAnswer({ candidates: [{ content: { parts: [{ text: JSON.stringify({
  answer: 'ตัวอย่างคำตอบจากหลักฐาน', source_ids: [functionalUnit[0].id],
}) }] } }] }, new Set(functionalUnit.map(hit => hit.id)));
assert.deepEqual(accepted.source_ids, [functionalUnit[0].id]);
assert.throws(() => parseGeminiAnswer({ candidates: [{ content: { parts: [{ text: JSON.stringify({
  answer: 'มีอ้างอิง', source_ids: ['not-in-evidence'],
}) }] } }] }, new Set(functionalUnit.map(hit => hit.id))));
assert.equal(isReleaseReady({}), false, 'missing release configuration must stay closed');
assert.equal(isReleaseReady({
  VERCEL_ENV: 'preview',
  VERCEL_URL: 'tamsoodbase-git-feature-neroadawats-projects.vercel.app',
  TAMSOOD_RAG_PREVIEW_ENABLED: 'true',
  TAMSOOD_GEMINI_DATA_PROCESSING_ACCEPTED: 'true',
  GEMINI_API_KEY: 'test-only',
}), true, 'preview needs explicit flags, an API key, and the reviewed narrow corpus');

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

Promise.all([testRouteStaysClosed(), testGeminiRequestKeepsKeyOutOfUrlAndChecksCitationIds()])
  .then(() => console.log('Vercel RAG checks passed (Gemini request contract works; public route stays closed).'));
