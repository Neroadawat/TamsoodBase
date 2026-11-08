"""Bounded, conservative facets for the reviewed evidence-card pilot."""
import json
import hashlib
import re
import unicodedata
from pathlib import Path

SCOPE_PATH = Path(__file__).resolve().parents[1] / 'docs/rag/retrieval-scope.json'


def normalized_question(question):
    text = unicodedata.normalize('NFKC', question).lower().replace('\u0e4d\u0e32', '\u0e33')
    text = text.translate(str.maketrans('๐๑๒๓๔๕๖๗๘๙', '0123456789'))
    text = re.sub(r'(?<![a-z0-9])([eb])[ -]+(\d+)', r'\1\2', text)
    text = re.sub(r'(?<![a-z0-9])h[ _-]+fame(?![a-z0-9])', 'h-fame', text)
    for pattern, formula in ((r'(?<![a-z0-9])n\s*2\s*o(?![a-z0-9])', 'n2o'),
                             (r'(?<![a-z0-9])c\s*h\s*4(?![a-z0-9])', 'ch4')):
        text = re.sub(pattern, formula, text)
    # Translate query wording only; source values and index remain untouched.
    for pattern, replacement in (
        (r'cold[ _-]?start', 'สตาร์ตเย็น'),
        (r'hot[ _-]?start', 'สตาร์ตร้อน'),
        (r'warm[ _-]?start', 'สตาร์ตอุ่น'),
        (r'fuel consumption', 'อัตราสิ้นเปลืองน้ำมัน'),
        (r'การกินน้ำมัน|กินน้ำมัน', 'อัตราสิ้นเปลือง'),
        (r'carbon dioxide', 'คาร์บอนไดออกไซด์ co2'),
        (r'methane', 'มีเทน ch4'),
        (r'nitrous oxide', 'ไนตรัสออกไซด์ n2o'),
        (r'electricity', 'ไฟฟ้า'), (r'steam', 'ไอน้ำ'),
        (r'ทั้งวัฏจักรชีวิต|ตลอดวัฏจักรชีวิต', 'ทั้งวงจร'),
        (r'วัฏจักรชีวิต', 'วงจรชีวิต'),
        (r'functional unit', 'หน่วยหน้าที่'),
        (r'allocation', 'การจัดสรร'),
    ):
        text = re.sub(pattern, replacement, text)
    return re.sub(r'(?<=[\u0e00-\u0e7f]) +(?=[\u0e00-\u0e7f])', '', text)


def constraints(question):
    text = normalized_question(question)
    fuels = set(re.findall(r'(?<![a-z0-9])(?:e|b)\d+(?!\d)', text))
    if re.search(r'diesel|ดีเซล', text): fuels.add('diesel')
    h_fame = r'(?<![a-z0-9])h-fame(?![a-z0-9])'
    if re.search(h_fame, text): fuels.add('h-fame')
    if re.search(r'(?<![a-z0-9])fame(?![a-z0-9])', re.sub(h_fame, '', text)): fuels.add('fame')
    if not fuels and re.search(r'เอทานอล|ethanol', text): fuels.add('ethanol')
    species = set()
    for name, pattern in {
        'co2e': r'co2\s*(?:eq|e)(?![a-z0-9])|คาร์บอนเทียบเท่า',
        'co2': r'co2(?!\s*(?:eq|e)(?![a-z0-9]))|คาร์บอนไดออกไซด์',
        'ch4': r'ch4|มีเทน', 'n2o': r'n2o|ไนตรัสออกไซด์',
        'nox': r'nox|ไนโตรเจนออกไซด์',
        'co': r'(?<![a-z0-9])co(?![a-z0-9])|คาร์บอนมอนอกไซด์',
        'pm': r'pm\s*2[.]?5|ฝุ่น',
    }.items():
        if re.search(pattern, text): species.add(name)
    stages = set()
    if re.search(r'สตาร์ตเย็น|สตาร์ทเย็น|เครื่องเย็น|เริ่มติดเครื่อง|เครื่องยังเย็น', text): stages.add('cold')
    if re.search(r'สตาร์ตร้อน|สตาร์ทร้อน|เครื่องร้อน', text): stages.add('hot')
    if re.search(r'สตาร์ตอุ่น|สตาร์ทอุ่น|เครื่องอุ่น', text): stages.add('warm')
    if re.search(r'เดินเบา|\bidl(?:e|ing)\b', text): stages.add('idle')
    if re.search(r'ตลอดรอบ|ทั้งรอบ|(?:full|entire)[ -]?(?:driving[ -]?)?cycle', text): stages.add('full_cycle')
    if re.search(r'ทางไกล|highway', text): stages.add('highway')
    numeric = bool(re.search(r'เท่าไหร่|เท่าไร|เท่าใด|กี่(?!ยว)|how much|how many', text))
    topics = set()
    if re.search(r'หน่วยหน้าที่|ฐาน|\bfu\b', text): topics.add('basis')
    if re.search(r'จัดสรร|ปันส่วน|สัดส่วน', text): topics.add('allocation')
    # The pilot has no plant/year-specific observations. Fail closed if requested.
    specific = bool(re.search(r'\b(?:tsm|bbgi|dmf)\b|(?<!\d)(?:19|20|25|26)\d{2}(?!\d)|(?:แก๊สโซฮอล์?|gasohol|octane|ออกเทน|เบนซิน)\s*(?:91|95)', text))
    return {'fuels': fuels, 'species': species, 'vehicle_stages': stages,
            'numeric': numeric, 'specific': specific, 'topics': topics, 'text': text}


def load_scope(cards):
    document = json.loads(SCOPE_PATH.read_text(encoding='utf-8'))
    corpus = SCOPE_PATH.with_name('public-evidence.json').read_bytes()
    scope = document['cards']
    if (hashlib.sha256(corpus).hexdigest() != document['corpus_sha256']
            or cards != json.loads(corpus) or set(scope) != {c['id'] for c in cards}):
        raise ValueError('Corpus scope must be reviewed when cards change')
    return scope


def compatible(card_scope, wanted):
    if ('required_terms_any' in card_scope
            and not any(term in wanted['text'] for term in card_scope['required_terms_any'])):
        return False
    if wanted['specific']:
        return False
    if wanted['numeric'] and not card_scope['quantitative']:
        return False
    if (wanted['numeric'] and 'numeric_topics' in card_scope
            and not wanted['topics'].intersection(card_scope['numeric_topics'])):
        return False
    return all(wanted[key].issubset(set(card_scope[key]))
               for key in ('fuels', 'species', 'vehicle_stages'))
