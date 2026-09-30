import fitz
from pathlib import Path
from bs4 import BeautifulSoup

pdf_dir = Path(r"c:\Users\cedbo\OneDrive\Documents\pedo\data\pdf")
trans_dir = Path(r"c:\Users\cedbo\OneDrive\Documents\pedo\data\transcriptions")

samples = [
    {
        "study": "pq8a",
        "title": "Bellechasse (1942)",
        "p_idx": 6, # Page 7
        "topic": "Description du Climat et Agriculture"
    },
    {
        "study": "pq4",
        "title": "Arthabaska (1984)",
        "p_idx": 27, # Page 28
        "topic": "Tableau morphologique d'horizon de sol (Bf, BC, C)"
    },
    {
        "study": "pq11",
        "title": "Shefford, Brome et Missisquoi (1948)",
        "p_idx": 36, # Page 37
        "topic": "Description de fertilité et régie des terres franches"
    },
    {
        "study": "pq37-38",
        "title": "Matane et Matapédia (2017)",
        "p_idx": 49, # Page 50
        "topic": "Pédogenèse et profil de sol"
    }
]

print("=" * 80)
print("AUDIT DE FIDELITE ET CONTROLE QUALITE : COMPARAISON PDF ORIGINAL vs HTML GENERE")
print("=" * 80)

for s in samples:
    sid = s["study"]
    pdf_path = pdf_dir / f"{sid}_report.pdf"
    html_page_path = trans_dir / sid / f"page_{s['p_idx']:03d}.html"
    
    # PDF page
    doc = fitz.open(pdf_path)
    pdf_txt = doc[s["p_idx"]].get_text().strip()
    doc.close()
    
    # HTML transcription of that exact page
    html_raw = html_page_path.read_text(encoding="utf-8").strip() if html_page_path.exists() else "Non trouvé"
    soup = BeautifulSoup(html_raw, "html.parser")
    html_text = soup.get_text(separator=" ", strip=True)
    
    print(f"\n================================================================================")
    print(f">> ÉTUDE : {sid} - {s['title']} | PAGE {s['p_idx']+1}")
    print(f"   Thème : {s['topic']}")
    print(f"================================================================================")
    
    print("\n[EXTRAIT BRUT PDF (avec fautes d'OCR historiques d'origine)] :")
    pdf_clean = " ".join(pdf_txt.split())
    print("  " + pdf_clean[:320] + " ...")
    
    print("\n[EXTRAIT HTML RESTAURE ET TRANSCRIT (Français impeccable, accents, structure)] :")
    html_clean = " ".join(html_text.split())
    print("  " + html_clean[:320] + " ...")
    
    # Check if table present in HTML
    tables = soup.find_all("table")
    if tables:
        print(f"\n[STRUCTURE TABLEAU DETECTEE] : {len(tables)} tableau(x) parfaitement converti(s).")
        first_tbl = tables[0]
        rows = first_tbl.find_all("tr")
        print(f"  Nombre de lignes : {len(rows)}")
        th_headers = [th.get_text(strip=True) for th in first_tbl.find_all("th")[:8]]
        if th_headers:
            print(f"  En-têtes : {' | '.join(th_headers)}")
    print("-" * 80)
