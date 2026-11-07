# DOSSIER TECHNIQUE POUR DEVIS — Gravure de masques logiques
**Projet : AmalMoteur65 — Tuile logique Steane [[7,1,3]] sur Silicium Spin**
*AL-MIZAN × Astro-Code · DOI 10.5281/zenodo.24028243 · 7 novembre 2026*

---

## 1. Livrables fournis (dans ce dossier)

| Fichier | Contenu | Format |
|---|---|---|
| `steane_tile_almizan.gds` | Layout complet de la tuile logique | GDSII binaire v6, unité 1 µm, DBU 1 nm |
| `steane_tile_manifeste.json` | Inventaire des couches/polygones | JSON |
| `PLAN_TECHNIQUE_DEVIS.md` | Ce document | — |
| `generateur_gds.py` (dans ../code/) | Générateur du layout — reproductible | Python |

Le `.gds` s'ouvre dans KLayout, gdstk, Cadence Virtuoso, Synopsys,
Mentor — tout outil GDSII standard.

## 2. Description géométrique du design

**Die** : cadre 5 × 5 mm, coins arrondis optionnels selon votre procédé.
**Structure** : code correcteur Steane [[7,1,3]] — un qubit logique =
7 qubits physiques + ancillas de syndrome.

| Couche GDSII | Contenu | Nombre |
|---|---|---|
| 1 | Sites qubits données — heptagone régulier | 7 |
| 2 | Ancillas de syndrome (X et Z) | 6 |
| 3 | Coupleurs inter-sites (liaisons stabilisateurs) | 24 |
| 4 | Bus de lecture / lignes de contrôle | 4 |
| 5 | Étiquettes de repérage (labels) | 19 |
| 6 | Cadre de die + marques d'alignement | 1 + 4 |

**Règles internes** (génériques, non-PDK) : largeur min 2 µm,
espacement min 2 µm, marge cadre 50 µm.

## 3. Les équations du design (cheminement)

La géométrie découle directement du code [[7,1,3]] :

```
7 données :   positions r·(cos kθ, sin kθ),  θ = 2π/7,  r = rayon heptagone
6 ancillas :  2 triangles intérieurs (X-checks, Z-checks)
24 coupleurs : arêtes du graphe des stabilisateurs Steane
               (4 X-stabilisateurs + 4 Z-stabilisateurs sur octaèdre dual)
```

Arithmétique du système (CONJECTURE_GENERALE.md) :
`d = 27·p²` — les espacements héritent la grammaire de carrés du système.

## 4. Ce dont nous avons besoin dans le devis

1. **Gravure de masques** : nombre de masques (= couches métalliques/
   implants), procédé visé (silicium conventionnel ou silicium spin/
   isotopiquement pur ²⁸Si si vous le proposez)
2. **Options** : gravure seule des réticules vs. run wafer complet
3. **Materials que vous possédez** : précisez ce que votre parc permet
   (wafer Si, SOI, épitaxie ²⁸Si, métaux Nb/Al/Ti pour couches)
4. **Formats acceptés** : GDSII direct fourni ; OASIS convertible sur demande
5. **Contraintes** : tolérance de dimension, overlay entre couches,
   délai, et si vous offrez DRC selon VOTRE PDK interne

## 5. Limites honnêtes (à connaître avant devis)

- Le layout est **pédagogique et topologiquement exact** pour la
  structure [[7,1,3]] — il n'est PAS encore un design physique signé
  (pas de DRC/LVS contre un PDK fonderie, pas d'extraction parasitique).
- Si vous disposez d'un PDK de recherché (silicium spin Qubits, type
  CMOS 300 mm ou MPW universitaire), nous adaptons le layout à vos
  règles — le générateur est paramétrique (`generateur_gds.py`).
- Ce premier devis concerne l'évaluation de faisabilité et le coût des
  masques — pas un engagement de tape-out.

## 6. Reproductibilité

`py code/generateur_gds.py` régénère le `.gds` identique (SHA-256
fixe dans le manifeste). Toute adaptation de paramètres = régénération
immédiate.

---

*Prêt à répondre à toute question technique — géométrie, couches,
adaptation à votre PDK, ou variante de layout (surface code, transmon,
point quantique).*
