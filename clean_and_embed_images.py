import os
import re
import fitz
from pathlib import Path
from bs4 import BeautifulSoup

out_dir = Path(r"c:\Users\cedbo\OneDrive\Documents\pedo\output_html")
pdf_dir = Path(r"c:\Users\cedbo\OneDrive\Documents\pedo\data\pdf")
images_base_dir = out_dir / "images"
images_base_dir.mkdir(exist_ok=True)

html_files = sorted([f for f in out_dir.glob("*.html") if f.name != "index.html"])
print(f"Processing {len(html_files)} HTML reports for image embedding and removing page-block wrappers...")

total_images_embedded = 0
total_cleaned = 0

for hf in html_files:
    sid = hf.stem
    pdf_path = pdf_dir / f"{sid}_report.pdf"
    if not pdf_path.exists():
        # check if prefix exists
        matches = list(pdf_dir.glob(f"{sid}*.pdf"))
        if matches:
            pdf_path = matches[0]
            
    doc = fitz.open(pdf_path) if pdf_path.exists() else None
    study_img_dir = images_base_dir / sid

    soup = BeautifulSoup(hf.read_text(encoding="utf-8"), "html.parser")
    modified = False

    # 1. Process images inside <figure> or <img>
    # Find all figures or images and determine their page index
    for figure in soup.find_all("figure"):
        # Check if figure is inside a page block or has page number
        # Look backwards for page number in parents or previous siblings
        p_num = None
        curr = figure
        while curr:
            if curr.get("id") and curr.get("id", "").startswith("page-"):
                try:
                    p_num = int(curr.get("id").replace("page-", ""))
                    break
                except ValueError:
                    pass
            curr = curr.parent

        if p_num and doc and 1 <= p_num <= len(doc):
            study_img_dir.mkdir(exist_ok=True)
            img_rel_path = f"images/{sid}/page_{p_num:03d}.jpg"
            img_full_path = out_dir / img_rel_path
            
            if not img_full_path.exists():
                page = doc[p_num - 1]
                # Render high-res image of page illustration
                pix = page.get_pixmap(dpi=180)
                pix.save(img_full_path)
            
            # Remove any placeholder or broken img
            for ph in figure.find_all(class_="figure-image-placeholder"):
                ph.decompose()
            for existing_img in figure.find_all("img"):
                existing_img.decompose()
                
            # Insert real image
            new_img = soup.new_tag("img", attrs={
                "src": img_rel_path,
                "alt": f"Illustration - Page {p_num}",
                "class": "report-illustration",
                "style": "max-width: 100%; height: auto; border: 1px solid #cbd5e1; border-radius: 4px; margin: 15px 0;"
            })
            # Insert before figcaption if present, else at beginning of figure
            fc = figure.find("figcaption")
            if fc:
                fc.insert_before(new_img)
            else:
                figure.append(new_img)
            total_images_embedded += 1
            modified = True

    # Also handle standalone <img> tags that might not be in a <figure>
    for img in soup.find_all("img"):
        src = img.get("src", "")
        if not src.startswith("images/"):
            # determine page
            p_num = None
            curr = img
            while curr:
                if curr.get("id") and curr.get("id", "").startswith("page-"):
                    try:
                        p_num = int(curr.get("id").replace("page-", ""))
                        break
                    except ValueError:
                        pass
                curr = curr.parent
            if p_num and doc and 1 <= p_num <= len(doc):
                study_img_dir.mkdir(exist_ok=True)
                img_rel_path = f"images/{sid}/page_{p_num:03d}.jpg"
                img_full_path = out_dir / img_rel_path
                if not img_full_path.exists():
                    page = doc[p_num - 1]
                    pix = page.get_pixmap(dpi=180)
                    pix.save(img_full_path)
                img["src"] = img_rel_path
                img["style"] = "max-width: 100%; height: auto; border: 1px solid #cbd5e1; border-radius: 4px; margin: 15px 0;"
                modified = True

    if doc:
        doc.close()

    # 2. Remove all .page-marker elements
    for pm in soup.find_all(class_="page-marker"):
        pm.decompose()
        modified = True

    # 3. Unwrap all .page-block containers (removes class="page-block")
    for pb in soup.find_all(class_="page-block"):
        # unwrap keeps children and removes the div container
        pb.unwrap()
        modified = True

    if modified:
        hf.write_text(str(soup), encoding="utf-8")
        total_cleaned += 1

print(f"\nDone! Cleaned and updated {total_cleaned} HTML reports.")
print(f"Total authentic report images embedded: {total_images_embedded}")
