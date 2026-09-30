import os
import re
from pathlib import Path
from bs4 import BeautifulSoup

out_dir = Path(r"c:\Users\cedbo\OneDrive\Documents\pedo\output_html")
html_files = sorted([f for f in out_dir.glob("*.html") if f.name != "index.html"])

print(f"Refining layout, headers, tables, and removing TOC/page numbers on {len(html_files)} reports...")

toc_patterns = [
    r"^TABLE\s+DES\s+MATI[EÈ]RES.*$",
    r"^TABLE\s+DES\s+TABLEAUX.*$",
    r"^LISTE\s+DES\s+TABLEAUX.*$",
    r"^TABLE\s+DES\s+FIGURES.*$",
    r"^LISTE\s+DES\s+FIGURES.*$",
    r"^LISTE\s+DES\s+ILLUSTRATIONS.*$",
    r"^TABLE\s+DES\s+PLANCHES.*$",
    r"^LISTE\s+DES\s+PLANCHES.*$"
]
toc_regex = re.compile("|".join(toc_patterns), re.IGNORECASE)

cleaned_count = 0
tables_fixed = 0

for hf in html_files:
    soup = BeautifulSoup(hf.read_text(encoding="utf-8"), "html.parser")
    
    # 1. Remove auto-generated <nav class="toc-box">
    for toc in soup.find_all("nav", class_="toc-box"):
        toc.decompose()

    # 2. Remove paper Table of Contents and Table of Tables / Figures sections
    for tag in list(soup.find_all(["h1", "h2", "h3", "h4", "p"])):
        txt = tag.get_text(strip=True)
        if toc_regex.match(txt) and len(txt) < 80:
            # Decompose following siblings until next major section
            sibling = tag.find_next_sibling()
            while sibling and sibling.name not in ["h1", "h2"]:
                next_sib = sibling.find_next_sibling()
                sib_text = sibling.get_text(strip=True)
                # If it's a list, table, or paragraph with dots/page numbers or short entry
                if sibling.name in ["ul", "ol", "table"] or "..." in sib_text or "…" in sib_text or re.search(r"\d+\s*$", sib_text):
                    sibling.decompose()
                elif sibling.name == "p" and len(sib_text) < 160:
                    sibling.decompose()
                elif sibling.name in ["h3", "h4"] and any(term in sib_text.upper() for term in ["PREMIÈRE", "DEUXIÈME", "CHAPITRE", "PARTIE", "ANNEXE"]):
                    # reached real content
                    break
                else:
                    break
                sibling = next_sib
            tag.decompose()

    # 3. Remove standalone page numbers and leading page numbers in text
    for tag in list(soup.find_all(["p", "div", "span"])):
        if tag.name in ["td", "th"] or tag.find_parent("table"):
            continue
        txt = tag.get_text(strip=True)
        # Standalone numbers like "6", "45", "Page 12"
        if re.match(r"^\d{1,4}$", txt) or re.match(r"^Page\s*\d{1,4}$", txt, re.IGNORECASE):
            tag.decompose()
            continue
        # Leading page number at the very start of a paragraph
        if tag.name == "p" and re.match(r"^\d{1,3}\s+[A-ZÀ-ÖØ-ß]", txt):
            tag.string = re.sub(r"^\d{1,3}\s+", "", txt)

    # 4. Remove residual page-marker / page-block
    for pm in soup.find_all(class_="page-marker"):
        pm.decompose()
    for pb in soup.find_all(class_="page-block"):
        pb.unwrap()

    # 5. Header hierarchy normalization
    # Exactly one h1 (in header-box)
    header_box = soup.find("header", class_="header-box")
    for h1 in soup.find_all("h1"):
        if header_box and h1 in header_box.descendants:
            continue
        h1.name = "h2"

    # 6. Table alignment and column balancing
    for tbl in soup.find_all("table"):
        # Wrap table if needed
        if not (tbl.parent and "table-wrapper" in tbl.parent.get("class", [])):
            wrapper = soup.new_tag("div", attrs={"class": "table-wrapper"})
            tbl.wrap(wrapper)

        # Style grouped headers
        for th in tbl.find_all("th"):
            colspan = int(th.get("colspan", 1))
            if colspan > 1:
                th["class"] = th.get("class", []) + ["th-grouped"]

        # Align data cells: if text has letters and spaces, left-align; if purely numbers/units, center
        for td in tbl.find_all("td"):
            txt = td.get_text(strip=True)
            # If cell has longer text (more than 3 words or > 25 chars)
            if len(txt.split()) > 3 or len(txt) > 25:
                td["class"] = td.get("class", []) + ["text-left"]

        # Header column width auto-balancing
        tbody = tbl.find("tbody")
        body_rows = tbody.find_all("tr") if tbody else [r for r in tbl.find_all("tr") if not r.find("th")]
        if body_rows:
            body_widths = [sum(int(c.get("colspan", 1)) for c in r.find_all(["td", "th"])) for r in body_rows]
            if body_widths:
                max_cols = max(body_widths)
                thead = tbl.find("thead")
                head_rows = thead.find_all("tr") if thead else [r for r in tbl.find_all("tr") if r.find("th")]
                for hr in head_rows:
                    hr_cols = sum(int(c.get("colspan", 1)) for c in hr.find_all("th"))
                    if hr_cols < max_cols:
                        diff = max_cols - hr_cols
                        if diff == 1:
                            # Prepend empty header cell for row-label column
                            empty_th = soup.new_tag("th", attrs={"class": "th-label"})
                            empty_th.string = ""
                            hr.insert(0, empty_th)
                            tables_fixed += 1
                        elif diff > 1:
                            # Add colspan to first cell
                            first_th = hr.find("th")
                            if first_th and int(first_th.get("colspan", 1)) == 1:
                                first_th["colspan"] = diff + 1
                                tables_fixed += 1

    # 7. Clean empty paragraphs
    for p in list(soup.find_all("p")):
        if not p.get_text(strip=True) and not p.find(["img", "figure", "table"]):
            p.decompose()

    hf.write_text(str(soup), encoding="utf-8")
    cleaned_count += 1

print(f"\nDone! Successfully refined {cleaned_count} reports.")
print(f"Total table headers balanced and aligned: {tables_fixed}")
