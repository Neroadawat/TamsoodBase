// Vercel-native RAG: retrieve only from the allowlisted corpus bundled with
// this function, then call Gemini from the server. No EC2 route is used.
const { URL } = require('node:url');
const manifest = require('../../docs/rag/public-release-manifest.json');
const previewCorpus = require('../../docs/rag/vercel-preview-corpus.json');

const MAX_REQUEST_BYTES = 2048;
const MAX_QUESTION_CHARS = 500;
const MAX_RESPONSE_BYTES = 48 * 1024;
const MAX_EVIDENCE = 4;
const DEADLINE_MS = 18000;
const MODEL = 'gemini-3.5-flash-lite';
const REQUIRED_GATES = [
  'source_rights_cleared',
  'rate_limit_and_cost_controls_verified',
  'public_user_evaluation_complete',
  'capacity_and_monitoring_accepted',
  'privacy_notice_and_data_retention_reviewed',
  'rollback_owner_and_drill_recorded',
];
const previewRateBuckets = new Map();
const PREVIEW_RATE_WINDOW_MS = 60_000;
const PREVIEW_RATE_LIMIT = 12;
const PREVIEW_RATE_BUCKET_LIMIT = 2048;
const PREVIEW_RATE_SWEEP_INTERVAL_MS = 10_000;
let previewRateLastSweepAt = 0;
const SCOPE_ANCHORS = [
  'e10', 'e-10', 'ethanol', 'เอทานอล', 'co2e', 'co₂e', 'co2', 'คาร์บอนไดออกไซด์',
  'tsm', 'thai sugar', 'fame', 'h-fame', 'ฮีดรอฟาเม', 'palm', 'ปาล์ม', 'ffb', 'cpo', 'rbdpo',
  'methane', 'มีเทน', 'biogas', 'ไบโอแก๊ส', 'bagasse', 'ชานอ้อย', 'กากอ้อย', 'ไอน้ำ',
  'lci', 'วัฏจักรชีวิต', 'หน่วยหน้าที่', 'functional unit', 'allocation', 'จัดสรร', 'inventory',
];

function fail(res, status, message) {
  if (res.writableEnded) return;
  res.statusCode = status;
  res.setHeader('Content-Type', 'application/json; charset=utf-8');
  res.end(JSON.stringify({ error: message }));
}

function parseHttpsOrigin(value) {
  try {
    const url = new URL(value || '');
    if (url.protocol !== 'https:' || !url.hostname || url.username || url.password
      || url.port || url.pathname !== '/' || url.search || url.hash) return null;
    return url.origin;
  } catch { return null; }
}

function isReleaseReady(env = process.env) {
  if (env.VERCEL_ENV === 'preview') {
    if (env.TAMSOOD_RAG_PREVIEW_ENABLED !== 'true') return false;
    return env.TAMSOOD_GEMINI_DATA_PROCESSING_ACCEPTED === 'true'
      && Boolean((env.GEMINI_API_KEY || '').trim())
      && Boolean(parseHttpsOrigin(`https://${env.VERCEL_URL || ''}`))
      && previewCorpus.scope === 'LIMITED_VERCEL_PREVIEW_CC_BY_4_0_NARRATIVE_ONLY'
      && previewCorpus.records.length === 6
      && previewCorpus.records.every(row => row.licence === 'CC BY 4.0'
        && row.licence_url === 'https://creativecommons.org/licenses/by/4.0/'
        && row.attribution && row.source_url === 'https://doi.org/10.3390/su12229415');
  }
  if (env.VERCEL_ENV !== 'production') return false;
  const gateRefs = [
    'TAMSOOD_RAG_RIGHTS_CLEARANCE_REF',
    'TAMSOOD_RAG_RATE_LIMIT_POLICY_ID',
    'TAMSOOD_RAG_PRIVACY_REVIEW_REF',
    'TAMSOOD_RAG_UAT_REF',
  ];
  return env.TAMSOOD_RAG_PUBLIC_ENABLED === 'true'
    && env.TAMSOOD_GEMINI_DATA_PROCESSING_ACCEPTED === 'true'
    && Boolean((env.GEMINI_API_KEY || '').trim())
    && gateRefs.every(name => Boolean((env[name] || '').trim()))
    && Boolean(parseHttpsOrigin(env.TAMSOOD_RAG_PUBLIC_ORIGIN))
    && manifest.status === 'APPROVED_FOR_PUBLIC_RELEASE'
    && manifest.publicly_usable === true
    && manifest.public_release_allowed === true
    && manifest.external_llm_allowed === true
    && manifest.narrative_cards.every(row => row.release_allowed === true && row.rights_review === 'CLEARED')
    && manifest.statistical_facts.every(row => row.release_allowed === true && row.rights_review === 'CLEARED')
    && REQUIRED_GATES.every(name => manifest.release_gates?.[name] === true);
}

function readBody(req) {
  return new Promise((resolve, reject) => {
    const chunks = [];
    let size = 0;
    let tooLarge = false;
    req.on('data', chunk => {
      if (tooLarge) return;
      size += chunk.length;
      if (size > MAX_REQUEST_BYTES) {
        tooLarge = true;
        chunks.length = 0;
      } else chunks.push(chunk);
    });
    req.on('end', () => tooLarge ? reject(new Error('too_large')) : resolve(Buffer.concat(chunks)));
    req.on('error', () => reject(new Error('request_error')));
    req.on('aborted', () => reject(new Error('request_aborted')));
  });
}

function previewRateAllowed(req, now = Date.now()) {
  const forwarded = req.headers['x-forwarded-for'];
  const address = typeof forwarded === 'string' ? forwarded.split(',')[0].trim() : '';
  if (!address || address.length > 64) return false;
  const previous = previewRateBuckets.get(address);
  if (!previous || now - previous.startedAt >= PREVIEW_RATE_WINDOW_MS) {
    if (!previous && previewRateBuckets.size >= PREVIEW_RATE_BUCKET_LIMIT) {
      if (now - previewRateLastSweepAt >= PREVIEW_RATE_SWEEP_INTERVAL_MS) {
        previewRateLastSweepAt = now;
        for (const [key, bucket] of previewRateBuckets) {
          if (now - bucket.startedAt >= PREVIEW_RATE_WINDOW_MS) previewRateBuckets.delete(key);
        }
      }
      if (previewRateBuckets.size >= PREVIEW_RATE_BUCKET_LIMIT) return false;
    }
    previewRateBuckets.set(address, { startedAt: now, count: 1 });
    return true;
  }
  if (previous.count >= PREVIEW_RATE_LIMIT) return false;
  previous.count++;
  return true;
}

function normalize(value) {
  return String(value || '').normalize('NFKC').toLocaleLowerCase('th');
}

// Character bigrams keep Thai words searchable without shipping an embedding
// model or a database to a short-lived serverless function.
function terms(value) {
  const compact = normalize(value).replace(/[^\p{L}\p{N}]+/gu, ' ').trim();
  const out = new Set(compact.split(/\s+/u).filter(word => word.length > 1));
  const thaiRuns = compact.match(/[ก-๙]{2,}/gu) || [];
  for (const run of thaiRuns) {
    for (let i = 0; i < run.length - 1; i++) out.add(run.slice(i, i + 2));
  }
  return out;
}

function evidenceRows() {
  return previewCorpus.records.map(card => ({
    id: card.id,
    title: card.title,
    text: card.text,
    locator: card.locator,
    source_url: card.source_url,
    attribution: card.attribution,
    licence: card.licence,
    licence_url: card.licence_url,
    kind: 'licensed-narrative',
  }));
}

function isCorpusOverviewQuestion(value) {
  const question = normalize(value);
  const compact = question.replace(/\s+/gu, '');
  return [
    'ทำอะไรได้บ้าง', 'ทำอะไรได้', 'ช่วยอะไรได้บ้าง', 'ช่วยอะไรได้', 'ทำอะไรบ้าง',
    'ถามอะไรได้บ้าง', 'ความสามารถ', 'มีข้อมูลอะไรบ้าง', 'มีข้อมูลอะไร', 'มีข้อมูลไรบ้าง',
    'มีข้อมูลไร', 'ข้อมูลอะไรบ้าง', 'ข้อมูลอะไรในระบบ', 'มีอะไรในระบบ', 'มีเอกสารอะไร',
    'มีเนื้อหาอะไร', 'ชุดข้อมูลอะไร',
  ].some(phrase => compact.includes(normalize(phrase).replace(/\s+/gu, '')))
    || ['what can you do', 'what data do you have', 'what information do you have', 'what do you know']
      .some(phrase => question.includes(phrase));
}

function corpusOverview() {
  const hits = evidenceRows();
  return {
    summary: {
      text: 'ตอนนี้แชต Preview ค้นได้จากบทความ Permpool, Ghani และ Gheewala (2020) เพียง 1 บทความ ซึ่งสรุปไว้ 6 ประเด็น: หน่วยหน้าที่ 1,000 MJ ของ FAME/H-FAME, ฐานผลิตภัณฑ์ต้นน้ำ FFB/CPO/RBDPO ที่ 1,000 kg, แถว Land seeding ที่พักไว้เพราะไม่มีหน่วย, ช่องว่างข้อมูล FFB input ของโรงสกัด CPO, ข้อควรระวังเรื่อง allocation FAME/กลีเซอรีน และช่วงปีที่วัดข้อมูลซึ่งยังไม่ระบุ\n\nฉันช่วยสรุปหรืออธิบายประเด็นเหล่านี้ เปรียบเทียบฐานข้อมูล และชี้ข้อจำกัดพร้อมตำแหน่งอ้างอิงได้ ชุด Preview นี้ยังไม่ใช่คลังข้อมูลทั้งหมดของโครงการ และไม่มีสถิติ NSO หรือข้อมูล TSM/เอทานอลในชุดค้นนี้ หากถามนอกขอบเขต ฉันควรแจ้งว่ายังไม่มีหลักฐาน แทนการเดาคำตอบ',
      source_ids: hits.map(hit => hit.id),
      kind: 'corpus-overview',
    },
    hits,
  };
}

function retrieve(question, limit = MAX_EVIDENCE) {
  const normalizedQuestion = normalize(question);
  if (!SCOPE_ANCHORS.some(anchor => normalizedQuestion.includes(normalize(anchor)))) return [];
  const query = terms(question);
  if (!query.size) return [];
  const rows = evidenceRows().map(row => ({ ...row, docTerms: terms(`${row.title} ${row.text} ${row.search_text || ''}`) }));
  const documentFrequency = new Map();
  for (const row of rows) for (const term of row.docTerms) documentFrequency.set(term, (documentFrequency.get(term) || 0) + 1);
  const weight = term => Math.log(1 + rows.length / (1 + (documentFrequency.get(term) || 0)));
  const totalQueryWeight = [...query].reduce((sum, term) => sum + weight(term), 0) || 1;
  const scored = rows.map(row => {
    let overlap = 0;
    let matchedWeight = 0;
    for (const term of query) if (row.docTerms.has(term)) { overlap++; matchedWeight += weight(term); }
    const coverage = matchedWeight / totalQueryWeight;
    const precision = matchedWeight / Math.max(1, [...row.docTerms].reduce((sum, term) => sum + weight(term), 0));
    const phrases = normalize(`${row.title} ${row.text} ${row.search_text || ''}`);
    const exactPhraseBoost = query.size && [...query].some(term => term.length > 5 && phrases.includes(term)) ? 0.12 : 0;
    const score = (2 * coverage * precision) / Math.max(0.001, coverage + precision) + exactPhraseBoost;
    const aliasPhraseBoost = row.kind === 'licensed-narrative' && normalizedQuestion.includes(normalize(row.title)) ? 0.7 : 0;
    return { ...row, score: score + aliasPhraseBoost, overlap, coverage };
  }).filter(row => row.overlap >= 2 && row.coverage >= 0.22 && row.score >= 0.018)
    .sort((a, b) => b.score - a.score || a.id.localeCompare(b.id));
  return scored.slice(0, limit).map(({ score, overlap, coverage, search_text, aliases, docTerms, ...row }) => row);
}

function parseGeminiAnswer(payload, allowedIds) {
  const parts = payload?.candidates?.[0]?.content?.parts;
  const raw = Array.isArray(parts) ? parts.map(part => part.text || '').join('').trim() : '';
  if (!raw || raw.length > MAX_RESPONSE_BYTES) throw new Error('invalid_model_response');
  let parsed;
  try { parsed = JSON.parse(raw); } catch { throw new Error('invalid_model_response'); }
  if (!parsed || typeof parsed.answer !== 'string' || !parsed.answer.trim()
    || parsed.answer.length > 3500 || !Array.isArray(parsed.source_ids)
    || parsed.source_ids.length < 1 || parsed.source_ids.length > MAX_EVIDENCE
    || parsed.source_ids.some(id => typeof id !== 'string' || !allowedIds.has(id))
    || new Set(parsed.source_ids).size !== parsed.source_ids.length) {
    throw new Error('invalid_model_response');
  }
  return { text: parsed.answer.trim(), source_ids: parsed.source_ids };
}

async function callGemini(question, hits, env = process.env, fetchImpl = fetch) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), DEADLINE_MS);
  const endpoint = `https://generativelanguage.googleapis.com/v1beta/models/${MODEL}:generateContent`;
  const evidence = hits.map(({ id, title, text, locator, attribution, licence }) => ({ id, title, text, locator, attribution, licence }));
  try {
    const response = await fetchImpl(endpoint, {
      method: 'POST',
      signal: controller.signal,
      headers: { 'Content-Type': 'application/json', 'x-goog-api-key': env.GEMINI_API_KEY },
      body: JSON.stringify({
        system_instruction: { parts: [{ text: 'ตอบเป็นภาษาไทยให้ตรงคำถาม ใช้เฉพาะ EVIDENCE ที่ให้มา ห้ามเติมข้อเท็จจริงหรือตัวเลขจากความจำ ถ้าหลักฐานไม่พอให้บอกข้อจำกัดและอ้างเฉพาะหลักฐานที่รองรับ ส่งคำตอบเป็น JSON ตาม schema เท่านั้น source_ids ต้องเป็น id ของหลักฐานที่ใช้จริง' }] },
        contents: [{ role: 'user', parts: [{ text: JSON.stringify({ question, evidence }) }] }],
        generationConfig: {
          temperature: 0.2,
          maxOutputTokens: 700,
          responseMimeType: 'application/json',
          responseSchema: {
            type: 'OBJECT',
            properties: {
              answer: { type: 'STRING' },
              source_ids: { type: 'ARRAY', items: { type: 'STRING' } },
            },
            required: ['answer', 'source_ids'],
          },
        },
      }),
    });
    if (!response.ok) throw new Error('model_unavailable');
    const length = Number(response.headers.get('content-length') || 0);
    if (length > MAX_RESPONSE_BYTES) throw new Error('model_response_too_large');
    const text = await response.text();
    if (Buffer.byteLength(text, 'utf8') > MAX_RESPONSE_BYTES) throw new Error('model_response_too_large');
    const payload = JSON.parse(text);
    return parseGeminiAnswer(payload, new Set(hits.map(hit => hit.id)));
  } finally {
    clearTimeout(timer);
  }
}

async function handler(req, res) {
  res.setHeader('Cache-Control', 'private, no-store');
  res.setHeader('X-Content-Type-Options', 'nosniff');
  res.setHeader('Referrer-Policy', 'no-referrer');

  if (req.method !== 'POST') {
    res.setHeader('Allow', 'POST');
    return fail(res, 405, 'Method not allowed');
  }
  if (!isReleaseReady()) return fail(res, 503, 'Evidence search is not available on the public website yet');
  if (process.env.VERCEL_ENV === 'preview' && !previewRateAllowed(req)) {
    res.setHeader('Retry-After', '60');
    return fail(res, 429, 'Too many questions; wait a minute and try again');
  }
  const expectedOrigin = process.env.VERCEL_ENV === 'preview'
    ? parseHttpsOrigin(`https://${process.env.VERCEL_URL || ''}`)
    : parseHttpsOrigin(process.env.TAMSOOD_RAG_PUBLIC_ORIGIN);
  if (req.headers.origin !== expectedOrigin) {
    return fail(res, 403, 'Origin not allowed');
  }
  if (!(req.headers['content-type'] || '').toLowerCase().startsWith('application/json')) {
    return fail(res, 415, 'JSON is required');
  }
  if (req.headers['content-length'] !== undefined) {
    const declaredLength = Number(req.headers['content-length']);
    if (!Number.isInteger(declaredLength) || declaredLength < 1 || declaredLength > MAX_REQUEST_BYTES) {
      return fail(res, 413, 'Question is too large');
    }
  }

  let payload;
  try {
    const body = await readBody(req);
    payload = JSON.parse(body.toString('utf8'));
    if (!payload || typeof payload !== 'object' || Array.isArray(payload)
      || Object.keys(payload).length !== 1 || typeof payload.question !== 'string'
      || !payload.question.trim() || payload.question.trim().length > MAX_QUESTION_CHARS) {
      throw new Error('invalid_question');
    }
  } catch (error) {
    return fail(res, error.message === 'too_large' ? 413 : 400, 'Invalid question');
  }

  if (isCorpusOverviewQuestion(payload.question.trim())) {
    const overview = corpusOverview();
    res.statusCode = 200;
    res.setHeader('Content-Type', 'application/json; charset=utf-8');
    return res.end(JSON.stringify(overview));
  }

  const hits = retrieve(payload.question.trim());
  if (!hits.length) {
    res.statusCode = 200;
    res.setHeader('Content-Type', 'application/json; charset=utf-8');
    return res.end(JSON.stringify({ summary: { text: '', source_ids: [] }, hits: [] }));
  }
  try {
    const summary = await callGemini(payload.question.trim(), hits);
    res.statusCode = 200;
    res.setHeader('Content-Type', 'application/json; charset=utf-8');
    return res.end(JSON.stringify({ summary, hits }));
  } catch {
    return fail(res, 503, 'Evidence search is temporarily unavailable');
  }
}

module.exports = handler;
module.exports.config = { api: { bodyParser: false } };
module.exports._internals = { isReleaseReady, terms, evidenceRows, retrieve, parseGeminiAnswer, callGemini, previewRateAllowed, isCorpusOverviewQuestion, corpusOverview };
