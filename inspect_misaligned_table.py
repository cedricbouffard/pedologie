from pathlib import Path
from bs4 import BeautifulSoup

out_dir = Path(r"c:\Users\cedbo\OneDrive\Documents\pedo\output_html")

def inspect_table(filename, table_idx):
    soup = BeautifulSoup((out_dir / filename).read_text(encoding="utf-8"), "html.parser")
    tables = soup.find_all("table")
    if table_idx < len(tables):
        tbl = tables[table_idx]
        print(f"\n==================== {filename} - Table #{table_idx} ====================")
        rows = tbl.find_all("tr")
        for r_idx, r in enumerate(rows[:6]):
            cells = r.find_all(["th", "td"])
            cell_info = [f"<{c.name} col={c.get('colspan',1)} row={c.get('rowspan',1)}>{c.get_text(strip=True)[:15]}</{c.name}>" for c in cells]
            print(f"Row {r_idx} (total cells {len(cells)}): {' | '.join(cell_info)}")

inspect_table("pq10a.html", 0)
inspect_table("pq10a.html", 1)
inspect_table("pq11.html", 1)
inspect_table("pq4.html", 2)
