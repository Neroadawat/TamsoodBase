"""Readable source-record view; values remain unchanged and all text is escaped."""
import html
from urllib.parse import urlsplit


def render_observation(row, graph_available=False):
    def text(value): return html.escape('ยังไม่ระบุ' if value is None else str(value), quote=True)
    oid = row['observation_id']
    fields = [('กระบวนการ',row.get('process')), ('รายการ',row.get('flow')),
              ('ปริมาณตามต้นทาง',row.get('amount')), ('หน่วย',row.get('unit')),
              ('ฐานอ้างอิง',str(row.get('reference_amount','')) + ' ' + str(row.get('reference_unit',''))),
              ('ทิศทาง',row.get('direction')), ('ปีเผยแพร่',row.get('publication_year')),
              ('ช่วงปีที่วัด',row.get('data_period')), ('ตาราง',row.get('table_id')),
              ('หน้า PDF',row.get('pdf_page')), ('แถวในตาราง',row.get('source_row',row.get('table_data_row')))]
    details = ''.join('<dt>' + text(label) + '</dt><dd>' + text(value) + '</dd>' for label,value in fields)
    held = row.get('unit') is None or str(row.get('status','')).startswith('HOLD')
    status = 'พักการใช้: ต้องตรวจหน่วยหรือข้อจำกัดก่อนคำนวณ' if held else 'รายการจากแหล่งต้นทางสำหรับทบทวน'
    source_url = row.get('source_url',''); endpoint = urlsplit(source_url)
    source = ('<a target="_blank" rel="noopener noreferrer" href="' + text(source_url) + '">เปิดแหล่งต้นฉบับ</a>') if endpoint.scheme == 'https' and endpoint.hostname and not endpoint.username and not endpoint.password else ''
    graph = '<a href="/graph?id=' + text(oid) + '">ดูรายการในกราฟทดลอง</a>' if graph_available else ''
    return ('''<!doctype html><html lang="th"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>รายการต้นทาง | TamsoodBase</title><style>
body{font:1.05rem/1.65 system-ui,sans-serif;background:#f2f7f5;color:#142e29;margin:0;padding:1rem}
main{max-width:48rem;margin:auto;background:white;padding:1.2rem;border:1px solid #c9ded6;border-radius:.75rem}
dl{display:grid;grid-template-columns:minmax(7rem,1fr) minmax(0,2fr);gap:.6rem}dt{font-weight:600}dd{margin:0;overflow-wrap:anywhere}
a{color:#125d4d;overflow-wrap:anywhere}.status{background:#e4f1eb;padding:.8rem}nav{display:flex;gap:1rem;flex-wrap:wrap}
</style><main><a href="/">กลับหน้าค้นหลักฐาน</a><h1>''' + text(row.get('flow')) + '</h1><p class="status">' + status + '</p>'
            '<p>ปริมาณนี้ใช้กับฐานและขอบเขตของรายการด้านล่าง การมีรายการต้นทางยังไม่ยืนยันว่ามีบัญชี LCI ครบทั้งวงจร</p><dl>' + details + '</dl><nav>'
            + source + '<a href="/evidence?id=' + text(oid) + '">ข้อมูลเดิมแบบ JSON</a>' + graph + '</nav><p>รหัสรายการ: ' + text(oid) + '</p></main></html>').encode('utf-8')
