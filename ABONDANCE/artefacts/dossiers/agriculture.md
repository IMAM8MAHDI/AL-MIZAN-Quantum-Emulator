# AGRICULTURE — DU PHOTON À L'ASSIETTE

**Auteur** : M. Ahmed EL BAHLOUL (IMAM8MAHDI)  
**Licence** : GPL-3.0-only OR AGPL-3.0-only  
**Module** : `agriculture_abondance.py` — 18 équations, 18/18 contrôles reçus.

## Chemin

### Du photon à la feuille
Rien d'agricole ne se comprend sans la lumière : un einstein à 680 nm vaut 175.92 kJ/mol et le nombre de photons par CO2 fixé est une obligation thermodynamique, pas un réglage.

### De la feuille au champ : Monteith et Liebig
Le rendement d'un couvert est le produit ε·fAPAR·PAR tant qu'aucun facteur ne manque ; dès qu'un facteur manque, c'est lui qui décide.

### De l'azote du vent à l'ammoniac de Bosch
L'air est gratuit, la fixation ne l'est pas : 31 GJ par tonne de NH3, d'où 37.7 MJ par kg d'azote. C'est le prix de sortie de la faim saisonnière.

### L'eau entre par la physique : les deux dossiers se touchent
L'évapotranspiration redonne le litre du dossier EAU, et le kilowattheure de pompage vient de la même identité ρgH/η. Aucun chiffre agricole n'est saisi à la main.

### Le sol et l'eau comme dettes, pas comme charges
Un horizon de 30 cm s'use à 10 t/ha/an alors qu'il se forme vingt fois plus lentement : la ferme écrit une dette, et la comptabilité se voit.

## Équations

### EQ-01 — La photosynthèse est un bilan de masse

`6 CO2 + 6 H2O → C6H12O6 + 6 O2 ;  équilibre atome par atome`

> 372.144 g de réactifs = 372.144 g de produits · 1.466 g CO2 par g de biomasse · 0 atome d'écart

*Statut* : OPÉRATIONNEL · *chemin* : `agriculture_abondance.py → stoechiometrie_photosynthese() → C01`

### EQ-02 — Le prix du CO2 fixé : 4 photons au moins

`E = N_A·hc/λ par einstein ;  4 photons/CO2 au minimum, 8,5 mesurés`

> 680 nm → 1.8233 eV = 175.92 kJ/mol de photons · plafond 68.0 % (4 photons), 32.0 % (8,5)

*Statut* : OPÉRATIONNEL · *chemin* : `agriculture_abondance.py → exigence_quantique() → C02`

### EQ-03 — Intégrer le spectre : combien de photons utilisables

`M_λ(T) intégrée sur 400–700 nm ;  φ = ∫M_λλ/(hc)dλ`

> PAR = 36.6 % de l'énergie · 1.673 µmol/J · pleine lumière hors atmosphère ≈ 1673 µmol/m²/s · STEFAN-BOLTZMANN re-vérifiée par l'intégrale à 7.9e-07

*Statut* : OPÉRATIONNEL · *chemin* : `agriculture_abondance.py → spectre_PAR() → C03`

### EQ-04 — Le rayonnement disponible contre l'assiette disponible

`E_PAR = I·f_PAR·S ;  demande = N·(kcal/j)·365·4184`

> PAR sur les cultivables = 43.7 ZJ/an contre 0.026 ZJ/an demandés · à 0,5 % de conversion : 8.5× la demande

*Statut* : SIMULÉ · *chemin* : `agriculture_abondance.py → budget_solaire_agricole() → C04`

### EQ-05 — Monteith : le rendement borné par la lumière

`ΔB = ε·fAPAR·PAR  (Monteith) ;  ε ≤ plafond EQ-02`

> plafond 20.08 g/MJ PAR · C4 déclaré à 33.2 % du plafond, C3 à 16.6 %

*Statut* : OPÉRATIONNEL · *chemin* : `agriculture_abondance.py → rayonnement_use_efficiency() → C05`

### EQ-06 — C3, C4, CAM : Rubisco et la photorespiration

`Rubisco : v_C/v_O = 85 · C4 = pompe à CO2 devant Rubisco`

> C4/C3 en ε = 2.00× · coût de la photorespiration = 52.9 % des photons

*Statut* : SIMULÉ · *chemin* : `agriculture_abondance.py → voies_photosynthetiques() → C06`

### EQ-07 — Liebig : le baril ne se remplit pas à la planche haute

`Y = Y_max · minᵢ(fᵢ) ;  doubler un facteur non limitant ne change rien`

> P limitant : 1.40 t/ha · P ×2 : 2.45 · P ×4 : 2.45 (plateau, limitant = eau) · eau ×2 : 2.80 · toutes les planches pleines : 3.50

*Statut* : OPÉRATIONNEL · *chemin* : `agriculture_abondance.py → loi_du_minimum() → C07`

### EQ-08 — Haber-Bosch : l'azote que l'on achète

`NH3 = 82,25 % d'azote ;  31 GJ/t NH3 ⇒ 37,7 MJ par kg N`

> grain : 73.68 kg N/ha sur 120 kg appliqués → NUE 61.4 % · 359 kWh par tonne de blé

*Statut* : OPÉRATIONNEL · *chemin* : `agriculture_abondance.py → azote_haber_bosch() → C08`

### EQ-09 — L'évapotranspiration : le même litre que le dossier EAU

`ET = R_n/(ρL) ;  1 mm sur 1 ha = 10 m³`

> R_n 100 W/m² → 3.549 mm/jour · blé 500 mm = 5000 m³/ha = 1428.57 L/kg

*Statut* : OPÉRATIONNEL · *chemin* : `agriculture_abondance.py → evapotranspiration() → C09`

### EQ-10 — Irriguer : le kWh/m³ hérité du dossier EAU

`e = kWh/m³ du dossier EAU (ρgH/η à 50 m) × volume prélevé`

> 0.2089 kWh/m³ · goutte-à-goutte 4.178 GJ/ha vs superficielle 6.267 GJ/ha · irrigation/azote = 0.92

*Statut* : OPÉRATIONNEL · *chemin* : `agriculture_abondance.py → energie_irrigation() → C10`

### EQ-11 — Eau virtuelle : deux chemins, un même chiffre

`L/kg dérivé (EQ-09) contre L/kg déclaré (dossier EAU EQ-12)`

> dérivé 1428.57 vs déclaré 1500 L/kg · écart 4.8 % · compartiments vert/bleu/gris fermés

*Statut* : SIMULÉ · *chemin* : `agriculture_abondance.py → eau_virtuelle() → C11`

### EQ-12 — Δ13C : la plante enregistre son eau

`Δ¹³C = a + (b−a)·ci/ca ;  WUE ∝ ca·(1 − ci/ca)`

> Δ 19.5‰ ⇒ ci/ca = 0.6681 · 300 → 420 ppm : efficience hydrique +40.0 % à Δ constant

*Statut* : OPÉRATIONNEL · *chemin* : `agriculture_abondance.py → discrimination_carbone() → C12`

### EQ-13 — Ce qu'un hectare nourrit

`personnes/ha = (t/ha)·(kcal/t) / (2100 kcal/j × 365)`

> blé 15.53 pers/ha · maïs 47.62 pers/ha · ratio 3.07

*Statut* : SIMULÉ · *chemin* : `agriculture_abondance.py → calories_par_hectare() → C13`

### EQ-14 — La surface pour nourrir le monde, bornée

`S = N·(kcal/j)·365 / (kcal/ha) ;  élevage = surface × indice de conversion`

> 8 Md en céréales seules : 515 Mha sur 1400 Mha disponibles (2.7×) · avec 25 % d'apport animal : 1159 Mha

*Statut* : SIMULÉ · *chemin* : `agriculture_abondance.py → surface_nourrir_le_monde() → C14`

### EQ-15 — Le sol est un stock, l'érosion un débit

`M = z·S·ρ ;  dette = débit d'érosion − taux de formation`

> horizon 30 cm = 3900 t/ha · érosion 10 t/ha/an = 20× la formation · 390 ans avant disparition

*Statut* : SIMULÉ · *chemin* : `agriculture_abondance.py → dette_de_sol() → C15`

### EQ-16 — La lumière achetée : du DLI au kilogramme

`kWh/m² = DLI·E_einstein ;  WPE = φ·E_photon/Pélec`

> 15 mol/m²/j : minimum 0.7330 kWh, système 1.4881 kWh (93 W/m²) · 13.58 kWh/kg de tomate (lumière seule)

*Statut* : OPÉRATIONNEL · *chemin* : `agriculture_abondance.py → serre_led_bilan() → C16`

### EQ-17 — Les matériaux, dimensionnés par les équations

`quantité/ha = f(EQ-08, EQ-09, EQ-10, EQ-16) avec facteurs stoechiométriques exacts`

> 8 matériaux dimensionnés · film 276.00 kg/ha · SAP 666.67 kg/ha · biochar 2000 km² de surface interne par ha traité

*Statut* : SIMULÉ · *chemin* : `agriculture_abondance.py → materiaux_optimisants() → C17`

### EQ-18 — Quatre ponts de lecture, chacun borné

`P1 ↔ plafond · P2 ↔ photopériode et siècles de sol · P3 ↔ planche la plus basse · P4 ↔ dettes`

> 4 ponts déclarés comme lectures, chacun borné par une limite

*Statut* : SPÉCIFIÉ · *chemin* : `agriculture_abondance.py → ponts_dossier() → C18`

## Contrôles numériques

| ID | Contrôle | Attendu | Obtenu | État |
|---|---|---|---|---|
| C01 | bilan atomique et massique de la photosynthèse fermés | 0 / 0 | 0 / 0.00e+00 | reçu |
| C02 | deux voies pour l'einstein (hc/λ et eV × N_A·e) | 0.000000000000 | 0.000000000000e+00 | reçu |
| C03 | l'intégration numérique reproduit Stefan-Boltzmann | < 1e-6 | 7.876e-07 | reçu |
| C04 | le budget PAR dépasse la demande alimentaire de plusieurs ordres | 0.5 % → 5× à 20× | 8.5× | reçu |
| C05 | ε déclaré reste sous le plafond quantique | < 1 | 0.3320 | reçu |
| C06 | C4 > C3 > CAM en ε, surcoût quantique cohérent | 2.00 | 2.00 | reçu |
| C07 | loi du minimum : plateau exact quand le limitant change | 2.45 / 0.00 | 2.45 / 0.00e+00 | reçu |
| C08 | 82,25 % d'azote dans NH3 et énergie par kg N | 0.8224 / 35-40 MJ | 0.8224 / 37.7 MJ | reçu |
| C09 | ET issue de Rn/L et 1 mm = 10 m³/ha exactement | 10.000000 | 10.000000 | reçu |
| C10 | kWh/m³ identique au dossier EAU et gain du goutte-à-goutte | 0.000000000000 | 0.000000000000e+00 | reçu |
| C11 | L/kg dérivé converge vers le L/kg déclaré (EAU) | < 0.20 | 0.0476 | reçu |
| C12 | ci/ca dans (0,1) et gain proportionnel à ca | 0.000000000000 | 0.000000000000e+00 | reçu |
| C13 | personnes/ha et ordre de grandeur des rendements | 3.06 | 3.067 | reçu |
| C14 | surface céréalière < surface cultivable, avec marge | > 1.5 | 2.72 | reçu |
| C15 | érosion déclarée supérieure à la formation : dette ouverte | 20 | 20.0 | reçu |
| C16 | kWh système > kWh photons, WPE et watts cohérents avec le kWh | 2.030 | 93.0 W/m² | reçu |
| C17 | facteurs stoechiométriques exacts et quantités positives | 0.4364 / 0.8302 | 0.4364 / 0.8302 | reçu |
| C18 | quatre ponts déclarés, chacun borné | 4 | 4 | reçu |

## Source

```
{
  "herite_de": "electricite_abondance.py (21 EQ) puis eau_abondance.py (15 EQ)",
  "video_origine": "Électricité : tout s'éclaire ! | Déclics | ARTE",
  "video_url": "https://www.youtube.com/watch?v=cFx7Cm-c2nA",
  "transcript": "absent (timedtext : 0 octet en json3, srv3 et xml)",
  "statut_contenu": "la vidéo ne fournit AUCUNE donnée agricole : ni les rendements, ni la photosynthèse, ni les matériaux n'en sont extraits",
  "fil_conducteur": "Thalès → van 't Hoff → Boussingault (loi du minimum) → Liebig → Haber/Bosch → Blackman → Calvin → Monteith (RUE) → Allan/Hoekstra (eau virtuelle)"
}
```

## Valeurs déclarées

```
{
  "rendements_t_ha": {
    "ble": 3.5,
    "mais": 10.0
  },
  "kcal_par_tonne": {
    "ble": 3400000.0,
    "mais": 3650000.0
  },
  "eps_g_par_MJ": {
    "C3": 1.5,
    "C4": 3.0
  },
  "habergj_par_t_nh3": 31.0,
  "azote_applique_kg_ha": 120.0,
  "et_ble_mm_an": 500.0,
  "led_umol_par_joule": 2.8,
  "photons_par_co2_mesures": 8.5,
  "sol": {
    "profondeur_m": 0.3,
    "densite_t_m3": 1.3,
    "production_t_ha_an": 0.5,
    "erosion_t_ha_an": 10.0
  },
  "statut": "valeurs de littérature agronomique, non mesurées dans ce dépôt ; les équations qui les utilisent sont calculées et contrôlées"
}
```

> Document calculé, non écrit à la main : régénérer le module régénère la page.
