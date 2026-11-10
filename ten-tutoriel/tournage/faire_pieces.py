import sys
from pathlib import Path
from docx import Document
from docx.shared import Pt
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
C = Path("/home/user/ten-assistant/moteur/tests/corpus")
out = Path(sys.argv[1])
# Bail -> docx
d = Document()
st = d.styles["Normal"]; st.font.name = "Times New Roman"; st.font.size = Pt(11)
for i, l in enumerate(C.joinpath("11-bail-commercial.txt").read_text().splitlines()):
    if i == 0: d.add_heading(l, 1)
    elif l.startswith("Article"): d.add_heading(l, 2)
    else: d.add_paragraph(l)
d.save(out / "Bail commercial - Boulangerie Soulier.docx")
# Commandement -> pdf
import glob
f = (glob.glob("/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf") or [None])[0]
pdfmetrics.registerFont(TTFont("S", f))
c = canvas.Canvas(str(out / "Commandement de payer 17-09-2025.pdf"), pagesize=A4)
y = 800
import textwrap
for l in C.joinpath("13-commandement-payer.txt").read_text().splitlines():
    for w in (textwrap.wrap(l, 95) or [""]):
        if y < 50: c.showPage(); y = 800
        c.setFont("S", 9.5); c.drawString(50, y, w); y -= 13
c.save()
print("ok")
