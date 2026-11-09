# DÉPÔT ZENODO — AL-MIZAN : Émulateur quantique & Arbre de savoir du millénaire

**Auteurs** : M. Ahmed EL BAHLOUL (IMAM8MAHDI) — développement assisté par IA générative (Devin SWE-2, Cognition AI), résultats relus et dirigés par l'auteur humain
**DOI Zenodo** : [10.5281/zenodo.24028242](https://doi.org/10.5281/zenodo.24028242) — DOI de concept, il résout toujours vers la dernière version publiée
**Chaîne de versions** : la dernière version publiée est v3.2.1, [10.5281/zenodo.24075082](https://doi.org/10.5281/zenodo.24075082), archive `AL-MIZAN_v321_c05f7ee.zip` (818 588 octets, SHA-256 `1d681d2d68ac45d2…`), construite par `git -c core.autocrlf=false archive --format=zip HEAD` — donc sur les octets des blobs scellés, jamais sur l'arbre de travail Windows. Un record publié n'est pas amendable : corriger un document du dépôt coûte un numéro de version. `CITATION.cff` porte la version du **contenu** de l'archive, jamais son propre DOI de version — même règle d'auto-référence que `MANIFESTE_SHA256.txt`, qui s'exclut lui-même du scellement.
**Licence** : AGPL-3.0 / GPL-3.0 (double licence, voir LICENSE.md, LICENSE-AGPL, LICENSE-GPL). Le champ licence, unique sur Zenodo, y porte AGPL-3.0-only.
**Horloge noyau** : copie intégrale scellée conforme au verrou A137 (lecture/copie autorisées, contenu intact)

## Contenu du dépôt

```
ZENODO_DEPOT_ALMIZAN/
├── code/                    # émulateur quantique complet (13 modules)
│   ├── noyau_statevector.py     # vecteur d'état, 20+ portes, Born
│   ├── noyau_matrice_densite.py # évolution Kraus, entropie, fidélité
│   ├── frontend_qasm.py         # OpenQASM 2.0 + .aq + canoniques
│   ├── metriques.py             # Bloch, concurrence, entropie partielle
│   ├── rendu_circuit.py         # dessin ASCII
│   ├── attenuation_zne.py       # ZNE Richardson
│   ├── algorithmes.py           # VQE H₂ (0.00 mHa), Shor 15=3×5
│   ├── serveur_die_5030.py      # die émulé TCP JSON (protocole système)
│   ├── generateur_gds.py        # GDSII binaire valide + DRC générique
│   ├── ponts_systeme.py         # QEC Steane, transducteur, horloge (RO)
│   ├── conjecture_point_carre.py# PC-1..PC-6, preuve par exhaustion
│   ├── chasse_theoremes.py      # invariants cachés (Q°·cycle=semence²)
│   └── emulateur_mizan.py       # CLI : run, qec, zne, vqe, shor, gds,
│                                #      serveur, canoniques, conjecture,
│                                #      arbre, reductions, plan
├── certificats/             # l'arbre de savoir (14 modules)
│   ├── n01..n07_*.py            # un nœud par problème du millénaire
│   ├── rigueur_intervalle.py    # Z(t) en enceintes garanties — TVI
│   ├── preuve_strip_riemann.py  # 29 zéros certifiés ≤ T=100
│   ├── preuve_N_T.py            # THÉORÈME : tous zéros ≤100 en ligne
│   ├── preuve_bsd_attaque.py    # L(E,1), L'(E,1) par équation fonctionnelle
│   ├── niveau3_reductions.py    # ponts fini→infini posés
│   ├── plan_global.py           # échelles de lemmes ×5
│   ├── equations_recherche.py   # énoncés exacts des goulots
│   └── arbre_savoir.py          # orchestrateur (10 branches)
├── ABONDANCE/             # 54 équations · 54 contrôles · 3 dossiers
│   ├── electricite_abondance.py #   électricité  · 21 équations bornées
│   ├── eau_abondance.py         #   eau          · 15 équations bornées
│   ├── agriculture_abondance.py #   agriculture  · 18 équations bornées
│   ├── generer_abondance.py     # pages FR/EN/AR + SVG + JSON + CSV Excel
│   ├── moteur_page_trilingue.py # garde-fou numérique des textes traduits
│   ├── artefacts/               # 31 livrables régénérés
│   └── tests/                   # 107 tests
├── CHIFFRES/              # π, e, √2 : 17 équations · 17 contrôles
│   ├── generer_chiffres.py      # deux voies INDÉPENDANTES par constante
│   ├── chiffres_pi.py           # 108 cellules pré-déclarées puis confrontées
│   ├── artefacts/               # predictions / mesures / confrontation (n = 10⁶)
│   ├── SOURCES_ET_PREDECESSEURS.md
│   └── tests/                   # 32 tests
├── FONDATION/             # la base universelle : 4 piliers, 3 couches, 18 équations
│   ├── fondation_base.py        # axiome hors matrice → prédiction gelée → NA62
│   ├── generer_fondation.py     # pages FR/EN/AR + SVG + JSON + CSV Excel
│   ├── OUTILS/audit_piliers.py  # rejoue les 4 piliers sur tout module du dépôt
│   ├── SIMULATIONS/simuler_kaons.py  # V1..V5 Monte-Carlo Poisson, graine 20261109
│   ├── artefacts/               # 13 livrables, dont la confrontation de 18 équations
│   ├── SOURCES_ET_PREDECESSEURS.md
│   └── tests/                   # 45 tests
├── tests/                 # 53 tests unittest — tous verts, 0 ignoré
├── resultats/             # rapports JSON scellés SHA-256 + .gds
├── bibliotheques/         # 5 modules du moteur ASTRO-Q°ODE : clôture
│   │                      # transitive exacte de ce que ce dépôt importe
│   ├── lib_informe.py           # MatriceLogiqueComplexe, Q·degré
│   ├── lib_physique.py          # états Sol/Terre/Lune, 14 Formes
│   ├── lib_temporelle.py        # cycles dx dy dz dt
│   ├── lib_monade.py            # MonadeSupreme, transcription >>=
│   └── lib_almizan_extension.py # 27 Formes, invariants 0.6225 / 0.122
├── moteur/                # 2 briques quantiques souveraines, pur stdlib
│   ├── qubit_logique_mizan.py              # Steane [[7,1,3]]
│   └── transducteur_quantique_deterministe_mizan.py  # A–S, MIZAN 0.6225
├── horloge_noyau/         # noyau logique scellé (copie A137) + ses 10 tests
├── HOMMAGE_PREDECESSSEURS.md
├── .zenodo.json           # métadonnées du dépôt
├── CITATION.cff, NOTICE.txt, LICENSE-*
└── MANIFESTE_SHA256.txt
```

**Convention du manifeste** : une empreinte par fichier, deux espaces,
puis le chemin ; tri global par chemin, ce qui regroupe de fait les
répertoires de premier niveau. Les hashes
portent sur les octets **normalisés LF** du blob git — donc `sha256sum`
sur un worktree Windows (`core.autocrlf=true`, fins CRLF) ne correspondra
pas. Pour vérifier depuis n'importe quel système :

```
git cat-file blob HEAD:CHEMIN | sha256sum     # une ligne du manifeste
```

Le même contrat est rejouable par un tiers sans copier de commande :

```
py -3 FONDATION/OUTILS/sceller_manifeste.py --verifier   # lecture seule, rc 1 si divergent
py -3 FONDATION/OUTILS/sceller_manifeste.py              # régénère après un commit
```

Le manifeste scelle tout fichier suivi par git **sauf lui-même** (pas
d'auto-référence).

`python code/conjecture_point_carre.py` se rejoue **avec** le moteur : les
cinq modules de `bibliotheques/` sont la clôture transitive exacte de ce que
ce dépôt importe, donc PC-3, PC-4 et PC-5 sont recalculés depuis la table et
`controles_en_repli` reste vide. Le repli sur les constantes déclarées — et la
note qui l'annonce dans le champ `statut` — ne se repeuple que si l'on retire
`bibliotheques/` du dépôt. Les deux modes rendent les mêmes nombres ; une
seule feuille diffère, `PC-4.ppcm_12`, que le repli ne sait pas calculer et
laisse à `null`.

`.gitattributes` impose `eol=lf` sur `horloge_noyau/`, `bibliotheques/` et
`moteur/` : la capsule `horloge_noyau` recompte le SHA-256 des octets **sur
disque** à chaque import, et un worktree Windows en CRLF faisait échouer son
propre sceau (`ALTERATION DÉTECTÉE`) sans que le dépôt ait bougé. Pour les
autres chemins, la commande `git cat-file` ci-dessus reste la voie sûre.

## Ce qui est démontré (théorèmes, pas mesures)

1. **Conjecture du Point Carré** — PC-1..PC-6 vérifiés par exhaustion sur
   le domaine fini Al-Mizan (19 échelons, 13 constantes).
2. **Riemann strip ≤ 100** — les 29 zéros non triviaux avec 0<Im≤100 sont
   sur Re=½ et simples (méthode de Turing : comptage ligne certifié par
   intervalles + N(T) calculé exactement + égalité).
3. **Invariants cachés** — 8766² = 12·dx et 8496² = 768·dy
   (dx = 6 403 563, dy = 93 987 ; en heures les cycles valent dx/128 et
   dy/2, d'où Q°·d' = s² avec Q° = 1536), 313², MIZAN=249/20² :
   relations exactes vérifiées par le chasseur de théorèmes.

## Ce qui est vérifié (borné, honnête)

BSD sur 3 courbes (L'(37a1)=0.306 = valeur LMFDB) · Hasse p≤97 ·
Hodge T²/CPⁿ · gap spectral Ising · Navier-Stokes 2D · Poincaré χ=2.

## Ce qui est posé (recherche)

Échelles de lemmes + équations précises des goulots pour BSD, Navier-Stokes,
Yang-Mills, Hodge, P vs NP — frontières exactes écrites, preuves ouvertes.

## Correction spectrale (matrice densité)

`noyau_matrice_densite.valeurs_propres()` diagonalisait la **partie réelle**
de ρ. C'était faux dès qu'une cohérence est imaginaire — portes S, T et les
rotations d'axe X ou Y — puisque la partie réelle d'un terme purement
imaginaire est nulle. Deux états **pur** rendaient donc une entropie non
nulle :

| état | entropie avant | entropie après |
|---|---|---|
| |+i⟩ = (|0⟩ + i|1⟩)/√2 | 1,000000 bit | 0,0 |
| Bell + T sur le contrôle | 0,6008760 bit | 0,0 |
| QPE idéal (3 qubits) | 0,9844738 bit | 0,0 |

Le solveur utilise maintenant des rotations **unitaires** de Jacobi : à
chaque pivot, une mise en phase rend le terme hors diagonale réel positif
(sans toucher la diagonale), puis la rotation réelle de Jacobi l'annule.
Contrôle croisé sur 300 états densité complexes aléatoires (dim ≤ 16) contre
`numpy.linalg.eigvalsh`, employé ici comme référence **externe et jetable** —
numpy n'est pas une dépendance du dépôt : écart spectral maximal
**1,2 × 10⁻¹⁵**. Les sept autres circuits canoniques sont inchangés — leurs
cohérences étaient déjà réelles, ce qui explique que la faute n'apparaisse
que sur QPE. `metriques.entropie_intrication_2q` employait déjà la formule
correcte en `|r01|²` : le défaut était isolé dans `valeurs_propres()`.

## Clause d'honnêteté

Aucun problème ouvert du millénaire n'est résolu ici. Émulation classique,
pas de QPU. GDSII pédagogique, pas de PDK. Chaque fait porte sa borne.

## Reproduction

```
py emulateur_mizan.py demo        # Bell, Grover, QEC, ZNE
py emulateur_mizan.py arbre       # arbre des 10 branches
py emulateur_mizan.py conjecture  # Point Carré PC-1..PC-6
py -m unittest tests.test_emulateur                     # 53 tests
py -m unittest horloge_noyau.tests.test_horloge_noyau_complet   # 10 tests
cd ABONDANCE && py -m unittest tests.test_electricite_abondance \
    tests.test_eau_abondance tests.test_agriculture_abondance   # 107 tests
cd CHIFFRES && py -m unittest tests.test_chiffres                #  32 tests
cd FONDATION && py -m unittest tests.test_fondation              #  45 tests

py -3 FONDATION/OUTILS/audit_piliers.py --tous --rigide          # 5 modules CONFORME
```

247 tests, 0 ignoré, depuis la seule archive : `bibliotheques/` et `moteur/`
sont embarqués, aucun `ASTRO-Q°ODE_SYSTEME` voisin n'est requis.

## Les quatre piliers, appliqués à tout le dépôt

`FONDATION/OUTILS/audit_piliers.py` appelle `resoudre()` de chaque module visé
et ne juge que ce que le module déclare déjà :

| Pilier | Exigence | Vérifié |
|---|---|---|
| **P1 UNITE** | une équation = un identifiant = un contrôle, en chaîne continue sans trou ni doublon | 89 équations, 89 contrôles |
| **P2 BORNE** | toute équation porte une `limite` écrite d'au moins 40 caractères | 89/89 |
| **P3 CONFRONTATION** | chemin `module → fonction → contrôle`, statut parmi OPÉRATIONNEL / SIMULÉ / SPÉCIFIÉ, attendu et obtenu non vides, aucun contrôle rouge | 89/89 |
| **P4 TRANSMISSION** | imports stdlib ou locaux seuls, `verifier()` callable, garde `__main__` | 5/5 modules |

Le coût est réel : l'audit exécute `resoudre()`, donc CHIFFRES calcule son
domaine court (20 000 chiffres de π, e et √2 plus un calibrage Monte-Carlo) et
demande une à deux minutes. `--rigide` fait échouer un pilier NON TENU ; le
code de sortie est 0 sur les cinq modules principaux.
