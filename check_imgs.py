import re
from pathlib import Path
from bs4 import BeautifulSoup

out_dir = Path(r"c:\Users\cedbo\OneDrive\Documents\pedo\output_html")
trans_dir = Path(r"c:\Users\cedbo\OneDrive\Documents\pedo\data\transcriptions")

found = []
for f in out_dir.glob("*.html"):
    if f.name == "index.html":
        continue
    content = f.read_text(encoding="utf-8")
    soup = BeautifulSoup(content, "html.parser")
    imgs = soup.find_all("img")
    if imgs:
        for img in imgs:
            found.append((f.name, str(img)))

print(f"Total img tags found across output_html: {len(found)}")
for fname, img in found:
    print(f"  [{fname}] {img}")
