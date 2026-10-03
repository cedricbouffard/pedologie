#  [Portail web](https://github.com/cedricbouffard/pedologie)


# Inventaire et Portail Pédologique du Québec

> **Portail numérique unifié des 79 mémoires d'inventaire pédologique, du répertoire des séries de sols et du glossaire pédologique québécois.**
> Agriculture et Agroalimentaire Canada (SISCan) & Ministère de l'Agriculture, des Pêcheries et de l'Alimentation du Québec (MAPAQ).
>
> 🌐 Dépôt & signalement d'erreurs : [https://github.com/cedricbouffard/pedologie](https://github.com/cedricbouffard/pedologie)

---

## Présentation du portail

Ce projet rassemble et valorise le corpus des inventaires pédologiques publiés entre 1936 et 2017 par les équipes de recherche fédérales, provinciales et de l'IRDA.

Le portail est articulé autour de 3 piliers interconnectés :
1. **Études Pédologiques** : Registre complet des 79 mémoires d'inventaire de comtés et régions, avec recherche plein-texte, métadonnées, transcriptions intégrales et planches photographiques d'origine.
2. **Répertoire des Séries de Sols** : Catalogue exhaustif des séries pédologiques répertoriées au Québec, avec comparaison des phases/variantes et analyse des différenciations d'une étude à l'autre.
3. **Glossaire Pédologique** : Dictionnaire des termes techniques, classifications taxonomiques canadiennes (CSSC / SCPS), processus de pédogenèse, horizons diagnostiques et régimes hydriques.

### Contribution & Amélioration collaborative
Ce répertoire documentaire d'envergure peut comporter des coquilles ou des erreurs résiduelles de transcription historique. Les utilisateurs, agronomes et chercheurs sont invités à soulever des anomalies ou à proposer des corrections directement :
- En ouvrant une [Issue GitHub](https://github.com/cedricbouffard/pedologie/issues)
- En soumettant une [Pull Request](https://github.com/cedricbouffard/pedologie/pulls)

1. **Recherche globale instantanée (`Ctrl+K` ou touche `/`)** :
   - Indexation plein texte des 79 rapports, 3 198 séries de sols et 1 222 sections.
   - Filtres par catégories : *Tous*, *Séries de sols*, *Rapports*, *Chapitres*.
   - Surlignage dynamique des termes recherchés.
   - Navigation complète au clavier (`↑`, `↓`, `Entrée`, `Échap`).
2. **Barre de navigation archivistique** :
   - Présente sur l'ensemble des 79 rapports pour revenir à l'inventaire ou lancer une recherche.
3. **Typographie et mise en page éditoriale** :
   - Présentation inspirée des publications scientifiques et des fonds d'archives nationales.
   - Mise en valeur sobre et rigoureuse des séries de sols.
   - Tableaux analytiques avec défilement horizontal et respect des alignements de colonnes.
   - Filtrage chronologique par période sur la page d'accueil (1936 à 2001).
   - Double mode d'affichage : grille bibliographique ou vue tabulaire dense.

---

## Consultation en local

Pour tester la collection en local avec l'index de recherche :

```bash
# À la racine du projet :
python -m http.server 8000
```

Accédez ensuite à l'adresse : **[http://localhost:8000/output_html/](http://localhost:8000/output_html/)** (ou **http://localhost:8000/**).

---

## Déploiement sur GitHub Pages

Le dépôt est configuré pour un déploiement direct sur **GitHub Pages**.

### Déploiement automatique avec GitHub Actions

1. Publiez le dépôt sur GitHub :
   ```bash
   git add .
   git commit -m "Mise à jour: Inventaire pédologique du Québec et recherche globale"
   git branch -M main
   git remote add origin https://github.com/<UTILISATEUR>/<DEPOT>.git
   git push -u origin main
   ```
2. Dans les paramètres du dépôt sur GitHub (**Settings** > **Pages**) :
   - Sous **Source**, sélectionnez **GitHub Actions**.
3. Le fichier de workflow `.github/workflows/deploy.yml` déploie automatiquement le sous-dossier `output_html/`.

---

## Organisation des fichiers

```text
├── .github/workflows/
│   └── deploy.yml            # Automatisation du déploiement GitHub Pages
├── output_html/              # Site statique complet
│   ├── index.html            # Inventaire général avec filtres et statistiques
│   ├── style.css             # Feuille de styles scientifique et patrimoniale
│   ├── search.js             # Moteur de recherche modal
│   ├── search_index.json     # Index (79 rapports, 3 198 séries, 1 222 sections)
│   ├── pq*.html              # 79 rapports pédologiques
│   ├── images/               # Photographies, coupes, cartes et schémas
│   └── .nojekyll             # Maintien des assets pour GitHub Pages
├── .gitignore                # Fichiers exclus (PDFs bruts, caches, environnement)
├── .nojekyll                 # Compatibilité racine
├── index.html                # Redirection racine vers output_html/
└── README.md                 # Documentation
```

---
