import os
import fitz # PyMuPDF
from google import genai
from google.genai import types

# Read API key from .env
api_key = None
with open(r"c:\Users\cedbo\OneDrive\Documents\pedo\.env", "r") as f:
    for line in f:
        if line.startswith("GEMINI_API_KEY="):
            api_key = line.strip().split("=", 1)[1]

if not api_key:
    raise ValueError("GEMINI_API_KEY not found in .env")

client = genai.Client(api_key=api_key)

# Let's inspect pages in pq4.pdf to find a page with both text and a table
pdf_path = r"C:\Users\cedbo\.gemini\antigravity\brain\0ca5d176-0dd0-4c83-b129-30bba4d04aa2\scratch\samples\pq4.pdf"
doc = fitz.open(pdf_path)

target_page_idx = 74 # Page 75: Fiche analytique Série HEMMING-FALLS

print(f"Testing page {target_page_idx + 1} of pq4.pdf")

# Render page to PNG at 200 DPI
page = doc[target_page_idx]
pix = page.get_pixmap(dpi=200)
img_bytes = pix.tobytes("png")

img_output_path = r"c:\Users\cedbo\OneDrive\Documents\pedo\sample_page.png"
with open(img_output_path, "wb") as f:
    f.write(img_bytes)
print(f"Saved page image to {img_output_path}")

prompt = """Tu es un expert archiviste et pédologue spécialisé dans la numérisation et la transcription haute-fidélité de rapports d'études pédologiques québécois.

Voici l'image d'une page d'un rapport pédologique officiel.
Ton objectif est de transcrire cette page en HTML5 sémantique pur, le plus fidèlement possible.

Directives strictes :
1. Structure et Titres : Respecte rigoureusement la hiérarchie des titres (<h1>, <h2>, <h3>, <h4>...), la numérotation des sections (ex. 1.2, 2.1...), les paragraphes (<p>), listes (<ul>, <ol>).
2. Tableaux : Transcris les tableaux avec les balises standards (<table>, <thead>, <tbody>, <tr>, <th>, <td>). Préserve exactement l'alignement des colonnes, les fusions de cellules (colspan/rowspan), les en-têtes et les notes de bas de tableau.
3. Orthographe et Vocabulaire Pédologique : Rétablis une orthographe française irréprochable avec tous les accents corrects (é, è, ê, à, ô, etc.) qui ont pu être détériorés par le vieil OCR d'origine. Conserve fidèlement la terminologie pédologique (horizons ex: Ah, Ae, Ap, Btg, C; textures; séries de sols).
4. Code propre : Ne retourne AUCUN bloc Markdown de type ```html ... ```, retourne UNIQUEMENT le code HTML brut de la section correspondant à la page.
"""

print("Sending request to Gemini 3.5 Flash Lite...")
response = client.models.generate_content(
    model='gemini-3.5-flash-lite',
    contents=[
        types.Part.from_bytes(
            data=img_bytes,
            mime_type='image/png',
        ),
        prompt
    ]
)

html_content = response.text.strip()
if html_content.startswith("```html"):
    html_content = html_content[7:]
if html_content.endswith("```"):
    html_content = html_content[:-3]

output_html_path = r"c:\Users\cedbo\OneDrive\Documents\pedo\sample_transcription.html"
# Wrap in a clean viewer with styling for review
full_page_html = f"""<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Échantillon de Transcription Pédologique - Page {target_page_idx + 1}</title>
<style>
  body {{
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    line-height: 1.6;
    color: #2c3e50;
    max-width: 900px;
    margin: 40px auto;
    padding: 0 20px;
    background: #fdfdfd;
  }}
  h1, h2, h3, h4 {{
    color: #1a365d;
    margin-top: 1.5em;
    margin-bottom: 0.5em;
  }}
  h1 {{ border-bottom: 2px solid #3182ce; padding-bottom: 8px; font-size: 1.8rem; }}
  h2 {{ border-bottom: 1px solid #e2e8f0; padding-bottom: 6px; font-size: 1.4rem; }}
  table {{
    width: 100%;
    border-collapse: collapse;
    margin: 25px 0;
    font-size: 0.9em;
    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
  }}
  th, td {{
    border: 1px solid #cbd5e0;
    padding: 8px 12px;
    text-align: left;
  }}
  th {{
    background-color: #ebf8ff;
    color: #2b6cb0;
    font-weight: 600;
  }}
  tr:nth-child(even) {{
    background-color: #f7fafc;
  }}
  .note {{
    font-size: 0.85em;
    color: #718096;
    font-style: italic;
  }}
</style>
</head>
<body>
<div style="background: #e6fffa; border-left: 4px solid #319795; padding: 12px 16px; margin-bottom: 30px;">
  <strong>Démonstration de conversion haute-fidélité :</strong> Page {target_page_idx + 1} du rapport <em>pq4 (Arthabaska)</em>.
</div>

{html_content}

</body>
</html>
"""

with open(output_html_path, "w", encoding="utf-8") as f:
    f.write(full_page_html)

print(f"Success! Generated HTML saved to {output_html_path}")
