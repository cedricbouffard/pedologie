from pathlib import Path
from bs4 import BeautifulSoup

out_dir = Path(r"c:\Users\cedbo\OneDrive\Documents\pedo\output_html")
soup = BeautifulSoup((out_dir / "pq10a.html").read_text(encoding="utf-8"), "html.parser")
tbl = soup.find_all("table")[0]
print("=== pq10a Table #0 Rows ===")
for r in tbl.find_all("tr")[:5]:
    cells = r.find_all(["th", "td"])
    info = [f"{c.name}(cs={c.get('colspan',1)},rs={c.get('rowspan',1)}): {c.get_text(strip=True)[:15]}" for c in cells]
    print(info)
