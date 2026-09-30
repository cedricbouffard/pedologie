from pathlib import Path
from bs4 import BeautifulSoup

out_dir = Path(r"c:\Users\cedbo\OneDrive\Documents\pedo\output_html")
soup = BeautifulSoup((out_dir / "pq8a.html").read_text(encoding="utf-8"), "html.parser")
for tidx, tbl in enumerate(soup.find_all("table")[:4]):
    print(f"\n--- pq8a Table #{tidx} ---")
    rows = tbl.find_all("tr")
    for r_idx, r in enumerate(rows[:5]):
        cells = r.find_all(["th", "td"])
        print(f"Row {r_idx}: " + " | ".join([f"{c.name}(cs={c.get('colspan',1)},rs={c.get('rowspan',1)}): {c.get_text(strip=True)[:20]}" for c in cells]))
