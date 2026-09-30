import os
import sys
import argparse
import time
import concurrent.futures
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from src.config import MAX_WORKERS, CATALOG_PATH, OUTPUT_DIR
from src.scraper import build_or_update_catalog
from src.rasterizer import render_page_to_image, cleanup_study_images
from src.transcriber import get_client, is_page_transcribed, transcribe_page_image
from src.assembler import assemble_study_report, generate_index_dashboard, ensure_css

def process_single_page(client, pdf_path: str, study_id: str, page_idx: int) -> bool:
    """Render and transcribe a single page if not already done."""
    if is_page_transcribed(study_id, page_idx):
        return True
    
    img_path = render_page_to_image(pdf_path, study_id, page_idx)
    transcribe_page_image(client, img_path, study_id, page_idx)
    return True

def process_study(client, study_info: dict, max_workers: int = MAX_WORKERS) -> str:
    """Process all pages of a study in parallel and assemble the final HTML report."""
    sid = study_info["study_id"]
    title = study_info.get("title", sid)
    pdf_path = study_info["pdf_path"]
    total_pages = study_info.get("page_count", 0)
    
    final_html = OUTPUT_DIR / f"{sid}.html"
    if final_html.exists():
        print(f"[{sid}] Already assembled -> {final_html.name}")
        return str(final_html)

    print(f"\n=======================================================")
    print(f">> Demarrage de l'etude {sid} : {title}")
    print(f"  Pages a traiter : {total_pages} | Fichier : {Path(pdf_path).name}")
    print(f"=======================================================")

    start_time = time.time()
    
    # Process pages using ThreadPoolExecutor
    completed_pages = 0
    pages_to_do = [p for p in range(total_pages) if not is_page_transcribed(sid, p)]
    print(f"  Pages déjà en cache : {total_pages - len(pages_to_do)} / {total_pages}")
    
    if pages_to_do:
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_page = {
                executor.submit(process_single_page, client, pdf_path, sid, p): p 
                for p in pages_to_do
            }
            for future in concurrent.futures.as_completed(future_to_page):
                page_idx = future_to_page[future]
                try:
                    future.result()
                    completed_pages += 1
                    done_total = (total_pages - len(pages_to_do)) + completed_pages
                    pct = (done_total / total_pages) * 100
                    print(f"  [{sid}] Page {page_idx+1}/{total_pages} transcrite ({pct:.1f}%)")
                except Exception as e:
                    print(f"  [ERREUR] Échec de la page {page_idx+1} ({sid}): {e}")

    # Assemble HTML
    print(f"  Assemblage du rapport HTML pour {sid}...")
    out_file = assemble_study_report(study_info)
    
    # Clean up page images to save disk space
    cleanup_study_images(sid)
    
    elapsed = time.time() - start_time
    print(f"[OK] Etude {sid} terminee en {elapsed:.1f}s -> {out_file}\n")
    
    # Update master dashboard index.html
    generate_index_dashboard()
    return out_file

def main():
    parser = argparse.ArgumentParser(description="Pipeline de conversion des rapports pédologiques québécois en HTML")
    parser.add_argument("--study", type=str, help="Traiter un identifiant d'étude précis (ex: pq8a, pq4)")
    parser.add_argument("--limit", type=int, help="Limiter le nombre d'études à traiter")
    parser.add_argument("--workers", type=int, default=MAX_WORKERS, help="Nombre de requêtes parallèles")
    parser.add_argument("--skip-download", action="store_true", help="Ignorer l'étape de vérification des téléchargements")
    args = parser.parse_args()

    ensure_css()
    
    # Step 1: Catalog & Scraper
    if not args.skip_download:
        print("Étape 1 : Vérification et téléchargement des rapports PDF...")
        catalog = build_or_update_catalog()
    else:
        import json
        with open(CATALOG_PATH, "r", encoding="utf-8") as f:
            catalog = json.load(f)

    # Initialize Gemini client
    client = get_client()

    # Filter studies
    studies_list = list(catalog.values())
    if args.study:
        studies_list = [s for s in studies_list if s["study_id"].lower() == args.study.lower()]
        if not studies_list:
            print(f"Erreur : Étude '{args.study}' non trouvée dans le catalogue.")
            sys.exit(1)
    
    if args.limit:
        studies_list = studies_list[:args.limit]

    print(f"\nLancement de la conversion sur {len(studies_list)} étude(s)...")
    for idx, s in enumerate(studies_list, 1):
        print(f"\n--- Progression globale : Étude {idx} sur {len(studies_list)} ---")
        try:
            process_study(client, s, max_workers=args.workers)
        except Exception as e:
            print(f"Erreur critique sur l'étude {s['study_id']}: {e}")
            continue

    generate_index_dashboard()
    print("\n[TERMINE] Traitement termine avec succes !")
    print(f"Portail general genere : {OUTPUT_DIR / 'index.html'}")

if __name__ == "__main__":
    main()
