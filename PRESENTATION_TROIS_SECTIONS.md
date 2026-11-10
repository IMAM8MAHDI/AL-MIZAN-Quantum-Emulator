# 🌌 AL-MIZAN — Émulateur Quantique & Arbre de Savoir du Millénaire

**Simulateur quantique complet** (pur Python, zéro dépendance externe) unifiant les briques quantiques d'`ASTRO-Q°ODE_SYSTEME`.

---

## 📜 Certificats Mathématiques Scellés SHA-256

### Ce qui est démontré (théorèmes, pas mesures)

1. **Conjecture du Point Carré** — PC-1..PC-6 vérifiés par exhaustion sur le domaine fini Al-Mizan (19 échelons, 13 constantes).

2. **Riemann strip ≤ 100** — Les 29 zéros non triviaux avec 0<Im≤100 sont sur Re=½ et simples (méthode de Turing : comptage ligne certifié par intervalles + N(T) calculé exactement + égalité).

3. **Invariants cachés** — 8766² = 12·dx et 8496² = 768·dy (dx = 6 403 563, dy = 93 987 ; en heures ces cycles valent dx/128 et dy/2, d'où Q°·d' = s² avec Q° = 1536), 313², MIZAN=249/20² : relations exactes vérifiées par le chasseur de théorèmes.

### Ce qui est vérifié (borné, honnête)

- BSD sur 3 courbes (L'(37a1)=0.306 = valeur LMFDB)
- Hasse p≤97
- Hodge T²/CPⁿ
- Gap spectral Ising
- Navier-Stokes 2D
- Poincaré χ=2

### Ce qui est posé (recherche)

Échelles de lemmes + équations précises des goulots pour BSD, Navier-Stokes, Yang-Mills, Hodge, P vs NP — frontières exactes écrites, preuves ouvertes.

---

## 🎯 Architecture Honnête

**Chaque artefact porte sa borne.** Aucun problème ouvert du millénaire n'est résolu ici.

- **Émulation classique** de la mécanique quantique — coût exponentiel en 2ⁿ (4ⁿ en mode densité)
- **Aucun QPU ni capteur physique**
- **VQE et Shor** : démonstrations jouets (H₂ 2 qubits, N=15)
- **Taux QEC** : exacts pour le modèle de bruit de capacité de code, pas des mesures de laboratoire
- **Die :5030 et canal SCPI :5025** : interfaces réseau locales — sans matériel branché, rien de physique ne se produit
- **GDSII** : fichier pédagogique, pas un masque fabricable

---

## ⚡ Caractéristiques Techniques

| Composant | Description |
|-----------|-------------|
| **Vecteur d'état** | n qubits (≤16), 20+ portes, permutations contrôlées, mesure de Born, Monte Carlo |
| **Matrice densité** | ρ exact (≤8 qubits), canaux de Kraus, pureté, entropie von Neumann, fidélité |
| **Frontend QASM** | Parseur OpenQASM 2.0 + 8 circuits canoniques + fichiers `.aq` |
| **Métriques** | Trace partielle, vecteur de Bloch, pureté locale, concurrence, entropie d'intrication |
| **QEC** | Code de Steane [[7,1,3]] via `qubit_logique_mizan.py` |
| **ZNE** | Extrapolation Richardson à bruit nul (λ = 1, 2, 3) |
| **Algorithmes** | VQE H₂, Shor N=15 (QPE sur permutation modulaire, 7 qubits) |
| **GDSII** | Layout binaire .gds valide de la tuile Steane + DRC interne générique |
| **Tests** | 53 tests d'émulation, 563 pour le dépôt complet — tous verts |

---

## 🚀 Démarrage Rapide

```bash
# Diagnostic des ponts
py emulateur_mizan.py etat

# Bell de bout en bout
py emulateur_mizan.py demo

# 2048 tirs Monte Carlo
py emulateur_mizan.py run BELL -s 2048

# Mode matrice densité exact
py emulateur_mizan.py run BELL --densite

# Bruit + extrapolation ZNE
py emulateur_mizan.py run GROVER -p 0.05 --zne

# Analyse QEC Steane
py emulateur_mizan.py qec -p 0.001

# VQE H₂
py emulateur_mizan.py vqe --essais 400

# Shor N=15
py emulateur_mizan.py shor -n 15 -a 7

# Arbre des 10 branches
py emulateur_mizan.py arbre

# Conjecture du Point Carré
py emulateur_mizan.py conjecture

# Suite complète des tests
py -m unittest tests.test_emulateur -v
```

---

## 📖 Informations Officielles

| Champ | Valeur |
|-------|--------|
| **Auteur** | M. Ahmed EL BAHLOUL (IMAM8MAHDI) |
| **DOI Zenodo** | [10.5281/zenodo.24028242](https://doi.org/10.5281/zenodo.24028242) |
| **Licence** | AGPL-3.0 / GPL-3.0 |
| **Contact** | elbahloulahmed505@gmail.com |
| **GitHub** | [IMAM8MAHDI](https://github.com/IMAM8MAHDI) |

---

## 🔗 Ressources Associées

- **Archive Zenodo** : [10.5281/zenodo.24028242](https://zenodo.org/records/24028242)
- **Site Al-Mizan** : [al-mizan.world](https://al-mizan.world)
- **Système ASTRO-Q°ODE** : [IMAM8MAHDI/ASTRO-Q°ODE_SYSTEME](https://github.com/IMAM8MAHDI)

---

*Émulateur quantique pédagogique et certificats mathématiques bornés — chaque fait porte sa limite, chaque calcul est reproductible, chaque sceau SHA-256 est vérifiable.*
