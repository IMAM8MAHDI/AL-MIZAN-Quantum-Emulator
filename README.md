# 🌌 ÉMULATEUR QUANTIQUE AL-MIZAN

**Simulateur quantique complet** (pur Python, zéro dépendance externe) unifiant les briques quantiques d'`ASTRO-Q°ODE_SYSTEME`.

---

## 📜 Certificats Mathématiques Scellés SHA-256

### Ce qui est démontré (théorèmes, pas mesures)

1. **Conjecture du Point Carré** — PC-1..PC-6 vérifiés par exhaustion sur le domaine fini Al-Mizan (19 échelons, 13 constantes)
2. **Riemann strip ≤ 100** — Les 29 zéros non triviaux avec 0<Im≤100 sont sur Re=½ et simples (méthode de Turing : comptage ligne certifié par intervalles + N(T) calculé exactement + égalité)
3. **Invariants cachés** — 8766² = 12·dx et 8496² = 768·dy (dx = 6 403 563, dy = 93 987 ; en heures ces cycles valent dx/128 et dy/2, d'où Q°·d' = s² avec Q° = 1536), 313², MIZAN=249/20² : relations exactes vérifiées par le chasseur de théorèmes

### Ce qui est vérifié (borné, honnête)

BSD sur 3 courbes (L'(37a1)=0.306 = valeur LMFDB) · Hasse p≤97 · Hodge T²/CPⁿ · Gap spectral Ising · Navier-Stokes 2D · Poincaré χ=2

### Ce qui est posé (recherche)

Échelles de lemmes + équations précises des goulots pour BSD, Navier-Stokes, Yang-Mills, Hodge, P vs NP — frontières exactes écrites, preuves ouvertes

---

## 🎯 Architecture Honnête

**Chaque artefact porte sa borne.** Aucun problème ouvert du millénaire n'est résolu ici.

- **Émulation classique** de la mécanique quantique — coût exponentiel en 2ⁿ (4ⁿ en mode densité), aucun QPU ni capteur physique
- **VQE et Shor** : démonstrations jouets (H₂ 2 qubits, N=15)
- **Taux QEC** : exacts pour le modèle de bruit de capacité de code, pas des mesures de laboratoire
- **Die :5030 et canal SCPI :5025** : interfaces réseau locales — sans matériel branché, rien de physique ne se produit
- **GDSII** : fichier pédagogique, pas un masque fabricable

---

## 📖 Informations Officielles

| Champ | Valeur |
|-------|--------|
| **Auteur** | M. Ahmed EL BAHLOUL (IMAM8MAHDI) |
| **DOI Zenodo** | [10.5281/zenodo.24028242](https://doi.org/10.5281/zenodo.24028242) |
| **Licence** | AGPL-3.0 / GPL-3.0 |
| **Contact** | elbahloulahmed505@gmail.com |
| **GitHub** | [IMAM8MAHDI/AL-MIZAN-Quantum-Emulator](https://github.com/IMAM8MAHDI/AL-MIZAN-Quantum-Emulator) |

---

## Architecture

| Brique | Fichier | Rôle |
|---|---|---|
| Vecteur d'état | `noyau_statevector.py` | n qubits (≤16), 20+ portes, permutations contrôlées (arithmétique modulaire), mesure de Born, trajectoires Monte Carlo |
| Matrice densité | `noyau_matrice_densite.py` | ρ exact (≤8 qubits), canaux de Kraus (dépolarisant, T1, déphasage T2), pureté, entropie von Neumann (Jacobi), fidélité |
| Frontend QASM | `frontend_qasm.py` | Parseur OpenQASM 2.0 + 8 circuits canoniques + fichiers `.aq` via `lang/compilateur_qasm_isa.py` |
| Métriques | `metriques.py` | Trace partielle, vecteur de Bloch, pureté locale, concurrence, entropie d'intrication |
| Rendu | `rendu_circuit.py` | Dessin ASCII du circuit (contrôles ●, cibles ⊕, liaisons │) |
| Bruit | `ModeleBruit` | Dépolarisant (p) + amortissement γ (T1) + déphasage (T2, mode densité) |
| ZNE | `attenuation_zne.py` | Extrapolation Richardson à bruit nul (λ = 1, 2, 3) |
| Algorithmes | `algorithmes.py` | VQE H₂ (2q, descente de coordonnées, écart à l'exact vérifié) · Shor N=15 (QPE sur permutation modulaire, 7 qubits) |
| Serveur die | `serveur_die_5030.py` | Backend TCP JSON-lignes :5030 compatible `PontMaterielEmuleAlmizan` (id/reset/pulse/cnot/measure, état partagé) |
| GDSII | `generateur_gds.py` | Layout binaire .gds valide de la tuile Steane [[7,1,3]] + DRC interne générique |
| QEC | `ponts_systeme.py` | Code de Steane [[7,1,3]] via `qubit_logique_mizan.py` (import) |
| Déterministe | `ponts_systeme.py` | `TransducteurQuantiqueDeterministe` → chiffre [-9;+9], lettre [A;S], tétrade, bride MIZAN 0.6225 |
| Horloge | `ponts_systeme.py` | Pulsation de `horloge_noyau/` (capsule scellée, **lecture seule**) |
| Conjecture | `conjecture_point_carre.py` | Point Carré PC-1..PC-4 : preuve par exhaustion + certificat scellé |
| Arbre de savoir | `certificats/` | Les 7 problèmes du millénaire : énoncé formel → certificat borné → sceau |
| Base universelle | `FONDATION/fondation_base.py` | 4 piliers · 3 couches · 18 équations : axiome posé hors matrice → registre de 14 grandeurs → prédiction gelée → confrontée aux mesures publiques NA62 (K⁺ → π⁺νν̄) |
| Piliers rejoués | `FONDATION/OUTILS/audit_piliers.py` | Audite `resoudre()` de chaque module du dépôt contre les 4 piliers — `--tous --rigide` |
| Chiffres | `CHIFFRES/chiffres_pi.py` | π, e, √2 par deux voies indépendantes, 108 cellules pré-déclarées avant mesure, confrontées sur domaine fini |
| Abondance | `ABONDANCE/` | 54 équations et 54 contrôles bornés (électricité 21 · eau 15 · agriculture 18) |
| Horlogerie | `HORLOGERIE/horlogerie.py` | 15 équations et 15 contrôles : l'arithmétique exacte des cycles (dx+dy+dz = dt) réécrite et recontrôlée par un vérificateur qui n'importe pas le dépôt (`verifier_certificats.py`, 16 contrôles), et la portée physique de τ mesurée séparément |

## Base universelle — FONDATION

`FONDATION/fondation_base.py` pose 18 équations, 18 contrôles, quatre piliers
et trois couches. Le pilier P2 BORNE exige une clause de limite écrite sur
chaque équation ; `FONDATION/OUTILS/audit_piliers.py` rejoue ces quatre piliers
sur n'importe quel module du dépôt, y compris ceux qui n'ont pas été écrits ici.

| Couche | Ce qu'elle porte |
|---|---|
| **S1 MESURABLE** | les nombres : comptes, taux, intervalles — ce qu'une expérience publie |
| **S2 REGULARITE** | les lois et les identités : ce qui se calcule sans mesure |
| **S3 HORS_MATRICE** | la source de la régularité : posée, non dérivée, non réfutable ici |

Le cas d'épreuve est le kaon rare K⁺ → π⁺νν̄ de NA62. La prédiction
(`prediction_gel`) ne reçoit **que** théorie, exposition et acceptances : sa
signature d'arguments est `['declares']` et son intersection avec les clés du
comparateur est vide. Elle rend 10,0119 événements attendus sur le domaine
2016-2018 contre 12,97 publiés (écart +0,7166 σ), 3,9852 σ de signification
Li-Ma contre 3,3975 publiés, et un `z` de désaccord au modèle standard dans
[1,3340 ; 1,4546] contre 1,7 déclaré par la collaboration.

Ce dernier point est un **désaccord de méthode assumé**, pas une erreur
corrigée : l'addition en quadrature est nôtre, NA62 ne la déclare pas. Aucun
de ces nombres ne confirme ni n'infirmé l'axiome, et le dossier l'écrit dans
la limite de chaque équation. Les sources publiques sont arXiv:1503.02693
(BR du modèle standard), arXiv:2103.15389, arXiv:2412.12015, arXiv:2605.02415
et le communiqué CERN du 2024-09-25 ; la vidéo d'amorce n'a fourni **aucun**
chiffre, aucune citation et aucun minutage (0 chapitre public, transcript de
0 octet) — voir `FONDATION/SOURCES_ET_PREDECESSEURS.md`.

## Circuits canoniques

`BELL` · `GHZ` (3q) · `GROVER` (2q, marque |11⟩) · `QFT` (3q) ·
`DJ` (Deutsch-Jozsa, oracle équilibré) · `BV` (Bernstein-Vazirani, s=11) ·
`TELEPORTATION` (3q, corrections différées) · `QPE` (estimation de phase)

## Usage

```bash
cd EMULATEUR_QUANTIQUE_MIZAN
py emulateur_mizan.py etat                      # diagnostic des ponts
py emulateur_mizan.py demo                      # Bell de bout en bout
py emulateur_mizan.py run BELL -s 2048          # 2048 tirs Monte Carlo
py emulateur_mizan.py run BELL --densite        # ρ exacte (pureté, S(ρ))
py emulateur_mizan.py run GROVER -p 0.05 --zne  # bruit + extrapolation nulle
py emulateur_mizan.py run circuit.qasm          # fichier OpenQASM 2.0
py emulateur_mizan.py run programme.aq          # source ASTRO-Q°ODE native
py emulateur_mizan.py run BELL --scpi           # émet trame AWG :5025
py emulateur_mizan.py qec -p 0.001              # analyse Steane [[7,1,3]]
py emulateur_mizan.py vqe --essais 400          # H₂ : écart à l'exact mesuré
py emulateur_mizan.py shor -n 15 -a 7           # → facteurs [3, 5]
py emulateur_mizan.py gds                       # layout .gds + DRC générique
py emulateur_mizan.py serveur --port 5030       # die émulé (TCP JSON-lignes)
py emulateur_mizan.py canoniques                # sources QASM
py emulateur_mizan.py conjecture                # Conjecture du Point Carré
py emulateur_mizan.py arbre                     # arbre des 7 problèmes du millénaire
```

Options `run` : `-s` tirs · `-p` bruit dépolarisant · `-g` amortissement T1 ·
`-d` déphasage T2 · `--densite` mode exact · `--zne` atténuation ·
`--scpi` trame AWG · `--no-deterministe` coupe la traduction · `--graine`.

Chaque exécution écrit un rapport JSON scellé SHA-256 dans `resultats/`.

## GDSII — limites strictes

`gds` produit `resultats/steane_tile_almizan.gds` : fichier binaire GDSII
**géométriquement valide** (ouvrable dans KLayout/gdstk) représentant la
tuile d'un qubit logique Steane — 7 données + 6 ancillas + coupleurs + bus
de lecture. Le DRC embarqué applique des règles internes génériques
(largeur ≥ 0.5 µm, espacement ≥ 0.5 µm, marge die 20 µm) qui ne sont
**pas** celles d'une fonderie. Une tape-out réelle exige un flot physique
complet sous CAO + PDK propriétaire + sign-off DRC/LVS fonderie.

## Tests

```bash
py -m unittest tests.test_emulateur -v                           # 53 tests
py -m unittest horloge_noyau.tests.test_horloge_noyau_complet     # 10 tests
cd ABONDANCE && py -m unittest tests.test_electricite_abondance \
    tests.test_eau_abondance tests.test_agriculture_abondance     # 107 tests
cd CHIFFRES && py -m unittest tests.test_chiffres                  # 32 tests
cd FONDATION && py -m unittest tests.test_fondation                # 45 tests
cd HORLOGERIE && py -m unittest tests.test_horlogerie               # 30 tests
py -3 FONDATION/OUTILS/audit_piliers.py --tous --rigide             # 6 modules CONFORME
```

53 tests : états, portes, permutations, intrication, Born, bruit
(trajectoire + Kraus), métriques, QASM, rendu, DJ/téléportation/QPE,
VQE (borne variationnelle vérifiée), Shor ([3,5]), TLV GDSII, DRC,
ZNE, Steane, transducteur, Point Carré (PC-1..PC-4), l'arbre des
7 problèmes (octaèdre χ=2, Hasse, Hodge, gap spectral, Navier 2D, RH≤200)
et le spectre hermitien complexe de la matrice densité.

**0 ignoré, et plus rien d'extérieur à l'archive.** Les deux ponts
(Steane, transducteur) se chargent depuis `moteur/` et la capsule
`horloge_noyau` depuis `bibliotheques/` : un `ASTRO-Q°ODE_SYSTEME`
voisin n'est plus requis. 277 tests au total, tous verts — et les 104
équations du parc (ABONDANCE 54, CHIFFRES 17, FONDATION 18, HORLOGERIE 15)
portent chacune sa clause de limite, contrôlée par le même audit.

## Statut honnête

Émulation **classique** de la mécanique quantique — coût exponentiel en 2ⁿ
(4ⁿ en mode densité), aucun QPU ni capteur physique. VQE et Shor sont des
démonstrations jouets (H₂ 2 qubits, N=15). Les taux QEC sont exacts pour
le modèle de bruit de capacité de code, pas des mesures de laboratoire.
Le die :5030 et le canal SCPI :5025 sont des interfaces réseau locales —
sans matériel branché, rien de physique ne se produit. Le .gds n'est pas
un masque fabricable.

Les quatre dossiers d'équations ne prouvent rien d'universel. ABONDANCE calcule
des régularités finies et les confronte ; CHIFFRES annonce 108 cellules avant
mesure puis constate un verdict de **CONTENU** — l'absence d'un rejet sur
n = 10⁶ chiffres n'établit pas que π est normal, et un résultat discordant
n'aurait pas prouvé le contraire ; FONDATION pose un axiome hors matrice qui
ne fournit **aucun** nombre et ne livre que des bornes ; HORLOGERIE scelle une
identité arithmétique exacte et montre que le rythme mesuré dépend de la
machine, ce qui réfute la lecture en hertz sur l'hôte qui l'a produite. Chaque
équation porte sa clause de limite, lue par `audit_piliers.py`.
