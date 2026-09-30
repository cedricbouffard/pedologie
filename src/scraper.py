import os
import json
import urllib.request
import urllib.parse
from bs4 import BeautifulSoup
import fitz # PyMuPDF
from .config import PDF_DIR, CATALOG_PATH

BASE_INDEX_URL = "https://sis.agr.gc.ca/siscan/publications/surveys/pq/index.html"
BASE_DOMAIN = "https://sis.agr.gc.ca"

def fetch_studies_list():
    """Fetch the main DSS table from SISCan Quebec."""
    print("Scraping main DSS table from SISCan...")
    req = urllib.request.Request(BASE_INDEX_URL, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        html = resp.read().decode("utf-8", errors="ignore")
    
    soup = BeautifulSoup(html, "html.parser")
    dss_anchor = soup.find("a", {"name": "DSS"})
    if not dss_anchor:
        raise ValueError("Could not find DSS anchor on page")
    
    table = dss_anchor.find_next("table")
    rows = table.find_all("tr")[1:]
    
    studies = []
    for r in rows:
        cols = r.find_all(["th", "td"])
        if len(cols) >= 5:
            study_id = cols[0].get_text(strip=True)
            title = cols[1].get_text(strip=True)
            date = cols[2].get_text(strip=True)
            scale = cols[3].get_text(strip=True)
            link = cols[4].find("a")
            href = link["href"] if link else None
            studies.append({
                "study_id": study_id,
                "title": title,
                "date": date,
                "scale": scale,
                "study_page_url": urllib.parse.urljoin(BASE_DOMAIN, href) if href else None
            })
    print(f"Found {len(studies)} studies in DSS section.")
    return studies

def find_report_pdf(study):
    """Visit study page and identify the non-map report PDF."""
    page_url = study["study_page_url"]
    if not page_url:
        return None
    try:
        req = urllib.request.Request(page_url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=20) as resp:
            html = resp.read().decode("utf-8", errors="ignore")
        soup = BeautifulSoup(html, "html.parser")
        
        pdf_links = []
        for a in soup.find_all("a", href=True):
            href = a["href"]
            if href.lower().endswith(".pdf"):
                text = a.get_text(strip=True)
                parent = a.find_parent(["div", "section", "p", "li"])
                ptext = parent.get_text(" ", strip=True) if parent else ""
                full_url = urllib.parse.urljoin(page_url, href)
                pdf_links.append((full_url, href.split("/")[-1], text, ptext))
        
        # Filter for report (not map)
        for url, fn, txt, ctx in pdf_links:
            lower = (fn + " " + txt + " " + ctx).lower()
            if "_report" in lower or "rapport" in lower or "étude" in lower:
                return url
        # If no explicit match, pick the first PDF that does not contain 'carte' or 'map'
        for url, fn, txt, ctx in pdf_links:
            lower = (fn + " " + txt + " " + ctx).lower()
            if "carte" not in lower and "map" not in lower:
                return url
        # Fallback to first PDF
        if pdf_links:
            return pdf_links[0][0]
    except Exception as e:
        print(f"Error fetching study page for {study['study_id']}: {e}")
    return None

import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

def download_file(url, target_path):
    """Download a file with streaming and error handling."""
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        with open(target_path, "wb") as f:
            while True:
                chunk = resp.read(64 * 1024)
                if not chunk:
                    break
                f.write(chunk)

def build_or_update_catalog():
    """Build the catalog of all 76 reports and download any missing PDFs concurrently."""
    catalog = {}
    if CATALOG_PATH.exists():
        with open(CATALOG_PATH, "r", encoding="utf-8") as f:
            catalog = json.load(f)
    
    studies = fetch_studies_list()
    
    # Step A: Identify PDF URLs for any studies missing from catalog
    missing_studies = [s for s in studies if s["study_id"] not in catalog or not catalog[s["study_id"]].get("pdf_url")]
    if missing_studies:
        print(f"Resolving PDF URLs for {len(missing_studies)} studies...")
        import concurrent.futures
        def resolve_url(s):
            url = find_report_pdf(s)
            return s, url
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as ex:
            futs = [ex.submit(resolve_url, s) for s in missing_studies]
            for f in concurrent.futures.as_completed(futs):
                s, pdf_url = f.result()
                if pdf_url:
                    sid = s["study_id"]
                    filename = f"{sid}_report.pdf"
                    target_path = str(PDF_DIR / filename)
                    catalog[sid] = {
                        "study_id": sid,
                        "title": s["title"],
                        "date": s["date"],
                        "scale": s["scale"],
                        "pdf_url": pdf_url,
                        "pdf_filename": filename,
                        "pdf_path": target_path,
                        "page_count": 0,
                        "downloaded": False,
                        "status": "pending"
                    }
        with open(CATALOG_PATH, "w", encoding="utf-8") as f:
            json.dump(catalog, f, indent=2, ensure_ascii=False)

    # Step B: Download any missing PDFs concurrently
    to_download = []
    for sid, info in catalog.items():
        target_path = info["pdf_path"]
        if not os.path.exists(target_path) or os.path.getsize(target_path) < 1000:
            to_download.append(info)

    if to_download:
        print(f"Downloading {len(to_download)} PDF reports ({len(catalog) - len(to_download)} already cached)...")
        import concurrent.futures
        def do_download(info):
            sid = info["study_id"]
            url = info["pdf_url"]
            path = info["pdf_path"]
            try:
                download_file(url, path)
                # Count pages
                doc = fitz.open(path)
                info["page_count"] = len(doc)
                doc.close()
                info["downloaded"] = True
                print(f"  [OK] [{sid}] Downloaded ({info['page_count']} pages)")
            except Exception as e:
                print(f"  [FAIL] [{sid}] Download failed: {e}")
            return info

        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as ex:
            futs = [ex.submit(do_download, item) for item in to_download]
            for f in concurrent.futures.as_completed(futs):
                f.result()

        with open(CATALOG_PATH, "w", encoding="utf-8") as f:
            json.dump(catalog, f, indent=2, ensure_ascii=False)

    # Ensure page counts are populated for all downloaded files
    updated = False
    for sid, info in catalog.items():
        if info.get("page_count", 0) == 0 and os.path.exists(info["pdf_path"]):
            try:
                doc = fitz.open(info["pdf_path"])
                info["page_count"] = len(doc)
                doc.close()
                info["downloaded"] = True
                updated = True
            except Exception:
                pass
    if updated:
        with open(CATALOG_PATH, "w", encoding="utf-8") as f:
            json.dump(catalog, f, indent=2, ensure_ascii=False)

    total_pages = sum(item.get("page_count", 0) for item in catalog.values())
    print(f"\nCatalog up to date: {len(catalog)} reports ready. Total pages: {total_pages}")
    return catalog

if __name__ == "__main__":
    build_or_update_catalog()
