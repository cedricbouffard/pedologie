import os
import re
import json
from pathlib import Path
from bs4 import BeautifulSoup
from .config import OUTPUT_DIR, TRANSCRIPTIONS_DIR, CATALOG_PATH

CSS_CONTENT = """/* Feuille de style Pédologie Québec - Haute Fidélité */
:root {
  --primary: #1a365d;
  --primary-light: #2b6cb0;
  --secondary: #744210;
  --bg: #f8fafc;
  --surface: #ffffff;
  --border: #e2e8f0;
  --text: #1e293b;
  --text-muted: #64748b;
  --accent: #0284c7;
  --table-header: #f1f5f9;
  --table-zebra: #f8fafc;
  --table-border: #cbd5e1;
}

* {
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
  line-height: 1.65;
  color: var(--text);
  background-color: var(--bg);
  margin: 0;
  padding: 0;
}

.report-container {
  max-width: 1050px;
  margin: 0 auto;
  background: var(--surface);
  padding: 40px 50px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
  min-height: 100vh;
}

/* Header & Metadata */
.header-box {
  border-bottom: 2px solid var(--primary-light);
  padding-bottom: 24px;
  margin-bottom: 30px;
}

.header-badges {
  display: flex;
  gap: 10px;
  margin-bottom: 12px;
  flex-wrap: wrap;
}

.badge {
  display: inline-block;
  padding: 4px 10px;
  font-size: 0.85rem;
  font-weight: 600;
  border-radius: 4px;
  background-color: #e0f2fe;
  color: #0369a1;
}

.badge-year {
  background-color: #fef3c7;
  color: #92400e;
}

.report-title {
  color: var(--primary);
  font-size: 2.1rem;
  margin: 0 0 10px 0;
  line-height: 1.25;
}

.report-subtitle {
  color: var(--text-muted);
  font-size: 1.05rem;
  margin: 0;
}

/* Navigation & TOC */
.toc-box {
  background: #f1f5f9;
  border-left: 4px solid var(--primary-light);
  padding: 20px 25px;
  margin: 30px 0 40px 0;
  border-radius: 0 6px 6px 0;
}

.toc-box h3 {
  margin-top: 0;
  color: var(--primary);
  font-size: 1.2rem;
}

.toc-box ul {
  list-style: none;
  padding-left: 0;
  margin: 0;
}

.toc-box li {
  margin: 6px 0;
}

.toc-box a {
  color: var(--primary-light);
  text-decoration: none;
  font-size: 0.95rem;
}

.toc-box a:hover {
  text-decoration: underline;
  color: var(--primary);
}

/* Headings */
h1, h2, h3, h4, h5, h6 {
  color: var(--primary);
  margin-top: 1.8em;
  margin-bottom: 0.6em;
  font-weight: 700;
  scroll-margin-top: 20px;
}

h2 {
  font-size: 1.5rem;
  border-bottom: 1px solid var(--border);
  padding-bottom: 8px;
}

h3 {
  font-size: 1.25rem;
}

h4 {
  font-size: 1.1rem;
}

p {
  margin: 0 0 1.2em 0;
  text-align: justify;
}

/* Tables */
.table-wrapper {
  overflow-x: auto;
  margin: 25px 0;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  border-radius: 4px;
}

table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.88rem;
  background: var(--surface);
  border: 1px solid var(--table-border);
}

th, td {
  border: 1px solid var(--table-border);
  padding: 8px 10px;
  text-align: left;
}

th {
  background-color: var(--table-header);
  color: var(--primary);
  font-weight: 600;
  vertical-align: middle;
}

tr:nth-child(even) {
  background-color: var(--table-zebra);
}

td:has(> p) p {
  margin: 0;
}

.table-note, caption, .note {
  font-size: 0.82rem;
  color: var(--text-muted);
  font-style: italic;
  margin-top: 6px;
}

/* Page separators */
.page-block {
  position: relative;
  margin-bottom: 30px;
}

.page-marker {
  font-size: 0.75rem;
  color: #94a3b8;
  text-align: right;
  border-bottom: 1px dashed #cbd5e1;
  padding-bottom: 4px;
  margin-bottom: 20px;
  user-select: none;
}

/* Figures */
figure {
  margin: 25px 0;
  padding: 15px;
  background: #f8fafc;
  border: 1px solid var(--border);
  border-radius: 6px;
  text-align: center;
}

figcaption {
  font-size: 0.85rem;
  color: var(--text-muted);
  font-style: italic;
  margin-top: 8px;
}

/* Print */
@media print {
  body {
    background: white;
  }
  .report-container {
    box-shadow: none;
    padding: 0;
    max-width: 100%;
  }
  .page-marker {
    display: none;
  }
  .page-block {
    page-break-after: auto;
  }
}
"""

def ensure_css():
    """Ensure style.css exists in output directory."""
    css_path = OUTPUT_DIR / "style.css"
    with open(css_path, "w", encoding="utf-8") as f:
        f.write(CSS_CONTENT)

def slugify(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s-]", "", text)
    return re.sub(r"[\s-]+", "-", text).strip("-")

def assemble_study_report(study_metadata: dict) -> str:
    """Combine all page transcriptions of a study into a complete standalone HTML document."""
    ensure_css()
    sid = study_metadata["study_id"]
    title = study_metadata.get("title", sid)
    year = study_metadata.get("date", "N/D")
    scale = study_metadata.get("scale", "")
    page_count = study_metadata.get("page_count", 0)
    
    study_trans_dir = TRANSCRIPTIONS_DIR / sid
    if not study_trans_dir.exists():
        return None
    
    page_files = sorted(study_trans_dir.glob("page_*.html"))
    if not page_files:
        return None

    # Collect content and build Table of Contents
    combined_body = []
    toc_items = []
    header_counter = 0

    for pf in page_files:
        p_idx = int(pf.stem.replace("page_", ""))
        with open(pf, "r", encoding="utf-8") as f:
            raw_html = f.read()
        
        soup = BeautifulSoup(raw_html, "html.parser")
        
        # Wrap tables in responsive wrapper if not already
        for tbl in soup.find_all("table"):
            if not (tbl.parent and "table-wrapper" in tbl.parent.get("class", [])):
                wrapper = soup.new_tag("div", attrs={"class": "table-wrapper"})
                tbl.wrap(wrapper)
        
        # Extract headings for TOC
        for tag in soup.find_all(["h2", "h3"]):
            header_counter += 1
            h_text = tag.get_text(strip=True)
            if len(h_text) > 3 and not tag.get("id"):
                anchor_id = f"sec-{header_counter}-{slugify(h_text[:30])}"
                tag["id"] = anchor_id
                toc_items.append((tag.name, h_text, anchor_id))
        
        page_html = f"""
        <div id="page-{p_idx+1}">
          {str(soup)}
        </div>
        """
        combined_body.append(page_html)

    # Build TOC HTML
    toc_html = ""
    if toc_items:
        toc_li = []
        for level, text, anchor in toc_items[:40]: # limit to top 40 major sections
            indent = "padding-left: 20px;" if level == "h3" else ""
            toc_li.append(f'<li style="{indent}"><a href="#{anchor}">{text}</a></li>')
        toc_html = f"""
        <nav class="toc-box">
          <h3>Sommaire du rapport</h3>
          <ul>
            {''.join(toc_li)}
          </ul>
        </nav>
        """

    full_html = f"""<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title} ({year}) - Étude pédologique</title>
  <link rel="stylesheet" href="style.css">
</head>
<body>

<div class="report-container">
  <header class="header-box">
    <div class="header-badges">
      <span class="badge">Étude détaillée {sid}</span>
      <span class="badge badge-year">{year}</span>
      {f'<span class="badge">Échelle 1:{scale}</span>' if scale else ''}
      <span class="badge">{len(page_files)} pages numérisées</span>
    </div>
    <h1 class="report-title">{title}</h1>
    <p class="report-subtitle">Agriculture et Agroalimentaire Canada (SISCan) — Transcription numérique haute fidélité</p>
  </header>

  {toc_html}

  <main>
    {''.join(combined_body)}
  </main>
</div>

</body>
</html>
"""
    output_filename = f"{sid}.html"
    out_path = OUTPUT_DIR / output_filename
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(full_html)
    return str(out_path)

def generate_index_dashboard():
    """Generate the main portal index.html listing all 79 reports with search, filter, and editorial design."""
    ensure_css()
    try:
        from src.portal_generator import generate_portal
        generate_portal()
        return str(OUTPUT_DIR / "index.html")
    except Exception as e:
        print(f"Error calling generate_portal: {e}")
        return str(OUTPUT_DIR / "index.html")

