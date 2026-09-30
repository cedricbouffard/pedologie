#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
portal_generator.py - Générateur du Registre Officiel des Études Pédologiques du Québec.
Direction artistique : Registre d'archives nationales, cartographie et bibliothèque savante.
Format exclusif : Grand Registre Récapitulatif (table d'inventaire souveraine).
"""

import json
import re
from pathlib import Path

BASE_DIR = Path(r"c:\Users\cedbo\OneDrive\Documents\pedo")
CATALOG_PATH = BASE_DIR / "data" / "catalog.json"
OUTPUT_DIR = BASE_DIR / "output_html"
OUTPUT_ETUDES_PATH = OUTPUT_DIR / "etudes.html"
SEARCH_INDEX_PATH = OUTPUT_DIR / "search_index.json"

# Mapping explicite des régions et toponymes majeurs pour chaque étude
GEO_REGIONS = {
    "pq1b": "Abitibi-Témiscamingue",
    "pq2": "Argenteuil, Deux-Montagnes & Terrebonne",
    "pq4": "Arthabaska",
    "pq5": "Bagot",
    "pq6": "Beauce",
    "pq7": "Huntingdon & Beauharnois",
    "pq8": "Bellechasse & Montmagny",
    "pq8a": "Bellechasse",
    "pq9": "Berthier",
    "pq10a": "Bonaventure",
    "pq11": "Shefford, Brome & Missisquoi",
    "pq12a": "Chambly (Carte & Légende)",
    "pq12b": "Chambly (Volume 1)",
    "pq12b-v2": "Chambly (Volume 2)",
    "pq12c": "Chambly",
    "pq13": "Champlain & Laviolette",
    "pq14": "Charlevoix",
    "pq16": "Châteauguay",
    "pq17": "Chicoutimi",
    "pq18": "Stanstead, Richmond, Sherbrooke & Compton",
    "pq18b": "Richmond",
    "pq19": "Dorchester",
    "pq20": "Drummond",
    "pq21": "Frontenac",
    "pq2223": "Bas-Saint-Laurent & Gaspésie",
    "pq233": "Îles-de-la-Madeleine",
    "pq235": "Kamouraska",
    "pq24": "Gatineau & Pontiac",
    "pq25": "Hull, Labelle & Papineau",
    "pq26": "Iberville",
    "pq27": "Îles-de-la-Madeleine",
    "pq28": "Joliette",
    "pq28b": "Région de Joliette",
    "pq29": "Kamouraska",
    "pq30": "Lac-Saint-Jean",
    "pq31a": "Laprairie (Carte 1943)",
    "pq31b": "Laprairie",
    "pq32": "L'Assomption & Montcalm",
    "pq32b": "L'Assomption (Carte)",
    "pq33": "Lévis",
    "pq33b": "Lévis (Ferme de Chapais)",
    "pq34": "L'Islet",
    "pq35": "Lotbinière",
    "pq36": "Maskinongé",
    "pq37-38": "Matane & Matapédia",
    "pq39": "Mégantic",
    "pq39a": "Bras d'Henri (Bassin versant)",
    "pq41": "Montréal, Île Jésus & Bizard",
    "pq42": "Napierville (Carte 1943)",
    "pq42b": "Napierville",
    "pq43": "Nicolet",
    "pq44": "Portneuf",
    "pq46a": "Richelieu (Carte 1942)",
    "pq46b": "Richelieu (Volume 1)",
    "pq46b-v2": "Richelieu (Volume 2)",
    "pq47": "Rimouski",
    "pq48": "Rivière-du-Loup",
    "pq49a": "Rouville (Carte 1942)",
    "pq49b": "Rouville",
    "pq50": "Sept-Îles",
    "pq51a": "Saint-Hyacinthe & Bagot",
    "pq51b": "Saint-Hyacinthe (Volume 1)",
    "pq51b-v2": "Saint-Hyacinthe (Volume 2)",
    "pq52a": "Saint-Jean (Carte 1942)",
    "pq52b": "Saint-Jean",
    "pq53": "Soulanges & Vaudreuil",
    "pq55": "Témiscouata",
    "pq56": "Trois-Rivières & Saint-Maurice",
    "pq57a": "Verchères (Carte 1942)",
    "pq57b": "Verchères (Volume 1)",
    "pq57b-v2": "Verchères (Volume 2)",
    "pq58": "Wolfe",
    "pq59": "Yamaska",
    "pq60": "Îles d'Orléans, Coudres & Grues",
    "pq62": "Vergers de la Province de Québec",
    "pq63": "Sols Organiques du Sud-Ouest",
    "pq96-09": "Île Sainte-Thérèse (Verchères)",
    "pqrda1": "Côte-de-Beaupré (MRC)",
    "pqrda2": "Région de Québec (Ste-Foy/Valcartier)"
}


def format_code(sid: str) -> str:
    """Formatte le code SISCan de façon élégante, ex: pq8a -> PQ-8A."""
    s = sid.upper()
    if s.startswith("PQ"):
        rest = s[2:]
        if rest and not rest.startswith("-"):
            return f"PQ-{rest}"
    return s

def format_scale(raw_scale):
    """Formate une échelle cartographique, ex 50000 -> 1:50 000."""
    if not raw_scale:
        return "1:63 360", "Levé cartographique"
    try:
        val = int(raw_scale)
        if val == 0:
            return "Détail", "Levé de détail"
        if val == 63360:
            return "1:63 360", "1 po = 1 mi"
        if val == 126720:
            return "1:126 720", "1 po = 2 mi"
        return f"1:{val:,}".replace(",", " "), ""
    except Exception:
        return "Cartographie", ""

def get_decade_info(year_str):
    try:
        y = int(year_str)
    except Exception:
        return "1990s-plus", "1990 et +"
    if y < 1950:
        return "1936-1949", "1936–1949 (Pionniers)"
    elif 1950 <= y <= 1959:
        return "1950s", "Années 1950"
    elif 1960 <= y <= 1969:
        return "1960s", "Années 1960"
    elif 1970 <= y <= 1979:
        return "1970s", "Années 1970"
    elif 1980 <= y <= 1989:
        return "1980s", "Années 1980"
    else:
        return "1990s-plus", "1990 et après"

def get_horizon_accent(decade_key):
    """Couleur d'horizon pédologique selon la période pour donner du relief tactile."""
    accents = {
        "1936-1949": "horizon-ochre",   # Ocre antique
        "1950s": "horizon-earth",        # Terre cuite
        "1960s": "horizon-forest",       # Vert forêt
        "1970s": "horizon-moss",         # Mousse végétale
        "1980s": "horizon-slate",        # Ardoise
        "1990s-plus": "horizon-clay"     # Argile champlainienne
    }
    return accents.get(decade_key, "horizon-forest")

def clean_french_title(raw_title: str) -> str:
    t = raw_title.strip()
    if t and t[0].islower():
        t = t[0].upper() + t[1:]
    t = t.replace(" ,", ",").replace("  ", " ")
    return t

def generate_portal():
    print(f"Loading catalog from {CATALOG_PATH}...")
    with open(CATALOG_PATH, "r", encoding="utf-8") as f:
        catalog = json.load(f)

    # Récupération de l'index de recherche si existant pour lier les séries
    series_by_report = {}
    if SEARCH_INDEX_PATH.exists():
        with open(SEARCH_INDEX_PATH, "r", encoding="utf-8") as f:
            search_idx = json.load(f)
            for s in search_idx.get("series", []):
                code = s.get("code")
                if code:
                    series_by_report.setdefault(code, []).append(s.get("name", ""))

    # Compléter avec le comptage direct des séries caractérisées dans les fichiers HTML
    html_series_counts = {}
    for hf in OUTPUT_DIR.glob("*.html"):
        if hf.name == "index.html":
            continue
        try:
            content = hf.read_text(encoding="utf-8")
            c = len(re.findall(r'class="[^"]*soil-series-title[^"]*"', content))
            if c == 0:
                c = len(re.findall(r'<h2[^>]*>[^<]*\([A-Za-z0-9]{1,4}\)[^<]*</h2>', content))
            if c > 0:
                html_series_counts[hf.stem] = c
        except Exception:
            pass

    reports = []
    total_pages = 0

    for sid, info in sorted(catalog.items(), key=lambda x: x[0]):
        title = clean_french_title(info.get("title", ""))
        region = GEO_REGIONS.get(sid, title)
        year = str(info.get("date", "n/d"))
        pages = info.get("page_count", 0)
        total_pages += pages
        scale_main, scale_note = format_scale(info.get("scale"))
        pdf_url = info.get("pdf_url", "")
        code_disp = format_code(sid)
        decade_key, decade_label = get_decade_info(year)
        accent_class = get_horizon_accent(decade_key)
        series_count = max(len(series_by_report.get(sid, [])), html_series_counts.get(sid, 0))

        # Texte combiné pour filtre instantané rapide en Javascript
        search_blob = f"{sid} {code_disp} {region} {title} {year} {scale_main} {scale_note} {series_count} séries".lower()
        if sid in series_by_report:
            search_blob += " " + " ".join(series_by_report[sid][:10]).lower()

        reports.append({
            "sid": sid,
            "code_disp": code_disp,
            "region": region,
            "title": title,
            "year": year,
            "pages": pages,
            "scale_main": scale_main,
            "scale_note": scale_note,
            "pdf_url": pdf_url,
            "decade_key": decade_key,
            "decade_label": decade_label,
            "accent_class": accent_class,
            "series_count": series_count,
            "search_blob": search_blob
        })

    total_series_count = sum(r["series_count"] for r in reports) or 3198

    # Construction des lignes du Grand Registre (Table Rows)
    rows_html = []
    for r in reports:
        pdf_link = f'<a href="{r["pdf_url"]}" target="_blank" rel="noopener" class="reg-pdf-btn" title="Consulter le fac-similé original numérisé par Agriculture Canada (PDF)">PDF &rarr;</a>' if r["pdf_url"] else ''
        
        if r["series_count"] > 1:
            series_badge = f'<span class="reg-series-badge" title="Nombre de séries pédologiques caractérisées dans ce mémoire">{r["series_count"]}&nbsp;séries</span>'
        elif r["series_count"] == 1:
            series_badge = f'<span class="reg-series-badge" title="Nombre de séries pédologiques caractérisées dans ce mémoire">1&nbsp;série</span>'
        else:
            series_badge = '<span class="reg-series-badge" style="color: var(--ink-faint); font-weight: 400;" title="Aucune monographie de série distincte">—</span>'
        
        scale_html = f'<span class="reg-scale-val">{r["scale_main"]}</span>'
        if r["scale_note"]:
            scale_html += f'<span class="reg-scale-sub">{r["scale_note"]}</span>'

        row = f"""
        <tr class="reg-row {r['accent_class']}" 
            data-code="{r['sid']}" 
            data-region="{r['region'].lower()}" 
            data-title="{r['title'].lower()}" 
            data-year="{r['year']}" 
            data-pages="{r['pages']}"
            data-series="{r['series_count']}"
            data-decade="{r['decade_key']}" 
            data-search="{r['search_blob']}">
          <td class="col-cote">
            <a href="{r['sid']}.html" class="reg-cote-badge" title="Cote officielle SISCan">{r['code_disp']}</a>
          </td>
          <td class="col-region">
            <span class="reg-region-name">{r['region']}</span>
          </td>
          <td class="col-title">
            <a href="{r['sid']}.html" class="reg-title-link">{r['title']}</a>
          </td>
          <td class="col-year">
            <span class="reg-year-badge">{r['year']}</span>
          </td>
          <td class="col-scale">
            {scale_html}
          </td>
          <td class="col-volume">
            <div class="reg-vol-box">
              <span class="reg-pages-count"><strong>{r['pages']}</strong>&nbsp;pages</span>
              {series_badge}
            </div>
          </td>
          <td class="col-actions">
            <div class="reg-actions-box">
              <a href="{r['sid']}.html" class="reg-consult-btn">
                <span>Consulter</span>
                <span class="btn-arrow">&rarr;</span>
              </a>
              {pdf_link}
            </div>
          </td>
        </tr>"""
        rows_html.append(row)

    formatted_pages = f"{total_pages:,}".replace(",", " ")
    formatted_series = f"{total_series_count:,}".replace(",", " ")

    # HTML complet du registre des études
    portal_html = f"""<!DOCTYPE html>
<html lang="fr" class="portal-html">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1"/>
  <title>Études Pédologiques du Québec (1936–2017) — Inventaire Officiel</title>
  <meta name="description" content="Registre officiel des 79 mémoires d'inventaire pédologique du Québec publiés de 1936 à 2017 par Agriculture Canada et le MAPAQ."/>

  <!-- Typographie d'archive, de cartographie & de bibliothèque savante -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@500;600;700&family=Newsreader:ital,opsz,wght@0,6..72,400;0,6..72,500;0,6..72,600;0,6..72,700;1,6..72,400;1,6..72,600&family=Plus+Jakarta+Sans:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
  
  <link rel="stylesheet" href="style.css"/>
</head>
<body class="portal-body">

  <!-- Barre de navigation institutionnelle patrimoniale -->
  <nav class="portal-navbar" aria-label="Navigation principale">
    <div class="navbar-content">
      <a href="index.html" class="nav-brand">
        <div class="nav-titles">
          <span class="nav-brand-title">Inventaire Pédologique du Québec</span>
          <span class="nav-brand-sub">Archives agronomiques &amp; cartographiques • 1936–2017</span>
        </div>
      </a>
      <div class="nav-actions">
        <a href="index.html" class="nav-search-btn" style="text-decoration:none;margin-right:8px;" title="Retour à l'accueil du portail">
          <span>Accueil</span>
        </a>
        <a href="etudes.html" class="nav-search-btn active" style="text-decoration:none;margin-right:8px;font-weight:700;" title="Registre des 79 études régionales">
          <span>Études</span>
        </a>
        <a href="series/index.html" class="nav-search-btn" style="text-decoration:none;margin-right:8px;" title="Consulter le répertoire des séries de sols du Québec">
          <span>Séries de Sols</span>
        </a>
        <a href="glossaire.html" class="nav-search-btn" style="text-decoration:none;margin-right:8px;" title="Consulter le glossaire pédologique officiel">
          <span>Glossaire</span>
        </a>
        <button type="button" class="nav-search-btn" onclick="PedoSearch.open()" aria-label="Recherche globale plein-texte">
          <svg fill="none" stroke="currentColor" stroke-width="2" height="15" viewBox="0 0 24 24" width="15">
            <circle cx="11" cy="11" r="8"></circle>
            <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
          </svg>
          <span class="nav-search-text">Recherche plein-texte</span>
          <kbd class="nav-kbd">Ctrl+K</kbd>
        </button>
      </div>
    </div>
  </nav>

  <main class="portal-container" id="top">

    <nav class="breadcrumb" style="margin-bottom: 12px; margin-top: 10px;">
      <a href="index.html">Accueil</a> &rsaquo; 
      <span class="active">Études Pédologiques</span>
    </nav>

    <!-- Cartouche éditorial et frontispice -->
    <header class="portal-cartouche">
      <div class="cartouche-frame">
        <h1 class="cartouche-title">Les Études Pédologiques du Québec</h1>

        <!-- Registre des statistiques patrimoniales -->
        <div class="cartouche-stats-strip">
          <div class="stat-cell">
            <span class="stat-number">{len(reports)}</span>
            <span class="stat-name">Monographies régionales</span>
          </div>
          <div class="stat-divider"></div>
          <div class="stat-cell">
            <span class="stat-number">{formatted_pages}</span>
            <span class="stat-name">Pages et mémoires transcrits</span>
          </div>
          <div class="stat-divider"></div>
          <div class="stat-cell">
            <span class="stat-number">65 ans</span>
            <span class="stat-name">De recherches pédologiques</span>
          </div>
        </div>
      </div>
    </header>

    <!-- Pupitre de consultation : Recherche unifiée et filtres de terroir -->
    <section class="portal-console" aria-label="Filtres et recherche de la collection">
      
      <!-- Console de recherche principale unifiée -->
      <div class="console-search-bar">
        <div class="search-input-wrapper">
          <svg class="search-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="11" cy="11" r="8"></circle>
            <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
          </svg>
          <input type="text" 
                 id="unifiedSearchInput" 
                 class="search-input-field" 
                 placeholder="Rechercher une étude par comté, région, auteur, année ou cote (ex: Bellechasse, Arthabaska, 1961)..." 
                 autocomplete="off"
                 oninput="handleSearchInput()"/>
          <button type="button" id="searchClearBtn" class="search-clear-btn" onclick="clearSearch()" aria-label="Effacer la recherche" style="display: none;">✕</button>
        </div>
        <div class="search-indicator">
          <span id="resultsCountBadge" class="results-badge">{len(reports)} études au registre</span>
        </div>
      </div>

      <!-- Bandeau d'aide aux séries de sols (suggéré lors de la saisie) -->
      <div id="seriesSuggestionBox" class="series-suggestion-strip" style="display: none;">
        <span class="suggestion-label">Séries de sols correspondantes :</span>
        <div id="seriesSuggestionChips" class="suggestion-chips"></div>
      </div>

      <!-- Filtres d'époque et barre de commande -->
      <div class="console-controls-bar" id="studiesControlsBar">
        
        <!-- Périodes historiques -->
        <div class="decade-selector" id="decadeFilter" role="tablist" aria-label="Filtrer par époque de publication">
          <button type="button" class="tab-pill active" data-decade="all" role="tab" aria-selected="true">
            Toutes ({len(reports)})
          </button>
          <button type="button" class="tab-pill" data-decade="1936-1949" role="tab" aria-selected="false" title="Les pionniers de la pédologie québécoise">
            1936–1949
          </button>
          <button type="button" class="tab-pill" data-decade="1950s" role="tab" aria-selected="false">
            Années 1950
          </button>
          <button type="button" class="tab-pill" data-decade="1960s" role="tab" aria-selected="false">
            Années 1960
          </button>
          <button type="button" class="tab-pill" data-decade="1970s" role="tab" aria-selected="false">
            Années 1970
          </button>
          <button type="button" class="tab-pill" data-decade="1980s" role="tab" aria-selected="false">
            Années 1980
          </button>
          <button type="button" class="tab-pill" data-decade="1990s-plus" role="tab" aria-selected="false">
            1990 et après
          </button>
        </div>

        <!-- Options de tri rapide -->
        <div class="console-tools">
          <div class="sort-selector-wrapper">
            <label for="sortSelect" class="sort-label">Trier par :</label>
            <select id="sortSelect" class="sort-select" onchange="applySorting()">
              <option value="region-asc">Comté / Région (A → Z)</option>
              <option value="year-asc">Chronologique (1936 → 2017)</option>
              <option value="year-desc">Plus récents d'abord (2017 → 1936)</option>
              <option value="pages-desc">Volume (Pagination décroissante)</option>
              <option value="series-desc">Nombre de séries (Décroissant)</option>
              <option value="code-asc">Cote d'archive (PQ)</option>
            </select>
          </div>
        </div>
      </div>

    </section>

    <!-- Registre d'inventaire officiel -->
    <section class="register-folio-section" aria-label="Inventaire officiel">

      <div class="register-table-wrapper" id="reportsTableWrapper">
        <table class="register-table" id="reportsTable">
          <thead>
            <tr>
              <th class="th-cote sortable" onclick="handleHeaderSort('code-asc')" title="Trier par cote d'archive">
                <span class="th-content">Cote <span class="sort-indicator">↕</span></span>
              </th>
              <th class="th-region sortable active-sort" onclick="handleHeaderSort('region-asc')" title="Trier par comté ou région">
                <span class="th-content">Comté / Région <span class="sort-indicator">▲</span></span>
              </th>
              <th class="th-title">
                <span class="th-content">Titre officiel &amp; Objet de l'étude</span>
              </th>
              <th class="th-year sortable" onclick="handleHeaderSort('year-asc')" title="Trier par année de parution">
                <span class="th-content">Année <span class="sort-indicator">↕</span></span>
              </th>
              <th class="th-scale">
                <span class="th-content">Échelle</span>
              </th>
              <th class="th-volume sortable" onclick="handleHeaderSort('pages-desc')" title="Trier par volume et séries">
                <span class="th-content">Volume &amp; Séries <span class="sort-indicator">↕</span></span>
              </th>
              <th class="th-actions">
                <span class="th-content">Consultation</span>
              </th>
            </tr>
          </thead>
          <tbody id="tableBody">
            {''.join(rows_html)}
          </tbody>
        </table>
      </div>
    </section>

    <!-- État aucun résultat -->
    <div id="filterEmptyState" class="collection-empty-state" style="display: none;">
      <div class="empty-state-frame">
        <div class="empty-icon">📜</div>
        <h3 class="empty-title">Aucune étude ne correspond à votre recherche</h3>
        <p class="empty-desc">Aucun rapport pédologique ne correspond aux termes ou filtres sélectionnés.</p>
        <button type="button" class="empty-reset-btn" onclick="resetFilters()">
          Réinitialiser tous les critères
        </button>
      </div>
    </div>

    <!-- Colophon & Mentions légales -->
    <footer class="portal-colophon">
      <div class="colophon-seal">
        <div class="seal-line"></div>
        <span class="seal-icon">⚜</span>
        <div class="seal-line"></div>
      </div>
      <div class="colophon-text">
        <p class="colophon-heading">Corpus de l'Inventaire Pédologique du Québec (1936–2017)</p>
        <p class="colophon-sub">
          Sources bibliographiques primaires : Système d'information sur les sols du Canada (SISCan), 
          Direction générale de la recherche agronomique, Agriculture et Agroalimentaire Canada (AAC) 
          en partenariat avec le Ministère de l'Agriculture, des Pêcheries et de l'Alimentation du Québec (MAPAQ).
        </p>
        <p class="colophon-sub">
          79 études numérisées et transmutées en documents HTML sémantiques haute-fidélité.
        </p>
      </div>
    </footer>

  </main>

  <script src="search.js" defer></script>
  <script>
    // Variables d'état
    let currentDecade = 'all';
    let currentSort = 'region-asc';

    // Gestion des onglets de décennies
    document.querySelectorAll('#decadeFilter .tab-pill').forEach(pill => {{
      pill.addEventListener('click', () => {{
        document.querySelectorAll('#decadeFilter .tab-pill').forEach(p => {{
          p.classList.remove('active');
          p.setAttribute('aria-selected', 'false');
        }});
        pill.classList.add('active');
        pill.setAttribute('aria-selected', 'true');
        currentDecade = pill.getAttribute('data-decade');
        filterCollection();
      }});
    }});

    // Cible de recherche active : 'studies' | 'series' | 'glossary'
    let currentSearchTarget = 'studies';

    function setSearchTarget(target) {{
      currentSearchTarget = target;
      document.querySelectorAll('.search-target-tab').forEach(tab => {{
        const isActive = tab.getAttribute('data-target') === target;
        tab.classList.toggle('active', isActive);
        tab.setAttribute('aria-selected', isActive ? 'true' : 'false');
      }});

      const input = document.getElementById('unifiedSearchInput');
      const tableWrapper = document.getElementById('reportsTableWrapper');
      const controlsBar = document.getElementById('studiesControlsBar');
      const resultsPanel = document.getElementById('searchModeResults');
      const suggestions = document.getElementById('seriesSuggestionBox');
      const emptyState = document.getElementById('filterEmptyState');

      suggestions.style.display = 'none';

      if (target === 'studies') {{
        input.placeholder = "Rechercher une étude par comté, région, auteur, année ou cote...";
        tableWrapper.style.display = '';
        controlsBar.style.display = '';
        resultsPanel.style.display = 'none';
        filterCollection();
      }} else if (target === 'series') {{
        input.placeholder = "Rechercher une série par nom, symbole ou ordre (ex: Sainte-Rosalie, Kamouraska)...";
        tableWrapper.style.display = 'none';
        controlsBar.style.display = 'none';
        emptyState.style.display = 'none';
        resultsPanel.style.display = 'block';
        renderSeriesSearchResults(input.value.trim());
      }} else if (target === 'glossary') {{
        input.placeholder = "Rechercher une notion, un horizon ou un ordre (ex: Gleysol, Podzol, Ae, Bnt, Ortstein)...";
        tableWrapper.style.display = 'none';
        controlsBar.style.display = 'none';
        emptyState.style.display = 'none';
        resultsPanel.style.display = 'block';
        renderGlossarySearchResults(input.value.trim());
      }}
      input.focus();
    }}

    // Filtrage unifié en temps réel
    function handleSearchInput() {{
      const query = document.getElementById('unifiedSearchInput').value.trim();
      const clearBtn = document.getElementById('searchClearBtn');
      clearBtn.style.display = query ? 'flex' : 'none';

      if (currentSearchTarget === 'studies') {{
        filterCollection();
        checkSeriesSuggestions(query);
      }} else if (currentSearchTarget === 'series') {{
        renderSeriesSearchResults(query);
      }} else if (currentSearchTarget === 'glossary') {{
        renderGlossarySearchResults(query);
      }}
    }}

    function clearSearch() {{
      const input = document.getElementById('unifiedSearchInput');
      input.value = '';
      document.getElementById('searchClearBtn').style.display = 'none';
      document.getElementById('seriesSuggestionBox').style.display = 'none';
      if (currentSearchTarget === 'studies') {{
        filterCollection();
      }} else if (currentSearchTarget === 'series') {{
        renderSeriesSearchResults('');
      }} else if (currentSearchTarget === 'glossary') {{
        renderGlossarySearchResults('');
      }}
      input.focus();
    }}

    function normalizeText(str) {{
      return (str || '')
        .normalize('NFD')
        .replace(/[\\u0300-\\u036f]/g, '')
        .toLowerCase();
    }}

    function filterCollection() {{
      const rawQuery = document.getElementById('unifiedSearchInput').value;
      const query = normalizeText(rawQuery).trim();
      const terms = query.split(/\\s+/).filter(t => t.length > 0);

      const rows = document.querySelectorAll('.reg-row');
      let visibleCount = 0;

      rows.forEach(row => {{
        const decade = row.getAttribute('data-decade');
        const searchBlob = normalizeText(row.getAttribute('data-search'));

        const matchDecade = (currentDecade === 'all' || decade === currentDecade);
        
        let matchQuery = true;
        for (const t of terms) {{
          if (!searchBlob.includes(t)) {{
            matchQuery = false;
            break;
          }}
        }}

        if (matchDecade && matchQuery) {{
          row.style.display = '';
          visibleCount++;
        }} else {{
          row.style.display = 'none';
        }}
      }});

      // Mise à jour du badge de décompte
      const badge = document.getElementById('resultsCountBadge');
      if (rawQuery.trim() || currentDecade !== 'all') {{
        badge.textContent = visibleCount + (visibleCount > 1 ? ' études trouvées' : ' étude trouvée');
      }} else {{
        badge.textContent = visibleCount + ' études au registre';
      }}

      // Affichage de l'état vide si nécessaire
      const emptyState = document.getElementById('filterEmptyState');
      emptyState.style.display = visibleCount === 0 ? 'block' : 'none';
    }}

    // Tri de la collection
    function handleHeaderSort(targetMode) {{
      // Si on clique sur la même colonne, inverser le sens
      if (currentSort === targetMode) {{
        if (targetMode === 'region-asc') targetMode = 'region-desc';
        else if (targetMode === 'region-desc') targetMode = 'region-asc';
        else if (targetMode === 'year-asc') targetMode = 'year-desc';
        else if (targetMode === 'year-desc') targetMode = 'year-asc';
        else if (targetMode === 'pages-desc') targetMode = 'pages-asc';
        else if (targetMode === 'pages-asc') targetMode = 'pages-desc';
        else if (targetMode === 'code-asc') targetMode = 'code-desc';
        else if (targetMode === 'code-desc') targetMode = 'code-asc';
      }}
      currentSort = targetMode;
      const select = document.getElementById('sortSelect');
      if (select) {{
        select.value = targetMode.includes('asc') || targetMode === 'pages-desc' ? targetMode : select.value;
      }}
      applySorting(targetMode);
    }}

    function applySorting(forcedMode) {{
      const mode = forcedMode || document.getElementById('sortSelect').value;
      currentSort = mode;
      const tbody = document.getElementById('tableBody');
      const rows = Array.from(tbody.querySelectorAll('.reg-row'));

      const comparator = (a, b) => {{
        if (mode === 'region-asc') {{
          return (a.getAttribute('data-region') || '').localeCompare(b.getAttribute('data-region') || '', 'fr');
        }} else if (mode === 'region-desc') {{
          return (b.getAttribute('data-region') || '').localeCompare(a.getAttribute('data-region') || '', 'fr');
        }} else if (mode === 'year-asc') {{
          return parseInt(a.getAttribute('data-year') || 0) - parseInt(b.getAttribute('data-year') || 0);
        }} else if (mode === 'year-desc') {{
          return parseInt(b.getAttribute('data-year') || 0) - parseInt(a.getAttribute('data-year') || 0);
        }} else if (mode === 'pages-desc') {{
          return parseInt(b.getAttribute('data-pages') || 0) - parseInt(a.getAttribute('data-pages') || 0);
        }} else if (mode === 'pages-asc') {{
          return parseInt(a.getAttribute('data-pages') || 0) - parseInt(b.getAttribute('data-pages') || 0);
        }} else if (mode === 'series-desc') {{
          return parseInt(b.getAttribute('data-series') || 0) - parseInt(a.getAttribute('data-series') || 0);
        }} else if (mode === 'code-asc') {{
          return (a.getAttribute('data-code') || '').localeCompare(b.getAttribute('data-code') || '', undefined, {{numeric: true}});
        }} else if (mode === 'code-desc') {{
          return (b.getAttribute('data-code') || '').localeCompare(a.getAttribute('data-code') || '', undefined, {{numeric: true}});
        }}
        return 0;
      }};

      rows.sort(comparator);
      rows.forEach(r => tbody.appendChild(r));

      // Mettre à jour l'en-tête actif
      updateHeaderSortIndicators(mode);
    }}

    function updateHeaderSortIndicators(mode) {{
      document.querySelectorAll('.register-table th.sortable').forEach(th => {{
        th.classList.remove('active-sort');
        const ind = th.querySelector('.sort-indicator');
        if (ind) ind.textContent = '↕';
      }});

      let activeTh = null;
      let symbol = '▲';
      if (mode.startsWith('region')) {{
        activeTh = document.querySelector('.th-region');
        symbol = mode.endsWith('asc') ? '▲' : '▼';
      }} else if (mode.startsWith('year')) {{
        activeTh = document.querySelector('.th-year');
        symbol = mode.endsWith('asc') ? '▲' : '▼';
      }} else if (mode.startsWith('pages') || mode.startsWith('series')) {{
        activeTh = document.querySelector('.th-volume');
        symbol = mode.endsWith('desc') ? '▼' : '▲';
      }} else if (mode.startsWith('code')) {{
        activeTh = document.querySelector('.th-cote');
        symbol = mode.endsWith('asc') ? '▲' : '▼';
      }}

      if (activeTh) {{
        activeTh.classList.add('active-sort');
        const ind = activeTh.querySelector('.sort-indicator');
        if (ind) ind.textContent = symbol;
      }}
    }}

    // Index de recherche globale
    let globalSearchIndex = null;
    async function getIndexData() {{
      if (globalSearchIndex) return globalSearchIndex;
      try {{
        const res = await fetch('search_index.json');
        globalSearchIndex = await res.json();
        return globalSearchIndex;
      }} catch (e) {{
        return null;
      }}
    }}

    // Rendu dynamique de la recherche par Séries sur l'accueil
    async function renderSeriesSearchResults(rawQuery) {{
      const panel = document.getElementById('searchModeResults');
      const badge = document.getElementById('resultsCountBadge');
      const index = await getIndexData();
      if (!index || !index.series) {{
        panel.innerHTML = '<p class="search-empty-state">Chargement de l\\\'index des séries...</p>';
        return;
      }}

      const q = normalizeText(rawQuery).trim();
      if (!q) {{
        badge.textContent = index.series.length + ' séries au répertoire';
        let html = '<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;flex-wrap:wrap;gap:8px;">';
        html += '<div style="font-weight:600;font-size:0.95rem;color:var(--accent-forest);">🌱 Répertoire des Séries Pédologiques du Québec</div>';
        html += '<a href="series/index.html" class="reg-consult-btn" style="text-decoration:none;">Consulter l\\\'index complet (A-Z) →</a>';
        html += '</div>';
        html += '<p style="color:var(--ink-muted);font-size:0.88rem;margin:0 0 14px 0;">Saisissez le nom d\\\'une série ou un symbole de sol pour filtrer en direct parmi les monographies officielles.</p>';
        html += '<div class="mode-results-grid">';
        const samples = index.series.slice(0, 12);
        for (let i = 0; i < samples.length; i++) {{
          const s = samples[i];
          const clean = s.name.split('—')[0].replace(/^(?:la\\s+)?série\\s+(?:de\\s+)?/i, '').trim();
          html += '<a href="' + s.url + '" class="mode-result-card">';
          html += '<div class="mode-result-card-header">';
          html += '<span class="mode-result-card-title">' + clean + '</span>';
          html += '<span class="badge font-mono" style="font-size:0.75rem;">' + (s.code || 'SÉRIE') + '</span>';
          html += '</div>';
          html += '<div class="mode-result-card-desc">' + (s.report || 'Monographie pédologique québécoise') + '</div>';
          html += '</a>';
        }}
        html += '</div>';
        panel.innerHTML = html;
        return;
      }}

      const words = q.split(/\\s+/).filter(w => w.length > 0);
      const matches = [];

      for (let i = 0; i < index.series.length; i++) {{
        const s = index.series[i];
        const normName = normalizeText(s.name);
        const normCode = normalizeText(s.code || '');
        const normReport = normalizeText(s.report || '');

        let matchAll = true;
        for (let j = 0; j < words.length; j++) {{
          const w = words[j];
          if (!normName.includes(w) && !normCode.includes(w) && !normReport.includes(w)) {{
            matchAll = false;
            break;
          }}
        }}

        if (matchAll) {{
          matches.push(s);
          if (matches.length >= 60) break;
        }}
      }}

      badge.textContent = matches.length + (matches.length > 1 ? ' séries trouvées' : ' série trouvée');

      if (matches.length === 0) {{
        panel.innerHTML = '<div class="search-empty-state"><p>Aucune série ne correspond à « <strong>' + rawQuery + '</strong> ».</p><p class="search-tips">Vous pouvez aussi consulter l\\\'ensemble des séries dans le <a href="series/index.html" style="color:var(--accent-forest);text-decoration:underline;">Répertoire des Séries</a>.</p></div>';
        return;
      }}

      let html = '<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;flex-wrap:wrap;gap:8px;">';
      html += '<div style="font-weight:600;font-size:0.95rem;color:var(--accent-forest);">🌱 Séries correspondantes (' + matches.length + ')</div>';
      html += '<a href="series/index.html" class="reg-consult-btn" style="text-decoration:none;">Index complet A-Z →</a>';
      html += '</div>';
      html += '<div class="mode-results-grid">';
      for (let i = 0; i < matches.length; i++) {{
        const s = matches[i];
        const clean = s.name.split('—')[0].replace(/^(?:la\\s+)?série\\s+(?:de\\s+)?/i, '').trim();
        html += '<a href="' + s.url + '" class="mode-result-card">';
        html += '<div class="mode-result-card-header">';
        html += '<span class="mode-result-card-title">' + clean + '</span>';
        html += '<span class="badge font-mono" style="font-size:0.75rem;">' + (s.code || 'SÉRIE') + '</span>';
        html += '</div>';
        html += '<div class="mode-result-card-desc">' + (s.report || 'Monographie pédologique québécoise') + '</div>';
        html += '</a>';
      }}
      html += '</div>';
      panel.innerHTML = html;
    }}

    // Rendu dynamique de la recherche Glossaire sur l'accueil
    async function renderGlossarySearchResults(rawQuery) {{
      const panel = document.getElementById('searchModeResults');
      const badge = document.getElementById('resultsCountBadge');
      const index = await getIndexData();
      if (!index || !index.glossary) {{
        panel.innerHTML = '<p class="search-empty-state">Chargement du glossaire...</p>';
        return;
      }}

      const q = normalizeText(rawQuery).trim();
      if (!q) {{
        badge.textContent = index.glossary.length + ' termes au glossaire';
        let html = '<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;flex-wrap:wrap;gap:8px;">';
        html += '<div style="font-weight:600;font-size:0.95rem;color:var(--accent-forest);">📖 Glossaire Pédologique & Nomenclature Officielle</div>';
        html += '<a href="glossaire.html" class="reg-consult-btn" style="text-decoration:none;">Consulter le glossaire complet →</a>';
        html += '</div>';
        html += '<p style="color:var(--ink-muted);font-size:0.88rem;margin:0 0 14px 0;">Saisissez un concept, un ordre, un grand groupe ou un symbole d\\\'horizon (ex: Sol brun, Ae, Podzol, Ortstein) pour voir la définition normalisée du SCSS.</p>';
        html += '<div class="mode-results-grid">';
        const samples = index.glossary.slice(0, 12);
        for (let i = 0; i < samples.length; i++) {{
          const g = samples[i];
          html += '<a href="' + g.url + '" class="mode-result-card">';
          html += '<div class="mode-result-card-header">';
          html += '<span class="mode-result-card-title">' + g.name + '</span>';
          html += '<span class="badge" style="font-size:0.72rem;background:var(--surface-tint);">' + (g.category || 'SCSS') + '</span>';
          html += '</div>';
          html += '<div class="mode-result-card-desc">' + (g.definition ? g.definition.slice(0, 110) + '...' : 'Définition officielle SCSS') + '</div>';
          html += '</a>';
        }}
        html += '</div>';
        panel.innerHTML = html;
        return;
      }}

      const words = q.split(/\\s+/).filter(w => w.length > 0);
      const matches = [];

      for (let i = 0; i < index.glossary.length; i++) {{
        const g = index.glossary[i];
        const normName = normalizeText(g.name);
        const normDef = normalizeText(g.definition || '');
        const normCat = normalizeText(g.category || '');

        let matchAll = true;
        for (let j = 0; j < words.length; j++) {{
          const w = words[j];
          if (!normName.includes(w) && !normDef.includes(w) && !normCat.includes(w)) {{
            matchAll = false;
            break;
          }}
        }}

        if (matchAll) {{
          matches.push(g);
          if (matches.length >= 40) break;
        }}
      }}

      badge.textContent = matches.length + (matches.length > 1 ? ' termes trouvés' : ' terme trouvé');

      if (matches.length === 0) {{
        panel.innerHTML = '<div class="search-empty-state"><p>Aucun terme du glossaire ne correspond à « <strong>' + rawQuery + '</strong> ».</p><p class="search-tips">Explorez la liste thématique dans le <a href="glossaire.html" style="color:var(--accent-forest);text-decoration:underline;">Glossaire Pédologique</a>.</p></div>';
        return;
      }}

      let html = '<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;flex-wrap:wrap;gap:8px;">';
      html += '<div style="font-weight:600;font-size:0.95rem;color:var(--accent-forest);">📖 Termes du glossaire correspondants (' + matches.length + ')</div>';
      html += '<a href="glossaire.html" class="reg-consult-btn" style="text-decoration:none;">Glossaire complet →</a>';
      html += '</div>';
      html += '<div class="mode-results-grid">';
      for (let i = 0; i < matches.length; i++) {{
        const g = matches[i];
        html += '<a href="' + g.url + '" class="mode-result-card">';
        html += '<div class="mode-result-card-header">';
        html += '<span class="mode-result-card-title">' + g.name + '</span>';
        html += '<span class="badge" style="font-size:0.72rem;background:var(--surface-tint);">' + (g.category || 'SCSS') + '</span>';
        html += '</div>';
        html += '<div class="mode-result-card-desc">' + (g.definition ? g.definition.slice(0, 110) + '...' : 'Définition officielle SCSS') + '</div>';
        html += '</a>';
      }}
      html += '</div>';
      panel.innerHTML = html;
    }}

    async function checkSeriesSuggestions(rawQuery) {{
      const q = normalizeText(rawQuery).trim();
      const box = document.getElementById('seriesSuggestionBox');
      const container = document.getElementById('seriesSuggestionChips');

      if (!q || q.length < 3) {{
        box.style.display = 'none';
        return;
      }}

      const index = await getIndexData();
      if (!index || !index.series) return;

      const matchedSeries = [];
      const seen = new Set();

      for (const s of index.series) {{
        const nameNorm = normalizeText(s.name);
        if (nameNorm.includes(q)) {{
          const cleanName = s.name.split('—')[0].split('--')[0].replace(/^(?:la\\s+)?série\\s+(?:de\\s+)?/i, '').trim();
          if (!seen.has(cleanName) && cleanName.length > 2) {{
            seen.add(cleanName);
            matchedSeries.push({{ name: cleanName, url: s.url, report: s.report }});
            if (matchedSeries.length >= 4) break;
          }}
        }}
      }}

      if (matchedSeries.length > 0) {{
        container.innerHTML = matchedSeries.map(s => 
          `<a href="${{s.url}}" class="suggestion-pill" title="Voir la description dans : ${{s.report}}">
            <span class="pill-bullet">•</span> ${{s.name}} <span class="pill-arrow">&rarr;</span>
          </a>`
        ).join('');
        box.style.display = 'flex';
      }} else {{
        box.style.display = 'none';
      }}
    }}

    function resetFilters() {{
      document.getElementById('unifiedSearchInput').value = '';
      document.getElementById('searchClearBtn').style.display = 'none';
      document.getElementById('seriesSuggestionBox').style.display = 'none';
      document.getElementById('sortSelect').value = 'region-asc';
      document.querySelector('#decadeFilter .tab-pill[data-decade="all"]').click();
      applySorting('region-asc');
      filterCollection();
    }}

    // Initialiser le tri par région par défaut
    window.addEventListener('DOMContentLoaded', () => {{
      applySorting('region-asc');
    }});
  </script>
  <script src="search.js" defer></script>
</body>
</html>
"""

    print(f"Writing updated studies register to {OUTPUT_ETUDES_PATH}...")
    with open(OUTPUT_ETUDES_PATH, "w", encoding="utf-8") as f:
        f.write(portal_html)

    print("Studies register generated successfully at etudes.html!")

if __name__ == "__main__":
    generate_portal()
