import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# Data directories
DATA_DIR = BASE_DIR / "data"
PDF_DIR = DATA_DIR / "pdf"
CACHE_IMAGES_DIR = DATA_DIR / "cache_images"
TRANSCRIPTIONS_DIR = DATA_DIR / "transcriptions"
CATALOG_PATH = DATA_DIR / "catalog.json"

# Output directories
OUTPUT_DIR = BASE_DIR / "output_html"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
PDF_DIR.mkdir(parents=True, exist_ok=True)
CACHE_IMAGES_DIR.mkdir(parents=True, exist_ok=True)
TRANSCRIPTIONS_DIR.mkdir(parents=True, exist_ok=True)

# Load GEMINI_API_KEY from .env
ENV_FILE = BASE_DIR / ".env"
GEMINI_API_KEY = None
if ENV_FILE.exists():
    with open(ENV_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line.startswith("GEMINI_API_KEY="):
                GEMINI_API_KEY = line.split("=", 1)[1].strip()

if not GEMINI_API_KEY:
    GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# Model configuration
MODEL_NAME = "gemini-3.5-flash-lite"
MAX_WORKERS = 4  # Concurrency limit for API calls
DPI = 180        # Rendering resolution: 180 DPI offers great clarity and fast processing
