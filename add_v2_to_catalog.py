import json
from pathlib import Path
import fitz

cat_path = Path(r"c:\Users\cedbo\OneDrive\Documents\pedo\data\catalog.json")
pdf_dir = Path(r"c:\Users\cedbo\OneDrive\Documents\pedo\data\pdf")

with open(cat_path, "r", encoding="utf-8") as f:
    catalog = json.load(f)

v2_entries = [
    {
        "study_id": "pq12b-v2",
        "title": "Étude pédologique du comté de Chambly (Volume 2)",
        "date": "1991",
        "scale": "20000",
        "pdf_url": "https://sis.agr.gc.ca/siscan/publications/surveys/pq/pq12b/pq12b-v2_report.pdf",
        "pdf_filename": "pq12b-v2_report.pdf"
    },
    {
        "study_id": "pq46b-v2",
        "title": "Étude pédologique du comté de Richelieu (Volume 2)",
        "date": "1990",
        "scale": "20000",
        "pdf_url": "https://sis.agr.gc.ca/siscan/publications/surveys/pq/pq46b/pq46b-v2_report.pdf",
        "pdf_filename": "pq46b-v2_report.pdf"
    },
    {
        "study_id": "pq51b-v2",
        "title": "Étude pédologique du comté de Saint-Hyacinthe (Volume 2)",
        "date": "1991",
        "scale": "20000",
        "pdf_url": "https://sis.agr.gc.ca/siscan/publications/surveys/pq/pq51b/pq51b-v2_report.pdf",
        "pdf_filename": "pq51b-v2_report.pdf"
    },
    {
        "study_id": "pq57b-v2",
        "title": "Étude pédologique du comté de Verchères (Volume 2)",
        "date": "1990",
        "scale": "20000",
        "pdf_url": "https://sis.agr.gc.ca/siscan/publications/surveys/pq/pq57b/pq57b-v2_report.pdf",
        "pdf_filename": "pq57b-v2_report.pdf"
    }
]

for v in v2_entries:
    sid = v["study_id"]
    pdf_path = pdf_dir / v["pdf_filename"]
    doc = fitz.open(pdf_path)
    page_count = len(doc)
    doc.close()
    
    catalog[sid] = {
        "study_id": sid,
        "title": v["title"],
        "date": v["date"],
        "scale": v["scale"],
        "pdf_url": v["pdf_url"],
        "pdf_filename": v["pdf_filename"],
        "pdf_path": str(pdf_path),
        "page_count": page_count,
        "downloaded": True,
        "status": "pending"
    }
    print(f"Added {sid}: {page_count} pages")

with open(cat_path, "w", encoding="utf-8") as f:
    json.dump(catalog, f, indent=2, ensure_ascii=False)

print(f"Catalog updated. Total studies in catalog: {len(catalog)}")
