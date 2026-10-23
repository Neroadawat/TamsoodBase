"""Render the human-readable board from the single structured task list."""
import json
from collections import Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


def render():
    data=json.loads((ROOT/'docs/tasks.json').read_text(encoding='utf-8'))
    tasks=data['tasks'];counts=Counter(t['status'] for t in tasks)
    lines=['# Task board — TamsoodBase','',
      'สถานะนี้นับเป็นหน่วยงาน ไม่ใช่เปอร์เซ็นต์ความสมบูรณ์หรือประมาณเวลา แต่ละงานมีขนาดต่างกัน',
      '',f"ทั้งหมด {len(tasks)} งาน: DONE {counts['DONE']} · IN_PROGRESS {counts['IN_PROGRESS']} · TODO {counts['TODO']} · WAITING {counts['WAITING']}",
      '', 'DONE หมายถึงผ่านเกณฑ์เฉพาะงานนั้น ไม่ได้หมายความว่า dataset ผ่าน MTEC แล้ว',
      'WAITING คือรอข้อมูล/การยืนยัน/การมีส่วนร่วมของมนุษย์ ทำงานอิสระส่วนอื่นต่อได้',
      '', '| ID | ลำดับ | สถานะ | งาน / เกณฑ์จบ | หลักฐาน | ขึ้นกับ |',
      '|---|---|---|---|---|---|']
    for task in tasks:
        evidence=task['evidence'];link='['+evidence+'](../'+evidence+')'
        lines.append('| '+' | '.join([task['id'],task['priority'],task['status'],task['title']+'<br>'+task['done_when'],link,', '.join(task['dependencies']) or '—'])+' |')
    lines+=['','## วิธีทำต่อในแต่ละรอบ','',
       'อ่าน tasks.json และผลตรวจจริง เลือก P0 ที่ยังทำได้ก่อน P1 ทำให้จบพร้อมหลักฐานแล้วอัปเดตสถานะและรัน scripts/task_board.py ไม่ทดสอบซ้ำโดยไม่มีการเปลี่ยนแปลงหรือข้อกังวลใหม่',
       'อย่ากำหนดชื่อสมาชิกหรือ contribution แทนมนุษย์ อย่าส่งคำถาม/เอกสารออกไปเอง และอย่าประกาศว่าได้รับอนุมัติโดยไม่มีต้นฉบับคำตอบ',
       '', data.get('automation_note', 'ไม่มีรอบทำงานอัตโนมัติที่ยืนยันไว้'),
       'แจ้งเฉพาะความคืบหน้าสำคัญ งานเสร็จ ปัญหา หรือสิ่งที่ต้องให้ผู้ใช้ตัดสินใจ หากไม่มีอะไรเปลี่ยนให้ไม่รายงานซ้ำ','']
    (ROOT/'docs/tasks.md').write_text('\n'.join(lines),encoding='utf-8')
    print(dict(counts))


if __name__=='__main__': render()
