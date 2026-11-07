# DÉPÔT ZENODO — AL-MIZAN : Émulateur quantique & Arbre de savoir du millénaire

**Auteurs** : M. Ahmed EL BAHLOUL (IMAM8MAHDI) × Devin (SWE-2), Cognition AI
**DOI Zenodo** : [10.5281/zenodo.24028243](https://doi.org/10.5281/zenodo.24028243)
**Licence** : AGPL-3.0 / GPL-3.0 (voir LICENSE-AGPL, LICENSE-GPL)
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
├── tests/                 # 48 tests unittest — tous verts
├── resultats/             # rapports JSON scellés SHA-256 + .gds
├── horloge_noyau/         # noyau logique scellé (copie A137)
├── HOMMAGE_PREDECESSSEURS.md
├── .zenodo.json           # métadonnées du dépôt
├── CITATION.cff, NOTICE.txt, LICENSE-*
└── MANIFESTE_SHA256.txt
```

**Convention du manifeste** : une empreinte par fichier, deux espaces,
puis le chemin ; groupé par répertoire de premier niveau, trié à
l'intérieur de chaque groupe. Les hashes
portent sur les octets **normalisés LF** du blob git — donc `sha256sum`
sur un worktree Windows (`core.autocrlf=true`, fins CRLF) ne correspondra
pas. Pour vérifier depuis n'importe quel système :

```
git cat-file blob HEAD:CHEMIN | sha256sum     # une ligne du manifeste
```

Le manifeste scelle tout fichier suivi par git **sauf lui-même** (pas
d'auto-référence). `python code/conjecture_point_carre.py` se rejoue sans
le moteur ASTRO-Q°ODE : dans ce cas PC-3/PC-4/PC-5 utilisent les
constantes déclarées et le champ `controles_en_repli` du certificat le
dit explicitement.

## Ce qui est démontré (théorèmes, pas mesures)

1. **Conjecture du Point Carré** — PC-1..PC-6 prouvés par exhaustion sur
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

## Clause d'honnêteté

Aucun problème ouvert du millénaire n'est résolu ici. Émulation classique,
pas de QPU. GDSII pédagogique, pas de PDK. Chaque fait porte sa borne.

## Reproduction

```
py emulateur_mizan.py demo        # Bell, Grover, QEC, ZNE
py emulateur_mizan.py arbre       # arbre des 10 branches
py emulateur_mizan.py conjecture  # Point Carré PC-1..PC-6
py -m unittest tests.test_emulateur  # 48 tests
```
