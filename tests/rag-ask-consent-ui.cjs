const fs = require('node:fs');
const path = require('node:path');
const assert = require('node:assert/strict');

const root = path.resolve(__dirname, '..');
const page = fs.readFileSync(path.join(root, 'web/ask.html'), 'utf8');
const script = [...page.matchAll(/<script>([\s\S]*?)<\/script>/g)].at(-1)?.[1];

assert.ok(script, 'the RAG page must contain its inline interaction script');
assert.match(page, /<input id="gemini-consent" type="checkbox" disabled>/,
  'consent must be off and unavailable by default while RAG is closed');
assert.match(page, /ติ๊กครั้งเดียวใช้ได้ตลอดจนปิดแท็บ และยกเลิกได้ทุกเมื่อ/,
  'the Thai notice must say consent lasts for this tab and can be withdrawn');
assert.match(page, /บทสนทนาล่าสุดในแท็บนี้/,
  'the notice must disclose that recent conversation turns are sent as well');
assert.match(page, /เก็บคำถาม บริบท และคำตอบไว้ 55 วัน/,
  'the privacy notice must disclose the documented abuse-monitoring retention period');
assert.match(page, /ai\.google\.dev\/gemini-api\/docs\/usage-policies/,
  'the privacy notice must link to the official usage and retention policy');
assert.match(script, /sessionStorage\.(setItem|removeItem)\(CONSENT_KEY/,
  'consent is remembered per tab only (sessionStorage), never across browser sessions');
assert.doesNotMatch(script, /localStorage/, 'consent and conversation must not persist beyond the tab');

const submitHandler = script.slice(script.indexOf("form.addEventListener('submit'"));
assert.ok(submitHandler.startsWith("form.addEventListener('submit'"),
  'the form submit handler must exist');
const guard = submitHandler.indexOf('if (!asked || !consent.checked || busy) return;');
const request = submitHandler.indexOf("fetch('/api/rag/ask'");
assert.ok(guard >= 0 && request > guard,
  'the consent guard must run before the network request');
assert.match(submitHandler, /geminiConsent:\s*consent\.checked/,
  'the server request must carry the explicit consent state');
assert.match(submitHandler, /history:\s*history\.slice\(-MAX_HISTORY_TURNS\)/,
  'only a bounded number of recent turns may be sent');
assert.equal((script.match(/fetch\('\/api\/rag\/ask'/g) || []).length, 1,
  'there must be exactly one chat request callsite covered by the consent guard');
assert.match(script, /history\.length = 0/, 'clearing the screen must also forget the conversation');

console.log('RAG ask-page consent contract passed (static source assertions only).');
