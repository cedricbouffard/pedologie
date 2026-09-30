import os
import fitz # PyMuPDF
from .config import CACHE_IMAGES_DIR, DPI

def get_page_image_path(study_id: str, page_num: int) -> str:
    """Return cache path for a rendered page image."""
    study_cache = CACHE_IMAGES_DIR / study_id
    study_cache.mkdir(parents=True, exist_ok=True)
    return str(study_cache / f"page_{page_num:03d}.png")

def render_page_to_image(pdf_path: str, study_id: str, page_num: int, dpi: int = DPI) -> str:
    """Render a single PDF page (0-indexed) to an image file and return the path."""
    target_path = get_page_image_path(study_id, page_num)
    if os.path.exists(target_path) and os.path.getsize(target_path) > 1000:
        return target_path

    doc = fitz.open(pdf_path)
    if page_num >= len(doc):
        doc.close()
        raise IndexError(f"Page {page_num} out of bounds for {pdf_path} (length {len(doc)})")
    
    page = doc[page_num]
    pix = page.get_pixmap(dpi=dpi)
    pix.save(target_path)
    doc.close()
    return target_path

def cleanup_study_images(study_id: str):
    """Optionally remove rendered PNG images for a study after transcription to save disk space."""
    study_cache = CACHE_IMAGES_DIR / study_id
    if study_cache.exists():
        for f in study_cache.glob("*.png"):
            try:
                f.unlink()
            except OSError:
                pass
