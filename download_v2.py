import urllib.request
from pathlib import Path
import fitz

pdf_dir = Path(r"c:\Users\cedbo\OneDrive\Documents\pedo\data\pdf")

v2_files = [
    ("pq12b-v2", "https://sis.agr.gc.ca/siscan/publications/surveys/pq/pq12b/pq12b-v2_report.pdf"),
    ("pq46b-v2", "https://sis.agr.gc.ca/siscan/publications/surveys/pq/pq46b/pq46b-v2_report.pdf"),
    ("pq51b-v2", "https://sis.agr.gc.ca/siscan/publications/surveys/pq/pq51b/pq51b-v2_report.pdf"),
    ("pq57b-v2", "https://sis.agr.gc.ca/siscan/publications/surveys/pq/pq57b/pq57b-v2_report.pdf")
]

for name, url in v2_files:
    target = pdf_dir / f"{name}_report.pdf"
    if not target.exists() or target.stat().st_size < 1000:
        print(f"Downloading {name} from {url}...")
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            target.write_bytes(resp.read())
    doc = fitz.open(target)
    print(f"  [OK] {target.name}: {len(doc)} pages, {target.stat().st_size / (1024*1024):.2f} MB")
    doc.close()
