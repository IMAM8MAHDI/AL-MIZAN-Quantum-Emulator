# ÉLECTRICITÉ & ABONDANCE ÉNERGÉTIQUE

**Auteur** : M. Ahmed EL BAHLOUL (IMAM8MAHDI)  
**Licence** : GPL-3.0-only OR AGPL-3.0-only  
**Module** : `electricite_abondance.py` — 21 équations, 21/21 contrôles reçus.

## Chemin

### Thalès et le frottement
un morceau d'ambre frotté attire la poussière : la première fois, une propriété de la matière est isolée, nommée, et non expliquée par un mythe.

### De Gilbert à Coulomb : compter la force
Gilbert sépare l'électrique du magnétique ; von Guericke fabrique une machine à sphère ; Franklin donne un nom (positif, négatif) ; Coulomb pèse la force avec une balance de torsion.

### Ampère, Ohm, Faraday : le circuit devient grandeur
Le courant devient une intensité mesurable, la tension une résistance, l'induction une tension qui naît du mouvement. L'électricité cesse d'être un spectacle de salon.

### Maxwell, Tesla, Steinmetz : la fréquence et le réseau
Maxwell enferme la lumière dans deux constantes ; Tesla et Steinmetz donnent le polyphase et le calcul en nombres complexes. Un réseau à 50 Hz est une équation qui tourne.

### Betz, Carnot, Shockley : les plafonds d'abord
Avant de promettre une machine, on pose la limite : 16/27 pour le vent, 1 − T_froid/T_source pour la chaleur, le seuil du semi-conducteur pour la lumière. Le reste est de l'ingénierie.

## Équations

### EQ-01 — La charge se compte en électrons

`F = q₁q₂/(4π ε₀ r²) ;  k = 1/(4πε₀) = μ₀c²/4π ;  1 C = 1/e`

> k = 8.9876 × 10^9 N·m²/C² · 1 C = 6.2415 × 10^18 e · 2 × 1 C à 1 m : 8.9876 × 10^9 N

*Statut* : OPÉRATIONNEL · *chemin* : `electricite_abondance.py → coulomb() → C01`

### EQ-02 — Le condensateur : champ et énergie stockée

`E = U/d ;  C = ε₀S/d ;  W = ½CU² = ½QU = ½ε₀E²·(Sd)`

> C(1 m², 1 mm) = 0.000000008854 F · W à 1 kV = 0.0044 J

*Statut* : OPÉRATIONNEL · *chemin* : `electricite_abondance.py → condensateur() → C02`

### EQ-03 — Résistance et vitesse de dérive

`R = ρ·ℓ/S ;  σ = 1/ρ ;  v_dérive = I/(n·e·S)`

> 1 km sous 10 mm² : Cu 1.680 Ω, Al 2.650 Ω · dérive 0.3671 mm/s

*Statut* : OPÉRATIONNEL · *chemin* : `electricite_abondance.py → ohm() → C03`

### EQ-04 — Puissance : trois écritures d'une même grandeur

`P = UI = I²R = U²/R ;  1 kW·h = 3,6 MJ`

> 230 V × 10 A = 2 300.0 W · trois écritures à 0.00e+00 W près

*Statut* : OPÉRATIONNEL · *chemin* : `electricite_abondance.py → puissance() → C04`

### EQ-05 — Kirchhoff résolu en rationnels

`ΣI(nœud) = 0 ;  ΣU(maille) = 0 ;  résolution en rationnels`

> I = 0.005455 A · nœud 0 · bilan 0 (exact, sans arrondi)

*Statut* : OPÉRATIONNEL · *chemin* : `electricite_abondance.py → kirchhoff() → C05`

### EQ-06 — Le champ d'un fil, défini au dixième chiffre

`B = μ₀I/(2πr) ;  F/ℓ = μ₀I₁I₂/(2πd)`

> B(1 A, 1 m) = 2.00000000109 × 10^-7 T · écart relatif à 2·10⁻⁷ = 5.44 × 10^-10

*Statut* : OPÉRATIONNEL · *chemin* : `electricite_abondance.py → champ_fil() → C06`

### EQ-07 — Faraday : l'alternateur né du mouvement

`ℰ = −N·dΦ/dt ;  Φ = B·S·cos(ωt) ;  ℰ_rms = N·B·S·ω/√2`

> 100 spires à 50 Hz : crête 314.16 V, rms 222.14 V

*Statut* : OPÉRATIONNEL · *chemin* : `electricite_abondance.py → faraday() → C07`

### EQ-08 — Inductance : l'énergie du champ magnétique

`L = μ₀N²S/ℓ ;  W = ½LI² ;  u_B = B²/(2μ₀) ;  u_E = ½ε₀E²`

> L = 0.000314159 H · W = 0.000628 J · u_B/u_E = 1.42 × 10^1

*Statut* : OPÉRATIONNEL · *chemin* : `electricite_abondance.py → inductance() → C08`

### EQ-09 — Maxwell : la lumière était déjà électrique

`c = 1/√(μ₀ε₀) ;  Z₀ = √(μ₀/ε₀) = μ₀c ;  E/B = c`

> c calculée = 2.997924580 × 10^8 m/s · Z₀ = 376.7303 Ω

*Statut* : OPÉRATIONNEL · *chemin* : `electricite_abondance.py → ondes() → C09`

### EQ-10 — Le facteur de puissance : ce qu'on paie et ce qui travaille

`U_rms = Û/√2 ;  P = UI·cos φ ;  S² = P² + Q²`

> 325 V crête → 229.81 V · cos 60° = 0.500000 · P = 1149.05 W sur 2298.10 VA

*Statut* : OPÉRATIONNEL · *chemin* : `electricite_abondance.py → courant_alternatif() → C10`

### EQ-11 — Le triphasé : trois courants, une somme nulle

`U_ligne = √3·U_phase ;  Σ phasores = 0 ;  P = √3·U_L·I_L·cos φ`

> √3 = 1.732050807569 · somme = 3.1e-16 · 230 V → 398.37 V

*Statut* : OPÉRATIONNEL · *chemin* : `electricite_abondance.py → triphase() → C11`

### EQ-12 — Le transformateur ne crée rien : il échange

`U₂/U₁ = N₂/N₁ ;  I₂/I₁ = N₁/N₂ ;  S = UI conservée`

> 20 kV → 400 V : I₂ = 1000.00 A · rendement 97.37 % avec pertes déclarées

*Statut* : SIMULÉ · *chemin* : `electricite_abondance.py → transformateur() → C12`

### EQ-13 — Haute tension : le facteur 10^6 sur les pertes

`P_pertes = (P/U)²·R  ⇒  pertes ∝ 1/U²`

> 1 GW : 400 V → 3.12 × 10^11 W · 400 kV → 3.12 × 10^5 W · facteur 1.0 × 10^6

*Statut* : OPÉRATIONNEL · *chemin* : `electricite_abondance.py → transport_haute_tension() → C13`

### EQ-14 — Chute d'eau : la puissance déjà écrite dans la gravité

`P = ρ·g·Q·H·η ;  e = ρ·g·H (par m³)`

> 100 m, 10 m³/s, η = 0,90 → 8.83 MW · 0.2724 kWh/m³

*Statut* : OPÉRATIONNEL · *chemin* : `electricite_abondance.py → hydro() → C14`

### EQ-15 — Betz : la limite se dérive, elle ne se négocie pas

`C_P(a) = 4a(1−a)² ;  a* = 1/3 ;  C_P,max = 16/27`

> C_P,max = 0.592592593 · 16/27 = 0.592592593 · a* = 0.333333322

*Statut* : OPÉRATIONNEL · *chemin* : `electricite_abondance.py → betz() → C15`

### EQ-16 — Carnot : la chaleur a un plafond politique

`η ≤ 1 − T_froid/T_source ;  rejet = T_froid/T_source`

> 800 K / 300 K → 62.50 % · meilleur rendement déclaré à 97.6 % du plafond

*Statut* : OPÉRATIONNEL · *chemin* : `electricite_abondance.py → carnot() → C16`

### EQ-17 — Le seuil du semi-conducteur : qui paie les photons

`λ_seuil = hc/E_g ;  perte = (E_photon − E_g)/E_photon`

> Si 1,12 eV → 1107.0 nm · un photon à 2E_g perd 50 %

*Statut* : OPÉRATIONNEL · *chemin* : `electricite_abondance.py → photovoltaique() → C17`

### EQ-18 — Stocker : la matière ne ment pas sur sa densité

`e = U·capacité (Wh/kg) ;  Wh = J/3600 ;  gravitaire = g·h`

> LiFePO₄ actif 586 Wh/kg · H₂ LHV 33.33 kWh/kg · 100 m d'eau 0.272 Wh/kg

*Statut* : SIMULÉ · *chemin* : `electricite_abondance.py → stockage_materiau() → C18`

### EQ-19 — Supraconductivité : zéro, mais à quel prix

`2Δ(0)/(k_B·T_c) ≈ 3,53 (déclaré) ;  R = 0 ⇒ pertes ohmiques nulles`

> NbTi Δ = 1.399 meV · rapport recalculé 3.530 · 1 km de Cu à 50 A : 4200.00 W

*Statut* : SIMULÉ · *chemin* : `electricite_abondance.py → supraconductivite() → C19`

### EQ-20 — Le budget solaire de la Terre

`Φ = L☉/(4π·AU²) ;  P interceptée = Φ·πR⊕² ;  S = P/(η·Φ)`

> Φ = 1361.17 W/m² · interceptée = 1.736 × 10^17 W = 9135× la consommation déclarée

*Statut* : SIMULÉ · *chemin* : `electricite_abondance.py → budget_solaire_terre() → C20`

### EQ-21 — Quatre ponts de lecture, chacun avec sa limite

`P1 ↔ contrôle · P2 ↔ 50 Hz · P3 ↔ redondance N-1 · P4 ↔ comptage`

> 4 ponts déclarés comme analogies de lecture, chacun avec sa limite

*Statut* : SPÉCIFIÉ · *chemin* : `electricite_abondance.py → ponts_dossier() → C21`

## Contrôles numériques

| ID | Contrôle | Attendu | Obtenu | État |
|---|---|---|---|---|
| C01 | k = 1/(4πε₀) coïncide avec μ₀c²/4π | 8.9876 × 10^9 | 8.9876 × 10^9 | reçu |
| C02 | ½CU² = ½ε₀E²·volume = ½QU | 0.000000000000 | 0.000000000000 | reçu |
| C03 | ρσ = 1 et R(Al)/R(Cu) ≈ 1,58 | 1.000000000000 | 1.000000000000 | reçu |
| C04 | P = UI = I²R = U²/R et 1 kW·h = 3,6 MJ | 2300.000000 | 2 300.000000 | reçu |
| C05 | nœud et bilan de puissance exacts (rationnels) | 0 / 0 | 0 / 0 | reçu |
| C06 | B(1 A, 1 m) à 10⁻⁸ près de 2·10⁻⁷ T | < 1e-8 | 5.444 × 10^-10 | reçu |
| C07 | dΦ/dt numérique contre analytique | < 1e-6 | 5.50 × 10^-11 | reçu |
| C08 | ½LI² = u_B·volume | 0.000000000000 | 0.000000000000 | reçu |
| C09 | 1/√(μ₀ε₀) = c et Z₀ = μ₀c | 299 792 458.000 | 299 792 458.000 | reçu |
| C10 | ∮sin² = π et S² = P² + Q² | 3.141592654 | 3.141592654 | reçu |
| C11 | déphasage de 120° ⇒ √3 et somme nulle | 0.000000000000 | 2.220446049250e-16 | reçu |
| C12 | S primaire = S secondaire (transformateur idéal) | 0.000000000000 | 0.000000000000 | reçu |
| C13 | pertes en 1/U² sur quatre tensions | 0.000000000000 | 0.000000000000e+00 | reçu |
| C14 | P = ρgQHη cohérent avec (ρgH)·Q·η | 0.000000000000 | 0.000000000000 | reçu |
| C15 | max 4a(1−a)² = 16/27 à a = 1/3 | 0.592592593 | 0.592592593 | reçu |
| C16 | η + rejet = 1 exactement | 1.000000000000 | 1.000000000000 | reçu |
| C17 | hc/e = 1239,841984 eV·nm et seuil Si ≈ 1107 nm | 1239.841984 | 1239.841984 | reçu |
| C18 | Wh/kg × 3600 = J/kg et H₂ > essence > Li-ion | 120 000 000.0 | 120 000 000.0 | reçu |
| C19 | 2Δ/kTc reproduit le rapport déclaré 3,53 | 3.530000 | 3.530000 | reçu |
| C20 | L☉/(4π AU²) ≈ 1361 W/m² et ordre de grandeur du budget | 1361.000000 | 1 361.166465 | reçu |
| C21 | quatre ponts déclarés, chacun borné par une limite | 4 | 4 | reçu |

## Source

```
{
  "titre": "Électricité : tout s'éclaire ! | Déclics | ARTE",
  "chaine": "ARTE",
  "video_id": "cFx7Cm-c2nA",
  "url": "https://www.youtube.com/watch?v=cFx7Cm-c2nA",
  "duree_s": 1565,
  "auteur_scenario": "Pierre Lergenmüller (Points de repères)",
  "programme": "France, 2020, 26 mn",
  "chapitres_publics": 0,
  "transcript": "absent (timedtext : 0 octet en json3, srv3 et xml)",
  "mesure_le": "2026-11-08T16:56:27Z"
}
```

## Valeurs déclarées

```
{
  "resistivites_ohm_m": {
    "cuivre pur": 1.68e-08,
    "cuivre IEC": 1.7241e-08,
    "aluminium": 2.65e-08
  },
  "bandes_gap_eV": {
    "Si": 1.12,
    "GaAs": 1.42,
    "MAPbI3": 1.55,
    "CdTe": 1.45
  },
  "stockage": {
    "LiFePO4 mAh/g": 170.0,
    "LiFePO4 V": 3.45,
    "graphite mAh/g": 372.0,
    "H2 LHV J/kg": 120000000.0,
    "H2 HHV J/kg": 141800000.0,
    "essence J/kg": 46000000.0
  },
  "supraconducteurs": {
    "YBCO Tc K": 92.0,
    "NbTi Tc K": 9.2
  },
  "statut": "valeurs déclarées de littérature, non mesurées dans ce dépôt"
}
```

> Document calculé, non écrit à la main : régénérer le module régénère la page.
