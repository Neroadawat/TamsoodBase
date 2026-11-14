"""Build the 10-block A4 poster: poster10.template.html + QR from the old poster -> poster10.html -> PDF (Edge headless)."""
import re
import subprocess
from pathlib import Path

here = Path(__file__).parent
old = (here / 'poster.html').read_text(encoding='utf-8')
qr = re.search(r'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 29 29".*?</svg>', old, flags=re.S).group(0)
html = (here / 'poster10.template.html').read_text(encoding='utf-8').replace('%%QR%%', qr)
(here / 'poster10.html').write_text(html, encoding='utf-8')
# standalone HTML: font embedded so the single file opens correctly anywhere
import base64
font = base64.b64encode((here / 'NotoSansThai.ttf').read_bytes()).decode()
standalone = html.replace('url("NotoSansThai.ttf")', f'url("data:font/ttf;base64,{font}")')
standalone_path = here.parent / 'S2-G05_M4_Poster_A4_10blocks.html'
standalone_path.write_text(standalone, encoding='utf-8')
print('wrote', standalone_path)
out = here.parent / 'S2-G05_M4_Poster_A4_10blocks.pdf'
edge = r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'
subprocess.run([edge, '--headless=new', '--disable-gpu', '--no-pdf-header-footer',
                f'--print-to-pdf={out}', (here / 'poster10.html').as_uri()], check=True, timeout=120)
print('wrote', out)
