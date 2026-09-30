import os
import time
from pathlib import Path
from google import genai
from google.genai import types
from google.genai.errors import APIError
from .config import GEMINI_API_KEY, MODEL_NAME, TRANSCRIPTIONS_DIR

SYSTEM_PROMPT = """Tu es un expert archiviste et pédologue hautement qualifié, spécialisé dans la numérisation et la transcription haute-fidélité des études pédologiques québécoises (Agriculture et Agroalimentaire Canada - SISCan).

Voici l'image d'une page extraite d'un rapport pédologique officiel.
Ton rôle est de transcrire l'intégralité du contenu visible sur cette page en code HTML5 sémantique pur, le plus fidèlement possible.

Directives absolues :
1. Hiérarchie & Titres :
   - Identifie précisément les titres de parties, chapitres, sections et sous-sections (ex. 'PREMIÈRE PARTIE', '1.', '1.1', 'a)', 'b)') et utilise les balises sémantiques adéquates (<h2>, <h3>, <h4>, <h5>...).
   - Préserve la numérotation exacte et la structure des paragraphes (<p>).

2. Tableaux pédologiques & Données analytiques :
   - Transcris fidèlement tous les tableaux avec <table>, <thead>, <tbody>, <tr>, <th>, <td>.
   - Gère parfaitement les fusions de cellules horizontales et verticales (colspan et rowspan) pour les en-têtes complexes (ex: Granulométrie, Sables, Limons, Argiles, pH, Bases échangeables, CEC, etc.).
   - Conserve toutes les valeurs numériques exactes, y compris les décimales avec virgule, les mentions 'traces' ou '-', et les unités de mesure (%, me/100g, ppm, kg/ha).
   - Inclus les titres de tableaux (ex. 'Tableau 4 - ...') et les notes de bas de tableau (<p class="table-note">).

3. Correction de l'OCR & Terminologie pédologique :
   - Rétablis une orthographe française irréprochable avec tous les accents corrects (é, è, ê, à, ô, etc.) qui ont pu être détériorés par le scan historique.
   - Respecte scrupuleusement la nomenclature pédologique canadienne :
     * Horizons pédologiques : Ah, Ap, Ae, Bf, Bhf, Btg, BC, Ck, Cg, etc.
     * Ordres et sous-ordres : Podzols, Brunisols, Gleysols, Luvisols, Régosols, Sols organiques.
     * Séries de sols et géologie québécoise : tills de Sillery, mer de Champlain, dépôts fluvio-glaciaires, etc.

4. Nettoyage & Format de sortie :
   - Si la page contient une photo ou une figure graphique, insère une balise <figure><figcaption>[Description ou titre de l'illustration]</figcaption></figure>.
   - Ignore les en-têtes et pieds de page répétitifs (comme le simple numéro de page ou le titre courant répété en haut de chaque page).
   - Ne retourne AUCUN bloc Markdown de type ```html ... ```, retourne UNIQUEMENT le code HTML brut de la section.
"""

def get_client():
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY is not configured.")
    return genai.Client(api_key=GEMINI_API_KEY)

def get_page_transcription_path(study_id: str, page_num: int) -> Path:
    study_dir = TRANSCRIPTIONS_DIR / study_id
    study_dir.mkdir(parents=True, exist_ok=True)
    return study_dir / f"page_{page_num:03d}.html"

def is_page_transcribed(study_id: str, page_num: int) -> bool:
    path = get_page_transcription_path(study_id, page_num)
    return path.exists() and path.stat().st_size > 20

def transcribe_page_image(client, image_path: str, study_id: str, page_num: int, max_retries: int = 5) -> str:
    """Send page image to Gemini with exponential backoff on errors."""
    output_path = get_page_transcription_path(study_id, page_num)
    if is_page_transcribed(study_id, page_num):
        with open(output_path, "r", encoding="utf-8") as f:
            return f.read()

    with open(image_path, "rb") as f:
        img_bytes = f.read()

    backoff = 3.0
    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=[
                    types.Part.from_bytes(
                        data=img_bytes,
                        mime_type="image/png",
                    ),
                    SYSTEM_PROMPT
                ]
            )
            raw_html = response.text.strip()
            # Clean possible markdown ticks
            if raw_html.startswith("```html"):
                raw_html = raw_html[7:]
            elif raw_html.startswith("```"):
                raw_html = raw_html[3:]
            if raw_html.endswith("```"):
                raw_html = raw_html[:-3]
            raw_html = raw_html.strip()

            # Save page transcription atomically
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(raw_html)
            return raw_html

        except Exception as e:
            err_str = str(e).lower()
            if "429" in err_str or "503" in err_str or "quota" in err_str or "unavailable" in err_str:
                print(f"  [Wait] Page {page_num+1} ({study_id}) rate limit/server busy. Sleeping {backoff:.1f}s... (Attempt {attempt+1}/{max_retries})")
                time.sleep(backoff)
                backoff = min(backoff * 2.0, 60.0)
            else:
                print(f"  [Error] Page {page_num+1} ({study_id}) failed: {e}")
                if attempt == max_retries - 1:
                    raise e
                time.sleep(backoff)

    raise RuntimeError(f"Failed to transcribe page {page_num+1} after {max_retries} attempts.")
