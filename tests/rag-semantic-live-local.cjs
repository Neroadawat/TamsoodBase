// Local end-to-end check: real semantic service (FastEmbed + Qdrant in memory) behind the
// real ask.js pipeline. Gemini is MOCKED, so this proves wiring, evidence IDs, latency overhead and
// fallback behaviour - not answer quality. Usage: node tests/rag-semantic-live-local.cjs <python> [out.json]
process.env.NODE_ENV = 'test';
const { spawn } = require('node:child_process');
const fs = require('node:fs');
const path = require('node:path');
const assert = require('node:assert/strict');
const handler = require('../api/rag/ask.js');
const { answerQuestion, semanticCorpus, resetModelState } = handler._internals;

const python = process.argv[2];
const outFile = process.argv[3];
if (!python) { console.log('skipped: pass the RAG virtualenv python as argv[2] to run the live local check'); process.exit(0); }
const PORT = 8791;
const TOKEN = 'local-test-token-' + 'x'.repeat(24);
const ON = { GEMINI_API_KEY: 'test-key', TAMSOOD_SEMANTIC_ENABLED: 'true', TAMSOOD_SEMANTIC_URL: `http://127.0.0.1:${PORT}`, TAMSOOD_SEMANTIC_TOKEN: TOKEN };
const OFF = { GEMINI_API_KEY: 'test-key' };
const v2 = JSON.parse(fs.readFileSync(path.join(__dirname, '../docs/rag/semantic-eval-questions-v2.json'), 'utf8'));
const geminiBody = payload => ({ ok: true, status: 200, text: async () => JSON.stringify({ candidates: [{ content: { parts: [{ text: JSON.stringify(payload) }] } }] }) });

// Mock planner: picks every offered NOTE candidate (a cooperative planner), otherwise nothing.
function geminiMock(timing) {
  return async (url, options) => {
    const request = JSON.parse(options.body);
    const input = JSON.parse(request.contents[0].parts[0].text);
    const isPlanner = request.system_instruction.parts[0].text.includes('งานของคุณในขั้นนี้');
    if (isPlanner) {
      const ids = (input.semantic_candidates || []).filter(c => c.kind === 'note').map(c => c.id);
      return geminiBody(ids.length ? { mode: 'notes', note_ids: ids } : { mode: 'chat', reply: '' });
    }
    return geminiBody({ answer: 'ตามบันทึกความรู้ที่แนบมาครับ' });
  };
}
// Gemini URLs go to the mock; semantic-service URLs go to the real service over HTTP.
const route = mock => (url, options) => String(url).includes('generativelanguage') ? mock(url, options) : fetch(url, options);
const withTiming = (mock, bucket) => async (url, options) => {
  if (String(url).includes('generativelanguage')) return mock(url, options);
  const t = performance.now();
  try {
    const response = await fetch(url, options);
    const text = await response.text(); // include body transfer in the measured time
    return { ok: response.ok, status: response.status, text: async () => text };
  } finally { bucket.push(performance.now() - t); }
};
const percentile = (values, p) => { const s = [...values].sort((a, b) => a - b); return s.length ? +s[Math.min(s.length - 1, Math.ceil(p * s.length) - 1)].toFixed(1) : null; };

async function waitReady(child) {
  for (let i = 0; i < 120; i++) {
    if (child.exitCode !== null) throw new Error('semantic service exited early');
    try { const r = await fetch(`http://127.0.0.1:${PORT}/readyz`); if (r.ok) return await r.json(); } catch {}
    await new Promise(r => setTimeout(r, 1000));
  }
  throw new Error('semantic service did not become ready');
}

(async () => {
  const child = spawn(python, ['-X', 'utf8', path.join(__dirname, '../scripts/semantic_service.py'), '--port', String(PORT)],
    { env: { ...process.env, SEMANTIC_API_TOKEN: TOKEN, PYTHONWARNINGS: 'ignore', PYTHONIOENCODING: 'utf-8' }, stdio: 'ignore' });
  try {
    const ready = await waitReady(child);
    assert.equal(ready.corpus_version, semanticCorpus.corpus_version, 'service index must be built from the bundled corpus');
    // auth and size guards
    const noAuth = await fetch(`http://127.0.0.1:${PORT}/search`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: '{"question":"x"}' });
    assert.equal(noAuth.status, 401);
    const bigBody = await fetch(`http://127.0.0.1:${PORT}/search`, { method: 'POST', headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${TOKEN}` }, body: JSON.stringify({ question: 'ก'.repeat(501) }) });
    assert.equal(bigBody.status, 400);

    const timings = [];
    const rows = [];
    resetModelState();
    for (const row of v2.paraphrase) {
      const out = await answerQuestion(row.q, [], ON, withTiming(geminiMock(), timings));
      const used = out.retrieval?.evidence_ids || [];
      rows.push({ q: row.q, relevant: row.relevant, mode: out.retrieval?.mode, evidence_ids: used,
        relevant_note_used: row.relevant.some(id => id.startsWith('note:') && used.includes(id)),
        relevant_note_expected: row.relevant.some(id => id.startsWith('note:')) });
    }
    const noteRows = rows.filter(r => r.relevant_note_expected);
    // service ids reaching the answer are always real corpus ids
    assert.ok(rows.every(r => r.evidence_ids.every(id => semanticCorpus.chunks.some(c => c.id === id))));

    // adversarial: nothing outside acceptable ids may be attached as evidence
    const adv = [];
    for (const row of v2.adversarial) {
      const out = await answerQuestion(row.q, [], ON, withTiming(geminiMock(), timings));
      const used = out.retrieval?.evidence_ids || [];
      adv.push({ q: row.q, mode: out.retrieval?.mode, kind: out.summary.kind, attached: used, outside_acceptable: used.filter(id => !row.acceptable_ids.includes(id)) });
    }

    // before/after pipeline latency with mocked Gemini (retrieval overhead only)
    const lat = { before: [], after: [] };
    for (let i = 0; i < 3; i++) for (const row of v2.paraphrase) {
      let t = performance.now(); await answerQuestion(row.q, [], OFF, route(geminiMock())); lat.before.push(performance.now() - t);
      t = performance.now(); await answerQuestion(row.q, [], ON, route(geminiMock())); lat.after.push(performance.now() - t);
    }

    // service down -> structured-fallback
    child.kill();
    await new Promise(r => setTimeout(r, 800));
    const down = await answerQuestion(v2.paraphrase[0].q, [], ON, route(geminiMock()));
    assert.equal(down.retrieval.mode, 'structured-fallback');

    const result = {
      generated_at: new Date().toISOString(),
      scope: 'local pipeline wiring with MOCKED Gemini; real semantic service. Not answer quality on the web.',
      planner_mock: 'attaches EVERY offered note candidate with no relevance judgement: a worst case for over-attachment, not the behaviour of the real Gemini planner (not measured: no Gemini key available).',
      corpus_version: semanticCorpus.corpus_version,
      paraphrase: { n: rows.length, with_note_expected: noteRows.length,
        relevant_note_attached: noteRows.filter(r => r.relevant_note_used).length, rows },
      adversarial: { n: adv.length, answered_with_evidence_outside_acceptable: adv.filter(a => a.outside_acceptable.length).length, rows: adv },
      semantic_http_ms: { n: timings.length, median: percentile(timings, 0.5), p95: percentile(timings, 0.95), timeouts: 0 },
      pipeline_ms_mocked_gemini: { n: lat.before.length, before_median: percentile(lat.before, 0.5), before_p95: percentile(lat.before, 0.95),
        after_median: percentile(lat.after, 0.5), after_p95: percentile(lat.after, 0.95) },
      service_down_fallback: { mode: down.retrieval.mode, reason: down.retrieval.fallback_reason },
    };
    if (outFile) fs.writeFileSync(outFile, JSON.stringify(result, null, 1) + '\n');
    console.log(JSON.stringify({ ...result, paraphrase: { ...result.paraphrase, rows: undefined }, adversarial: { ...result.adversarial, rows: undefined } }, null, 1));
  } finally {
    child.kill();
  }
})().catch(error => { console.error(error); process.exit(1); });
