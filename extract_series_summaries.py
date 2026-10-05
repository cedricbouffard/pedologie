"""
Extraction ultra-rapide (regex) des synthèses de séries de sols pour l'assistant IA.
Génère data/series_summaries.json en moins de 1 seconde.
"""

import os
import re
import json
import unicodedata
from pathlib import Path

def slugify(text: str) -> str:
    if not text:
        return ""
    text = unicodedata.normalize('NFD', text)
    text = "".join(c for c in text if unicodedata.category(c) != 'Mn')
    text = re.sub(r'[^a-zA-Z0-9]+', '-', text).strip('-').lower()
    return text

def clean_html_text(raw_html: str) -> str:
    if not raw_html:
        return ""
    # Remove HTML tags
    txt = re.sub(r'<[^>]+>', ' ', raw_html)
    # Unescape common entities
    txt = txt.replace('&#x27;', "'").replace('&nbsp;', ' ').replace('&rarr;', '->').replace('&amp;', '&').replace('&quot;', '"')
    return re.sub(r'\s+', ' ', txt).strip()

def build_series_summaries():
    series_dir = Path("output_html/series")
    if not series_dir.exists():
        print(f"Directory {series_dir} does not exist.")
        return

    html_files = [f for f in series_dir.glob("*.html") if f.name != "index.html"]
    print(f"Parsing {len(html_files)} series HTML files with regex...")

    re_name = re.compile(r'<h1 class="series-name">([^<]+)</h1>', re.IGNORECASE)
    re_meta = re.compile(
        r'<div class="meta-item">\s*<span class="meta-label">([^<]+)</span>\s*<span class="meta-val[^>]*>([\s\S]*?)</span>\s*</div>',
        re.IGNORECASE
    )
    re_defn = re.compile(r'<div class="definition-box">([\s\S]*?)</div>', re.IGNORECASE)

    summaries = {}

    for file_path in html_files:
        slug = file_path.stem
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
        except Exception:
            continue

        # Extract name
        m_name = re_name.search(content)
        raw_name = m_name.group(1).strip() if m_name else slug.replace("-", " ").title()
        clean_name = re.sub(r'^Série\s+', '', raw_name, flags=re.IGNORECASE).strip()

        # Extract metas
        metas = {}
        for m_lbl, m_val in re_meta.findall(content):
            lbl_clean = m_lbl.strip()
            val_clean = clean_html_text(m_val)
            metas[lbl_clean] = val_clean

        # Extract definition
        m_defn = re_defn.search(content)
        raw_defn = m_defn.group(1) if m_defn else ""
        clean_defn = clean_html_text(raw_defn)
        if len(clean_defn) > 420:
            clean_defn = clean_defn[:420].strip() + "..."

        entry = {
            "nom": clean_name,
            "symbole": metas.get("Symbole Cartographique", ""),
            "ordre": metas.get("Ordre Taxonomique", ""),
            "groupe": metas.get("Grand Groupe", ""),
            "drainage": metas.get("Régime Hydrique", ""),
            "texture": metas.get("Texture Principale", ""),
            "materiau": metas.get("Matériau Parental", ""),
            "description": clean_defn
        }

        # Index by slug
        summaries[slug] = entry

        # Also index by normalized name for direct lookup from s1_desc
        norm_name = slugify(clean_name)
        if norm_name and norm_name not in summaries:
            summaries[norm_name] = entry

    # Save to data/
    out_file = Path("data/series_summaries.json")
    out_file.parent.mkdir(parents=True, exist_ok=True)
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(summaries, f, ensure_ascii=False, indent=2)

    # Save to output_html/data/ and site/data/
    for dest_dir in [Path("output_html/data"), Path("site/data")]:
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest_file = dest_dir / "series_summaries.json"
        with open(dest_file, "w", encoding="utf-8") as f:
            json.dump(summaries, f, ensure_ascii=False, separators=(',', ':'))

    print(f"Successfully generated series_summaries.json with {len(summaries)} entries!")

if __name__ == "__main__":
    build_series_summaries()
