from pathlib import Path

log_file = Path(r"C:\Users\cedbo\.gemini\antigravity\brain\0ca5d176-0dd0-4c83-b129-30bba4d04aa2\.system_generated\tasks\task-427.log")
lines = log_file.read_text(encoding="utf-8", errors="ignore").splitlines()
for l in lines[-30:]:
    print(l)

p51 = Path(r"c:\Users\cedbo\OneDrive\Documents\pedo\data\transcriptions\pq51b-v2")
if p51.exists():
    files = list(p51.glob("*.html"))
    print(f"pq51b-v2: {len(files)}/133 pages")
    missing = [i for i in range(133) if not (p51 / f"page_{i:03d}.html").exists()]
    print("Missing in pq51b-v2:", missing)

out = Path(r"c:\Users\cedbo\OneDrive\Documents\pedo\output_html")
print("Assembled v2 reports:")
for h in out.glob("*-v2.html"):
    print(" ", h.name, f"{h.stat().st_size/1024:.1f} KB")
