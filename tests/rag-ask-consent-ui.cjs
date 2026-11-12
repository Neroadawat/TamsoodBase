const fs = require('node:fs');
const path = require('node:path');
const assert = require('node:assert/strict');

const root = path.resolve(__dirname, '..');
const page = fs.readFileSync(path.join(root, 'web/ask.html'), 'utf8');
const script = [...page.matchAll(/<script>([\s\S]*?)<\/script>/g)].at(-1)?.[1];

assert.ok(script, 'the RAG page must contain its inline interaction script');
assert.match(page, /<input id="gemini-consent" type="checkbox" disabled>/,
  'consent must be off and unavailable by default while RAG is closed');
assert.match(page, /ขอความยินยอมใหม่ทุกครั้ง/,
  'the Thai notice must explain that consent is requested for every question');
assert.match(page, /เก็บคำถาม บริบท และคำตอบไว้ 55 วัน/,
  'the privacy notice must disclose the documented abuse-monitoring retention period');
assert.match(page, /ai\.google\.dev\/gemini-api\/docs\/usage-policies/,
  'the privacy notice must link to the official usage and retention policy');
assert.match(script, /summary\?\.kind === 'grounding-abstention'/,
  'a rejected numeric answer must render the friendly no-answer state instead of an outage message');

const submitHandler = script.slice(script.indexOf("form.addEventListener('submit'"));
assert.ok(submitHandler.startsWith("form.addEventListener('submit'"),
  'the form submit handler must exist');
const guard = submitHandler.indexOf('if (!asked || !consent.checked || submit.disabled) return;');
const request = submitHandler.indexOf("fetch('/api/rag/ask'");
assert.ok(guard >= 0 && request > guard,
  'the consent and enabled-state guard must run before the network request');
assert.match(submitHandler, /body:\s*JSON\.stringify\(\{question:\s*asked,\s*geminiConsent:\s*consent\.checked\}\)/,
  'the server request must carry the explicit consent state');
assert.match(submitHandler, /finally\s*\{[\s\S]*?consent\.checked\s*=\s*false;[\s\S]*?syncSubmitState\(\);/,
  'consent must reset after both a successful request and a failure');
assert.equal((script.match(/fetch\('\/api\/rag\/ask'/g) || []).length, 1,
  'there must be exactly one RAG request callsite covered by the consent guard');

console.log('RAG ask-page consent contract passed (static source assertions only).');
