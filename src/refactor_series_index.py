#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
refactor_series_index.py - Harmonise le tableau du répertoire des séries (series/index.html)
avec le design exact du grand registre des études (register-table, portal-navbar, console-search).
Garantit l'absence totale d'émojis.
"""

import re
from pathlib import Path

BASE_DIR = Path(r"c:\Users\cedbo\OneDrive\Documents\pedo")
SERIES_INDEX_PATH = BASE_DIR / "output_html" / "series" / "index.html"

def refactor_series_index():
    print(f"Reading {SERIES_INDEX_PATH}...")
    with open(SERIES_INDEX_PATH, "r", encoding="utf-8") as f:
        html = f.read()

    # Extraction des lignes existantes
    # <tr>
    #   <td><a href="abitibi.html" class="series-link"><strong>Abitibi</strong></a></td>
    #   <td><span class="badge font-mono">ABT</span></td>
    #   <td>Gleysolique</td>
    #   <td><small>Gleysol luvique orthique</small></td>
    #   <td style="text-align:right;"><a href="abitibi.html" class="btn btn-sm btn-outline">Consulter &rarr;</a></td>
    # </tr>
    pattern = re.compile(
        r'<tr>\s*<td><a href="([^"]+)"[^>]*><strong>([^<]+)</strong></a></td>\s*'
        r'<td><span class="badge font-mono">([^<]+)</span></td>\s*'
        r'<td>([^<]+)</td>\s*'
        r'<td><small>([^<]+)</small></td>',
        re.DOTALL
    )

    matches = pattern.findall(html)
    print(f"Extracted {len(matches)} series entries.")

    orders = sorted(list(set(m[3].strip() for m in matches if m[3].strip())))
    print(f"Found orders: {orders}")

    # Construction des lignes avec le design system .register-table
    rows_html = []
    for url, name, symbol, order, subgroup in matches:
        url_clean = url.strip()
        name_clean = name.strip()
        symbol_clean = symbol.strip()
        order_clean = order.strip()
        subgroup_clean = subgroup.strip()
        search_blob = f"{symbol_clean} {name_clean} {order_clean} {subgroup_clean}".lower()

        row = f"""
        <tr class="reg-row" 
            data-code="{symbol_clean.lower()}" 
            data-name="{name_clean.lower()}" 
            data-order="{order_clean.lower()}"
            data-subgroup="{subgroup_clean.lower()}"
            data-search="{search_blob}">
          <td class="col-cote">
            <a href="{url_clean}" class="reg-cote-badge font-mono" title="Symbole officiel de la série">{symbol_clean}</a>
          </td>
          <td class="col-title">
            <a href="{url_clean}" class="reg-title-link"><strong>{name_clean}</strong></a>
          </td>
          <td class="col-region">
            <span class="reg-region-name">{order_clean}</span>
          </td>
          <td class="col-scale">
            <span class="reg-scale-val">{subgroup_clean}</span>
          </td>
          <td class="col-actions">
            <div class="reg-actions-box">
              <a href="{url_clean}" class="reg-consult-btn">
                <span>Consulter</span>
                <span class="btn-arrow">&rarr;</span>
              </a>
            </div>
          </td>
        </tr>"""
        rows_html.append(row)

    table_body = "\n".join(rows_html)

    # Création de la page complète
    new_html = f"""<!DOCTYPE html>
<html lang="fr" class="portal-html">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1"/>
  <title>Répertoire des Séries de Sols du Québec — Inventaire Officiel</title>
  <meta name="description" content="Répertoire officiel des 699 séries pédologiques reconnues au Québec : classification SCSS, symboles officiels, ordres et sous-groupes."/>

  <!-- Typographie d'archive, de cartographie & de bibliothèque savante -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@500;600;700&family=Newsreader:ital,opsz,wght@0,6..72,400;0,6..72,500;0,6..72,600;0,6..72,700;1,6..72,400;1,6..72,600&family=Plus+Jakarta+Sans:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
  
  <link rel="stylesheet" href="../style.css"/>
</head>
<body class="portal-body">

  <!-- Barre de navigation institutionnelle patrimoniale -->
  <nav class="portal-navbar" aria-label="Navigation principale">
    <div class="navbar-content">
      <a href="../index.html" class="nav-brand">
        <div class="nav-titles">
          <span class="nav-brand-title">Inventaire Pédologique du Québec</span>
          <span class="nav-brand-sub">Archives agronomiques &amp; cartographiques • 1936–2017</span>
        </div>
      </a>
      <div class="nav-actions">
        <a href="../index.html" class="nav-search-btn" style="text-decoration:none;margin-right:8px;" title="Retour à l'accueil du portail">
          <span>Accueil</span>
        </a>
        <a href="../etudes.html" class="nav-search-btn" style="text-decoration:none;margin-right:8px;" title="Consulter les 79 mémoires d'inventaire pédologique régionaux">
          <span>Études</span>
        </a>
        <a href="index.html" class="nav-search-btn active" style="text-decoration:none;margin-right:8px;font-weight:700;" title="Consulter le répertoire des séries de sols du Québec">
          <span>Séries de Sols</span>
        </a>
        <a href="../glossaire.html" class="nav-search-btn" style="text-decoration:none;margin-right:8px;" title="Consulter le glossaire pédologique officiel">
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
      <a href="../index.html">Accueil</a> &rsaquo; 
      <span class="active">Répertoire des Séries de Sols</span>
    </nav>

    <!-- Cartouche éditorial et frontispice -->
    <header class="portal-cartouche">
      <div class="cartouche-frame">
        <h1 class="cartouche-title">Répertoire des Séries de Sols du Québec</h1>

        <!-- Registre des statistiques patrimoniales -->
        <div class="cartouche-stats-strip">
          <div class="stat-cell">
            <span class="stat-number">{len(matches)}</span>
            <span class="stat-name">Séries répertoriées</span>
          </div>
          <div class="stat-divider"></div>
          <div class="stat-cell">
            <span class="stat-number">{len(orders)}</span>
            <span class="stat-name">Ordres taxonomiques SCSS</span>
          </div>
          <div class="stat-divider"></div>
          <div class="stat-cell">
            <span class="stat-number">100 %</span>
            <span class="stat-name">Couverture provinciale</span>
          </div>
        </div>
      </div>
    </header>

    <!-- Pupitre de consultation : Recherche unifiée et filtres taxonomiques -->
    <section class="portal-console" aria-label="Filtres et recherche des séries">
      
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
                 placeholder="Rechercher une série par nom, symbole ou ordre (ex: Sainte-Rosalie, SSL, Gleysol, Podzol, Kamouraska)..." 
                 autocomplete="off"
                 oninput="handleSearchInput()"/>
          <button type="button" id="searchClearBtn" class="search-clear-btn" onclick="clearSearch()" aria-label="Effacer la recherche" style="display: none;">✕</button>
        </div>
        <div class="search-indicator">
          <span id="resultsCountBadge" class="results-badge">{len(matches)} séries au répertoire</span>
        </div>
      </div>

      <!-- Filtres par ordre taxonomique -->
      <div class="console-controls-bar">
        
        <div class="decade-selector" id="orderFilter" role="tablist" aria-label="Filtrer par ordre taxonomique">
          <button type="button" class="tab-pill active" data-order="all" role="tab" aria-selected="true">
            Tous ({len(matches)})
          </button>
          <button type="button" class="tab-pill" data-order="podzolique" role="tab" aria-selected="false">
            Podzolique
          </button>
          <button type="button" class="tab-pill" data-order="brunisolique" role="tab" aria-selected="false">
            Brunisolique
          </button>
          <button type="button" class="tab-pill" data-order="gleysolique" role="tab" aria-selected="false">
            Gleysolique
          </button>
          <button type="button" class="tab-pill" data-order="luvisolique" role="tab" aria-selected="false">
            Luvisolique
          </button>
          <button type="button" class="tab-pill" data-order="régosolique" role="tab" aria-selected="false">
            Régosolique
          </button>
          <button type="button" class="tab-pill" data-order="organique" role="tab" aria-selected="false">
            Organique
          </button>
        </div>

        <!-- Options de tri rapide -->
        <div class="console-tools">
          <div class="sort-selector-wrapper">
            <label for="sortSelect" class="sort-label">Trier par :</label>
            <select id="sortSelect" class="sort-select" onchange="applySorting()">
              <option value="name-asc">Nom de Série (A &rarr; Z)</option>
              <option value="name-desc">Nom de Série (Z &rarr; A)</option>
              <option value="code-asc">Symbole (A &rarr; Z)</option>
              <option value="order-asc">Ordre Taxonomique (A &rarr; Z)</option>
            </select>
          </div>
        </div>
      </div>

    </section>

    <!-- Registre officiel des séries -->
    <section class="register-folio-section" aria-label="Tableau des séries">

      <div class="register-table-wrapper" id="seriesTableWrapper">
        <table class="register-table" id="seriesTable">
          <thead>
            <tr>
              <th class="th-cote sortable" onclick="handleHeaderSort('code-asc')" title="Trier par symbole officiel" style="width: 100px;">
                <span class="th-content">Symbole <span class="sort-indicator">↕</span></span>
              </th>
              <th class="th-title sortable active-sort" onclick="handleHeaderSort('name-asc')" title="Trier par nom de série">
                <span class="th-content">Nom de la Série <span class="sort-indicator">▲</span></span>
              </th>
              <th class="th-region sortable" onclick="handleHeaderSort('order-asc')" title="Trier par ordre taxonomique" style="width: 200px;">
                <span class="th-content">Ordre Taxonomique <span class="sort-indicator">↕</span></span>
              </th>
              <th class="th-scale" style="min-width: 250px;">
                <span class="th-content">Sous-Groupe (SCSS)</span>
              </th>
              <th class="th-actions" style="width: 140px; text-align: right;">
                <span class="th-content" style="justify-content: flex-end;">Monographie</span>
              </th>
            </tr>
          </thead>
          <tbody id="tableBody">
{table_body}
          </tbody>
        </table>
      </div>

      <!-- État vide -->
      <div id="filterEmptyState" class="filter-empty-state" style="display: none; padding: 45px 20px; text-align: center;">
        <p style="font-size: 1.1rem; font-family: var(--font-serif); margin-bottom: 8px;">Aucune série trouvée pour ces critères de recherche.</p>
        <p style="font-size: 0.88rem; color: var(--ink-muted); margin-bottom: 18px;">Vérifiez l'orthographe du nom ou du symbole officiel.</p>
        <button type="button" class="tab-pill" onclick="resetFilters()">Réinitialiser les filtres</button>
      </div>

    </section>

    <!-- Pied de page officiel du portail -->
    <footer class="portal-footer" style="margin-top: 50px; padding: 30px 0; border-top: 1px solid var(--border); text-align: center; font-size: 0.86rem; color: var(--ink-muted);">
      <p style="margin: 0 0 8px 0;">
        <a href="../index.html" style="color: var(--accent-forest); text-decoration: none;">Accueil</a> • 
        <a href="../etudes.html" style="color: var(--accent-forest); text-decoration: none;">Études Pédologiques</a> • 
        <a href="index.html" style="color: var(--accent-forest); text-decoration: none; font-weight: 600;">Séries de Sols</a> • 
        <a href="../glossaire.html" style="color: var(--accent-forest); text-decoration: none;">Glossaire Pédologique</a> • 
        <a href="javascript:void(0)" onclick="PedoSearch.open()" style="color: var(--accent-forest); text-decoration: none;">Recherche Plein-Texte (Ctrl+K)</a>
      </p>
      <p style="margin: 0;">
        Répertoire Pédologique Québécois • Données certifiées Agriculture Canada, MAPAQ &amp; IRDA.
      </p>
    </footer>

  </main>

  <script>
    let currentOrder = 'all';
    let currentSort = 'name-asc';

    // Gestion des onglets d'ordres taxonomiques
    document.querySelectorAll('#orderFilter .tab-pill').forEach(pill => {{
      pill.addEventListener('click', () => {{
        document.querySelectorAll('#orderFilter .tab-pill').forEach(p => {{
          p.classList.remove('active');
          p.setAttribute('aria-selected', 'false');
        }});
        pill.classList.add('active');
        pill.setAttribute('aria-selected', 'true');
        currentOrder = pill.getAttribute('data-order');
        filterCollection();
      }});
    }});

    function handleSearchInput() {{
      const query = document.getElementById('unifiedSearchInput').value.trim();
      const clearBtn = document.getElementById('searchClearBtn');
      clearBtn.style.display = query ? 'flex' : 'none';
      filterCollection();
    }}

    function clearSearch() {{
      const input = document.getElementById('unifiedSearchInput');
      input.value = '';
      document.getElementById('searchClearBtn').style.display = 'none';
      filterCollection();
      input.focus();
    }}

    function normalizeText(str) {{
      return (str || '')
        .normalize('NFD')
        .replace(/[\u0300-\u036f]/g, '')
        .toLowerCase();
    }}

    function filterCollection() {{
      const rawQuery = document.getElementById('unifiedSearchInput').value;
      const query = normalizeText(rawQuery).trim();
      const terms = query.split(/\\s+/).filter(t => t.length > 0);

      const rows = document.querySelectorAll('.reg-row');
      let visibleCount = 0;

      rows.forEach(row => {{
        const rowOrder = row.getAttribute('data-order');
        const searchBlob = normalizeText(row.getAttribute('data-search'));

        const matchOrder = (currentOrder === 'all' || rowOrder.includes(currentOrder));
        
        let matchQuery = true;
        for (const t of terms) {{
          if (!searchBlob.includes(t)) {{
            matchQuery = false;
            break;
          }}
        }}

        if (matchOrder && matchQuery) {{
          row.style.display = '';
          visibleCount++;
        }} else {{
          row.style.display = 'none';
        }}
      }});

      const badge = document.getElementById('resultsCountBadge');
      if (rawQuery.trim() || currentOrder !== 'all') {{
        badge.textContent = visibleCount + (visibleCount > 1 ? ' séries trouvées' : ' série trouvée');
      }} else {{
        badge.textContent = visibleCount + ' séries au répertoire';
      }}

      const emptyState = document.getElementById('filterEmptyState');
      emptyState.style.display = visibleCount === 0 ? 'block' : 'none';
    }}

    function handleHeaderSort(targetMode) {{
      if (currentSort === targetMode) {{
        if (targetMode === 'name-asc') targetMode = 'name-desc';
        else if (targetMode === 'name-desc') targetMode = 'name-asc';
        else if (targetMode === 'code-asc') targetMode = 'code-desc';
        else if (targetMode === 'code-desc') targetMode = 'code-asc';
        else if (targetMode === 'order-asc') targetMode = 'order-desc';
        else if (targetMode === 'order-desc') targetMode = 'order-asc';
      }}
      currentSort = targetMode;
      const select = document.getElementById('sortSelect');
      if (select) {{
        select.value = targetMode;
      }}
      applySorting(targetMode);
    }}

    function applySorting(forcedMode) {{
      const mode = forcedMode || document.getElementById('sortSelect').value;
      currentSort = mode;
      const tbody = document.getElementById('tableBody');
      const rows = Array.from(tbody.querySelectorAll('.reg-row'));

      const comparator = (a, b) => {{
        if (mode === 'name-asc') {{
          return (a.getAttribute('data-name') || '').localeCompare(b.getAttribute('data-name') || '', 'fr');
        }} else if (mode === 'name-desc') {{
          return (b.getAttribute('data-name') || '').localeCompare(a.getAttribute('data-name') || '', 'fr');
        }} else if (mode === 'code-asc') {{
          return (a.getAttribute('data-code') || '').localeCompare(b.getAttribute('data-code') || '');
        }} else if (mode === 'code-desc') {{
          return (b.getAttribute('data-code') || '').localeCompare(a.getAttribute('data-code') || '');
        }} else if (mode === 'order-asc') {{
          return (a.getAttribute('data-order') || '').localeCompare(b.getAttribute('data-order') || '', 'fr');
        }} else if (mode === 'order-desc') {{
          return (b.getAttribute('data-order') || '').localeCompare(a.getAttribute('data-order') || '', 'fr');
        }}
        return 0;
      }};

      rows.sort(comparator);
      rows.forEach(r => tbody.appendChild(r));

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
      if (mode.startsWith('name')) {{
        activeTh = document.querySelector('.th-title');
        symbol = mode.endsWith('asc') ? '▲' : '▼';
      }} else if (mode.startsWith('code')) {{
        activeTh = document.querySelector('.th-cote');
        symbol = mode.endsWith('asc') ? '▲' : '▼';
      }} else if (mode.startsWith('order')) {{
        activeTh = document.querySelector('.th-region');
        symbol = mode.endsWith('asc') ? '▲' : '▼';
      }}

      if (activeTh) {{
        activeTh.classList.add('active-sort');
        const ind = activeTh.querySelector('.sort-indicator');
        if (ind) ind.textContent = symbol;
      }}
    }}

    function resetFilters() {{
      document.getElementById('unifiedSearchInput').value = '';
      document.getElementById('searchClearBtn').style.display = 'none';
      document.getElementById('sortSelect').value = 'name-asc';
      document.querySelector('#orderFilter .tab-pill[data-order="all"]').click();
      applySorting('name-asc');
      filterCollection();
    }}

    window.addEventListener('DOMContentLoaded', () => {{
      applySorting('name-asc');
    }});
  </script>
  <script src="../search.js" defer></script>
</body>
</html>
"""

    print(f"Writing updated series index to {SERIES_INDEX_PATH}...")
    with open(SERIES_INDEX_PATH, "w", encoding="utf-8") as f:
        f.write(new_html)

    print("Series index refactored successfully to match register-table design!")

if __name__ == "__main__":
    refactor_series_index()
