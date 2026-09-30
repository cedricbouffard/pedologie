import re
from pathlib import Path
from bs4 import BeautifulSoup

out_dir = Path(r"c:\Users\cedbo\OneDrive\Documents\pedo\output_html")

def clean_report_html(filepath):
    html = filepath.read_text(encoding="utf-8")
    soup = BeautifulSoup(html, "html.parser")
    
    # 1. Remove auto-generated <nav class="toc-box"> if present
    for toc in soup.find_all("nav", class_="toc-box"):
        toc.decompose()
        
    # 2. Remove paper Table of Contents and Table of Tables / Figures sections
    # Typical titles: "TABLE DES MATIÈRES", "TABLE DES TABLEAUX", "LISTE DES TABLEAUX", "LISTE DES FIGURES", "TABLE DES FIGURES"
    toc_patterns = [
        r"TABLE\s+DES\s+MATI[EÈ]RES",
        r"TABLE\s+DES\s+TABLEAUX",
        r"LISTE\s+DES\s+TABLEAUX",
        r"TABLE\s+DES\s+FIGURES",
        r"LISTE\s+DES\s+FIGURES",
        r"LISTE\s+DES\s+ILLUSTRATIONS",
        r"TABLE\s+DES\s+PLANCHES"
    ]
    toc_regex = re.compile("|".join(toc_patterns), re.IGNORECASE)
    
    # Find headers matching these patterns
    for tag in list(soup.find_all(["h1", "h2", "h3", "h4", "p"])):
        txt = tag.get_text(strip=True)
        if toc_regex.fullmatch(txt) or (toc_regex.search(txt) and len(txt) < 40):
            # Check what follows this header: usually a <ul>, <ol>, <table>, or <div> containing the TOC items
            # Decompose the header and its following list/div
            sibling = tag.find_next_sibling()
            # Decompose siblings that look like TOC list or dot-leader list until next major header
            while sibling and sibling.name not in ["h1", "h2", "h3"]:
                next_sib = sibling.find_next_sibling()
                # If it's a list, table of contents, or p with dots/page numbers
                sib_text = sibling.get_text(strip=True)
                if sibling.name in ["ul", "ol", "table"] or "..." in sib_text or "…" in sib_text or re.search(r"\d+\s*$", sib_text):
                    sibling.decompose()
                elif sibling.name == "p" and len(sib_text) < 150:
                    sibling.decompose()
                else:
                    break
                sibling = next_sib
            tag.decompose()

    # 3. Remove standalone page numbers
    # e.g. <p>6</p>, <p> 45 </p>, or text that is purely a 1-3 digit number
    for tag in list(soup.find_all(["p", "div", "span"])):
        # don't remove cells in tables!
        if tag.name in ["td", "th"] or tag.find_parent("table"):
            continue
        txt = tag.get_text(strip=True)
        if re.match(r"^\d{1,4}$", txt) or re.match(r"^Page\s*\d{1,4}$", txt, re.IGNORECASE):
            tag.decompose()
            continue
        # Also remove page numbers at the very beginning of a paragraph left over from scan headers:
        # e.g. "37 Bien cultivée..." -> "Bien cultivée..."
        if tag.name == "p" and re.match(r"^\d{1,3}\s+[A-ZÀ-ÖØ-ß]", txt):
            new_text = re.sub(r"^\d{1,3}\s+", "", txt)
            tag.string = new_text

    # 4. Normalize Header Hierarchy
    # Ensure only ONE <h1> in the whole document (the main title in header)
    main_header = soup.find("header", class_="header-box")
    for h1 in soup.find_all("h1"):
        if main_header and h1 in main_header.descendants:
            continue
        # Demote internal h1 to h2
        h1.name = "h2"

    # Clean up empty tags
    for p in soup.find_all("p"):
        if not p.get_text(strip=True) and not p.find(["img", "figure"]):
            p.decompose()

    # 5. Table Header Alignment & Structure Fix
    for tbl in soup.find_all("table"):
        # Wrap table in responsive wrapper if not wrapped
        if not (tbl.parent and "table-wrapper" in tbl.parent.get("class", [])):
            wrapper = soup.new_tag("div", attrs={"class": "table-wrapper"})
            tbl.wrap(wrapper)

        # Style multi-column headers
        for th in tbl.find_all("th"):
            colspan = int(th.get("colspan", 1))
            if colspan > 1:
                th["class"] = th.get("class", []) + ["th-grouped"]
            # Detect numeric / code columns in data cells below
            
        # Detect table width (number of columns) from body
        body_rows = tbl.find("tbody").find_all("tr") if tbl.find("tbody") else [r for r in tbl.find_all("tr") if not r.find("th")]
        if not body_rows:
            body_rows = tbl.find_all("tr")[1:] # fallback

        if body_rows:
            max_cols = max(sum(int(c.get("colspan", 1)) for c in r.find_all(["td", "th"])) for r in body_rows)
            
            # Check header rows
            head_rows = tbl.find("thead").find_all("tr") if tbl.find("thead") else [r for r in tbl.find_all("tr") if r.find("th")]
            if head_rows:
                for hr in head_rows:
                    hr_cols = sum(int(c.get("colspan", 1)) for c in hr.find_all("th"))
                    # If header row has fewer columns than body, check if first cell is missing
                    if hr_cols < max_cols:
                        diff = max_cols - hr_cols
                        # If diff is 1, often the first column (e.g. series name or horizon) had no header label in original scan!
                        if diff == 1:
                            # Prepend an empty <th> for the row label column
                            empty_th = soup.new_tag("th", attrs={"class": "th-label"})
                            empty_th.string = ""
                            hr.insert(0, empty_th)
                        else:
                            # Add colspan to first or last header
                            first_th = hr.find("th")
                            if first_th and not first_th.get("colspan"):
                                first_th["colspan"] = diff + 1

    return str(soup)

# Test on pq8a.html, pq4.html, pq10a.html
for sf in ["pq8a.html", "pq4.html", "pq10a.html"]:
    cleaned = clean_report_html(out_dir / sf)
    # Check lines of cleaned output
    s = BeautifulSoup(cleaned, "html.parser")
    print(f"[{sf}] Cleaned successfully.")
    print(f"  h1 count: {len(s.find_all('h1'))}")
    print(f"  h2 count: {len(s.find_all('h2'))}")
    print(f"  nav toc count: {len(s.find_all('nav', class_='toc-box'))}")
    # Check for any remaining TABLE DES MATIERES
    found_tocs = [t.get_text(strip=True) for t in s.find_all(["h2", "h3"]) if "TABLE DES" in t.get_text(strip=True).upper()]
    print(f"  Remaining TOC headers: {found_tocs}")
