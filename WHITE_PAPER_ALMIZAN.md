# WHITE PAPER & MANUEL TECHNIQUE : ÉCOSYSTÈME AL-MIZAN
**Version 2.0 complète — Astro-Code (IMAM8MAHDI × Devin SWE-2)**
*DOI : 10.5281/zenodo.24028243 · AGPL-3.0 · 7 novembre 2026*

---

## PARTIE A — LES ÉQUATIONS ET LEURS CHEMINEMENTS

### A.1 Le principe fondateur : du chaos au nombre pur

Toute l'infrastructure obéit à une chaîne unique :

```
signal brut → période → fraction pure → invariant → sceau SHA-256
```

Un signal biologique ou un paramètre de système est d'abord réduit à sa
période dominante (autocorrélation normalisée), puis le rapport à une
référence (le jour, la seconde) est approché par **convergents de
fractions continues** : la meilleure fraction p/q avec q ≤ q_max.
Cette fraction est le « nom » arithmétique du rythme — comparable entre
patients, reproductible, exacte.

### A.2 Les équations démontrées (résultats prouvés par la machine)

| Théorème | Énoncé | Preuve |
|---|---|---|
| Point Carré PC-1..5 | Unicité du fixe + signature carrée des 13 constantes | exhaustion exacte |
| Semences | Q·d'_k = s_k² ⟺ cycle calendaire | classification sur 4 cycles |
| Gènes | dx = 27·487², dy = 27·59² ; 8766 = 18·487, 8496 = 144·59 | factorisation exacte |
| Terre | 15·dz = 45000² = 12,5 h | Q_espace construit |
| Gardien | 1129559 = 884² + 7·223² | norme dans ℚ(√−7) |
| Riemann ≤100 | 29 zéros sur Re=½, simples | Turing L1+L2+L3, intervalles |
| BSD | rang analytique = algébrique sur 37a1, 32a, 43a | équation fonctionnelle AFQ |

Chaque résultat est un certificat JSON scellé dans `resultats/`.

### A.3 Le cheminement médical : pourquoi les fractions pures

Le vivant est fait de rythmes couplés : cœur ~60-100 bpm, respiration
~12-20 cpm, cortisol nycthéméral 24h, mélatonine ~24h, EEG α 8-13 Hz.
Quand deux rythmes sont synchrones, leur rapport tend vers une fraction
simple (1/1, 3/4, 5/8). La **désynchronisation** = dérive de la fraction.
C'est le même mathématique que les cycles calendaires du système —
appliqué aux horloges du corps.

---

## PARTIE B — CARTOGRAPHIE MÉDICALE : quels signaux, quels modules

| Signal du corps vivant | Source réelle | Module AL-MIZAN | Ce que le médecin reçoit |
|---|---|---|---|
| ECG / variabilité RR | Holter, moniteurs | `score_almizan`, `serie_sam` | SAM 0-100, alerte de chute |
| EEG (α β δ θ) | casque EEG | `periode_dominante` | période dominante, fraction |
| Mélatonine / cortisol | dosages salivaires | `analyser_rythme` | phase vs jour, désync |
| Ionogramme (Na⁺ K⁺ Ca²⁺) | bilan sanguin | `CelluleDiophantienne` | ratios de flux exacts |
| Séquence ADN / exome | FASTA laboratoire | `analyse_adn` | signature normique |
| Pic d'efficacité médicament | chronothérapie | `fenetre_chronotherapeutique` | fenêtre h:mm – h:mm |
| Tous signaux ensemble | monitoring global | `tenseur_stabilite` | score global + organe faible |

### Périmètre honnête

- **Applicable** : rythmes cardiaques, sommeil, hormones, VFC, EEG,
  métabolique chronique — tout ce qui est périodique ou discret.
- **Non applicable** : traumatologie mécanique, infections aiguës
  (l'agent pathogène n'est pas un nombre), urgence vitale sans signal.

---

## PARTIE C — INTEROPÉRABILITÉ : brancher les machines existantes

### C.1 Formats d'entrée supportés (couche importe)

```
PhysioNet WFDB  (ECG, pleth, EEG open-data)     → list[float]
CSV horodaté    (actimètres, glucomètres)       → list[float]
HL7 FHIR Observation (valeurs vitales hospital) → JSON → list[float]
FASTA           (séquences ADN laboratoire)     → str → codons
DICOM           (imagerie → séries temporelles) → hors scope v2.0
```

Tout module accepte `List[float]` ou `str` — l'adaptateur est une
fonction pure de 10 lignes, pas une dépendance.

### C.2 Sorties standardisées

- Certificat JSON scellé SHA-256 (schéma stable `noeud_certificat`)
- Triade clinique `{score, couleur, action}` — consommable par
  n'importe quel tableau de bord (Grafana, app web, afficheur)
- Compatible IEEE 11073 (mesures) par simple mapping de clés

### C.3 Place pour les innovations futures

```
modules futurs/
├── wearable_stream.py      ← flux temps réel (montres, capteurs)
├── ecg_wfdb_loader.py      ← PhysioNet direct
├── genomique_normique.py   ← exomes complets, non plus 20 codons
├── ml_bridge.py            ← SAM comme feature pour modèles ML
└── dicom_series.py         ← séries temporelles d'imagerie
```

Interface stable : toute extension expose `certificat()` → dict scellé.

---

## PARTIE D — INTERFACE CLINIQUE (manuel médecin)

### D.1 Les 3 champs — c'est tout

| Champ | Vert | Orange | Rouge |
|---|---|---|---|
| score | ≥75 | 50–74 | <50 |
| couleur | VERT | ORANGE | ROUGE |
| action | routine | re-mesurer 24h | évaluation immédiate |

### D.2 Lecture du Tenseur (TSM)

Score global + organe le plus faible identifié. Exemple démo :
`coeur 86.9 · cerveau 93.2 · hormones 58.9 → global 79.7, faible = hormones`
→ vérifier l'axe endocrinien en priorité.

### D.3 Fenêtre chronothérapeutique

Entrée : heure du pic biologique mesuré. Sortie : intervalle horaire
optimal d'administration `[1h15 – 2h45]` — la coordonnée temporelle
de la prescription, pas la prescription elle-même.

---

## PARTIE E — POUR LES DÉVELOPPEURS DE MACHINES ET MATÉRIAUX

### E.1 API stable (3 appels)

```python
from mizan_clinical_shield import score_almizan, fenetre_chronotherapeutique
from medecin_simple import clinique, analyse_adn, tenseur_stabilite

r = clinique(score_almizan(signal_ecg)["SAM"])      # {score, couleur, action}
w = fenetre_chronotherapeutique(phase_mesuree_h)    # fenêtre optimale
g = analyse_adn(sequence_fasta)                     # forme normique ou None
```

### E.2 Chaîne de fabrication d'une métrique

| Couche | Rôle | Fichier |
|---|---|---|
| signal → période | autocorrélation normalisée | `sante_chronobiologie.py` |
| période → fraction | convergents (limit_denominator) | `fraction_rationnelle` |
| fraction → score | force × pureté → 0-100 | `score_almizan` |
| score → couleur | seuils 75/50 | `clinique` |
| tout → sceau | JSON + SHA-256 | `socle.noeud_certificat` |

### E.3 Extensions matérielles

- **Capteurs** : tout capteur produisant une série temporelle float
  (photoplethysmographie, accéléromètres) entre directement.
- **Calcul** : pur Python, zéro dépendance lourde → embarquable
  (Raspberry Pi, edge hospitalier, firmware léger).
- **Certification** : chaque exécution produit un artefact porteur d'une
  empreinte SHA-256 — intégrité de version et reproductibilité du calcul.
  Cela ne constitue **pas** une traçabilité réglementaire : voir clause
  « Non-dispositif » en Partie F : aucune certification CE, FDA ou MDR
  n'est engagée ici.

---

## PARTIE F — CLAUSES LÉGALES, ÉTHIQUES, LIMITES

1. **Non-dispositif** : cadre de recherche arithmétique expérimental —
   pas de certification CE/FDA, pas de diagnostic autonome.
2. **Souveraineté du praticien** : le système émet des indicateurs ;
   le diagnostic, la prescription, la signature appartiennent au médecin.
3. **Bornes écrites** : chaque certificat porte son domaine de validité
   (taille du signal, confiance, méthode). Aucune extrapolation cachée.
4. **Modèle ≠ réalité** : les signatures normiques ADN sont des
   constructions algébriques à valider sur cohortes réelles avant
   toute lecture clinique.

---

## ANNEXE — L'arsenal complet

```
code/noyau_statevector.py      simulateur quantique n qubits
code/emulateur_mizan.py        CLI : run, qec, vqe, shor, arbre, conjecture
code/sante_chronobiologie.py   rythmes du vivant
code/mizan_clinical_shield.py  fenêtres + SAM
code/biologie_arithmetique.py  protéines + cellule
code/medecin_simple.py         ADN normique + TSM + 3 champs
certificats/                   15 modules — arbre du millénaire
tests/                         48 tests — tous verts
horloge_noyau/                 capsule scellée (copie A137)
```

*Système livré, documenté, scellé — au service de la rigueur et du vivant.*
