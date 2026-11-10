# REDACTION — harmoniser ce qui est écrit

Corpus mesuré : **21 pages**, 7 trios FR/EN/AR, 89 lignes d'équation par langue.

## Les six règles tenues par le corpus

1. **Un rang, trois langues.** Le badge porte sa classe `o`/`p`/`s` partout, seul le mot se traduit : 178 badges alignés.
2. **La ligne calculée n'est pas une phrase.** Elle est rendue identiquement dans les trois langues : 89/89 lignes portant les nombres, contre 56/89 en anglais et 55/89 en arabe quand on la retire.
3. **Un chemin de vérification par équation.** 89/89 lignes donnent `module.py → une ou plusieurs fonctions() → Cnn` dans les trois langues, dont 85 en une seule fonction.
4. **Une idée par ligne, 30 mots au plus.** Ce module s'y tient : 38 lignes auto-mesurées, maximum 20 mots.
5. **La coupe respecte la langue.** L'arabe sépare par « ؛ » : 45 occurrences ; l'ignorer déplace la moyenne de 1.03 mots.
6. **Ce qui n'est pas traduit est écrit.** 89 lignes de contrôle restent françaises en EN et AR ; 0 balise `<dfn>` sur 21 pages.

## Les phrases longues, mesurées

- moyennes de mots par phrase : FR 8.74–20.18, EN 7.53–20.05, AR 6.21–16.21
- phrase la plus longue : 95 mots, page CHIFFRES/artefacts/pages/chiffres_en.html
- pages au-dessus de 10 % de phrases longues : {'fr': 2, 'en': 2, 'ar': 1}

## Ce qui reste ouvert

- 89 lignes de contrôle restent en français dans les pages anglaise et arabe
- 5 pages sur 21 dépassent 10 % de phrases de plus de 30 mots
- 0 balise <dfn> et 0 occurrence de « glossaire » : aucun terme n'est défini à sa première occurrence
- aucune lecture humaine mesurée : aucun test de compréhension n'a été conduit
- la ligne calculée harmonisée n'est pas traduite : elle porte les nombres, pas la phrase qui les explique

## Ce que cela ne dit pas

- ce dossier compte des mots et des cellules : il ne mesure pas la compréhension, aucun lecteur n'a été testé
- aucun indice de lisibilité publié n'est utilisé : le seul seuil est celui que l'auteur a retenu, 30 mots par phrase
- la ligne calculée harmonisée n'est pas traduite : elle donne les nombres, pas la phrase qui les explique dans la langue du lecteur
- 89 lignes de contrôle restent en français dans les pages anglaise et arabe
- 5 pages sur 21 dépassent encore 10 % de phrases de plus de 30 mots
- 0 balise <dfn> : aucun terme n'est défini à sa première occurrence
- les valeurs mesurées sont celles du corpus à l'instant de la lecture : une régénération des pages peut les déplacer
- la vidéo n'a fourni que des titres de chapitres : son contenu parlé est absent et n'est cité nulle part

Racine Merkle : `eac768b27c7314703b94a6bc72839034db77f7d1f249cbadd0882974c2be3a6c`
