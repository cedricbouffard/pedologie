import json
import os

with open('data/study_names.json', 'r', encoding='utf-8') as f:
    study_names = json.load(f)

study_names_json = json.dumps(study_names, ensure_ascii=False)

with open('build_carte.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix the google url in content and the f-string
# Let's write the exact html template directly
html_template = """<!DOCTYPE html>
<html lang="fr" class="portal-html">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>Carte Pédologique &amp; Topographique — Inventaire Pédologique du Québec</title>
  <meta name="description" content="Carte interactive vectorielle de la couverture pédologique officielle du Québec avec relief topographique MNE HRDEM (1m) et courbes de niveau dynamiques."/>

  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@500;600;700&family=Newsreader:ital,opsz,wght@0,6..72,400;0,6..72,600;1,6..72,400&family=Plus+Jakarta+Sans:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
  
  <link rel="stylesheet" href="style.css"/>
  <link rel="stylesheet" href="geolibre-contour.css"/>

  <!-- MapLibre GL JS & PMTiles -->
  <link rel="stylesheet" href="https://unpkg.com/maplibre-gl@4.7.1/dist/maplibre-gl.css"/>
  <script src="https://unpkg.com/maplibre-gl@4.7.1/dist/maplibre-gl.js"></script>
  <script src="https://unpkg.com/pmtiles@3.0.7/dist/pmtiles.js"></script>
  <script src="geolibre-contour.js"></script>

  <style>
    * { box-sizing: border-box; }
    html, body {
      margin: 0;
      padding: 0;
      width: 100%;
      height: 100%;
      overflow: hidden;
      font-family: var(--font-sans, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif);
      background: #f1f5f9;
    }

    /* Fixed Top Navbar */
    .portal-navbar {
      position: fixed;
      top: 0;
      left: 0;
      right: 0;
      height: 54px;
      z-index: 1000;
      background: rgba(255, 255, 255, 0.96);
      backdrop-filter: blur(10px);
      -webkit-backdrop-filter: blur(10px);
      border-bottom: 1px solid var(--border, #e2e8f0);
      display: flex;
      align-items: center;
      padding: 0 18px;
    }
    .navbar-content {
      width: 100%;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
    .nav-brand {
      display: flex;
      align-items: center;
      gap: 10px;
      text-decoration: none;
      color: var(--ink, #1f1d1a);
    }
    .nav-titles {
      display: flex;
      flex-direction: column;
    }
    .nav-brand-title {
      font-family: var(--font-serif, Georgia, serif);
      font-weight: 700;
      font-size: 1rem;
      letter-spacing: -0.01em;
      color: #1f1d1a;
      line-height: 1.2;
    }
    .nav-brand-sub {
      font-size: 0.68rem;
      color: #64748b;
      letter-spacing: 0.02em;
    }
    .nav-actions {
      display: flex;
      align-items: center;
      gap: 6px;
    }
    .nav-btn {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      padding: 6px 12px;
      font-size: 0.82rem;
      font-weight: 500;
      color: #4a4640;
      text-decoration: none;
      border-radius: 6px;
      border: 1px solid transparent;
      transition: all 0.15s ease;
    }
    .nav-btn:hover {
      background: #f1f5f9;
      color: #1e4535;
    }
    .nav-btn.active {
      background: #1e4535;
      color: #ffffff;
      font-weight: 600;
    }

    /* Map container */
    #map {
      width: 100%;
      height: calc(100% - 54px);
      position: absolute;
      top: 54px;
      left: 0;
    }

    /* Floating control panel (desktop) */
    .map-controls-panel {
      position: absolute;
      top: 68px;
      left: 14px;
      z-index: 100;
      width: 350px;
      max-width: calc(100vw - 28px);
      max-height: calc(100vh - 84px);
      background: rgba(255, 255, 255, 0.97);
      backdrop-filter: blur(14px);
      -webkit-backdrop-filter: blur(14px);
      border-radius: 14px;
      box-shadow: 0 10px 30px -5px rgba(0, 0, 0, 0.16), 0 4px 10px -2px rgba(0, 0, 0, 0.08);
      border: 1px solid rgba(226, 232, 240, 0.9);
      padding: 14px 16px;
      display: flex;
      flex-direction: column;
      gap: 12px;
      pointer-events: auto;
      overflow-y: auto;
    }
    .panel-header {
      border-bottom: 1px solid #f1f5f9;
      padding-bottom: 8px;
    }
    .panel-title {
      font-size: 13px;
      font-weight: 700;
      color: #0f172a;
      letter-spacing: -0.01em;
    }
    .panel-subtitle {
      font-size: 11px;
      color: #64748b;
      margin-top: 2px;
    }

    /* Search input */
    .search-and-toggle-row {
      display: flex;
      align-items: center;
      gap: 8px;
      width: 100%;
    }
    .search-box {
      position: relative;
      flex: 1;
    }
    .search-input-wrapper {
      position: relative;
      display: flex;
      align-items: center;
    }
    .search-icon {
      position: absolute;
      left: 10px;
      color: #94a3b8;
      pointer-events: none;
    }
    .search-input {
      width: 100%;
      padding: 8px 28px 8px 30px;
      border: 1px solid #cbd5e1;
      border-radius: 8px;
      font-size: 12px;
      color: #1e293b;
      background: #f8fafc;
      outline: none;
      transition: all 0.15s ease;
    }
    .search-input:focus {
      background: #ffffff;
      border-color: #204838;
      box-shadow: 0 0 0 2px rgba(32, 72, 56, 0.15);
    }
    .clear-btn {
      position: absolute;
      right: 8px;
      background: none;
      border: none;
      font-size: 14px;
      color: #94a3b8;
      cursor: pointer;
      padding: 2px 4px;
    }
    .clear-btn:hover {
      color: #475569;
    }
    .search-suggestions {
      position: absolute;
      top: 100%;
      left: 0;
      right: 0;
      margin-top: 4px;
      background: #ffffff;
      border: 1px solid #e2e8f0;
      border-radius: 8px;
      box-shadow: 0 10px 25px rgba(0, 0, 0, 0.12);
      max-height: 220px;
      overflow-y: auto;
      z-index: 50;
    }
    .suggestion-item {
      padding: 8px 12px;
      font-size: 11px;
      color: #1e293b;
      cursor: pointer;
      border-bottom: 1px solid #f1f5f9;
      line-height: 1.35;
      transition: background 0.1s;
    }
    .suggestion-item:last-child {
      border-bottom: none;
    }
    .suggestion-item:hover {
      background: #f0fdf4;
      color: #166534;
    }

    /* Mobile Toggle Button (hidden on desktop) */
    .mobile-tools-toggle {
      display: none;
      align-items: center;
      gap: 6px;
      padding: 8px 12px;
      background: #ffffff;
      border: 1px solid #cbd5e1;
      border-radius: 8px;
      font-size: 12px;
      font-weight: 600;
      color: #1e4535;
      cursor: pointer;
      white-space: nowrap;
      box-shadow: 0 1px 3px rgba(0,0,0,0.08);
      transition: all 0.15s ease;
    }
    .mobile-tools-toggle:hover, .mobile-tools-toggle.active {
      background: #1e4535;
      color: #ffffff;
      border-color: #1e4535;
    }

    /* Panel tools cards */
    .panel-tools {
      display: flex;
      flex-direction: column;
      gap: 12px;
    }
    .tools-drawer-header {
      display: none;
      justify-content: space-between;
      align-items: center;
      padding-bottom: 8px;
      margin-bottom: 4px;
      border-bottom: 1px solid #e2e8f0;
    }
    .tools-drawer-title {
      font-size: 14px;
      font-weight: 700;
      color: #0f172a;
    }
    .tools-close-btn {
      background: #f1f5f9;
      border: none;
      font-size: 20px;
      line-height: 1;
      color: #475569;
      cursor: pointer;
      width: 30px;
      height: 30px;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      transition: background 0.15s;
    }
    .tools-close-btn:hover {
      background: #e2e8f0;
      color: #0f172a;
    }

    .tool-card {
      background: #f8fafc;
      border: 1px solid #e2e8f0;
      border-radius: 10px;
      padding: 10px 12px;
      display: flex;
      flex-direction: column;
      gap: 8px;
    }
    .tool-card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      cursor: pointer;
      user-select: none;
    }
    .tool-card-title {
      font-size: 11px;
      font-weight: 700;
      color: #334155;
      text-transform: uppercase;
      letter-spacing: 0.04em;
      display: flex;
      align-items: center;
      gap: 6px;
    }
    .tool-card-title svg {
      color: #1e4535;
    }

    /* Modern Switch Toggle */
    .switch-label {
      position: relative;
      display: inline-block;
      width: 34px;
      height: 18px;
      margin: 0;
      cursor: pointer;
    }
    .switch-label input {
      opacity: 0;
      width: 0;
      height: 0;
    }
    .switch-slider {
      position: absolute;
      cursor: pointer;
      top: 0; left: 0; right: 0; bottom: 0;
      background-color: #cbd5e1;
      transition: .2s;
      border-radius: 18px;
    }
    .switch-slider:before {
      position: absolute;
      content: "";
      height: 14px;
      width: 14px;
      left: 2px;
      bottom: 2px;
      background-color: white;
      transition: .2s;
      border-radius: 50%;
      box-shadow: 0 1px 3px rgba(0,0,0,0.2);
    }
    input:checked + .switch-slider {
      background-color: #10b981;
    }
    input:checked + .switch-slider:before {
      transform: translateX(16px);
    }

    /* Segmented basemap toggle */
    .segmented-control {
      display: grid;
      grid-template-columns: 1fr 1fr;
      background: #e2e8f0;
      padding: 2px;
      border-radius: 8px;
      gap: 2px;
    }
    .seg-btn {
      background: transparent;
      border: none;
      padding: 5px 8px;
      font-size: 11px;
      font-weight: 600;
      color: #64748b;
      border-radius: 6px;
      cursor: pointer;
      transition: all 0.15s ease;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 4px;
    }
    .seg-btn.active {
      background: #ffffff;
      color: #0f172a;
      box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    }

    /* Sliders */
    .tool-label-row {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-top: 2px;
    }
    .tool-sublabel {
      font-size: 11px;
      font-weight: 500;
      color: #64748b;
    }
    .val-badge {
      font-size: 10px;
      font-weight: 700;
      color: #166534;
      background: #f0fdf4;
      padding: 1px 6px;
      border-radius: 5px;
    }
    .slider {
      -webkit-appearance: none;
      appearance: none;
      width: 100%;
      height: 5px;
      background: #e2e8f0;
      border-radius: 4px;
      outline: none;
      margin: 4px 0;
    }
    .slider::-webkit-slider-thumb {
      -webkit-appearance: none;
      appearance: none;
      width: 15px;
      height: 15px;
      border-radius: 50%;
      background: #204838;
      cursor: pointer;
      box-shadow: 0 1px 3px rgba(32, 72, 56, 0.4);
      transition: transform 0.1s;
    }
    .slider::-webkit-slider-thumb:hover {
      transform: scale(1.15);
    }
    .slider::-moz-range-thumb {
      width: 15px;
      height: 15px;
      border-radius: 50%;
      background: #204838;
      cursor: pointer;
      border: none;
      box-shadow: 0 1px 3px rgba(32, 72, 56, 0.4);
    }

    /* Topo Colorbar Preview */
    .topo-gradient-bar {
      height: 10px;
      border-radius: 5px;
      background: linear-gradient(90deg, #4c1d95 0%, #7c3aed 15%, #2563eb 30%, #0d9488 45%, #16a34a 60%, #eab308 75%, #ea580c 88%, #dc2626 100%);
      box-shadow: inset 0 1px 2px rgba(0,0,0,0.2);
      margin: 4px 0 2px 0;
    }
    .topo-gradient-labels {
      display: flex;
      justify-content: space-between;
      font-size: 9.5px;
      color: #64748b;
      font-weight: 600;
    }
    .topo-alt-badge {
      font-family: var(--font-mono, monospace);
      font-size: 10.5px;
      font-weight: 600;
      background: #f1f5f9;
      border: 1px solid #cbd5e1;
      border-radius: 6px;
      padding: 4px 8px;
      color: #0f172a;
      text-align: center;
      margin-top: 2px;
    }

    /* Contour pills */
    .pills-group {
      display: flex;
      gap: 4px;
      margin-top: 2px;
    }
    .pill-btn {
      flex: 1;
      padding: 4px 0;
      font-size: 10.5px;
      font-weight: 600;
      color: #475569;
      background: #ffffff;
      border: 1px solid #cbd5e1;
      border-radius: 6px;
      cursor: pointer;
      text-align: center;
      transition: all 0.15s ease;
    }
    .pill-btn:hover {
      background: #f8fafc;
      border-color: #94a3b8;
    }
    .pill-btn.active {
      background: #1e4535;
      color: #ffffff;
      border-color: #1e4535;
    }

    .contour-status-badge {
      font-size: 10px;
      color: #64748b;
      background: #f1f5f9;
      border-radius: 5px;
      padding: 4px 8px;
      line-height: 1.35;
      margin-top: 2px;
    }
    .contour-status-badge.active {
      color: #0369a1;
      background: #e0f2fe;
    }

    /* Color picker row */
    .color-select-row {
      display: flex;
      align-items: center;
      gap: 8px;
      margin-top: 2px;
    }
    .color-circle {
      width: 18px;
      height: 18px;
      border-radius: 50%;
      cursor: pointer;
      border: 2px solid transparent;
      transition: transform 0.15s;
    }
    .color-circle:hover {
      transform: scale(1.15);
    }
    .color-circle.active {
      border-color: #0f172a;
      box-shadow: 0 0 0 1px white;
    }

    /* Source info line */
    .source-info-line {
      font-size: 9.5px;
      color: #94a3b8;
      line-height: 1.3;
      border-top: 1px solid #f1f5f9;
      padding-top: 6px;
      margin-top: 2px;
    }

    /* Backdrop for mobile drawer */
    .tools-backdrop {
      display: none;
      position: fixed;
      top: 0; left: 0; right: 0; bottom: 0;
      background: rgba(15, 23, 42, 0.45);
      backdrop-filter: blur(2px);
      -webkit-backdrop-filter: blur(2px);
      z-index: 1500;
      opacity: 0;
      pointer-events: none;
      transition: opacity 0.25s ease;
    }

    /* Popup card styling */
    .maplibregl-popup {
      max-width: 380px !important;
      z-index: 30;
    }
    .maplibregl-popup-content {
      padding: 0;
      border-radius: 14px;
      box-shadow: 0 12px 28px -4px rgba(0, 0, 0, 0.18), 0 6px 12px -2px rgba(0, 0, 0, 0.08);
      overflow: hidden;
      border: 1px solid #cbd5e1;
      font-family: inherit;
    }
    .maplibregl-popup-close-button {
      padding: 8px 12px;
      font-size: 18px;
      color: #64748b;
      outline: none;
      transition: color 0.15s, transform 0.15s;
    }
    .maplibregl-popup-close-button:hover {
      color: #0f172a;
      background: transparent;
      transform: scale(1.1);
    }
    .pedo-popup {
      display: flex;
      flex-direction: column;
      background: #ffffff;
      font-size: 12px;
    }
    .pedo-popup-header {
      padding: 14px 16px 12px 16px;
      background: linear-gradient(180deg, #f8fafc 0%, #f1f5f9 100%);
      border-bottom: 1px solid #e2e8f0;
      padding-right: 36px;
      display: flex;
      flex-direction: column;
      gap: 6px;
    }
    .pedo-study-meta {
      display: flex;
      align-items: center;
      gap: 6px;
    }
    .pedo-study-badge {
      background: #1e4535;
      color: #ffffff;
      font-size: 10px;
      font-weight: 700;
      padding: 2px 7px;
      border-radius: 4px;
      letter-spacing: 0.02em;
    }
    .pedo-study-year {
      font-size: 11px;
      color: #64748b;
      font-weight: 500;
    }
    .pedo-popup-title {
      font-size: 13px;
      font-weight: 700;
      color: #0f172a;
      line-height: 1.35;
      margin: 0;
    }
    .pedo-appellation {
      font-family: var(--font-mono, monospace);
      font-size: 11px;
      background: #ffffff;
      border: 1px solid #cbd5e1;
      padding: 2px 6px;
      border-radius: 4px;
      color: #334155;
      align-self: flex-start;
      font-weight: 600;
    }
    .pedo-links-row {
      display: flex;
      align-items: center;
      gap: 8px;
      margin-top: 4px;
      flex-wrap: wrap;
    }
    .pedo-study-link {
      display: inline-flex;
      align-items: center;
      gap: 4px;
      font-size: 11px;
      font-weight: 600;
      color: #1e4535;
      text-decoration: none;
      padding: 3px 8px;
      border-radius: 5px;
      background: #f0fdf4;
      border: 1px solid #bbf7d0;
      transition: background 0.15s, border-color 0.15s;
    }
    .pedo-study-link:hover {
      background: #dcfce7;
      border-color: #86efac;
    }
    .pedo-pdf-link {
      display: inline-flex;
      align-items: center;
      gap: 4px;
      font-size: 11px;
      font-weight: 600;
      color: #2563eb;
      text-decoration: none;
      padding: 3px 8px;
      border-radius: 5px;
      background: #eff6ff;
      border: 1px solid #bfdbfe;
      transition: background 0.15s;
    }
    .pedo-pdf-link:hover {
      background: #dbeafe;
    }

    .pedo-popup-body {
      padding: 12px 16px 14px 16px;
      display: flex;
      flex-direction: column;
      gap: 10px;
      max-height: 360px;
      overflow-y: auto;
    }
    .pedo-series-heading {
      font-size: 11px;
      font-weight: 700;
      color: #64748b;
      text-transform: uppercase;
      letter-spacing: 0.04em;
      margin-bottom: -2px;
    }
    .pedo-series-card {
      background: #ffffff;
      border: 1px solid #e2e8f0;
      border-radius: 9px;
      padding: 10px 12px;
      display: flex;
      flex-direction: column;
      gap: 6px;
      box-shadow: 0 1px 3px rgba(0, 0, 0, 0.03);
      transition: border-color 0.15s, box-shadow 0.15s;
    }
    .pedo-series-card:hover {
      border-color: #cbd5e1;
      box-shadow: 0 3px 8px rgba(0, 0, 0, 0.06);
    }
    .pedo-series-top {
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 8px;
    }
    .pedo-series-name {
      font-weight: 700;
      color: #0f172a;
      font-size: 13px;
      line-height: 1.3;
    }
    .pedo-series-pct {
      background: #e0f2fe;
      color: #0369a1;
      font-weight: 700;
      font-size: 12px;
      padding: 2px 8px;
      border-radius: 12px;
      white-space: nowrap;
    }
    .pedo-progress-track {
      width: 100%;
      height: 5px;
      background: #f1f5f9;
      border-radius: 3px;
      overflow: hidden;
    }
    .pedo-progress-fill {
      height: 100%;
      background: linear-gradient(90deg, #10b981 0%, #059669 100%);
      border-radius: 3px;
    }
    .pedo-series-action {
      margin-top: 2px;
    }
    .pedo-series-link {
      font-size: 11px;
      color: #1e4535;
      text-decoration: none;
      font-weight: 600;
      display: inline-flex;
      align-items: center;
      gap: 4px;
    }
    .pedo-series-link:hover {
      color: #14532d;
      text-decoration: underline;
    }

    /* Mobile Responsive Rules */
    @media (max-width: 768px) {
      .nav-brand-sub { display: none; }
      .nav-btn span { font-size: 0.76rem; }
      .nav-btn { padding: 5px 8px; }

      .map-controls-panel {
        display: contents;
      }
      .panel-header {
        display: none;
      }

      .search-and-toggle-row {
        position: fixed;
        top: 62px;
        left: 10px;
        right: 10px;
        width: auto;
        z-index: 1000;
        pointer-events: auto;
      }
      .search-input {
        background: rgba(255, 255, 255, 0.98);
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
        padding: 10px 30px 10px 34px;
        font-size: 13px;
        border: 1px solid rgba(203, 213, 225, 0.8);
      }
      .mobile-tools-toggle {
        display: inline-flex;
        padding: 9px 12px;
        background: rgba(255, 255, 255, 0.98);
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
        border: 1px solid rgba(203, 213, 225, 0.8);
      }

      .tools-backdrop {
        display: none;
      }
      .tools-backdrop.active {
        display: block !important;
        opacity: 1 !important;
        pointer-events: auto !important;
      }

      .panel-tools {
        display: none !important;
        position: fixed !important;
        top: auto !important;
        bottom: 0 !important;
        left: 0 !important;
        right: 0 !important;
        width: 100% !important;
        max-width: 100vw !important;
        max-height: 82vh !important;
        overflow-y: auto !important;
        -webkit-overflow-scrolling: touch !important;
        z-index: 2000 !important;
        background: #ffffff !important;
        border-radius: 20px 20px 0 0 !important;
        box-shadow: 0 -8px 32px rgba(0, 0, 0, 0.35) !important;
        padding: 18px 20px 36px 20px !important;
        border: none !important;
        border-top: 1px solid #cbd5e1 !important;
        pointer-events: auto !important;
        gap: 14px !important;
      }
      .panel-tools.open {
        display: flex !important;
        animation: slideUpBottom 0.25s cubic-bezier(0.16, 1, 0.3, 1) forwards !important;
      }

      @keyframes slideUpBottom {
        from { transform: translateY(100%); }
        to { transform: translateY(0); }
      }

      .tools-drawer-header {
        display: flex !important;
      }
    }
  </style>
</head>
<body>

  <!-- Navigation principale du portail -->
  <nav class="portal-navbar" aria-label="Navigation principale">
    <div class="navbar-content">
      <a href="index.html" class="nav-brand">
        <div class="nav-titles">
          <span class="nav-brand-title">Inventaire Pédologique du Québec</span>
          <span class="nav-brand-sub">Archives agronomiques &amp; cartographiques • 1936–2017</span>
        </div>
      </a>
      <div class="nav-actions">
        <a href="index.html" class="nav-btn" title="Accueil du portail">
          <span>Accueil</span>
        </a>
        <a href="carte.html" class="nav-btn active" title="Carte interactive des sols du Québec">
          <span>Carte</span>
        </a>
        <a href="etudes.html" class="nav-btn" title="Consulter les 79 mémoires d'inventaire pédologique régionaux">
          <span>Études</span>
        </a>
        <a href="series/index.html" class="nav-btn" title="Consulter le répertoire des séries de sols du Québec">
          <span>Séries de Sols</span>
        </a>
        <a href="glossaire.html" class="nav-btn" title="Consulter le glossaire pédologique officiel">
          <span>Glossaire</span>
        </a>
      </div>
    </div>
  </nav>

  <!-- Floating Control Panel -->
  <div class="map-controls-panel">
    <div class="panel-header">
      <div class="panel-title">Couverture Pédologique &amp; Topographie</div>
      <div class="panel-subtitle">Sols du Québec, relief MNE 1m &amp; courbes de niveau</div>
    </div>

    <!-- Search Box and Mobile Toggle -->
    <div class="search-and-toggle-row">
      <div class="search-box">
        <div class="search-input-wrapper">
          <svg class="search-icon" viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="11" cy="11" r="8"></circle>
            <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
          </svg>
          <input type="text" id="address-input" class="search-input" placeholder="Rechercher une adresse, ville..." autocomplete="off" />
          <button id="clear-search" class="clear-btn" style="display:none;" title="Effacer">&times;</button>
        </div>
        <div id="search-suggestions" class="search-suggestions" style="display:none;"></div>
      </div>

      <!-- Mobile Toggle Button -->
      <button id="btn-toggle-tools" class="mobile-tools-toggle" type="button" aria-label="Couches et relief" title="Contrôles des couches">
        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <polygon points="12 2 2 7 12 12 22 7 12 2"></polygon>
          <polyline points="2 17 12 22 22 17"></polyline>
          <polyline points="2 12 12 17 22 12"></polyline>
        </svg>
        <span class="mobile-toggle-label">Couches</span>
      </button>
    </div>

    <!-- Tools Panel / Drawer -->
    <div class="panel-tools" id="panel-tools">
      <div class="tools-drawer-header">
        <div class="tools-drawer-title">Affichage &amp; Couches</div>
        <button id="btn-close-tools" class="tools-close-btn" type="button" aria-label="Fermer le panneau">&times;</button>
      </div>

      <!-- 1. Fond de carte -->
      <div class="tool-card">
        <div class="tool-card-title">
          <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><rect x="3" y="3" width="18" height="18" rx="2"></rect><path d="M3 9h18"></path><path d="M9 21V9"></path></svg>
          <span>Fond de carte</span>
        </div>
        <div class="segmented-control">
          <button id="btn-basemap-plan" class="seg-btn active" type="button">Plan</button>
          <button id="btn-basemap-sat" class="seg-btn" type="button">Google Hybride</button>
        </div>
      </div>

      <!-- 2. Sols pédologiques -->
      <div class="tool-card">
        <div class="tool-card-header">
          <div class="tool-card-title">
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"></path></svg>
            <span>Sols pédologiques</span>
          </div>
          <label class="switch-label" title="Afficher/Masquer les sols">
            <input type="checkbox" id="toggle-pedo" checked />
            <span class="switch-slider"></span>
          </label>
        </div>
        <div class="tool-label-row">
          <span class="tool-sublabel">Opacité des sols</span>
          <span id="opacity-val" class="val-badge">80%</span>
        </div>
        <input type="range" id="pedo-opacity" min="0" max="100" value="80" class="slider" />
      </div>

      <!-- 3. Topographie MNE (HRDEM 1m) -->
      <div class="tool-card">
        <div class="tool-card-header">
          <div class="tool-card-title">
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"></polyline></svg>
            <span>Topographie (MNE HRDEM)</span>
          </div>
          <label class="switch-label" title="Afficher/Masquer le relief">
            <input type="checkbox" id="toggle-topo" checked />
            <span class="switch-slider"></span>
          </label>
        </div>

        <div class="topo-gradient-bar" title="Dégradé d'altitude dynamique : mauve au plus bas, rouge au plus haut"></div>
        <div class="topo-gradient-labels">
          <span>Bas (mauve)</span>
          <span>Haut (rouge)</span>
        </div>

        <div id="topo-alt-badge" class="topo-alt-badge">
          Altitude : initialisation...
        </div>

        <div class="tool-label-row">
          <span class="tool-sublabel">Opacité du relief</span>
          <span id="topo-opacity-val" class="val-badge">70%</span>
        </div>
        <input type="range" id="topo-opacity" min="0" max="100" value="70" class="slider" />

        <div class="tool-label-row">
          <span class="tool-sublabel">Étirement viewport</span>
          <div class="segmented-control" style="width: 140px;">
            <button id="btn-stretch-pct" class="seg-btn active" type="button" title="Percentile 5-95%">5-95%</button>
            <button id="btn-stretch-minmax" class="seg-btn" type="button" title="Min-Max total">Min/Max</button>
          </div>
        </div>
      </div>

      <!-- 4. Courbes de niveau dynamiques -->
      <div class="tool-card">
        <div class="tool-card-header">
          <div class="tool-card-title">
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M3 12c3-4 6-4 9 0s6 4 9 0"></path><path d="M3 6c3-4 6-4 9 0s6 4 9 0"></path><path d="M3 18c3-4 6-4 9 0s6 4 9 0"></path></svg>
            <span>Courbes de niveau</span>
          </div>
          <label class="switch-label" title="Afficher/Masquer les courbes de niveau (dès zoom 11)">
            <input type="checkbox" id="toggle-contours" checked />
            <span class="switch-slider"></span>
          </label>
        </div>

        <div class="tool-label-row">
          <span class="tool-sublabel">Intervalle</span>
        </div>
        <div class="pills-group">
          <button class="pill-btn" data-interval="0.1">10 cm</button>
          <button class="pill-btn" data-interval="0.3">30 cm</button>
          <button class="pill-btn active" data-interval="1">1 m</button>
          <button class="pill-btn" data-interval="3">3 m</button>
        </div>

        <div class="tool-label-row" style="margin-top: 4px;">
          <span class="tool-sublabel">Couleur des courbes</span>
          <div class="color-select-row">
            <div class="color-circle active" data-color="#78350f" style="background: #78350f;" title="Brun sépia"></div>
            <div class="color-circle" data-color="#334155" style="background: #334155;" title="Gris ardoise"></div>
            <div class="color-circle" data-color="#0f172a" style="background: #0f172a;" title="Noir profond"></div>
            <div class="color-circle" data-color="#1e4535" style="background: #1e4535;" title="Vert forêt"></div>
          </div>
        </div>

        <div id="contour-status" class="contour-status-badge">
          Zoom 10+ requis pour le calcul dynamique
        </div>
      </div>

      <!-- Source information -->
      <div class="source-info-line">
        <strong>Mosaïque VRT HRDEM Canada 1 m</strong> (56 tuiles) • Sols IRDA 2026
      </div>
    </div>
  </div>

  <!-- Mobile Backdrop Overlay -->
  <div id="tools-backdrop" class="tools-backdrop"></div>

  <div id="map"></div>

  <script>
    const { ContourManager, readCogRegion, fromUrl, proj4 } = window.GeoLibreContour;

    // Initialize PMTiles protocol
    const protocol = new pmtiles.Protocol();
    maplibregl.addProtocol("pmtiles", protocol.tile);

    // Initial map view: Quebec agricultural heartland
    const initialCenter = [-71.2944, 46.3833];
    const initialZoom = 10.5;

    const map = new maplibregl.Map({
      container: "map",
      style: "https://tiles.openfreemap.org/styles/liberty",
      center: initialCenter,
      zoom: initialZoom,
      attributionControl: true
    });

    map.addControl(new maplibregl.NavigationControl({ showCompass: true }), "top-right");
    map.addControl(
      new maplibregl.GeolocateControl({
        positionOptions: { enableHighAccuracy: true },
        trackUserLocation: true,
        showUserLocation: true,
        showAccuracyCircle: true
      }),
      "top-right"
    );
    map.addControl(new maplibregl.ScaleControl({ maxWidth: 100, unit: "metric" }), "bottom-right");

    let searchMarker = null;

    // Study titles dictionary
    const STUDY_NAMES = __STUDY_NAMES_PLACEHOLDER__;

    // Exact HRDEM Mosaics (56 tiles covering Canada & Quebec)
    const EPSG_3979_DEF = '+proj=lcc +lat_1=49 +lat_2=77 +lat_0=49 +lon_0=-95 +x_0=0 +y_0=0 +ellps=GRS80 +towgs84=0,0,0,0,0,0,0 +units=m +no_defs';
    const VALID_HRDEM_TILES = new Set([
      '1_3','1_4','1_5','1_6','1_7','2_3','2_4','2_5','2_6','2_7','2_8',
      '3_3','3_4','3_5','3_6','3_7','3_8','4_3','4_4','4_5','4_6',
      '5_3','5_4','5_6','5_7','5_8','6_2','6_3','6_5','6_6','6_7','6_8',
      '7_2','7_3','7_4','7_5','7_6','7_7','7_8','8_1','8_2','8_3','8_4',
      '8_5','8_6','8_7','9_2','9_3','9_4','9_5','10_2','10_3','10_4','10_5',
      '11_3','11_4'
    ]);

    function findTileForCoords(lng, lat) {
      try {
        const pt = proj4('EPSG:4326', EPSG_3979_DEF, [lng, lat]);
        const col = Math.floor(pt[0] / 500000) + 6;
        const row = Math.floor(pt[1] / 500000) + 3;
        const key = `${col}_${row}`;
        if (VALID_HRDEM_TILES.has(key)) {
          return `https://canelevation-dem.s3.ca-central-1.amazonaws.com/hrdem-mosaic-1m/${key}-mosaic-1m-dtm.tif`;
        }
      } catch (e) {
        console.warn('findTileForCoords calculation error:', e);
      }
      return null;
    }

    // Viewport Raster Stretch Color Ramp: Mauve (lowest) -> Red (highest)
    const TOPO_COLORMAP = [
      { t: 0.00, r: 76,  g: 29,  b: 149 }, // mauve sombre (#4c1d95)
      { t: 0.15, r: 124, g: 58,  b: 237 }, // violet (#7c3aed)
      { t: 0.30, r: 37,  g: 99,  b: 235 }, // bleu royal (#2563eb)
      { t: 0.45, r: 13,  g: 148, b: 136 }, // cyan/sarcelle (#0d9488)
      { t: 0.60, r: 22,  g: 163, b: 74  }, // vert (#16a34a)
      { t: 0.75, r: 234, g: 179, b: 8   }, // jaune (#eab308)
      { t: 0.88, r: 234, g: 88,  b: 12  }, // orange (#ea580c)
      { t: 1.00, r: 220, g: 38,  b: 38  }  // rouge (#dc2626)
    ];

    function interpolateColor(t) {
      if (t <= 0) return TOPO_COLORMAP[0];
      if (t >= 1) return TOPO_COLORMAP[TOPO_COLORMAP.length - 1];
      for (let i = 0; i < TOPO_COLORMAP.length - 1; i++) {
        const c1 = TOPO_COLORMAP[i];
        const c2 = TOPO_COLORMAP[i + 1];
        if (t >= c1.t && t <= c2.t) {
          const ratio = (t - c1.t) / (c2.t - c1.t);
          return {
            r: Math.round(c1.r + (c2.r - c1.r) * ratio),
            g: Math.round(c1.g + (c2.g - c1.g) * ratio),
            b: Math.round(c1.b + (c2.b - c1.b) * ratio)
          };
        }
      }
      return TOPO_COLORMAP[TOPO_COLORMAP.length - 1];
    }

    function stretchPercentile(sorted, fraction) {
      if (sorted.length === 1) return sorted[0];
      const pos = fraction * (sorted.length - 1);
      const low = Math.floor(pos);
      const up = Math.ceil(pos);
      return sorted[low] + (sorted[up] - sorted[low]) * (pos - low);
    }

    function calculateViewportStretchRange(rawValues, method) {
      const valid = [];
      for (let i = 0; i < rawValues.length; i++) {
        const v = rawValues[i];
        if (Number.isFinite(v) && v > -1000 && v < 9000) {
          valid.push(v);
        }
      }
      if (valid.length === 0) return [0, 100];
      valid.sort((a, b) => a - b);
      if (method === "minmax") {
        return [valid[0], valid[valid.length - 1]];
      }
      // Percentile 5-95%
      return [stretchPercentile(valid, 0.05), stretchPercentile(valid, 0.95)];
    }

    // TopoManager handles real-time dynamic viewport raster stretch
    class TopoManager {
      constructor(mapInstance) {
        this.map = mapInstance;
        this.enabled = true;
        this.opacity = 0.70;
        this.stretchMethod = 'percentile'; // 'percentile' or 'minmax'
        this.activeCogUrl = '';
        this.cogPromise = null;
        this.canvas = document.createElement('canvas');
        this.ctx = this.canvas.getContext('2d');
        this.debounceTimer = null;
        this.abortController = null;
        this.sourceAdded = false;
      }

      setStretchMethod(method) {
        this.stretchMethod = method;
        this.scheduleUpdate();
      }

      setOpacity(val) {
        this.opacity = val;
        if (this.map.getLayer('hrdem-topo-layer')) {
          this.map.setPaintProperty('hrdem-topo-layer', 'raster-opacity', this.opacity);
        }
      }

      setEnabled(on) {
        this.enabled = on;
        if (this.map.getLayer('hrdem-topo-layer')) {
          this.map.setLayoutProperty('hrdem-topo-layer', 'visibility', on ? 'visible' : 'none');
        }
        if (on) this.scheduleUpdate();
      }

      async getCog(url) {
        if (this.activeCogUrl === url && this.cogPromise) return this.cogPromise;
        this.activeCogUrl = url;
        this.cogPromise = fromUrl(url, {}, AbortSignal.timeout(30000));
        return this.cogPromise;
      }

      scheduleUpdate() {
        if (!this.enabled) return;
        if (this.debounceTimer) clearTimeout(this.debounceTimer);
        this.debounceTimer = setTimeout(() => {
          this.updateViewport();
        }, 150);
      }

      async updateViewport() {
        if (!this.enabled || !this.map) return;
        const zoom = this.map.getZoom();
        if (zoom < 7) {
          const badge = document.getElementById('topo-alt-badge');
          if (badge) badge.textContent = 'Zoomer pour le relief détaillé (zoom 7+)';
          return;
        }

        const center = this.map.getCenter();
        const tileUrl = findTileForCoords(center.lng, center.lat);
        if (!tileUrl) {
          const badge = document.getElementById('topo-alt-badge');
          if (badge) badge.textContent = 'Hors de la zone MNE HRDEM';
          return;
        }

        if (this.abortController) this.abortController.abort();
        this.abortController = new AbortController();

        const bounds = this.map.getBounds();
        const w = bounds.getWest();
        const s = bounds.getSouth();
        const e = bounds.getEast();
        const n = bounds.getNorth();
        const bbox = [w, s, e, n];

        const badge = document.getElementById('topo-alt-badge');
        if (badge) badge.textContent = 'Calcul du relief...';

        try {
          const cog = await this.getCog(tileUrl);
          const targetSize = 256;
          const region = await readCogRegion(
            cog,
            bbox,
            targetSize,
            -32767,
            false,
            this.abortController.signal,
            'bilinear'
          );

          if (!region || !region.data || region.data.length === 0) {
            if (badge) badge.textContent = 'Aucune donnée MNE dans la vue';
            return;
          }

          const [minAlt, maxAlt] = calculateViewportStretchRange(region.data, this.stretchMethod);
          if (badge) {
            badge.textContent = `Alt: ${Math.round(minAlt)} m (mauve) → ${Math.round(maxAlt)} m (rouge)`;
          }

          const span = Math.max(1, maxAlt - minAlt);
          const width = region.width;
          const height = region.height;

          this.canvas.width = width;
          this.canvas.height = height;
          const imgData = this.ctx.createImageData(width, height);
          const pixels = imgData.data;

          for (let i = 0; i < region.data.length; i++) {
            const val = region.data[i];
            const pIdx = i * 4;
            if (isNaN(val) || val <= -1000 || val >= 9000) {
              pixels[pIdx + 3] = 0;
            } else {
              const norm = Math.max(0, Math.min(1, (val - minAlt) / span));
              const color = interpolateColor(norm);
              pixels[pIdx] = color.r;
              pixels[pIdx + 1] = color.g;
              pixels[pIdx + 2] = color.b;
              pixels[pIdx + 3] = 255;
            }
          }

          this.ctx.putImageData(imgData, 0, 0);
          const dataUrl = this.canvas.toDataURL();

          const actualBbox = region.bboxWgs84 || bbox;
          const coords = region.cornersWgs84 || [
            [actualBbox[0], actualBbox[3]], // Top-Left (NW)
            [actualBbox[2], actualBbox[3]], // Top-Right (NE)
            [actualBbox[2], actualBbox[1]], // Bottom-Right (SE)
            [actualBbox[0], actualBbox[1]]  // Bottom-Left (SW)
          ];

          const source = this.map.getSource('hrdem-topo-source');
          if (source) {
            source.updateImage({
              url: dataUrl,
              coordinates: coords
            });
          } else {
            this.map.addSource('hrdem-topo-source', {
              type: 'image',
              url: dataUrl,
              coordinates: coords
            });
            this.map.addLayer({
              id: 'hrdem-topo-layer',
              type: 'raster',
              source: 'hrdem-topo-source',
              layout: { visibility: this.enabled ? 'visible' : 'none' },
              paint: {
                'raster-opacity': this.opacity,
                'raster-resampling': 'linear',
                'raster-fade-duration': 180
              }
            }, 'pedologie-fill');
            this.sourceAdded = true;
          }
        } catch (err) {
          if (err.name === 'AbortError') return;
          console.warn('Topo viewport stretch update failed:', err);
        }
      }
    }

    let topoManager = null;
    let contourManager = null;

    map.on("load", () => {
      // 1. Google Hybrid Raster Source
      map.addSource("google-hybrid-source", {
        type: "raster",
        tiles: [
          "https://mt0.google.com/vt/lyrs=y&x={x}&y={y}&z={z}",
          "https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}",
          "https://mt2.google.com/vt/lyrs=y&x={x}&y={y}&z={z}",
          "https://mt3.google.com/vt/lyrs=y&x={x}&y={y}&z={z}"
        ],
        tileSize: 256,
        attribution: "© Google"
      });

      // 2. Vector PMTiles Source
      map.addSource("pedologie", {
        type: "vector",
        url: "pmtiles://https://storage.googleapis.com/geoqc/Pedologie/couverture_pedologique.pmtiles"
      });

      // Google Hybrid Layer
      map.addLayer({
        id: "google-hybrid-layer",
        type: "raster",
        source: "google-hybrid-source",
        layout: { visibility: "none" }
      });

      // 3. Polygon Fill layer
      map.addLayer({
        id: "pedologie-fill",
        type: "fill",
        source: "pedologie",
        "source-layer": "pedologie_quebec",
        filter: ["==", ["geometry-type"], "Polygon"],
        paint: {
          "fill-color": ["coalesce", ["get", "color"], "#b23434"],
          "fill-opacity": 0.8
        }
      });

      // 4. Polygon Boundaries
      map.addLayer({
        id: "pedologie-line",
        type: "line",
        source: "pedologie",
        "source-layer": "pedologie_quebec",
        paint: {
          "line-color": "#1e293b",
          "line-width": [
            "interpolate", ["linear"], ["zoom"],
            8, 0.4,
            12, 0.8,
            16, 1.5
          ],
          "line-opacity": 0.4
        }
      });

      // 5. Polygon LABELS (minzoom: 12)
      map.addLayer({
        id: "pedologie-labels",
        type: "symbol",
        source: "pedologie",
        "source-layer": "pedologie_quebec",
        minzoom: 12,
        maxzoom: 24,
        layout: {
          "text-field": ["to-string", ["coalesce", ["get", "Appellation_cartographique"], ""]],
          "text-font": ["Noto Sans Regular"],
          "text-size": [
            "interpolate", ["linear"], ["zoom"],
            12, 10,
            14, 12,
            16, 15
          ],
          "text-anchor": "center",
          "text-allow-overlap": false,
          "text-ignore-placement": false,
          "text-max-width": 8
        },
        paint: {
          "text-color": "#0f172a",
          "text-halo-color": "rgba(255, 255, 255, 0.85)",
          "text-halo-width": 2,
          "text-halo-blur": 0.5,
          "text-opacity": 0.8
        }
      });

      // Instantiate Topography Manager
      topoManager = new TopoManager(map);
      topoManager.scheduleUpdate();

      // Instantiate ContourManager from geolibre-plugin
      const mockApp = {
        getMap: () => map,
        getLocale: () => 'fr',
        translate: (k, fallback) => fallback
      };
      contourManager = new ContourManager(mockApp);
      
      const defaultTile = findTileForCoords(initialCenter[0], initialCenter[1]);
      contourManager.updateConfig({
        cogUrl: defaultTile,
        interval: 1,
        majorEvery: 5,
        gridSize: 128,
        minZoom: 10,
        lineColor: "#78350f",
        majorWidth: 1.6,
        minorWidth: 0.8,
        labelSize: 10
      });

      const contourStatusEl = document.getElementById('contour-status');
      contourManager.setStatusListener((text, kind) => {
        if (contourStatusEl) {
          contourStatusEl.textContent = text;
          contourStatusEl.className = 'contour-status-badge ' + (kind === 'success' ? 'active' : '');
        }
      });

      contourManager.setup(map);

      // Camera move listeners
      map.on('moveend', () => {
        if (topoManager) topoManager.scheduleUpdate();
        
        if (contourManager) {
          const center = map.getCenter();
          const currentTile = findTileForCoords(center.lng, center.lat);
          if (contourManager.config.cogUrl !== currentTile) {
            contourManager.updateConfig({ cogUrl: currentTile });
          }
        }
      });

      // Cursor pointer on polygon hover
      map.on("mouseenter", "pedologie-fill", () => {
        map.getCanvas().style.cursor = "pointer";
      });
      map.on("mouseleave", "pedologie-fill", () => {
        map.getCanvas().style.cursor = "";
      });

      // Click to identify with rich popup
      map.on("click", "pedologie-fill", (e) => {
        if (!e.features || !e.features.length) return;
        const p = e.features[0].properties;

        const rawEtude = String(p.No_etude || p.etude_code || "").trim();
        const etudeUrl = (p.etude_url || "").trim();
        const appellation = (p.Appellation_cartographique || "").trim();

        let studyInfo = null;
        let cleanEtudeCode = rawEtude.replace(/^0+/, "");
        if (rawEtude) {
          studyInfo = STUDY_NAMES[rawEtude] || STUDY_NAMES[cleanEtudeCode] || STUDY_NAMES[rawEtude.padStart(2, "0")];
        }
        const studyTitle = studyInfo ? studyInfo.title : (rawEtude ? "Étude pédologique nº " + rawEtude : "Étude pédologique");
        const studyYear = studyInfo ? studyInfo.year : "";
        const localPqFile = "pq" + cleanEtudeCode.toLowerCase() + ".html";

        let cardsHtml = "";
        let validSeriesCount = 0;

        for (let i = 1; i <= 4; i++) {
          const desc = (p["s" + i + "_desc"] || "").trim();
          const rawPct = p["s" + i + "_pct"];
          const pctNum = parseFloat(rawPct);
          const rawUrl = (p["s" + i + "_url"] || "").trim();

          if (!desc || isNaN(pctNum) || pctNum <= 0) continue;

          validSeriesCount++;
          const pctDisplay = Math.round(pctNum);

          cardsHtml += `
            <div class="pedo-series-card">
              <div class="pedo-series-top">
                <span class="pedo-series-name">${desc}</span>
                <span class="pedo-series-pct">${pctDisplay}%</span>
              </div>
              <div class="pedo-progress-track">
                <div class="pedo-progress-fill" style="width: ${Math.min(pctDisplay, 100)}%;"></div>
              </div>
              ${rawUrl ? `
                <div class="pedo-series-action">
                  <a href="${rawUrl}" target="_blank" rel="noopener noreferrer" class="pedo-series-link">
                    <span>Consulter la fiche descriptive</span>
                    <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                      <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"></path>
                      <polyline points="15 3 21 3 21 9"></polyline>
                      <line x1="10" y1="14" x2="21" y2="3"></line>
                    </svg>
                  </a>
                </div>` : ""}
            </div>
          `;
        }

        if (!cardsHtml) {
          cardsHtml = '<div style="color: #64748b; font-style: italic; padding: 6px 0;">Séries de sols non détaillées pour ce polygone.</div>';
        }

        const popupHtml = `
          <div class="pedo-popup">
            <div class="pedo-popup-header">
              <div class="pedo-study-meta">
                ${rawEtude ? `<span class="pedo-study-badge">Étude nº ${rawEtude}</span>` : ""}
                ${studyYear ? `<span class="pedo-study-year">(${studyYear})</span>` : ""}
              </div>
              <h3 class="pedo-popup-title">${studyTitle}</h3>
              ${appellation ? `<div class="pedo-appellation" title="Appellation cartographique">${appellation}</div>` : ""}
              
              <div class="pedo-links-row">
                <a href="${localPqFile}" target="_blank" rel="noopener noreferrer" class="pedo-study-link">
                  <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"></path>
                    <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"></path>
                  </svg>
                  <span>Mémoire sur le portail &rarr;</span>
                </a>
                ${etudeUrl ? `
                  <a href="${etudeUrl}" target="_blank" rel="noopener noreferrer" class="pedo-pdf-link">
                    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                      <polyline points="14 2 14 8 20 8"></polyline>
                      <line x1="16" y1="13" x2="8" y2="13"></line>
                    </svg>
                    <span>Rapport PDF &rarr;</span>
                  </a>` : ""}
              </div>
            </div>
            <div class="pedo-popup-body">
              ${validSeriesCount > 0 ? '<div class="pedo-series-heading">Séries de sols identifiées</div>' : ''}
              ${cardsHtml}
            </div>
          </div>
        `;

        new maplibregl.Popup({ closeButton: true, offset: 8 })
          .setLngLat(e.lngLat)
          .setHTML(popupHtml)
          .addTo(map);
      });
    });

    // --- UI Controls Event Handlers ---

    // Basemap Switcher
    const btnPlan = document.getElementById("btn-basemap-plan");
    const btnSat = document.getElementById("btn-basemap-sat");

    btnPlan.addEventListener("click", () => {
      btnPlan.classList.add("active");
      btnSat.classList.remove("active");
      if (map.getLayer("google-hybrid-layer")) {
        map.setLayoutProperty("google-hybrid-layer", "visibility", "none");
      }
    });

    btnSat.addEventListener("click", () => {
      btnSat.classList.add("active");
      btnPlan.classList.remove("active");
      if (map.getLayer("google-hybrid-layer")) {
        map.setLayoutProperty("google-hybrid-layer", "visibility", "visible");
      }
    });

    // Pedo Layer Toggle & Opacity Slider
    const togglePedo = document.getElementById("toggle-pedo");
    const opacitySlider = document.getElementById("pedo-opacity");
    const opacityVal = document.getElementById("opacity-val");

    function updatePedoLayerVisibility() {
      const isVisible = togglePedo.checked;
      const opacity = isVisible ? (parseInt(opacitySlider.value, 10) / 100) : 0;
      
      opacityVal.textContent = isVisible ? (opacitySlider.value + "%") : "Masqué";
      
      if (map.getLayer("pedologie-fill")) {
        map.setLayoutProperty("pedologie-fill", "visibility", isVisible ? "visible" : "none");
        map.setPaintProperty("pedologie-fill", "fill-opacity", opacity);
      }
      if (map.getLayer("pedologie-line")) {
        map.setLayoutProperty("pedologie-line", "visibility", isVisible ? "visible" : "none");
        map.setPaintProperty("pedologie-line", "line-opacity", opacity * 0.5);
      }
      if (map.getLayer("pedologie-labels")) {
        map.setLayoutProperty("pedologie-labels", "visibility", isVisible ? "visible" : "none");
        map.setPaintProperty("pedologie-labels", "text-opacity", opacity);
      }
    }

    togglePedo.addEventListener("change", updatePedoLayerVisibility);
    opacitySlider.addEventListener("input", updatePedoLayerVisibility);

    // Topo Layer Toggle, Opacity & Stretch Controls
    const toggleTopo = document.getElementById("toggle-topo");
    const topoOpacitySlider = document.getElementById("topo-opacity");
    const topoOpacityVal = document.getElementById("topo-opacity-val");
    const btnStretchPct = document.getElementById("btn-stretch-pct");
    const btnStretchMinMax = document.getElementById("btn-stretch-minmax");

    toggleTopo.addEventListener("change", (e) => {
      if (topoManager) topoManager.setEnabled(e.target.checked);
    });

    topoOpacitySlider.addEventListener("input", (e) => {
      const pct = parseInt(e.target.value, 10);
      topoOpacityVal.textContent = pct + "%";
      if (topoManager) topoManager.setOpacity(pct / 100);
    });

    btnStretchPct.addEventListener("click", () => {
      btnStretchPct.classList.add("active");
      btnStretchMinMax.classList.remove("active");
      if (topoManager) topoManager.setStretchMethod("percentile");
    });

    btnStretchMinMax.addEventListener("click", () => {
      btnStretchMinMax.classList.add("active");
      btnStretchPct.classList.remove("active");
      if (topoManager) topoManager.setStretchMethod("minmax");
    });

    // Dynamic Contours Controls
    const toggleContours = document.getElementById("toggle-contours");
    const pillButtons = document.querySelectorAll(".pill-btn");
    const colorCircles = document.querySelectorAll(".color-circle");

    toggleContours.addEventListener("change", (e) => {
      const on = e.target.checked;
      for (const layerId of ["gc-contour-minor", "gc-contour-major", "gc-contour-labels"]) {
        if (map.getLayer(layerId)) {
          map.setLayoutProperty(layerId, "visibility", on ? "visible" : "none");
        }
      }
      if (on && contourManager) {
        contourManager.generateForView();
      }
    });

    pillButtons.forEach(btn => {
      btn.addEventListener("click", () => {
        pillButtons.forEach(b => b.classList.remove("active"));
        btn.classList.add("active");
        const interval = parseFloat(btn.dataset.interval);
        let majorEvery = 5;
        if (interval === 0.1) majorEvery = 10;
        else if (interval === 0.3) majorEvery = 5;
        else if (interval === 1) majorEvery = 5;
        else if (interval === 3) majorEvery = 5;
        if (contourManager) {
          contourManager.updateConfig({ interval, majorEvery });
          contourManager.generateForView();
        }
      });
    });

    colorCircles.forEach(circle => {
      circle.addEventListener("click", () => {
        colorCircles.forEach(c => c.classList.remove("active"));
        circle.classList.add("active");
        const color = circle.dataset.color;
        if (contourManager) {
          contourManager.updateConfig({ lineColor: color });
          contourManager.updatePaintProperties();
        }
      });
    });

    // Address Search Logic (Nominatim API)
    const addressInput = document.getElementById("address-input");
    const clearBtn = document.getElementById("clear-search");
    const suggestionsBox = document.getElementById("search-suggestions");
    let searchDebounce = null;

    addressInput.addEventListener("input", (e) => {
      const q = e.target.value.trim();
      clearBtn.style.display = q ? "block" : "none";
      clearTimeout(searchDebounce);

      if (q.length < 3) {
        suggestionsBox.style.display = "none";
        suggestionsBox.innerHTML = "";
        return;
      }

      searchDebounce = setTimeout(async () => {
        try {
          const url = `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(q)}&countrycodes=ca&limit=5&addressdetails=1`;
          const res = await fetch(url, { headers: { "User-Agent": "PedologieQuebecApp/1.0" } });
          const results = await res.json();

          if (!results || results.length === 0) {
            suggestionsBox.innerHTML = '<div style="padding: 10px; font-size: 11px; color: #64748b;">Aucun résultat trouvé</div>';
            suggestionsBox.style.display = "block";
            return;
          }

          suggestionsBox.innerHTML = "";
          results.forEach((item) => {
            const div = document.createElement("div");
            div.className = "suggestion-item";
            div.textContent = item.display_name;
            div.addEventListener("click", () => {
              const lat = parseFloat(item.lat);
              const lon = parseFloat(item.lon);
              addressInput.value = item.display_name;
              suggestionsBox.style.display = "none";

              if (searchMarker) searchMarker.remove();
              searchMarker = new maplibregl.Marker({ color: "#204838" })
                .setLngLat([lon, lat])
                .addTo(map);

              map.flyTo({ center: [lon, lat], zoom: 14, duration: 1500 });
            });
            suggestionsBox.appendChild(div);
          });
          suggestionsBox.style.display = "block";
        } catch (err) {
          console.error("Erreur de recherche d'adresse:", err);
        }
      }, 300);
    });

    clearBtn.addEventListener("click", () => {
      addressInput.value = "";
      clearBtn.style.display = "none";
      suggestionsBox.style.display = "none";
      suggestionsBox.innerHTML = "";
      if (searchMarker) {
        searchMarker.remove();
        searchMarker = null;
      }
      addressInput.focus();
    });

    document.addEventListener("click", (e) => {
      if (!e.target.closest(".search-box")) {
        suggestionsBox.style.display = "none";
      }
    });
  
    // Mobile Tools Drawer Toggle
    const btnToggleTools = document.getElementById("btn-toggle-tools");
    const btnCloseTools = document.getElementById("btn-close-tools");
    const panelTools = document.getElementById("panel-tools");
    const toolsBackdrop = document.getElementById("tools-backdrop");

    function openMobileTools() {
      if (panelTools) panelTools.classList.add("open");
      if (toolsBackdrop) toolsBackdrop.classList.add("active");
      if (btnToggleTools) btnToggleTools.classList.add("active");
    }

    function closeMobileTools() {
      if (panelTools) panelTools.classList.remove("open");
      if (toolsBackdrop) toolsBackdrop.classList.remove("active");
      if (btnToggleTools) btnToggleTools.classList.remove("active");
    }

    if (btnToggleTools) {
      btnToggleTools.addEventListener("click", function(e) {
        e.preventDefault();
        e.stopPropagation();
        if (panelTools && panelTools.classList.contains("open")) {
          closeMobileTools();
        } else {
          openMobileTools();
        }
      });
    }

    if (btnCloseTools) {
      btnCloseTools.addEventListener("click", function(e) {
        e.preventDefault();
        e.stopPropagation();
        closeMobileTools();
      });
    }

    if (toolsBackdrop) {
      toolsBackdrop.addEventListener("click", function(e) {
        e.preventDefault();
        e.stopPropagation();
        closeMobileTools();
      });
    }
  </script>
</body>
</html>
"""

html_final = html_template.replace('__STUDY_NAMES_PLACEHOLDER__', study_names_json)

with open('output_html/carte.html', 'w', encoding='utf-8') as f:
    f.write(html_final)

with open('site/untitled-project.html', 'w', encoding='utf-8') as f:
    f.write(html_final)

print('Successfully created output_html/carte.html and site/untitled-project.html!')
