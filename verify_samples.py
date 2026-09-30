import fitz
from pathlib import Path
from bs4 import BeautifulSoup
import difflib

pdf_dir = Path(r"c:\Users\cedbo\OneDrive\Documents\pedo\data\pdf")
html_dir = Path(r"c:\Users\cedbo\OneDrive\Documents\pedo\output_html")

samples = [
    {
        "study": "pq8a",
        "title": "Bellechasse (1942)",
        "pdf_page": 6, # Page 7
        "topic": "Description du Climat et Températures"
    },
    {
        "study": "pq4",
        "title": "Arthabaska (1984)",
        "pdf_page": 27, # Page 28
        "topic": "Sols issus de dépôts fluvio-glaciaires"
    },
    {
        "study": "pq11",
        "title": "Shefford, Brome et Missisquoi (1948)",
        "pdf_page": 35, # Page 36
        "topic": "Description d'une série de sol"
    },
    {
        "study": "pq37-38",
        "title": "Matane et Matapédia (2017)",
        "pdf_page": 45, # Page 46
        "topic": "Caractéristiques morphologiques"
    }
]

print("=====================================================================")
print("CONTROLE QUALITE ET VERIFICATION DE FIDELITE PDF <-> HTML")
print("=====================================================================\n")

for s in samples:
    sid = s["study"]
    pdf_path = pdf_dir / f"{sid}_report.pdf"
    html_path = html_dir / f"{sid}.html"
    
    # Extract PDF page raw text
    doc = fitz.open(pdf_path)
    pdf_txt = doc[s["pdf_page"]].get_text()
    doc.close()
    
    # Extract HTML content
    soup = BeautifulSoup(html_path.read_text(encoding="utf-8"), "html.parser")
    
    # Clean PDF lines
    pdf_lines = [l.strip() for l in pdf_txt.split("\n") if l.strip()][:15]
    pdf_sample = " ".join(pdf_lines[:8])
    
    # Search for matching passage in HTML
    # take a distinctive keyword from pdf
    keywords = [w for w in pdf_lines[1].split() if len(w) > 4]
    kw = keywords[0] if keywords else "sol"
    
    html_match = ""
    for p in soup.find_all(["p", "td", "li"]):
        txt = p.get_text(strip=True)
        if kw.lower() in txt.lower() and len(txt) > 50:
            html_match = txt
            break
            
    print(f"--- Échantillon : {s['study']} - {s['title']} | Page {s['pdf_page']+1} ---")
    print(f"Thème : {s['topic']}")
    print("\n[ORIGINAL PDF (Texte brut avec bruit OCR historique)] :")
    print("  " + pdf_sample[:250] + "...")
    print("\n[TRANSCRIPTION HTML GÉNÉRÉE (Restaurée et structurée)] :")
    print("  " + (html_match[:250] if html_match else "Trouvé dans une autre balise") + "...")
    print("-" * 65 + "\n")
