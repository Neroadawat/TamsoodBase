// Contract tests for the public chat function. Gemini is always mocked here;
// nothing in this file calls a real service.
process.env.NODE_ENV = 'test';
const assert = require('node:assert/strict');
const { EventEmitter } = require('node:events');
const handler = require('../api/rag/ask.js');
const { isReleaseReady, rateAllowed, runQuery, isGrounded, plainListing, callGemini,
  answerQuestion, validPayload, rateBuckets, PLANNER_INSTRUCTION } = handler._internals;
const manifest = require('../docs/rag/public-release-manifest.json');
const pack = require('../docs/rag/knowledge-pack.json');

const READY_ENV = { VERCEL_ENV: 'production', TAMSOOD_RAG_PUBLIC_ENABLED: 'true', GEMINI_API_KEY: 'test-key' };

// ---------------------------------------------------------------- release gate
assert.equal(isReleaseReady(READY_ENV), true);
assert.equal(isReleaseReady({ ...READY_ENV, TAMSOOD_RAG_PUBLIC_ENABLED: 'false' }), false, 'the switch must turn the chat off');
assert.equal(isReleaseReady({ ...READY_ENV, GEMINI_API_KEY: ' ' }), false, 'no key, no chat');
assert.equal(isReleaseReady({ ...READY_ENV, VERCEL_ENV: 'development' }), false);
assert.equal(manifest.knowledge_pack.content_sha256, pack.content_sha256,
  'the owner decision must cover exactly the bundled pack');
assert.equal(manifest.status, 'OWNER_APPROVED_PUBLIC_DEMO');
assert.ok(Object.values(manifest.release_gates).every(value => value === false),
  'unverified checks must not be recorded as passed');
assert.equal(pack.contains_company_report_values, false);
assert.doesNotMatch(JSON.stringify(pack.datasets), /thaioil|sprc\.co\.th|ijame/i,
  'company-report and non-released sources must not be in the answerable data');
assert.ok(pack.catalogue.some(item => item.id === 'company_reports' && item.answerable === false),
  'the catalogue still tells users that company reports exist');

// ----------------------------------------------------------------- query engine
const oilByYear = runQuery({ dataset: 'dmf_production', filters: [{ column: 'product', values: ['oil'] }],
  year_from: 2023, year_to: 2024, group_by: ['year'], aggregate: 'sum' });
assert.equal(oilByYear.aggregate, 'avg', 'DMF monthly values must not be added across months');
assert.match(oilByYear.notes.join(' '), /ไม่บวกข้ามเดือน/);
assert.deepEqual(oilByYear.rows.map(row => row.year), [2023, 2024]);
assert.ok(oilByYear.rows.every(row => row.unit === 'บาร์เรล' && row.months_with_data === 12));

const mixed = runQuery({ dataset: 'dmf_production', year_from: 2024, year_to: 2024, aggregate: 'avg' });
assert.equal(mixed.rows.length, 3, 'oil, condensate and gas have different units and stay separate');

const gasPeak = runQuery({ dataset: 'dmf_production', filters: [{ column: 'product', values: ['gas'] }],
  year_from: 2020, year_to: 2020, aggregate: 'max' });
assert.ok(gasPeak.rows[0].value < 100000, 'the flagged source value must not become the reported maximum');
assert.match(gasPeak.notes.join(' '), /ไม่นับค่า 3,500,000/, 'leaving a value out must be disclosed');

const intake = runQuery({ dataset: 'eppo_refinery_intake', year_from: 2024, year_to: 2024, group_by: ['year'], aggregate: 'sum' });
assert.equal(intake.aggregate, 'avg', 'barrels per day are averaged, never summed across months');
const diesel = runQuery({ dataset: 'eppo_product_output', filters: [{ column: 'product', values: ['diesel'] }],
  year_from: 2024, year_to: 2024, group_by: ['year'], aggregate: 'sum' });
assert.equal(diesel.aggregate, 'sum');
assert.equal(diesel.rows[0].unit, 'Million Litres');

const hfame = runQuery({ dataset: 'fame_inventory', filters: [{ column: 'process', values: ['H-FAME'] }], aggregate: 'list' });
assert.ok(hfame.rows.length > 0 && hfame.rows.every(row => row.process === 'H-FAME'), 'H-FAME must not also match FAME');
const unknownField = runQuery({ dataset: 'dmf_production', filters: [{ column: 'field', values: ['ไม่มีจริง'] }], aggregate: 'avg' });
assert.equal(unknownField.rows.length, 0);
assert.match(unknownField.notes[0], /ไม่พบแหล่งผลิต/);
assert.equal(runQuery({ dataset: 'company_reports', aggregate: 'list' }), null, 'withheld layers are not queryable');
const erawanGroup = runQuery({ dataset: 'dmf_production', filters: [{ column: 'product', values: ['gas'] },
  { column: 'field', values: ['เอราวัณ', 'กลุ่มเอราวัณ+'] }], year_from: 2017, year_to: 2017, group_by: ['year'], aggregate: 'avg' });
assert.match(erawanGroup.notes.join(' '), /นับจากชื่อในไฟล์ต้นทาง: กลุ่มเอราวัณ\+.*กลุ่มรวมหลายแหล่ง/,
  'a figure built from a group label must say so');
const erawanSingle = runQuery({ dataset: 'dmf_production', filters: [{ column: 'product', values: ['gas'] },
  { column: 'field', values: ['เอราวัณ'] }], year_from: 2024, year_to: 2024, group_by: ['year'], aggregate: 'avg' });
assert.equal(erawanSingle.notes.length, 0, 'a single exact field label needs no grouping note');
assert.ok(runQuery({ dataset: 'dmf_production', aggregate: 'list', limit: 9999 }).rows.length <= 40);

// -------------------------------------------------------------------- grounding
assert.equal(isGrounded('ปี 2567 (2024) เฉลี่ย 80,575.03 บาร์เรล', [{ year: 2024, value: 80575.03 }]), true);
assert.equal(isGrounded('ประมาณ 80,600 บาร์เรล', [{ year: 2024, value: 80575.03 }]), false, 'rounded figures are rejected');
assert.equal(isGrounded('เพิ่มขึ้น 21%', [{ value: 66493.89 }, { value: 80575.03 }]), false, 'model arithmetic is rejected');
assert.match(plainListing([oilByYear]), /80,575\.03 บาร์เรล/);

// ------------------------------------------------------------- request checking
assert.equal(validPayload({ question: 'สวัสดี', geminiConsent: true }), true);
assert.equal(validPayload({ question: 'x'.repeat(501) }), false);
assert.equal(validPayload({ question: 'ok', extra: 1 }), false);
assert.equal(validPayload({ question: 'ok', history: Array(5).fill({ question: 'a', answer: 'b' }) }), false);
assert.equal(validPayload({ question: 'ok', history: [{ question: 'a', answer: 'b', role: 'system' }] }), false);

rateBuckets.clear();
const limited = { headers: { 'x-forwarded-for': '203.0.113.9' } };
for (let index = 0; index < 10; index++) assert.equal(rateAllowed(limited, 1000), true);
assert.equal(rateAllowed(limited, 1000), false, 'the eleventh question in a minute waits');
assert.equal(rateAllowed(limited, 62_000), true);
assert.equal(rateAllowed({ headers: {} }, 1000), false, 'requests without a client address are refused');
rateBuckets.clear();

assert.match(PLANNER_INSTRUCTION, /company_reports \(แชตไม่คัดตัวเลขชุดนี้มาตอบ\)/);

// ------------------------------------------------------------------ mock Gemini
function geminiReply(object, status = 200) {
  const body = JSON.stringify({ candidates: [{ content: { parts: [{ text: JSON.stringify(object) }] } }] });
  return { ok: status >= 200 && status < 300, status, text: async () => body };
}
function scripted(...replies) {
  const calls = [];
  const fetchImpl = async (url, options) => {
    calls.push({ url, body: JSON.parse(options.body), headers: options.headers });
    const next = replies.shift();
    if (!next) throw new Error('unexpected model call');
    return next;
  };
  return { fetchImpl, calls };
}
const PLAN = { mode: 'data', queries: [{ dataset: 'dmf_production', filters: [{ column: 'product', values: ['oil'] }],
  year_from: 2024, year_to: 2024, group_by: ['year'], aggregate: 'avg' }] };

(async () => {
  // A data question: the model plans, code computes, the model words it.
  let mock = scripted(geminiReply(PLAN), geminiReply({ answer: 'ปี 2567 (2024) ไทยผลิตน้ำมันดิบเฉลี่ยเดือนละ 80,575.03 บาร์เรลครับ' }));
  let result = await answerQuestion('ปี 2567 ผลิตน้ำมันดิบเท่าไหร่', [], READY_ENV, mock.fetchImpl);
  assert.equal(result.summary.kind, 'answer');
  assert.match(result.summary.text, /80,575\.03/);
  assert.equal(result.hits[0].id, 'dmf_production');
  assert.match(result.hits[0].source_url, /^https:\/\/catalog\.dmf\.go\.th\//);
  assert.equal(result.tables[0].rows[0].value, 80575.03);
  assert.equal(mock.calls.length, 2);
  assert.equal(mock.calls[0].headers['x-goog-api-key'], 'test-key');
  assert.doesNotMatch(mock.calls[0].url, /key=/, 'the key travels in a header, never in the URL');
  assert.equal(mock.calls[1].body.contents[0].parts[0].text.includes('80575.03'), true,
    'the wording step receives the computed rows');

  // A reply with an invented number is replaced by a plain listing of the data.
  handler._internals.resetModelState();
  mock = scripted(geminiReply(PLAN), geminiReply({ answer: 'ประมาณ 81,000 บาร์เรลครับ' }));
  result = await answerQuestion('ปี 2567 ผลิตน้ำมันดิบเท่าไหร่', [], READY_ENV, mock.fetchImpl);
  assert.equal(result.summary.kind, 'plain-listing');
  assert.match(result.summary.text, /80,575\.03 บาร์เรล/);
  assert.doesNotMatch(result.summary.text, /81,000/);

  // A right number with the wrong unit is rejected too.
  const famePlan = { mode: 'data', queries: [{ dataset: 'fame_inventory', filters: [{ column: 'process', values: ['FAME'] }], aggregate: 'list' }] };
  handler._internals.resetModelState();
  mock = scripted(geminiReply(famePlan), geminiReply({ answer: 'ใช้ไฟฟ้า 0.52 กิโลกรัมครับ' }));
  result = await answerQuestion('FAME ใช้ไฟฟ้าเท่าไหร่', [], READY_ENV, mock.fetchImpl);
  assert.equal(result.summary.kind, 'plain-listing');
  assert.match(result.summary.fallback_reason, /unit_not_matching_data/);
  handler._internals.resetModelState();
  mock = scripted(geminiReply(famePlan), geminiReply({ answer: 'ใช้ไฟฟ้า 0.52 กิโลวัตต์ชั่วโมง และ Methanol 3.47 kg ครับ' }));
  result = await answerQuestion('FAME ใช้ไฟฟ้าเท่าไหร่', [], READY_ENV, mock.fetchImpl);
  assert.equal(result.summary.kind, 'answer');

  // A value the engine left out is disclosed even if the model forgets to.
  const gasPlan = { mode: 'data', queries: [{ dataset: 'dmf_production', filters: [{ column: 'product', values: ['gas'] }],
    year_from: 2020, year_to: 2020, aggregate: 'max' }] };
  handler._internals.resetModelState();
  mock = scripted(geminiReply(gasPlan), geminiReply({ answer: 'เดือนมีนาคมสูงสุดครับ' }));
  result = await answerQuestion('เดือนไหนผลิตก๊าซมากสุดปี 2563', [], READY_ENV, mock.fetchImpl);
  assert.match(result.summary.text, /หมายเหตุ: ไม่นับค่า 3,500,000/);

  // If the wording call fails twice, the data is still returned.
  handler._internals.resetModelState();
  mock = scripted(geminiReply(PLAN), geminiReply({}, 503), geminiReply({}, 503));
  result = await answerQuestion('ปี 2567 ผลิตน้ำมันดิบเท่าไหร่', [], READY_ENV, mock.fetchImpl);
  assert.equal(result.summary.kind, 'plain-listing');

  // An overloaded model is retried on the fallback model.
  handler._internals.resetModelState();
  mock = scripted(geminiReply({}, 503), geminiReply({ mode: 'chat', reply: 'สวัสดีครับ' }));
  result = await answerQuestion('สวัสดี', [], READY_ENV, mock.fetchImpl);
  assert.equal(result.summary.text, 'สวัสดีครับ');
  assert.match(mock.calls[0].url, /gemini-3\.5-flash-lite:generateContent/);
  assert.match(mock.calls[1].url, /gemini-3\.1-flash-lite:generateContent/);
  // ...and the next question goes straight to the fallback while the cooldown lasts.
  mock = scripted(geminiReply({ mode: 'chat', reply: 'สวัสดีครับ' }));
  await answerQuestion('สวัสดี', [], READY_ENV, mock.fetchImpl);
  assert.match(mock.calls[0].url, /gemini-3\.1-flash-lite:generateContent/);
  handler._internals.resetModelState();

  // One malformed planner reply is retried instead of failing the question.
  handler._internals.resetModelState();
  mock = scripted({ ok: true, status: 200, text: async () => 'not json' }, geminiReply({ mode: 'chat', reply: 'สวัสดีครับ' }));
  result = await answerQuestion('สวัสดี', [], READY_ENV, mock.fetchImpl);
  assert.equal(result.summary.text, 'สวัสดีครับ');
  assert.equal(mock.calls.length, 2);

  // Small talk and catalogue questions are answered in one call, without data.
  handler._internals.resetModelState();
  mock = scripted(geminiReply({ mode: 'chat', reply: 'สวัสดีครับ ถามเรื่องการผลิตน้ำมันดิบ ก๊าซธรรมชาติ หรือไบโอดีเซลได้เลยครับ' }));
  result = await answerQuestion('สวัสดี', [], READY_ENV, mock.fetchImpl);
  assert.equal(result.summary.kind, 'chat');
  assert.equal(result.hits.length, 0);
  assert.equal(mock.calls.length, 1);

  // A chat reply may not smuggle in statistics.
  handler._internals.resetModelState();
  mock = scripted(geminiReply({ mode: 'chat', reply: 'ไทยผลิตน้ำมันดิบ 987,654 บาร์เรลครับ' }));
  result = await answerQuestion('ผลิตเท่าไหร่', [], READY_ENV, mock.fetchImpl);
  assert.doesNotMatch(result.summary.text, /987,654/);

  // Notes: explanatory questions use the CC BY summaries with attribution.
  handler._internals.resetModelState();
  mock = scripted(geminiReply({ mode: 'notes', note_ids: ['fame-functional-unit', 'no-such-note'] }),
    geminiReply({ answer: 'หน่วยหน้าที่คือการใช้เชื้อเพลิง 1,000 MJ ครับ' }));
  result = await answerQuestion('หน่วยหน้าที่ของ FAME คืออะไร', [], READY_ENV, mock.fetchImpl);
  assert.equal(result.summary.kind, 'answer');
  assert.deepEqual(result.hits.map(hit => hit.id), ['fame-functional-unit']);
  assert.equal(result.hits[0].licence, 'CC BY 4.0');

  // Conversation history reaches the planner so follow-ups make sense.
  handler._internals.resetModelState();
  mock = scripted(geminiReply({ mode: 'chat', reply: 'ได้ครับ' }));
  await answerQuestion('แล้วปีก่อนล่ะ', [{ question: 'ปี 2567 ผลิตเท่าไหร่', answer: 'เฉลี่ย 80,575.03 บาร์เรล' }], READY_ENV, mock.fetchImpl);
  assert.match(mock.calls[0].body.contents[0].parts[0].text, /ปี 2567 ผลิตเท่าไหร่/);

  // The structured-output field is retried in another shape on HTTP 400.
  handler._internals.resetModelState();
  mock = scripted(geminiReply({}, 400), geminiReply({ answer: 'ok' }));
  const fallback = await callGemini('instruction', {}, { type: 'object' }, 50, READY_ENV, mock.fetchImpl);
  assert.equal(fallback.answer, 'ok');
  assert.notDeepEqual(mock.calls[1].body.generationConfig, mock.calls[0].body.generationConfig);
  await assert.rejects(callGemini('i', {}, {}, 50, READY_ENV, scripted({ ok: true, status: 200, text: async () => 'not json' }).fetchImpl),
    /invalid_model_response/);

  // ---------------------------------------------------------------- HTTP layer
  function request({ method = 'POST', headers = {}, body } = {}) {
    const req = new EventEmitter();
    req.method = method;
    req.headers = { host: 'tamsoodbase.vercel.app', origin: 'https://tamsoodbase.vercel.app',
      'content-type': 'application/json', 'x-forwarded-for': '198.51.100.7', ...headers };
    const res = { headers: {}, statusCode: 0, writableEnded: false,
      setHeader(name, value) { this.headers[name] = value; },
      end(text) { this.body = text; this.writableEnded = true; this.done(); } };
    const finished = new Promise(resolve => { res.done = resolve; });
    const run = handler(req, res);
    if (body !== undefined) process.nextTick(() => { req.emit('data', Buffer.from(body)); req.emit('end'); });
    return Promise.all([run, finished]).then(() => res);
  }
  const saved = { ...process.env };
  const realFetch = global.fetch;
  let modelCalls = 0;
  global.fetch = async () => { modelCalls++; return geminiReply({ mode: 'chat', reply: 'สวัสดีครับ' }); };
  try {
    Object.assign(process.env, { VERCEL_ENV: 'production', GEMINI_API_KEY: 'test-key' });
    delete process.env.TAMSOOD_RAG_PUBLIC_ENABLED;
    assert.equal((await request({ body: '{"question":"hi","geminiConsent":true}' })).statusCode, 503, 'closed unless switched on');
    process.env.TAMSOOD_RAG_PUBLIC_ENABLED = 'true';
    assert.equal((await request({ method: 'GET' })).statusCode, 405);
    assert.equal((await request({ headers: { origin: 'https://evil.example' }, body: '{}' })).statusCode, 403);
    assert.equal((await request({ headers: { 'content-type': 'text/plain' }, body: '{}' })).statusCode, 415);
    assert.equal((await request({ body: '{"question":""}' })).statusCode, 400);
    assert.equal((await request({ body: JSON.stringify({ question: 'x'.repeat(9000) }) })).statusCode, 413);
    assert.equal((await request({ body: '{"question":"สวัสดี"}' })).statusCode, 403, 'consent is required for every question');
    assert.equal(modelCalls, 0, 'nothing reaches the model before the checks pass');
    const ok = await request({ body: '{"question":"สวัสดี","geminiConsent":true}' });
    assert.equal(ok.statusCode, 200);
    assert.equal(JSON.parse(ok.body).summary.text, 'สวัสดีครับ');
    assert.equal(ok.headers['Cache-Control'], 'private, no-store');
    assert.equal(modelCalls, 1);
    global.fetch = async () => geminiReply({}, 500);
    const quiet = console.error;
    console.error = () => {};
    try { assert.equal((await request({ body: '{"question":"สวัสดี","geminiConsent":true}' })).statusCode, 503); }
    finally { console.error = quiet; }
    assert.equal((await request({ headers: { 'x-forwarded-for': undefined }, body: '{"question":"hi","geminiConsent":true}' })).statusCode, 429);
  } finally {
    global.fetch = realFetch;
    for (const key of Object.keys(process.env)) if (!(key in saved)) delete process.env[key];
    Object.assign(process.env, saved);
    rateBuckets.clear();
  }
  console.log('rag-vercel-api: ok');
})().catch(error => { console.error(error); process.exit(1); });
