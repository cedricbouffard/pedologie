import json
import urllib.request
import urllib.parse
from bs4 import BeautifulSoup
import os
import fitz

BASE_INDEX_URL = "https://sis.agr.gc.ca/siscan/publications/surveys/pq/index.html"
BASE_DOMAIN = "https://sis.agr.gc.ca"

print("--- 1. Checking for studies with multiple non-map PDFs ---")
req = urllib.request.Request(BASE_INDEX_URL, headers={"User-Agent": "Mozilla/5.0"})
with urllib.request.urlopen(req, timeout=30) as resp:
    html = resp.read().decode("utf-8", errors="ignore")

soup = BeautifulSoup(html, "html.parser")
dss_anchor = soup.find("a", {"name": "DSS"})
table = dss_anchor.find_next("table")
rows = table.find_all("tr")[1:]

studies = []
for r in rows:
    cols = r.find_all(["th", "td"])
    if len(cols) >= 5:
        sid = cols[0].get_text(strip=True)
        title = cols[1].get_text(strip=True)
        link = cols[4].find("a")
        href = link["href"] if link else None
        if href:
            studies.append((sid, title, urllib.parse.urljoin(BASE_DOMAIN, href)))

multi_pdf_studies = []
import concurrent.futures

def inspect_study_pdfs(s):
    sid, title, url = s
    try:
        r = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(r, timeout=15) as resp:
            p_html = resp.read().decode("utf-8", errors="ignore")
        p_soup = BeautifulSoup(p_html, "html.parser")
        
        pdf_links = []
        for a in p_soup.find_all("a", href=True):
            href = a["href"]
            if href.lower().endswith(".pdf"):
                text = a.get_text(strip=True)
                parent = a.find_parent(["div", "section", "p", "li"])
                ptext = parent.get_text(" ", strip=True) if parent else ""
                full_href = urllib.parse.urljoin(url, href)
                pdf_links.append({
                    "href": full_href,
                    "filename": href.split("/")[-1],
                    "text": text,
                    "context": ptext
                })
        
        # Deduplicate by full URL
        dedup = {}
        for p in pdf_links:
            dedup[p["href"]] = p
        
        # Now classify maps vs non-maps
        non_maps = []
        maps = []
        for p in dedup.values():
            fn = p["filename"].lower()
            txt = p["text"].lower()
            ctx = p["context"].lower()
            combo = fn + " " + txt + " " + ctx
            
            # Is it a map?
            # Maps usually have 'carte' without 'légende et carte' or 'rapport', or are numbered sheet files
            is_map = False
            if "carte" in combo or "map" in combo:
                # Check if it is a standalone map sheet vs report
                if not ("rapport" in fn or "report" in fn or "bulletin" in fn or "etude" in fn or "étude" in fn):
                    is_map = True
            if "_map.pdf" in fn or "_carte" in fn:
                is_map = True
                
            if is_map:
                maps.append(p)
            else:
                non_maps.append(p)
                
        return sid, title, url, non_maps, maps
    except Exception as e:
        return sid, title, url, str(e), []

with concurrent.futures.ThreadPoolExecutor(max_workers=8) as ex:
    results = list(ex.map(inspect_study_pdfs, studies))

print(f"\nInspection complete on {len(results)} studies.")
for sid, title, url, non_maps, maps in results:
    if isinstance(non_maps, list) and len(non_maps) > 1:
        print(f"\n>>> Study {sid} has {len(non_maps)} NON-MAP PDFs:")
        for nm in non_maps:
            print(f"    - Filename: {nm['filename']} | Text: {nm['text']} | Ctx: {nm['context'][:60]}")
    elif isinstance(non_maps, list) and len(non_maps) == 0:
        print(f"\n>>> Study {sid} has 0 non-map PDFs! Total maps: {len(maps)}")
        for m in maps:
            print(f"    - Map: {m['filename']} | Text: {m['text']}")

print("\n--- 2. Checking image extraction in PDFs (e.g. pq17, pq8a, pq4) ---")
for sample_id in ["pq17", "pq8a", "pq4"]:
    pdf_path = f"c:\\Users\\cedbo\\OneDrive\\Documents\\pedo\\data\\pdf\\{sample_id}_report.pdf"
    if os.path.exists(pdf_path):
        doc = fitz.open(pdf_path)
        total_images = 0
        pages_with_images = 0
        for pno in range(len(doc)):
            imgs = doc[pno].get_images()
            if imgs:
                total_images += len(imgs)
                pages_with_images += 1
        print(f"[{sample_id}] Total PDF pages: {len(doc)} | Pages with XObject images: {pages_with_images} | Total XObject images: {total_images}")
        if sample_id == "pq17":
            # inspect page 56 and 60
            for p in [55, 59]:
                print(f"  pq17 page {p+1} images:", doc[p].get_images())
        doc.close()
