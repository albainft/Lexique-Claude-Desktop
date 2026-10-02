# Lexique

Page de lexique autonome : une fiche par mot, avec sa version anglaise, sa catégorie, une définition et des renvois. Le fichier `lexique.md` fourni est un exemple de six mots, à remplacer par les vôtres.

La page `docs/index.html` est autonome (recherche, filtres par catégorie, lien direct vers un mot par `#mot`). Elle se publie telle quelle avec GitHub Pages (branche `main`, dossier `/docs`).

## Catégories
Les catégories se déclarent dans `lexique.md`, sous `# Catégories`, une ligne `- nom: description` chacune. Leur ordre fixe l'ordre des boutons de filtre ; la description s'affiche au survol. Une fiche ne peut utiliser qu'une catégorie déclarée.

## Ajouter ou modifier un mot
1. Éditer `lexique.md` : une section `## Mot` avec les champs `anglais`, `catégorie`, `définition`, et `voir` (facultatif, uniquement des mots existants).
2. Régénérer la page : `python3 gen_lexique.py` (`--check` vérifie sans écrire).

## Licence
MIT, voir `LICENSE`.
