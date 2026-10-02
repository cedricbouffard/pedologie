"""
Script de conversion et d'optimisation de la couverture pédologique du Québec en PMTiles.
Utilise freestiler (moteur vectoriel Rust) pour générer les tuiles vectorielles MVT
avec conservation des couleurs officielles et des composantes détaillées (Desc_sol, Pourcentage, URLs).
"""

import sqlite3
import xml.etree.ElementTree as ET
import json
import re
import unicodedata
from pathlib import Path
import geopandas as gpd
from freestiler import freestile

BASE_URL_SERIES = "https://cedricbouffard.github.io/pedologie/series"
BASE_URL_ETUDES = "https://cedricbouffard.github.io/pedologie"

def slugify(text: str) -> str:
    if not text:
        return ""
    text = unicodedata.normalize('NFD', text)
    text = "".join(c for c in text if unicodedata.category(c) != 'Mn')
    text = re.sub(r'[^a-zA-Z0-9]+', '-', text).strip('-').lower()
    return text

def extract_colors_from_gpkg(gpkg_path: Path) -> dict:
    conn = sqlite3.connect(gpkg_path)
    cur = conn.cursor()
    cur.execute("SELECT styleSLD FROM layer_styles WHERE f_table_name = 'Couverture_pedologique'")
    row = cur.fetchone()
    conn.close()
    
    colors = {}
    if not row or not row[0]:
        return colors

    root = ET.fromstring(row[0])
    for rule in root.findall(".//{*}Rule"):
        lit = rule.find(".//{*}PropertyIsEqualTo/{*}Literal")
        fill = rule.find(".//{*}SvgParameter[@name='fill']")
        if lit is not None and lit.text and fill is not None and fill.text:
            colors[lit.text.strip()] = fill.text.strip()
            
    print(f"Extracted {len(colors)} official style colors from GeoPackage SLD.")
    return colors

def get_existing_series_slugs(series_dir: Path) -> set:
    if not series_dir.exists():
        return set()
    return {f.stem for f in series_dir.glob("*.html") if f.name != "index.html"}

def find_series_slug(desc_sol: str, existing_slugs: set) -> str | None:
    if not desc_sol:
        return None
    words = desc_sol.split()
    for i in range(len(words), 0, -1):
        cand = slugify(" ".join(words[:i]))
        if cand in existing_slugs:
            return cand
    return None

def prepare_components_map(gpkg_path: Path, existing_slugs: set) -> dict:
    conn = sqlite3.connect(gpkg_path)
    cur = conn.cursor()
    
    print("Querying components from Couverture_pps and Proprietes_pedologiques...")
    query = """
        SELECT 
            pps.Code_polygone,
            pps.Numero_composante,
            pps.Pourcentage,
            prop.Desc_sol
        FROM Couverture_pps pps
        LEFT JOIN Proprietes_pedologiques prop ON pps.Composante = prop.Composante
        ORDER BY pps.Code_polygone, pps.Numero_composante
    """
    cur.execute(query)
    
    poly_components = {}
    for poly_id, num_comp, pct, desc in cur.fetchall():
        if poly_id not in poly_components:
            poly_components[poly_id] = []
        
        desc_clean = (desc or "").strip()
        slug = find_series_slug(desc_clean, existing_slugs)
        url = f"{BASE_URL_SERIES}/{slug}.html" if slug else None
        
        poly_components[poly_id].append({
            "num": num_comp,
            "pct": int(pct) if pct is not None else 0,
            "desc": desc_clean,
            "url": url
        })
        
    conn.close()
    print(f"Prepared components for {len(poly_components)} polygons.")
    return poly_components

def build_pedologie_pmtiles(
    gpkg_path: str = "couverture_pedologique_2026_01.gpkg",
    output_pmtiles: str = "couverture_pedologique.pmtiles",
    min_zoom: int = 5,
    max_zoom: int = 14,
    limit: int | None = None
):
    gpkg_file = Path(gpkg_path)
    series_dir = Path("output_html/series")
    
    # 1. Couleurs officielles
    colors = extract_colors_from_gpkg(gpkg_file)
    default_color = "#b0b0b0"
    
    # 2. Slugs des séries existantes
    existing_slugs = get_existing_series_slugs(series_dir)
    print(f"Loaded {len(existing_slugs)} existing series pages.")
    
    # 3. Préparer les composantes (Desc_sol + Pourcentage)
    comp_map = prepare_components_map(gpkg_file, existing_slugs)
    
    # 4. Charger la couche spatiale via GeoPandas
    print(f"Loading Couverture_pedologique from {gpkg_path}...")
    gdf = gpd.read_file(
        gpkg_file, 
        layer="Couverture_pedologique", 
        columns=["Code_polygone", "Appellation_cartographique", "No_etude", "Symbole"], 
        max_features=limit
    )
    print(f"Loaded {len(gdf)} polygon geometries.")
    
    # Reprojection en WGS84 (EPSG:4326) si nécessaire
    if gdf.crs and gdf.crs.to_epsg() != 4326:
        print(f"Reprojecting from {gdf.crs} to EPSG:4326...")
        gdf = gdf.to_crs(epsg=4326)
        
    # 5. Enrichir chaque polygone
    print("Enriching polygons with colors and components...")
    
    colors_list = []
    etude_code_list = []
    etude_url_list = []
    label_sols_list = []
    series_json_list = []
    
    s1_desc_list = []
    s1_pct_list = []
    s1_url_list = []
    
    s2_desc_list = []
    s2_pct_list = []
    s2_url_list = []
    
    s3_desc_list = []
    s3_pct_list = []
    s3_url_list = []

    s4_desc_list = []
    s4_pct_list = []
    s4_url_list = []
    
    for row in gdf.itertuples():
        poly_id = row.Code_polygone
        symbole = getattr(row, "Symbole", "")
        no_etude = getattr(row, "No_etude", None)
        
        # Couleur officielle
        colors_list.append(colors.get(symbole, default_color))
        
        # Étude
        if no_etude:
            e_code = f"pq{int(no_etude):02d}" if str(no_etude).isdigit() else f"pq{no_etude}"
            e_url = f"{BASE_URL_ETUDES}/{e_code}.html"
        else:
            e_code = ""
            e_url = ""
        etude_code_list.append(e_code)
        etude_url_list.append(e_url)
        
        # Composantes
        comps = comp_map.get(poly_id, [])
        labels = [f"{c['desc']} ({c['pct']}%)" for c in comps if c['desc']]
        label_sols_list.append(" + ".join(labels) if labels else getattr(row, "Appellation_cartographique", ""))
        
        # JSON compact pour GéoLibre
        series_json_list.append(json.dumps([
            {"desc": c["desc"], "pct": c["pct"], "url": c["url"]}
            for c in comps if c["desc"]
        ], ensure_ascii=False))
        
        # Colonnes directes s1, s2, s3
        c1 = comps[0] if len(comps) > 0 else {}
        s1_desc_list.append(c1.get("desc", ""))
        s1_pct_list.append(c1.get("pct", 0))
        s1_url_list.append(c1.get("url", ""))
        
        c2 = comps[1] if len(comps) > 1 else {}
        s2_desc_list.append(c2.get("desc", ""))
        s2_pct_list.append(c2.get("pct", 0))
        s2_url_list.append(c2.get("url", ""))
        
        c3 = comps[2] if len(comps) > 2 else {}
        s3_desc_list.append(c3.get("desc", ""))
        s3_pct_list.append(c3.get("pct", 0))
        s3_url_list.append(c3.get("url", ""))

        c4 = comps[3] if len(comps) > 3 else {}
        s4_desc_list.append(c4.get("desc", ""))
        s4_pct_list.append(c4.get("pct", 0))
        s4_url_list.append(c4.get("url", ""))

    gdf["color"] = colors_list
    gdf["etude_code"] = etude_code_list
    gdf["etude_url"] = etude_url_list
    gdf["label_sols"] = label_sols_list
    gdf["series_json"] = series_json_list
    
    gdf["s1_desc"] = s1_desc_list
    gdf["s1_pct"] = s1_pct_list
    gdf["s1_url"] = s1_url_list
    
    gdf["s2_desc"] = s2_desc_list
    gdf["s2_pct"] = s2_pct_list
    gdf["s2_url"] = s2_url_list
    
    gdf["s3_desc"] = s3_desc_list
    gdf["s3_pct"] = s3_pct_list
    gdf["s3_url"] = s3_url_list

    gdf["s4_desc"] = s4_desc_list
    gdf["s4_pct"] = s4_pct_list
    gdf["s4_url"] = s4_url_list

    # 6. Génération PMTiles via freestiler
    print(f"Generating PMTiles archive: {output_pmtiles} (zooms {min_zoom} to {max_zoom})...")
    out_path = freestile(
        gdf,
        output_pmtiles,
        layer_name="pedologie_quebec",
        min_zoom=min_zoom,
        max_zoom=max_zoom,
        simplification=True,
        overwrite=True
    )
    
    size_mb = Path(output_pmtiles).stat().st_size / (1024 * 1024)
    print(f"PMTiles generated successfully: {out_path} ({size_mb:.2f} MB)")
    return out_path

if __name__ == "__main__":
    import sys
    limit_val = 2000 if "--test" in sys.argv else None
    out_name = "sample_pedologie.pmtiles" if limit_val else "couverture_pedologique.pmtiles"
    build_pedologie_pmtiles(output_pmtiles=out_name, limit=limit_val)
