import os
import fitz
from pathlib import Path
from bs4 import BeautifulSoup

out_dir = Path(r"c:\Users\cedbo\OneDrive\Documents\pedo\output_html")
pdf_dir = Path(r"c:\Users\cedbo\OneDrive\Documents\pedo\data\pdf")
images_dir = out_dir / "images"
images_dir.mkdir(exist_ok=True)

# Test on pq17
doc = fitz.open(pdf_dir / "pq17_report.pdf")
study_img_dir = images_dir / "pq17"
study_img_dir.mkdir(exist_ok=True)

for p_num in [55, 59]: # page 56 and 60
    page = doc[p_num]
    pix = page.get_pixmap(dpi=180)
    target_img = study_img_dir / f"page_{p_num+1:03d}.jpg"
    pix.save(target_img)
    print(f"Saved actual image from pq17 page {p_num+1} to {target_img}")

doc.close()
