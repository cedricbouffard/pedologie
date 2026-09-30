/**
 * Moteur de recherche globale Pédologie Québec (SISCan)
 * Recherche instantanée parmi les rapports, séries de sols et termes du glossaire.
 */
(function () {
  let searchIndex = null;
  let activeIndex = -1;
  let currentResults = [];
  let activeFilter = 'all'; // 'all', 'reports', 'series', 'glossary', 'sections'

  function getBasePath() {
    const p = window.location.pathname.replace(/\\/g, '/');
    if (p.includes('/series/')) return '../';
    return '';
  }

  // Load index asynchronously
  async function loadIndex() {
    if (searchIndex) return searchIndex;
    try {
      const basePath = getBasePath();
      const res = await fetch(basePath + 'search_index.json');
      searchIndex = await res.json();
      return searchIndex;
    } catch (e) {
      console.error('Erreur chargement search_index.json:', e);
      return null;
    }
  }

  function normalize(str) {
    return (str || '')
      .normalize('NFD')
      .replace(/[\u0300-\u036f]/g, '')
      .toLowerCase();
  }

  function highlight(text, query) {
    if (!query || !text) return text || '';
    const normText = normalize(text);
    const normQuery = normalize(query);
    const idx = normText.indexOf(normQuery);
    if (idx === -1) return text;
    const match = text.slice(idx, idx + query.length);
    return text.slice(0, idx) + '<mark class="search-highlight">' + match + '</mark>' + text.slice(idx + query.length);
  }

  function performSearch(query) {
    if (!searchIndex || !query || query.trim().length < 2) {
      return [];
    }
    const q = normalize(query.trim());
    const words = q.split(/\s+/).filter(w => w.length > 0);
    const basePath = getBasePath();
    const matches = [];

    // 1. Match Reports / Études
    if ((activeFilter === 'all' || activeFilter === 'reports') && searchIndex.reports) {
      for (const r of searchIndex.reports) {
        const normCode = normalize(r.code);
        const normTitle = normalize(r.title);
        const normYear = normalize(r.year || '');
        let score = 0;

        if (normCode === q) score += 100;
        else if (normCode.includes(q)) score += 50;

        let allMatch = true;
        for (const w of words) {
          if (normTitle.includes(w) || normCode.includes(w) || normYear.includes(w)) {
            score += 20;
          } else {
            allMatch = false;
          }
        }
        if (allMatch || score >= 50) {
          matches.push({
            type: 'report',
            title: `${r.code.toUpperCase()} — ${r.title}`,
            subtitle: `Rapport pédologique (${r.year || 'Année n/d'} • ${r.pages || '?'} pages)`,
            url: basePath + r.url,
            score: score + 10
          });
        }
      }
    }

    // 2. Match Soil Series
    if ((activeFilter === 'all' || activeFilter === 'series') && searchIndex.series) {
      for (const s of searchIndex.series) {
        const normName = normalize(s.name);
        const normCode = normalize(s.code);
        let score = 0;

        if (normName.startsWith(q)) score += 80;
        else if (normName.includes(q)) score += 40;

        let allMatch = true;
        for (const w of words) {
          if (normName.includes(w) || normCode.includes(w)) {
            score += 15;
          } else {
            allMatch = false;
          }
        }
        if (allMatch || score >= 40) {
          let sUrl = s.url;
          if (basePath && !sUrl.startsWith('http') && !sUrl.startsWith('../')) {
            sUrl = basePath + sUrl;
          }
          matches.push({
            type: 'series',
            title: s.name,
            subtitle: `Série de sol • ${s.report} (${s.code.toUpperCase()})`,
            url: sUrl,
            score: score
          });
        }
      }
    }

    // 3. Match Glossary Terms
    if ((activeFilter === 'all' || activeFilter === 'glossary') && searchIndex.glossary) {
      for (const g of searchIndex.glossary) {
        const normTerm = normalize(g.term);
        const normDef = normalize(g.definition);
        let score = 0;

        if (normTerm === q) score += 120;
        else if (normTerm.startsWith(q)) score += 90;
        else if (normTerm.includes(q)) score += 50;

        let allMatch = true;
        for (const w of words) {
          if (normTerm.includes(w) || normDef.includes(w)) {
            score += 15;
          } else {
            allMatch = false;
          }
        }
        if (allMatch || score >= 40) {
          matches.push({
            type: 'glossary',
            title: g.term,
            subtitle: `${g.category} • ${g.definition.slice(0, 110)}...`,
            url: basePath + g.url,
            score: score
          });
        }
      }
    }

    // 4. Match Sections
    if ((activeFilter === 'all' || activeFilter === 'sections') && searchIndex.sections) {
      for (const sec of searchIndex.sections) {
        const normTitle = normalize(sec.title);
        let score = 0;
        let allMatch = true;
        for (const w of words) {
          if (normTitle.includes(w)) {
            score += 10;
          } else {
            allMatch = false;
          }
        }
        if (allMatch && score > 0) {
          matches.push({
            type: 'section',
            title: sec.title,
            subtitle: `Chapitre / Section • ${sec.code.toUpperCase()}`,
            url: basePath + sec.url,
            score: score
          });
        }
      }
    }

    // Sort by relevance score
    matches.sort((a, b) => b.score - a.score);
    return matches.slice(0, 40); // limit top 40 for optimal performance
  }

  // Build UI Modal
  function createModal() {
    if (document.getElementById('global-search-modal')) return;

    const modal = document.createElement('div');
    modal.id = 'global-search-modal';
    modal.className = 'search-modal-backdrop';
    modal.innerHTML = `
      <div class="search-modal-container" role="dialog" aria-modal="true" aria-label="Recherche globale">
        <div class="search-modal-header">
          <svg class="search-icon" viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M8 4a4 4 0 100 8 4 4 0 000-8zM2 8a6 6 0 1110.89 3.476l4.817 4.817a1 1 0 01-1.414 1.414l-4.816-4.816A6 6 0 012 8z" clip-rule="evenodd"/>
          </svg>
          <input type="text" id="global-search-input" class="search-modal-input" placeholder="Rechercher une étude, une série de sol ou un terme du glossaire..." autocomplete="off" spellcheck="false" />
          <button id="search-modal-close" class="search-close-btn" aria-label="Fermer (Échap)">✕</button>
        </div>
        <div class="search-modal-filters">
          <button class="filter-tab active" data-filter="all">Tous</button>
          <button class="filter-tab" data-filter="reports">Études</button>
          <button class="filter-tab" data-filter="series">Séries</button>
          <button class="filter-tab" data-filter="glossary">Glossaire</button>
          <button class="filter-tab" data-filter="sections">Chapitres</button>
        </div>
        <div id="search-results-list" class="search-results-list">
          <div class="search-empty-state">
            <p>Saisissez au moins deux caractères pour rechercher...</p>
            <div class="search-tips">
              <span>Exemples : <code>Bellechasse</code>, <code>Sainte-Rosalie</code>, <code>Ortstein</code>, <code>Gleysol</code></span>
            </div>
          </div>
        </div>
        <div class="search-modal-footer">
          <span class="footer-hint"><kbd>↑</kbd> <kbd>↓</kbd> naviguer</span>
          <span class="footer-hint"><kbd>Entrée</kbd> consulter</span>
          <span class="footer-hint"><kbd>Échap</kbd> fermer</span>
        </div>
      </div>
    `;

    document.body.appendChild(modal);

    const input = document.getElementById('global-search-input');
    const closeBtn = document.getElementById('search-modal-close');
    const resultsContainer = document.getElementById('search-results-list');
    const filterTabs = modal.querySelectorAll('.filter-tab');

    filterTabs.forEach(tab => {
      tab.addEventListener('click', () => {
        filterTabs.forEach(t => t.classList.remove('active'));
        tab.classList.add('active');
        activeFilter = tab.getAttribute('data-filter');
        renderResults(input.value);
      });
    });

    input.addEventListener('input', () => {
      renderResults(input.value);
    });

    input.addEventListener('keydown', (e) => {
      if (e.key === 'ArrowDown') {
        e.preventDefault();
        selectNextResult(1);
      } else if (e.key === 'ArrowUp') {
        e.preventDefault();
        selectNextResult(-1);
      } else if (e.key === 'Enter') {
        e.preventDefault();
        if (activeIndex >= 0 && activeIndex < currentResults.length) {
          window.location.href = currentResults[activeIndex].url;
        }
      } else if (e.key === 'Escape') {
        closeModal();
      }
    });

    closeBtn.addEventListener('click', closeModal);
    modal.addEventListener('click', (e) => {
      if (e.target === modal) closeModal();
    });
  }

  function renderResults(query) {
    const resultsContainer = document.getElementById('search-results-list');
    if (!query || query.trim().length < 2) {
      currentResults = [];
      activeIndex = -1;
      resultsContainer.innerHTML = `
        <div class="search-empty-state">
          <p>Saisissez au moins deux caractères pour lancer la recherche...</p>
          <div class="search-tips">
            <span>Exemples : <code>Bellechasse</code>, <code>Sainte-Rosalie</code>, <code>Ortstein</code>, <code>Gleysol</code></span>
          </div>
        </div>
      `;
      return;
    }

    currentResults = performSearch(query);
    activeIndex = currentResults.length > 0 ? 0 : -1;

    if (currentResults.length === 0) {
      resultsContainer.innerHTML = `
        <div class="search-empty-state">
          <p>Aucun résultat pour « <strong>${escapeHtml(query)}</strong> »</p>
          <p class="search-sub-empty">Vérifiez l'orthographe ou tentez un terme plus générique.</p>
        </div>
      `;
      return;
    }

    const typeLabels = {
      series: { label: 'Série', class: 'tag-series' },
      report: { label: 'Étude', class: 'tag-report' },
      glossary: { label: 'Glossaire', class: 'tag-glossary' },
      section: { label: 'Chapitre', class: 'tag-section' }
    };

    let html = '';
    currentResults.forEach((item, idx) => {
      const typeInfo = typeLabels[item.type] || { label: 'Élément', class: '' };
      const isSelected = idx === activeIndex ? ' selected' : '';
      html += `
        <a href="${item.url}" class="search-result-item${isSelected}" data-index="${idx}">
          <div class="result-badge-col">
            <span class="result-type-tag ${typeInfo.class}">${typeInfo.label}</span>
          </div>
          <div class="result-content-col">
            <div class="result-title">${highlight(item.title, query)}</div>
            <div class="result-subtitle">${escapeHtml(item.subtitle)}</div>
          </div>
          <div class="result-arrow-col">
            <svg viewBox="0 0 20 20" fill="currentColor" width="16" height="16">
              <path fill-rule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clip-rule="evenodd"/>
            </svg>
          </div>
        </a>
      `;
    });

    resultsContainer.innerHTML = html;

    resultsContainer.querySelectorAll('.search-result-item').forEach(el => {
      el.addEventListener('mouseenter', () => {
        resultsContainer.querySelectorAll('.search-result-item').forEach(i => i.classList.remove('selected'));
        el.classList.add('selected');
        activeIndex = parseInt(el.getAttribute('data-index'), 10);
      });
    });
  }

  function selectNextResult(direction) {
    if (currentResults.length === 0) return;
    const items = document.querySelectorAll('.search-result-item');
    if (items.length === 0) return;

    items.forEach(i => i.classList.remove('selected'));
    activeIndex += direction;
    if (activeIndex >= currentResults.length) activeIndex = 0;
    if (activeIndex < 0) activeIndex = currentResults.length - 1;

    const currentItem = items[activeIndex];
    if (currentItem) {
      currentItem.classList.add('selected');
      currentItem.scrollIntoView({ block: 'nearest' });
    }
  }

  function escapeHtml(str) {
    return (str || '')
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }

  function openModal(initialQuery = '') {
    createModal();
    const modal = document.getElementById('global-search-modal');
    modal.classList.add('open');
    document.body.style.overflow = 'hidden';

    loadIndex().then(() => {
      const input = document.getElementById('global-search-input');
      input.value = initialQuery;
      input.focus();
      input.select();
      if (initialQuery) {
        renderResults(initialQuery);
      }
    });
  }

  function closeModal() {
    const modal = document.getElementById('global-search-modal');
    if (modal) {
      modal.classList.remove('open');
      document.body.style.overflow = '';
    }
  }

  // Global key listener
  document.addEventListener('keydown', (e) => {
    if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k') {
      e.preventDefault();
      openModal();
    } else if (e.key === '/' && document.activeElement.tagName !== 'INPUT' && document.activeElement.tagName !== 'TEXTAREA') {
      e.preventDefault();
      openModal();
    } else if (e.key === 'Escape') {
      closeModal();
    }
  });

  window.PedoSearch = {
    open: openModal,
    close: closeModal,
    preload: loadIndex
  };

  if ('requestIdleCallback' in window) {
    window.requestIdleCallback(() => loadIndex());
  } else {
    setTimeout(loadIndex, 1000);
  }
})();
