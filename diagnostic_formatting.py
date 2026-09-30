import os
import re
from pathlib import Path
from bs4 import BeautifulSoup

out_dir = Path(r"c:\Users\cedbo\OneDrive\Documents\pedo\output_html")
sample_files = ["pq8a.html", "pq4.html", "pq17.html", "pq37-38.html", "pq11.html"]

print("=== 1. DIAGNOSTIC DES TABLES : ALIGNEMENT DES COLONNES ===")
misaligned_tables = []
for hf in out_dir.glob("*.html"):
    if hf.name == "index.html":
        continue
    soup = BeautifulSoup(hf.read_text(encoding="utf-8"), "html.parser")
    tables = soup.find_all("table")
    for tidx, tbl in enumerate(tables):
        # Calculate max columns in the table body rows
        tbody = tbl.find("tbody")
        thead = tbl.find("thead")
        
        row_widths = []
        for tr in tbl.find_all("tr"):
            w = 0
            for cell in tr.find_all(["th", "td"]):
                w += int(cell.get("colspan", 1))
            row_widths.append(w)
            
        if len(set(row_widths)) > 1:
            # Different rows have different total column widths!
            misaligned_tables.append({
                "file": hf.name,
                "table_idx": tidx,
                "widths": row_widths[:6]
            })

print(f"Total des tables avec largeur de colonnes inegale (mismatch colspan) : {len(misaligned_tables)}")
for mt in misaligned_tables[:10]:
    print(f"  [{mt['file']}] Table #{mt['table_idx']}: largeurs de lignes = {mt['widths']}")

print("\n=== 2. DIAGNOSTIC : TABLES DES MATIÈRES & TABLES DES TABLEAUX ===")
tocs_found = []
for hf in [out_dir / sf for sf in sample_files]:
    soup = BeautifulSoup(hf.read_text(encoding="utf-8"), "html.parser")
    for heading in soup.find_all(["h1", "h2", "h3", "h4", "p"]):
        txt = heading.get_text(strip=True).upper()
        if any(term in txt for term in ["TABLE DES MATIÈRES", "TABLE DES MATIERES", "TABLE DES TABLEAUX", "LISTE DES TABLEAUX", "LISTE DES FIGURES"]):
            tocs_found.append((hf.name, heading.name, txt[:60]))

for tf in tocs_found:
    print(f"  [{tf[0]}] <{tf[1]}>: {tf[2]}")

print("\n=== 3. DIAGNOSTIC : NUMÉROS DE PAGE ISOLES ===")
page_num_patterns = []
for hf in [out_dir / sf for sf in sample_files[:3]]:
    soup = BeautifulSoup(hf.read_text(encoding="utf-8"), "html.parser")
    for p in soup.find_all("p"):
        ptxt = p.get_text(strip=True)
        if re.match(r"^\d{1,3}$", ptxt):
            page_num_patterns.append((hf.name, ptxt))

print(f"Exemples de numéros de pages isolés trouvés : {page_num_patterns[:15]}")

print("\n=== 4. DIAGNOSTIC : HIÉRARCHIE DES HEADERS ===")
for sf in sample_files[:3]:
    soup = BeautifulSoup((out_dir / sf).read_text(encoding="utf-8"), "html.parser")
    h_counts = {f"h{i}": len(soup.find_all(f"h{i}")) for i in range(1, 6)}
    print(f"  [{sf}] Headers: {h_counts}")
