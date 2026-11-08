// Execute the real page script against controlled responses; no server or feedback writes.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const page = fs.readFileSync(require('node:path').join(__dirname, '../scripts/rag_demo.html'), 'utf8');
const script = page.match(/<script>([\s\S]*?)<\/script>/)[1];

function harness() {
  class Element {
    constructor() { this.handlers = {}; this.value = ''; this.disabled = false; this.readOnly = false; this.textContent = ''; this.attributes = {}; this.children = []; }
    addEventListener(name, callback) { this.handlers[name] = callback; }
    submit() { return this.handlers.submit({preventDefault() {}}); }
    focus() { document.activeElement = this; }
    setAttribute(name, value) { this.attributes[name] = value; }
    append(...children) { this.children.push(...children); }
    replaceChildren() { this.children = []; }
    querySelector(name) { assert.equal(name, 'button'); return this.button; }
    requestSubmit() { return this.submit(); }
  }
  const form = new Element(); form.button = new Element();
  const ids = Object.fromEntries(['question', 'status', 'results', 'review', 'review-status', 'verdict', 'note', 'searched-question'].map(id => [id, new Element()]));
  ids.review.button = new Element();
  const examples = Array.from({length: 5}, () => new Element());
  const document = {
    querySelector(selector) { return selector === 'form:not(#review)' ? form : ids[selector.slice(1)]; },
    querySelectorAll(selector) { assert.equal(selector, '.examples button'); return examples; },
    createElement() { return new Element(); },
  };
  const timers = new Map(); let timerId = 0; let nextSearchId = 'fixture-A';
  const requests = []; const reviewQueue = [];
  const fetch = async (path, options) => {
    const request = {path, payload: JSON.parse(options.body), signal: options.signal}; requests.push(request);
    if (path === '/ask') return {ok: true, json: async () => ({hits: [], search_id: nextSearchId})};
    assert.equal(path, '/review');
    return new Promise((resolve, reject) => {
      request.resolve = (saved = true) => resolve({ok: true, json: async () => ({saved})});
      request.reject = reject;
      // Tests may deliberately ignore cancellation to exercise late response protection.
      request.followAbort = () => options.signal?.addEventListener('abort', () => reject(Object.assign(new Error('deadline'), {name: 'AbortError'})), {once: true});
      reviewQueue.push(request);
    });
  };
  vm.runInNewContext(script, {document, fetch, AbortController,
    setTimeout(callback, ms) { assert.equal(ms, 12000); const id = ++timerId; timers.set(id, callback); return id; },
    clearTimeout(id) { timers.delete(id); },
  });
  return {form, ids, requests, reviewQueue, timers,
    async search(id) { nextSearchId = id; ids.question.value = 'คำถามทดสอบเฉพาะ fixture'; await form.submit(); },
    deadline() { assert.equal(timers.size, 1); [...timers.values()][0](); },
  };
}

(async () => {
  // A late confirmation for A must not clear B's feedback token or change B's status.
  {
    const h = harness(); await h.search('fixture-A');
    const old = h.ids.review.submit(); const a = h.reviewQueue[0];
    await h.search('fixture-B'); a.resolve(); await old;
    assert.equal(h.ids['review-status'].textContent, '');
    const current = h.ids.review.submit(); const b = h.reviewQueue[1];
    assert.ok(b, 'late A response must not consume the newer B search token');
    assert.equal(b.payload.search_id, 'fixture-B'); b.resolve(); await current;
    assert.match(h.ids['review-status'].textContent, /บันทึกแล้ว/);
    assert.equal(h.timers.size, 0);
  }
  // A late error for A must not replace the success message for B or unlock its form.
  {
    const h = harness(); await h.search('fixture-A');
    const old = h.ids.review.submit(); const a = h.reviewQueue[0];
    await h.search('fixture-B'); const current = h.ids.review.submit(); const b = h.reviewQueue[1];
    b.resolve(); await current; a.reject(new Error('old connection failed')); await old;
    assert.match(h.ids['review-status'].textContent, /บันทึกแล้ว/);
    assert.equal(h.ids.review.button.disabled, true);
    assert.equal(h.timers.size, 0);
  }
  // Timeout restores the current form; retry is still bound to the same search.
  {
    const h = harness(); await h.search('fixture-A');
    const pending = h.ids.review.submit(); const a = h.reviewQueue[0]; a.followAbort();
    assert.equal(h.ids.note.readOnly, true); assert.equal(h.ids.verdict.disabled, true);
    h.deadline(); await pending;
    assert.equal(h.ids.review.button.disabled, false);
    assert.equal(h.ids.note.readOnly, false); assert.equal(h.ids.verdict.disabled, false);
    assert.match(h.ids['review-status'].textContent, /ยืนยัน.*ไม่ได้/);
    const retry = h.ids.review.submit(); const b = h.reviewQueue[1];
    assert.equal(b.payload.search_id, 'fixture-A'); b.resolve(); await retry;
    assert.equal(h.timers.size, 0);
  }
  // Duplicate clicks send one request; a new search aborts it and restores the new form.
  {
    const h = harness(); await h.search('fixture-A');
    const old = h.ids.review.submit(); const a = h.reviewQueue[0]; a.followAbort();
    await h.ids.review.submit(); assert.equal(h.reviewQueue.length, 1);
    await h.search('fixture-B'); await old;
    assert.equal(a.signal.aborted, true); assert.equal(h.ids.review.hidden, false);
    assert.equal(h.ids.review.button.disabled, false);
    assert.equal(h.ids.note.readOnly, false); assert.equal(h.ids.verdict.disabled, false);
    assert.equal(h.ids['review-status'].textContent, ''); assert.equal(h.timers.size, 0);
  }
  // HTTP 200 without the server's saved=true acknowledgment cannot claim success.
  {
    const h = harness(); await h.search('fixture-A');
    const pending = h.ids.review.submit(); h.reviewQueue[0].resolve(false); await pending;
    assert.doesNotMatch(h.ids['review-status'].textContent, /บันทึกแล้ว/);
    assert.equal(h.ids.review.button.disabled, false);
    const retry = h.ids.review.submit(); h.reviewQueue[1].resolve(); await retry;
    assert.match(h.ids['review-status'].textContent, /บันทึกแล้ว/);
    assert.equal(h.timers.size, 0);
  }
  console.log('RAG UI: five delayed-response, deadline, retry and acknowledgment scenarios passed; no real requests or feedback writes');
})().catch(error => { console.error(error); process.exitCode = 1; });
