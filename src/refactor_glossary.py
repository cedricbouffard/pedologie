#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
refactor_glossary.py - Harmonise le glossaire (glossaire.html) avec le design system du portail.
Conserve le format cartes, ajuste leur style, intègre la console de recherche et la barre de navigation.
Garantit l'absence totale d'émojis.
"""

from pathlib import Path
import re

BASE_DIR = Path(r"c:\Users\cedbo\OneDrive\Documents\pedo")
GLOSSAIRE_PATH = BASE_DIR / "output_html" / "glossaire.html"

def refactor_glossary():
    print(f"Reading {GLOSSAIRE_PATH}...")
    with open(GLOSSAIRE_PATH, "r", encoding="utf-8") as f:
        html = f.read()

    # Extraction du contenu entre <main class="rubric-body"...> et </main>
    m = re.search(r'<main class="rubric-body"[^>]*>(.*?)</main>', html, re.DOTALL)
    if not m:
        print("Erreur: main rubric-body non trouvé!")
        return

    main_content = m.group(1).strip()

    # Compter le nombre de cartes
    card_count = len(re.findall(r'class="glossary-card"', main_content))
    print(f"Found {card_count} glossary cards.")

    new_html = f"""<!DOCTYPE html>
<html lang="fr" class="portal-html">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1"/>
  <title>Glossaire Pédologique &amp; Nomenclature Officielle — SCSS Québec</title>
  <meta name="description" content="Définitions normalisées du Système de classification des sols du Canada (SCSS) et des mémoires d'inventaire pédologique du Québec."/>

  <!-- Typographie d'archive, de cartographie & de bibliothèque savante -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@500;600;700&family=Newsreader:ital,opsz,wght@0,6..72,400;0,6..72,500;0,6..72,600;0,6..72,700;1,6..72,400;1,6..72,600&family=Plus+Jakarta+Sans:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
  
  <link rel="stylesheet" href="style.css"/>
  <style>
    /* Cartes du glossaire harmonisées avec le design system */
    .glossary-card {{
      background: var(--surface-raised, #fbfaf8);
      border: 1px solid var(--border, #e5e1d8);
      border-radius: 8px;
      padding: 16px 18px;
      box-shadow: 0 1px 4px rgba(0, 0, 0, 0.03);
      display: flex;
      flex-direction: column;
      transition: transform 0.15s ease, box-shadow 0.15s ease, border-color 0.15s ease;
    }}
    .glossary-card:hover {{
      transform: translateY(-2px);
      box-shadow: 0 6px 18px rgba(0, 0, 0, 0.07);
      border-color: var(--accent-forest, #204838);
      background: var(--surface, #ffffff);
    }}
    .glossary-term-header {{
      display: flex;
      justify-content: space-between;
      align-items: baseline;
      margin-bottom: 8px;
      border-bottom: 1px solid var(--border, #e5e1d8);
      padding-bottom: 6px;
      gap: 8px;
    }}
    .glossary-term-title {{
      margin: 0;
      font-family: var(--font-serif);
      font-size: 1.15rem;
      color: var(--accent-forest, #204838);
      font-weight: 700;
      line-height: 1.25;
    }}
    .glossary-term-def {{
      margin: 0;
      font-size: 0.88rem;
      line-height: 1.55;
      color: var(--ink-secondary, #4a4640);
      flex: 1;
    }}
    .rubric-header {{
      border-bottom: 2px solid var(--border-dark, #b5ad9e);
      padding-bottom: 8px;
      margin-bottom: 12px;
    }}
    .rubric-title {{
      font-family: var(--font-serif);
      font-size: 1.35rem;
      color: var(--ink, #1f1d1a);
      margin: 0;
      font-weight: 700;
    }}
  </style>
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
        <a href="etudes.html" class="nav-search-btn" style="text-decoration:none;margin-right:8px;" title="Consulter les 79 mémoires d'inventaire pédologique régionaux">
          <span>Études</span>
        </a>
        <a href="series/index.html" class="nav-search-btn" style="text-decoration:none;margin-right:8px;" title="Consulter le répertoire des séries de sols du Québec">
          <span>Séries de Sols</span>
        </a>
        <a href="glossaire.html" class="nav-search-btn active" style="text-decoration:none;margin-right:8px;font-weight:700;" title="Consulter le glossaire pédologique officiel">
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
      <span class="active">Glossaire Pédologique</span>
    </nav>

    <!-- Cartouche éditorial et frontispice -->
    <header class="portal-cartouche">
      <div class="cartouche-frame">
        <h1 class="cartouche-title">Glossaire Pédologique &amp; Nomenclature</h1>
        <p style="text-align:center;max-width:720px;margin:0 auto 16px auto;font-size:0.98rem;line-height:1.55;color:var(--ink-secondary);">
          Définitions normalisées du Système de classification des sols du Canada (SCSS) et des mémoires d'inventaire pédologique québécois.
        </p>

        <!-- Registre des statistiques patrimoniales -->
        <div class="cartouche-stats-strip">
          <div class="stat-cell">
            <span class="stat-number">{card_count}</span>
            <span class="stat-name">Termes &amp; concepts définis</span>
          </div>
          <div class="stat-divider"></div>
          <div class="stat-cell">
            <span class="stat-number">6</span>
            <span class="stat-name">Sections taxonomiques</span>
          </div>
          <div class="stat-divider"></div>
          <div class="stat-cell">
            <span class="stat-number">SCSS</span>
            <span class="stat-name">Référentiel certifié</span>
          </div>
        </div>
      </div>
    </header>

    <!-- Console de recherche interactive -->
    <section class="portal-console" aria-label="Recherche et filtres du glossaire" style="margin-bottom: 25px;">
      
      <!-- Barre de saisie -->
      <div class="console-search-bar">
        <div class="search-input-wrapper">
          <svg class="search-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="11" cy="11" r="8"></circle>
            <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
          </svg>
          <input type="text" 
                 id="glossarySearchInput" 
                 class="search-input-field" 
                 placeholder="Filtrer parmi les définitions (ex: Sol brun, Ae, Bnt, Gley, Ortstein, Podzol)..." 
                 autocomplete="off"
                 oninput="handleGlossarySearch()"/>
          <button type="button" id="searchClearBtn" class="search-clear-btn" onclick="clearGlossarySearch()" aria-label="Effacer la recherche" style="display: none;">✕</button>
        </div>
        <div class="search-indicator">
          <span id="resultsCountBadge" class="results-badge">{card_count} termes au glossaire</span>
        </div>
      </div>

      <!-- Navigation thématique par catégorie -->
      <div class="console-controls-bar">
        <div class="decade-selector" id="categoryNav" role="tablist" aria-label="Accès thématique">
          <a href="#ordres" class="tab-pill">Ordres</a>
          <a href="#grands_groupes" class="tab-pill">Grands Groupes</a>
          <a href="#sous_groupes" class="tab-pill">Sous-Groupes</a>
          <a href="#horizons_maitres" class="tab-pill">Horizons Maîtres</a>
          <a href="#horizons_specifiques" class="tab-pill">Horizons Spécifiques</a>
          <a href="#proprietes" class="tab-pill">Propriétés &amp; Notions</a>
        </div>
      </div>

    </section>

    <!-- Corps du glossaire : Cartes normalisées -->
    <main class="rubric-body" id="glossaryContainer" style="padding-top: 10px;">
{main_content}
    </main>

    <!-- État vide -->
    <div id="glossaryEmptyState" class="filter-empty-state" style="display: none; padding: 45px 20px; text-align: center;">
      <p style="font-size: 1.1rem; font-family: var(--font-serif); margin-bottom: 8px;">Aucun terme du glossaire ne correspond à cette recherche.</p>
      <p style="font-size: 0.88rem; color: var(--ink-muted); margin-bottom: 18px;">Vérifiez l'orthographe du concept ou du symbole recherché.</p>
      <button type="button" class="tab-pill" onclick="clearGlossarySearch()">Réinitialiser la recherche</button>
    </div>

    <!-- Pied de page officiel du portail -->
    <footer class="portal-footer" style="margin-top: 50px; padding: 30px 0; border-top: 1px solid var(--border); text-align: center; font-size: 0.86rem; color: var(--ink-muted);">
      <p style="margin: 0 0 8px 0;">
        <a href="index.html" style="color: var(--accent-forest); text-decoration: none;">Accueil</a> • 
        <a href="etudes.html" style="color: var(--accent-forest); text-decoration: none;">Études Pédologiques</a> • 
        <a href="series/index.html" style="color: var(--accent-forest); text-decoration: none;">Séries de Sols</a> • 
        <a href="glossaire.html" style="color: var(--accent-forest); text-decoration: none; font-weight: 600;">Glossaire Pédologique</a> • 
        <a href="javascript:void(0)" onclick="PedoSearch.open()" style="color: var(--accent-forest); text-decoration: none;">Recherche Plein-Texte (Ctrl+K)</a>
      </p>
      <p style="margin: 0;">
        Répertoire Pédologique Québécois • Données certifiées Agriculture Canada, MAPAQ &amp; IRDA.
      </p>
    </footer>

  </main>

  <script>
    function normalizeText(str) {{
      return (str || '')
        .normalize('NFD')
        .replace(/[\u0300-\u036f]/g, '')
        .toLowerCase();
    }}

    function handleGlossarySearch() {{
      const input = document.getElementById('glossarySearchInput');
      const query = normalizeText(input.value).trim();
      const clearBtn = document.getElementById('searchClearBtn');
      clearBtn.style.display = query ? 'flex' : 'none';

      const terms = query.split(/\\s+/).filter(t => t.length > 0);
      const cards = document.querySelectorAll('.glossary-card');
      const sections = document.querySelectorAll('.rubric-section');
      let visibleCount = 0;

      cards.forEach(card => {{
        const text = normalizeText(card.textContent);
        let match = true;
        for (const t of terms) {{
          if (!text.includes(t)) {{
            match = false;
            break;
          }}
        }}

        if (match) {{
          card.style.display = '';
          visibleCount++;
        }} else {{
          card.style.display = 'none';
        }}
      }});

      // Masquer les sections dont toutes les cartes sont masquées
      sections.forEach(sec => {{
        const visibleCards = sec.querySelectorAll('.glossary-card:not([style*="display: none"])');
        sec.style.display = visibleCards.length > 0 ? '' : 'none';
      }});

      const badge = document.getElementById('resultsCountBadge');
      if (query) {{
        badge.textContent = visibleCount + (visibleCount > 1 ? ' termes trouvés' : ' terme trouvé');
      }} else {{
        badge.textContent = '{card_count} termes au glossaire';
      }}

      const emptyState = document.getElementById('glossaryEmptyState');
      emptyState.style.display = visibleCount === 0 ? 'block' : 'none';
    }}

    function clearGlossarySearch() {{
      const input = document.getElementById('glossarySearchInput');
      input.value = '';
      document.getElementById('searchClearBtn').style.display = 'none';
      handleGlossarySearch();
      input.focus();
    }}
  </script>
  <script src="search.js" defer></script>
</body>
</html>
"""

    print(f"Writing updated glossaire to {GLOSSAIRE_PATH}...")
    with open(GLOSSAIRE_PATH, "w", encoding="utf-8") as f:
        f.write(new_html)

    print("Glossaire refactored successfully to match portal design system!")

if __name__ == "__main__":
    refactor_glossary()
