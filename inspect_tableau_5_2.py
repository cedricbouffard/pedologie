from pathlib import Path
from bs4 import BeautifulSoup
import fitz
import sys

sys.stdout.reconfigure(encoding="utf-8")

html_path = Path(r"c:\Users\cedbo\OneDrive\Documents\pedo\output_html\pq46b-v2.html")
pdf_path = Path(r"c:\Users\cedbo\OneDrive\Documents\pedo\data\pdf\pq46b-v2_report.pdf")

soup = BeautifulSoup(html_path.read_text(encoding="utf-8"), "html.parser")

target_table = None
target_title = None

# Search for Tableau 5.2
for p in soup.find_all(["p", "h2", "h3", "h4", "caption", "div"]):
    if "Tableau 5.2" in p.get_text() or "Analyses granulométriques et chimiques" in p.get_text():
        if "Saint-Aimé" in p.get_text() or "Aimé" in p.get_text():
            target_title = p.get_text(strip=True)
            # Find next table
            target_table = p.find_next("table")
            break

if not target_table:
    # search all tables for Saint-Aimé
    for tbl in soup.find_all("table"):
        txt = tbl.get_text()
        if "Saint-Aimé" in txt or "Aimé" in txt:
            target_table = tbl
            break

print("Found title:", target_title)
if target_table:
    rows = target_table.find_all("tr")
    print(f"Total rows in table: {len(rows)}")
    for r_idx, r in enumerate(rows):
        cells = r.find_all(["th", "td"])
        row_str = " | ".join([f"<{c.name} cs={c.get('colspan',1)} rs={c.get('rowspan',1)}>{c.get_text(strip=True)}</{c.name}>" for c in cells])
        print(f"Row {r_idx}: {row_str}")

# Search PDF for Tableau 5.2
doc = fitz.open(pdf_path)
print(f"\nSearching PDF ({len(doc)} pages)...")
for pno in range(len(doc)):
    txt = doc[pno].get_text()
    if "Tableau 5.2" in txt or ("5.2" in txt and "Saint-Aimé" in txt):
        print(f"Found on PDF page {pno + 1}:")
        print("\n".join(txt.split("\n")[:25]))
        # Render this PDF page as image so we can view it
        pix = doc[pno].get_pixmap(dpi=200)
        img_out = r"c:\Users\cedbo\OneDrive\Documents\pedo\tableau_5_2_pdf_page.png"
        pix.save(img_out)
        print(f"Saved PDF page image to {img_out}")
        break
doc.close()
