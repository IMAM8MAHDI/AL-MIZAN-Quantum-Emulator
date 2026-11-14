# DÉPÔT ZENODO — AL-MIZAN : Émulateur quantique & Arbre de savoir du millénaire

**Auteurs** : M. Ahmed EL BAHLOUL (IMAM8MAHDI) — développement assisté par IA générative (Devin SWE-2, Cognition AI), résultats relus et dirigés par l'auteur humain
**DOI Zenodo** : [10.5281/zenodo.24028242](https://doi.org/10.5281/zenodo.24028242) — DOI de concept, il résout toujours vers la dernière version publiée
**Chaîne de versions** : **v3.4.0 est publiée** — [10.5281/zenodo.24123150](https://doi.org/10.5281/zenodo.24123150), archive `AL-MIZAN_v340_3ec9560.zip` (1 510 344 octets, SHA-256 `dcdbbeb60dfb8bba4d5b57273f85b9961c2231b807dea69b62bb8c12085d5ed2`, MD5 `5e9b258f89053c59c2d0afc07ac06ee3`), scellée sur le HEAD `3ec9560` : 276 entrées au sceau, 277 fichiers nommés dans l'archive, 346 entrées avec les 69 répertoires. Contrôle fait dans l'archive re-téléchargée de Zenodo : identique octet pour octet à l'archive déposée, mêmes SHA-256 et MD5 ; sur les 276 entrées scellées, 256 re-hachent exactement et les 20 CSV « Excel français » re-hachent après normalisation des fins de ligne, 0 ne diverge ; le seul fichier du ZIP hors sceau est `MANIFESTE_SHA256.txt`, qui s'exclut lui-même. Son descriptif publié porte les comptes mesurés avant l'émission : 654 tests, 219 équations, 219 contrôles, 14 modules CONFORME, manifeste de 276 entrées portant 0 date. v3.3.2 — [10.5281/zenodo.24122287](https://doi.org/10.5281/zenodo.24122287), archive `AL-MIZAN_v332_c9b7fbd.zip` (1 414 446 octets, SHA-256 `3504ff10cc5a9027b2037a371433c16e6909aca0452db4b78c937bf4b06cd87c`, MD5 `c2feaaf172389ede1d31182afc5d20f2`), scellée sur le HEAD `c9b7fbd` (249 entrées). Contrôle fait dans l'archive re-téléchargée de Zenodo : 250 membres = les 249 entrées scellées + `MANIFESTE_SHA256.txt`, qui s'exclut lui-même ; 233 re-hachent exactement vers leur valeur scellée, les 16 CSV « Excel français » n'y re-hachent qu'après normalisation des fins de ligne, 0 divergent. Elle apporte `criteres_derivation_sans_intrant.py` (EQ-DSI-01..06, recensement exact des 40 959 999 formes a + b√2 + c√3 + d√6 sur n ≤ 31 104, verdict « appropriation non établie » sur la forme examinée) et sa treizième suite de 25 tests ; son descriptif publié porte les comptes de ce temps-là — 588 tests, 199 équations, 199 contrôles, 12 modules CONFORME, manifeste de 245 à 249 entrées — et un enregistrement publié n'étant pas amendable, la correction est portée par la version suivante. **v3.4.0 ajoute** `QPU_DISTANT/` (10 équations, 10 contrôles : le job `dbpkmr0ou4as73ctrm80` relu sur `ibm_marrakesh`, 256 tirs sur [0,1], compteurs recalculés depuis la table de résultats, deux bornes confrontées au support réel) et `GOULETS/` (10 équations, 10 contrôles : durée, cadence, plafond et disque mesurés) ; les deux entrent dans le registre d'audit, qui note le 11 novembre 2026 **14 modules CONFORME, 219 équations, 219 contrôles** sous code de sortie 0, et les quatorze suites documentées rendent **654 tests** — 566 dans les douze dossiers d'équations, 88 hors dossiers (`tests.test_emulateur` 53, la suite `horloge_noyau` 10, le critère EQ-DSI 25). Dans un clone, les 654 passent et aucun ne s'ignore ; dans la copie **sans `.git`** que fournit l'archive, 647 passent et 7 relectures d'histoire git s'ignorent d'elles-mêmes (5 VERROUS, 2 DECLARATION). Le sceau porte **276 entrées, 0 date**, et `pages_depot/generer_pages_site.py` produit **21 fichiers** du site après avoir revérifié 24 fichiers du dépôt contre ce sceau. La mesure d'antériorité de `DECLARATION/` est celle du HEAD `d9662d1`, sept commits avant `3ec9560` sur lequel est scellée l'archive publiée : 116 commits dont 98 humains et 18 d'automate, 276 entrées de sceau portant 0 date — même compte et même zéro date au HEAD scellé. v3.3.1 — [10.5281/zenodo.24114682](https://doi.org/10.5281/zenodo.24114682), archive `AL-MIZAN_v331_50afbb8.zip` (1 382 512 octets, SHA-256 `1b7a3c2f27481fa32884a8acb1fac02e…`, MD5 `667b49cd9442eea2d354586456f77c55`), scellée sur le HEAD `50afbb8` (245 entrées) et re-téléchargée de Zenodo identique octet pour octet, apportait `pages_depot/` — mesuré le 10 novembre 2026 sur une copie privée de `.git`, sans variable d'environnement et sans clone voisin : 17 fichiers produits, 17 identiques octet pour octet aux pages servies —, `docs/API_PASSERELLE_VPS.md`, table des routes réellement servies par la passerelle, et `oeuvre_universelle/espace_disque.py` (13 équations, 13 contrôles) ; ces trois nouveautés restent hors du registre d'audit, qui tenait alors 563 tests, 199 équations, 199 contrôles et 12 modules CONFORME. Contrôle mesuré dans le ZIP publié de v3.3.1 : 246 fichiers = les 245 entrées scellées + le manifeste, 229 re-hachages exacts et 16 CSV conformes après seuls fins de ligne — `.gitattributes` déclare `*.csv text eol=crlf`, donc `git archive` livre le CRLF que le livrable promet (BOM, séparateur « ; » et données inchangés) là où le scellement hache les octets LF du blob. La formule « chaque fichier de l'archive re-hache vers sa valeur scellée », écrite dans les fiches v3.1.0 à v3.2.1, était inexacte sur ce point ; la correction est portée par la version 3.2.2, un enregistrement publié n'étant pas amendable. Toute archive est construite par `git -c core.autocrlf=false archive --format=zip HEAD` sur le HEAD scellé, jamais sur l'arbre de travail Windows, et le DOI de version qu'elle porte ne peut pas figurer dans l'archive qu'il publie : il est consigné ici après l'émission. Le descriptif publié de v3.3.1 conserve les comptes relevés au HEAD `f8f474d` (86 commits, 240 entrées de sceau, 68 commits humains contre 18 d'automate) parce qu'un enregistrement publié n'est pas amendable ; le miroir `.zenodo.json` du dépôt, les deux README et le communiqué portaient la mesure du 10 novembre 2026 au HEAD `50afbb8` : 104 commits dont 86 humains et 18 d'automate, 245 entrées de sceau portant 0 date. Versions précédentes : v3.3.0, [10.5281/zenodo.24105422](https://doi.org/10.5281/zenodo.24105422), archive `AL-MIZAN_v33_9d80f3f.zip` (1 308 464 octets, SHA-256 `6b20512128361fe678ca540056395014…`, MD5 `4e2e8337a0c8aeef53424f19810456fa`), 240 entrées scellées sur le HEAD `9d80f3f`, 241 entrées dans le ZIP publié dont 224 re-hachages exacts et 16 CSV après seuls fins de ligne, dossiers VERROUS, DECLARATION et GUERRE, 563 tests, 199 équations, 12 modules CONFORME ; v3.2.2, [10.5281/zenodo.24091259](https://doi.org/10.5281/zenodo.24091259), archive `AL-MIZAN_v322_d19a542.zip` (987 836 octets, SHA-256 `32672bb029616343…`, MD5 `c3e6886023575a52…`), 204 entrées scellées sur le HEAD `d19a542`, 205 entrées dans le ZIP publié dont 194 re-hachages exacts et 10 CSV après seuls fins de ligne, dossier HORLOGERIE et écran de laboratoire (`laboratoire.py`), 311 tests, 104 équations, 6 modules CONFORME ; v3.2.1, [10.5281/zenodo.24075082](https://doi.org/10.5281/zenodo.24075082), archive `AL-MIZAN_v321_c05f7ee.zip` (818 588 octets, SHA-256 `1d681d2d68ac45d2…`) ; v3.2.0, [10.5281/zenodo.24074846](https://doi.org/10.5281/zenodo.24074846) ; v3.1.0, [10.5281/zenodo.24062292](https://doi.org/10.5281/zenodo.24062292) ; v3.0.0, [10.5281/zenodo.24054060](https://doi.org/10.5281/zenodo.24054060). `CITATION.cff` porte la version du **contenu** de l'archive, jamais son propre DOI de version — même règle d'auto-référence que `MANIFESTE_SHA256.txt`.
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
├── HORLOGERIE/            # l'horloge : 15 équations · 15 contrôles · 16 vérifications
│   ├── horlogerie.py            # producteur : identité dx+dy+dz=dt, confrontation céleste
│   ├── verifier_certificats.py  # vérificateur autonome : stdlib seule, aucun import du dépôt
│   ├── calibrer_horloge_almizan.py  # mesure τ = T/N sur l'hôte (non scellée, par nature)
│   ├── laboratoire.py           # écran : trajectoire 3D, repère à 14 coordonnées, ADEV
│   ├── artefacts/               # certificats.json + confrontation_astronomique.csv
│   │                            # + laboratoire.json, trajectoire et stabilité (CSV, SVG)
│   ├── SOURCES_ET_PREDECESSEURS.md
│   └── tests/                   # 64 tests
├── CONTINUITE/            # la chaîne : 15 équations · 15 contrôles
│   ├── continuite_base.py       # ρ = (249/400)^(1/12), télescopage exact, point fixe 61/500
│   ├── artefacts/               # certificat.json + chaine_de_pas.csv + énoncé markdown
│   └── tests/                   # 23 tests
├── REDACTION/             # l'intelligibilité comptée : 16 équations · 16 contrôles
│   ├── redaction_mizan.py       # déficit numérique 56/89 et 55/89, forme mesurée par page
│   ├── artefacts/               # certificat.json + mesures_par_page.csv + règles markdown
│   └── tests/                   # 32 tests
├── CONSTRUCTION/          # les cotes : 16 équations · 16 contrôles · 0 prototype
│   ├── construction_base.py     # 43 crans, cote 622,50 mm clampée à 122,00 mm, ε_a = 1/1000
│   ├── artefacts/               # certificat.json + nomenclature + plan SVG + prédictions
│   └── tests/                   # 42 tests
├── VERROUS/               # l'état de la protection mesuré : 16 équations · 16 contrôles
│   ├── verrous_base.py          # arbre, sceau re-haché, SPDX, 8 clauses, 4 instruments
│   ├── artefacts/               # certificat.json + registre d'accès + clauses MD + plan SVG
│   └── tests/                   # 62 tests
├── DECLARATION/           # l'antériorité re-mesurée : 16 équations · 16 contrôles
│   ├── declaration_base.py      # 126 commits au HEAD bf50a4a, 0 date au sceau, 3 ablations
│   ├── artefacts/               # certificat.json + chaîne d'antériorité CSV + ablations MD + plan SVG
│   └── tests/                   # 37 tests
├── GUERRE/                # la richesse face à la guerre : 16 équations · 16 contrôles
│   ├── guerre_base.py           # 153 pays, ρ(revenu, charge) = 0,0619 contre ρ(masse) = 0,5036
│   ├── snapshot/                # Banque mondiale 2022 + chapitres YouTube, engagés par SHA-256
│   ├── artefacts/               # certificat.json + registre CSV + dossier MD + frontière SVG
│   └── tests/                   # 56 tests
├── QPU_DISTANT/          # l'exécution chez un fournisseur quantique distant, relue :
│   │                      # 10 équations · 10 contrôles · statut OPÉRATIONNEL borné
│   ├── qpu_distant_base.py     # job dbpkmr0ou4as73ctrm80 sur ibm_marrakesh : 256 tirs
│   │                            # sur [0,1], 600 unités, compteurs recalculés depuis la
│   │                            # table de résultats, deux bornes confrontées au support
│   ├── sources/                # l'archive du fournisseur, engagée par empreinte
│   │                            # (result.json, portes transpilées, calibration, support)
│   ├── artefacts/              # certificat.json + compteurs et frontières (CSV, SVG)
│   └── tests/                   # 28 tests
├── GOULETS/             # les goulots de publication mesurés et bornés :
│   │                      # 10 équations · 10 contrôles · aucune levée revendiquée
│   ├── goulets_base.py         # 30 s contre seuil déclaré 900 s (marge 870 s), barème
│   │                            # 99/jour contre plafond constaté 10/jour, 78 fichiers
│   │                            # et 1 432,543 s en stock, 35 434 115 072 octets libres
│   │                            # sur 252 841 029 632 (14,01 %)
│   ├── sources/                # snapshots engagés par SHA-256 (chaîne YouTube, disque,
│   │                            # backlog local, quotas déclarés, chapitres de la vidéo)
│   ├── artefacts/               # certificat.json + cadence et bornes (CSV, SVG)
│   └── tests/                   # 38 tests
├── SURETE/              # la sécurité bornée : 13 équations · 13 contrôles ·
│   │                      # AUCUNE PREUVE · aucune mesure de produit réel
│   ├── surete_bornee_base.py    # Rice énoncé puis borné par 131 071 mots énumérés,
│   │                            # Poisson (P₀ par trois routes), fenêtre de correctif,
│   │                            # intervalle non majoré, fuite à deux couches,
│   │                            # disponibilité, critère sur l'énoncé d'une garantie,
│   │                            # coût pour un tiers, registre consigné, socle 313T,
│   │                            # et le critère retourné contre le module lui-même
│   ├── SOURCES_ET_PREDECESSEURS.md  # la demande requalifiée, les statuts, la filiation
│   ├── artefacts/               # certificat.json (racine Merkle des 13 équations)
│   └── tests/                   # 46 tests
├── pages_depot/           # publication du site al-mizan.world depuis CE dépôt
│   │                      # seul : 21 fichiers reproduits octet pour octet
│   ├── generer_pages_site.py    # orchestrateur FONDATION + CHIFFRES + LABORATOIRE
│   │                            # → web_cloud/ ; auto-localise le dépôt, aucune
│   │                            # variable d'environnement ni clone voisin requis
│   └── pages_laboratoire.py     # 9 livrables d'écran : FR/EN/AR + 6 exports
├── oeuvre_universelle/    # copies servies en production de la page « espace
│   │                      # disque » — hors registre d'équations, non auditées
│   │                      # par audit_piliers
│   ├── espace_disque.py         # 13 équations · 13 contrôles, en-tête SPDX
│   └── generer_page_espace_disque.py  # 3 pages trilingues + 1 JSON
├── criteres_derivation_sans_intrant.py  # EQ-DSI-01..06, 40 959 999 formes recensées
├── docs/                  # table des routes réellement servies par la passerelle
│   ├── API_PASSERELLE_VPS.md
│   └── VEILLE_CHAIN_THEORY_DERIVATION_SANS_INTRANT.md  # verdict sur pièces
│                            # nom sans date : C04 refuse toute date dans le sceau
├── tests/                 # 78 tests unittest (53 emulateur + 25 critère DSI)
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
py -m unittest tests.test_derivation_sans_intrant_mizan  # 25 tests (EQ-DSI)
py -m unittest horloge_noyau.tests.test_horloge_noyau_complet   # 10 tests
cd ABONDANCE && py -m unittest tests.test_electricite_abondance \
    tests.test_eau_abondance tests.test_agriculture_abondance   # 107 tests
cd CHIFFRES && py -m unittest tests.test_chiffres                #  32 tests
cd FONDATION && py -m unittest tests.test_fondation              #  45 tests
cd HORLOGERIE && py -m unittest tests.test_horlogerie tests.test_laboratoire   #  64 tests
cd CONTINUITE && py -m unittest tests.test_continuite               #  23 tests
cd REDACTION && py -m unittest tests.test_redaction                 #  32 tests
cd CONSTRUCTION && py -m unittest tests.test_construction           #  42 tests
cd VERROUS && py -m unittest tests.test_verrous                     #  62 tests
cd DECLARATION && py -m unittest tests.test_declaration             #  37 tests
cd GUERRE && py -m unittest tests.test_guerre                        #  56 tests
cd QPU_DISTANT && py -m unittest tests.test_qpu_distant              #  28 tests
cd GOULETS && py -m unittest tests.test_goulets                       #  38 tests
cd SURETE && py -m unittest tests.test_surete_bornee                   #  46 tests

py -3 FONDATION/OUTILS/audit_piliers.py --tous --rigide          # 15 modules CONFORME
```

700 tests : les treize suites de dossiers ci-dessus portent 612 tests, auxquels s'ajoutent
les 88 hors dossiers — `tests.test_emulateur` (53), la suite `horloge_noyau`
(10) et le critère de dérivation sans intrant (25). `bibliotheques/` et
`moteur/` sont embarqués, aucun `ASTRO-Q°ODE_SYSTEME` voisin n'est requis.

Mesure du 2026-11-14, les seize suites ci-dessus rejouées dans une copie du dépôt
**sans `.git`** extraite du HEAD `616744c` : 700 tests sont collectés, 7
s'ignorent d'eux-mêmes faute de dépôt git lisible — 5 dans
`VERROUS`, 2 dans `DECLARATION`, tous des relectures d'histoire de commits —
et les **693 restants passent**.
Dans un clone, les 700 passent et **aucun test ne s'ignore**. La mention
« 0 ignoré » portée ici jusqu'à la v3.3.0 ne décrivait donc que le cas du
clone, pas celui de l'archive.

La façon d'extraire cette copie compte : `git -c core.autocrlf=false archive`
rend les mêmes octets que le dépôt, alors qu'un `git archive` nu sur un hôte en
`core.autocrlf=true` rend tout le dépôt en CRLF et fait échouer
`HORLOGERIE/tests/test_horlogerie.py`, la méthode
`test_fichier_present_conforme_et_octet_pour_octet_reproductible` — 692 passent,
1 échoue, et le seul écart est la fin de ligne d'un certificat que le module
écrit en LF. Le scellement, lui, hache des blobs LF : une archive qui diverge
par ses fins de ligne n'est pas l'archive scellée.

### Reproduire le site public depuis l'archive

`pages_depot/generer_pages_site.py` régénère les 21 fichiers du site
al-mizan.world publiés par les dossiers FONDATION, CHIFFRES et LABORATOIRE —
les trois derniers noms du compte étant les livrables de l'exécution distante
jointe à LABORATOIRE. Il se localise lui-même : `git clone` du dépôt, un
répertoire `web_cloud/` là où l'on veut, puis :

```
py -3 pages_depot/generer_pages_site.py     # écrit 21 fichiers dans web_cloud/
```

Mesure du 2026-11-11, dans le dépôt scellé : les 21 fichiers sortent, code de
sortie 0, et 24 fichiers du dépôt sont revérifiés contre le sceau avant
écriture — soit 4 pour `chiffres_pi`, 4 pour `fondation` et 13 pour
`laboratoire`, dont les quatre livrables de l'exécution distante. La
confrontation octet pour octet aux fichiers servis, mesurée le 2026-11-10 sur
les 17 fichiers alors publiés (`PRODUITS 17 IDENTIQUES 17`), est re-jouée à
chaque déploiement et porte sur 21 fichiers depuis cet ajout. Re-jouée le
2026-11-11 après le déploiement de l'exécution distante : `IDENTIQUES 21`,
`ABSENTS_DU_SERVEUR 0`, `DIVERGENTS 0`. Le lot qui a produit cette égalité
porte onze fichiers — le passeur, les six pages `fondation` et `laboratoire`,
les quatre livrables `laboratoire_qpu_*` — expédiés depuis une archive dont
l'empreinte est vérifiée des deux côtés, après sauvegarde des sept fichiers
remplacés et restauration de leurs propriétaires et modes. La page
« espace disque » et ses trois variantes ne sont pas dans ce compte :
`oeuvre_universelle/` porte les modules **copiés depuis la production**,
pour lecture et re-jouabilité, et l'orchestrateur ne les appelle pas.

Le registre d'équations du dépôt — 232 équations, 232 contrôles, 15 modules
`CONFORME` — n'est pas touché par cet outillage : `pages_depot/`,
`oeuvre_universelle/` et `docs/` sont de la publication, pas des
dossiers soumis à `FONDATION/OUTILS/audit_piliers.py --tous`.

## Les quatre piliers, appliqués à tout le dépôt

`FONDATION/OUTILS/audit_piliers.py` appelle `resoudre()` de chaque module visé
et ne juge que ce que le module déclare déjà :

| Pilier | Exigence | Vérifié |
|---|---|---|
| **P1 UNITE** | une équation = un identifiant = un contrôle, en chaîne continue sans trou ni doublon | 232 équations, 232 contrôles |
| **P2 BORNE** | toute équation porte une `limite` écrite d'au moins 40 caractères | 232/232 |
| **P3 CONFRONTATION** | chemin `module → fonction → contrôle`, statut parmi OPÉRATIONNEL / SIMULÉ / SPÉCIFIÉ, attendu et obtenu non vides, aucun contrôle rouge | 232/232 |
| **P4 TRANSMISSION** | imports stdlib ou locaux seuls, `verifier()` callable, garde `__main__` | 15/15 modules |

Le coût est réel : l'audit exécute `resoudre()`, donc CHIFFRES calcule son
domaine court (20 000 chiffres de π, e et √2 plus un calibrage Monte-Carlo) et
demande une à deux minutes. `--rigide` fait échouer un pilier NON TENU ; le
code de sortie est 0 sur les quinze modules principaux.
