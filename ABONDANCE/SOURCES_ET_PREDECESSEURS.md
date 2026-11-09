# SOURCES ET PRÉDÉCESSEURS — dossier ABONDANCE

**Licence** : GPL-3.0-only OR AGPL-3.0-only (double licence, voir `LICENSE.md` à la racine du dépôt).

**Auteur** : M. Ahmed EL BAHLOUL (IMAM8MAHDI) — développement assisté par IA générative,
résultats relus et dirigés par l'auteur humain.
**Périmètre** : `electricite_abondance.py` (21 équations), `eau_abondance.py` (15),
`agriculture_abondance.py` (18) — 54 équations, 54 contrôles.

Ce fichier répond à une seule question : **qui a posé la brique, et qu'est-ce que ce dossier
en fait vraiment.** Il ne prétend pas rendre un hommage décoratif : chaque nom cité ici est
rangé dans un des trois statuts ci-dessous, et le troisième statut est écrit noir sur blanc.

## 1. Règle d'attribution — trois statuts

| Statut | Ce que ça veut dire | Ce que ça ne veut pas dire |
|---|---|---|
| **CALCULÉE** | la loi est écrite dans le module, son résultat est chiffré, et un contrôle `Cnn` la vérifie à chaque exécution | aucune mesure physique prise ici |
| **DÉCLARÉE** | la valeur vient de la littérature, d'une institution ou d'un constructeur ; le module en vérifie la cohérence (bilans, unités), pas la valeur | aucun mérite expérimental pour ce dossier |
| **LIGNÉE** | le nom figure dans le fil conducteur pour la filiation intellectuelle ; **aucune équation ne repose sur lui** | ce n'est pas une revendication de paternité d'un résultat chiffré |

Les trois fils conducteurs affichés en tête des pages (`fil_conducteur`) sont des lignées :
ils ne doivent pas être lus comme une liste d'auteurs de nos chiffres. La table ci-dessous
est l'autorité ; les trois pages du dossier, en français, anglais et arabe, nomment ce
fichier en toutes lettres — mention simple, pas de lien, pour que les 30 liens relatifs
publiés restent tous résolus.

## 2. Ce que la vidéo a fourni — et ce qu'elle n'a pas fourni

La mesure du 2026-11-08 est reproductible avec le script
`extraire_chapitres_youtube.py` (Skill éponyme). Sortie verbatim :

```
titre            : Électricité : tout s'éclaire ! | Déclics | ARTE
auteur           : ARTE
id               : cFx7Cm-c2nA
url              : https://www.youtube.com/watch?v=cFx7Cm-c2nA
duree_s          : 1565
horodatage_utc   : 2026-11-08T21:13:45Z
chapitres        : []            (resume.chapitres = 0)
transcript       : absent — 0 octet sur json3, srv3 et xml
```

Scénario : Pierre Lergenmüller, collection *Points de repères* / *Déclics*, France, 2020,
26 minutes (mention de la page, non mesurée ici).

Avertissements renvoyés par la sonde, repris tels quels :

```
aucun en-tete de chapitres : horodatages pris dans toute la description
aucun chapitre horodate dans la description
timedtext repond sans contenu : le transcript est tenu pour absent
```

**Conséquence, appliquée sans exception** : la vidéo a fourni une *méthode* (partir d'une
expérience quotidienne, remonter aux lois, chiffrer) et des *thèmes* (ampère, kV, kWh,
solaire). Elle n'a fourni **aucune citation, aucun minutage, aucun chiffre**. Aucun nombre de
ce dossier ne vient d'elle, et aucune phrase de nos pages n'est présentée comme tirée de sa
bande-son. Les chiffres viennent des constantes SI exactes, de la littérature citée en
commentaire de chaque fonction, et des valeurs déclarées listées §4.

## 3. Table des 54 équations

### ÉLECTRICITÉ — `electricite_abondance.py`

| EQ | Ce qui est calculé | Prédécesseur | Statut |
|---|---|---|---|
| 01 | `F = q₁q₂/(4πε₀r²)`, `k = μ₀c²/4π`, `1 C = 1/e` | Coulomb ; Maxwell (relation k–c) ; e exact depuis la 19e CGPM 2019 | CALCULÉE / DÉCLARÉE (valeur de e) |
| 02 | `E = U/d`, `C = ε₀S/d`, `W = ½CU²` | Faraday (capacité, diélectrique) ; Lenz n'intervient pas ici | CALCULÉE |
| 03 | `R = ρℓ/S`, `σ = 1/ρ`, `v = I/(neS)` | Ohm | CALCULÉE |
| 04 | `P = UI = I²R = U²/R`, `1 kWh = 3,6 MJ` | Joule | CALCULÉE |
| 05 | ΣI = 0, ΣU = 0, résolution en rationnels | Kirchhoff | CALCULÉE |
| 06 | `B = μ₀I/(2πr)`, `F/ℓ = μ₀I₁I₂/(2πd)` | Ampère | CALCULÉE |
| 07 | `ℰ = −N·dΦ/dt`, `ℰ_rms = NBSω/√2` | Faraday **et** Lenz (le signe moins est à Lenz) | CALCULÉE |
| 08 | `L = μ₀N²S/ℓ`, `W = ½LI²`, `u_B = B²/2μ₀` | Henry ; Maxwell (densités de champ) | CALCULÉE |
| 09 | `c = 1/√(μ₀ε₀)`, `Z₀ = √(μ₀/ε₀)`, `E/B = c` | Maxwell | CALCULÉE |
| 10 | `U_rms = Û/√2`, `P = UI cos φ`, `S² = P² + Q²` | Steinmetz (représentation des régimes sinusoïdaux) | CALCULÉE |
| 11 | `U_ligne = √3·U_phase`, somme des phaseurs = 0 | Tesla (systèmes polyphasés, 1888) | CALCULÉE |
| 12 | `U₂/U₁ = N₂/N₁`, `I₂/I₁ = N₁/N₂` | Faraday (induction mutuelle), Henry | CALCULÉE |
| 13 | `P_pertes = (P/U)²R ⇒ pertes ∝ 1/U²` | loi de Joule appliquée ; W. Thomson (Kelvin) pour l'idée du transport à haute tension | CALCULÉE / LIGNÉE (Kelvin) |
| 14 | `P = ρgQHη`, `e = ρgH` par m³ | Euler/Bernoulli pour la forme, Pascal pour `ρgH` | CALCULÉE |
| 15 | `C_P(a) = 4a(1−a)²`, `a* = 1/3`, `C_P,max = 16/27` | Betz (1920) | CALCULÉE (cadre actuator disk, hypothèses déclarées) |
| 16 | `η ≤ 1 − T_froid/T_source` | Carnot | CALCULÉE |
| 17 | `λ_seuil = hc/E_g`, part perdue en chaleur | Shockley et Queisser (1961) ; Planck pour `E = hc/λ` | CALCULÉE (gap `E_g` DÉCLARÉ par matériau) |
| 18 | `e = U × capacité` en Wh/kg, gravitaire `= gh` | — (convention d'échelle) ; Wh/kg des chimies | CALCULÉE / DÉCLARÉE (Wh/kg) |
| 19 | `R = 0 ⇒ pertes ohmiques nulles` ; `2Δ(0)/k_BT_c ≈ 3,53` | Onnes (1911) ; BCS (1957) | CALCULÉE (conséquence) / DÉCLARÉE (3,53) |
| 20 | `Φ = L☉/4πAU²`, `P_interceptée = ΦπR⊕²`, `S = P/(ηΦ)` | — (constantes astronomiques déclarées) | DÉCLARÉE (L☉, AU) / CALCULÉE (produit) |
| 21 | grille de lecture du dossier (4 ponts, 4 limites) | — (structure AL-MIZAN, auteur du dossier) | LIGNÉE par nature |

### EAU — `eau_abondance.py`

| EQ | Ce qui est calculé | Prédécesseur | Statut |
|---|---|---|---|
| 01 | `V_douce = V_totale × 2,59 %`, somme des compartiments | — (ordres de grandeur USGS) | DÉCLARÉE (volumes) / CALCULÉE (somme) |
| 02 | `P = ρgh`, `F = PS` | Pascal (barrique) | CALCULÉE |
| 03 | `F = ρ_fluide V g`, part immergée `= ρ_objet/ρ_fluide` | Archimède | CALCULÉE |
| 04 | `Q = A·v` constant | — (principe de continuité, non attribué dans ce dossier) | CALCULÉE |
| 05 | `P + ½ρv² + ρgh = cte`, `v = √(2gh)` | Daniel Bernoulli ; Torricelli | CALCULÉE |
| 06 | `e = ρgH/η` par m³, `P = e·Q` | reprise de EQ-14 électricité ; rendement `η` | CALCULÉE / DÉCLARÉE (η) |
| 07 | `π = i·c·R·T` | van 't Hoff (1886) ; coefficient `i` effectif NaCl | CALCULÉE / DÉCLARÉE (i) |
| 08 | `w_min = RT·ln(1/x_eau)` par mole extraite | Gibbs (travail de mélange) ; Raoult (activité idéale, hypothèse) | CALCULÉE (borne) / DÉCLARÉE (idéalité) |
| 09 | `C_saumure = C_alim/(1−Y)`, bilan salin fermé | — (conservation de la matière) | CALCULÉE |
| 10 | Magnus `e_s = 6,1094·exp(17,625t/(t+243,04))` contre Clausius–Clapeyron `d ln e/dT = L/R_vT²` | Magnus ; Clausius et Clapeyron ; Alduchov et Eskridge (les trois constantes 1996) | CALCULÉE (les deux formes) / DÉCLARÉE (constantes) |
| 11 | `P_terre = ET_terre + R`, `P_océan + R = ET_océan`, clôture à zéro | — (bilan du cycle, flux déclarés) | DÉCLARÉE (flux) / CALCULÉE (clôture) |
| 12 | `V_eau = Σ (L/kg)ᵢ · mᵢ` | Allan (eau virtuelle), Hoekstra (empreinte eau) | DÉCLARÉE (L/kg par aliment) / CALCULÉE (agrégat) |
| 13 | `S ≈ 0,64 × EC` et sa réciproque | — (facteur empirique normalisé) | DÉCLARÉE (0,64) / CALCULÉE (réciprocité) |
| 14 | `E = ρgHV` (même membre qu'électricité) | Pascal ; volume de barrage déclaré | CALCULÉE / DÉCLARÉE (100 Mm³) |
| 15 | grille de lecture appliquée à l'eau (analogies) | — | LIGNÉE par nature |

Trois noms de la lignée eau ne portent **aucune** équation : **Darcy** (milieu poreux — la
perméabilité n'est pas implantée ici), **Pfeffer** (osmomètre historique, `π` est à van 't
Hoff), **Loeb et Sourirajan** (membrane asymétrique 1963 — seule la borne EQ-08 est calculée,
les performances réelles d'une membrane sont déclarées et non mesurées).

### AGRICULTURE — `agriculture_abondance.py`

| EQ | Ce qui est calculé | Prédécesseur | Statut |
|---|---|---|---|
| 01 | `6CO₂ + 6H₂O → C₆H₁₂O₆ + 6O₂`, équilibre atome par atome | Calvin (cycle) ; bilan stœchiométrique classique | CALCULÉE |
| 02 | `E = N_A·hc/λ` par einstein ; 4 photons/CO₂ minimum, ~8,5 mesurés | Planck et Einstein (quantum de lumière) ; rendement quantique mesuré | CALCULÉE (prix minimal) / DÉCLARÉE (8,5) |
| 03 | `M_λ(5772 K)` intégrée sur 400–700 nm, `φ = ∫M_λλ/(hc)dλ` | Planck ; Stefan et Boltzmann (contrôle d'intégration) | CALCULÉE |
| 04 | `E_PAR = I·f_PAR·S` contre la demande `N × kcal/j` | — (constantes solar et kcal déclarées) | DÉCLARÉE (I, kcal) / CALCULÉE (produit) |
| 05 | `ΔB = ε · fAPAR · PAR`, `ε ≤` plafond EQ-02 | Monteith (Ray Use Efficiency, 1972) ; plafonds 42,67 et 20,08 g/MJ | CALCULÉE (forme) / DÉCLARÉE (plafonds) |
| 06 | `v_C/v_O = 85`, C4 comme pompe à CO₂ devant Rubisco | Calvin et Benson ; Farquhar (spécificité de Rubisco) ; la voie C4 est à Hatch et Slack (1966), non nommés dans notre fil conducteur | DÉCLARÉE (85) / CALCULÉE (rapports) |
| 07 | `Y = Y_max · minᵢ(fᵢ)` | Liebig (et Boussingault pour les mesures de terrain) ; Blackman pour le facteur limitant | CALCULÉE |
| 08 | `NH₃ = 82,25 % N`, `31 GJ/t ⇒ 37,7 MJ/kg N` | Haber et Bosch | CALCULÉE / DÉCLARÉE (31 GJ/t) |
| 09 | `ET = R_n/(ρL)`, `1 mm sur 1 ha = 10 m³` | Monteith (forme du bilan) ; la version Penman–Monteith complète n'est **pas** implantée | CALCULÉE (conversion) / DÉCLARÉE (R_n) |
| 10 | `e = kWh/m³` repris du dossier EAU × volume prélevé | reprise inter-dossiers | CALCULÉE |
| 11 | `L/kg` dérivé (EQ-09) contre `L/kg` déclaré (EAU EQ-12) | Allan et Hoekstra | CALCULÉE (écart) / DÉCLARÉE (les deux bornes) |
| 12 | `Δ¹³C = a + (b−a)·ci/ca`, `WUE ∝ ca(1 − ci/ca)` | Farquhar, **avec von Caemmerer et Berry** (1989) | CALCULÉE (forme) / DÉCLARÉE (a, b) |
| 13 | `personnes/ha = (t/ha)(kcal/t) / (2100 × 365)` | — (rendements et ration déclarés) | DÉCLARÉE (entrées) / CALCULÉE (sortie) |
| 14 | `S = N·(kcal/j)·365 / (kcal/ha)`, élevage × indice de conversion | — | DÉCLARÉE (N, rendements, ICA) / CALCULÉE (surface) |
| 15 | `M = z·S·ρ`, `dette = érosion − formation` | — (profondeur, densité, débits déclarés) | DÉCLARÉE (paramètres) / CALCULÉE (temps de dette) |
| 16 | `kWh/m² = DLI · E_einstein`, `WPE = φE_photon/Pélec` | — (efficacités LED déclarées) | CALCULÉE (chaîne) / DÉCLARÉE (η) |
| 17 | quantités/ha dérivées des EQ-08, 09, 10, 16 avec facteurs stœchiométriques | — (teneurs P₂O₅, K₂O, KCl déclarées) | CALCULÉE (dimensionnement) / DÉCLARÉE (teneurs) |
| 18 | grille de lecture appliquée à l'agriculture (analogies) | — | LIGNÉE par nature |

Dans le fil conducteur agriculture, **Thalès, Anaximandre et Théophraste** sont des noms de
lignée : aucune des 18 équations ne repose sur eux. Ils ouvrent la filiation (l'eau comme
principe, puis le premier traité de botanique), pas le calcul.

## 4. Où sont les valeurs déclarées

Toute valeur déclarée porte la mention `déclaré` dans le commentaire de la constante du
module, et la rubrique « valeurs déclarées » des pages. Les principales :

- volumes d'eau douce et compartiments (ordre de grandeur USGS),
- litres par kilogramme par aliment (tables d'empreinte eau),
- `i` de NaCl, rendement de pompe `η`, capacité Wh/kg des chimies,
- `L☉`, `AU`, R⊕, fractions PAR,
- plafonds g/MJ PAR de Monteith, spécificité 85 de Rubisco, `a` et `b` de la discrimination
  `Δ¹³C`,
- 31 GJ/t NH₃, teneurs 30 % P₂O₅ / 60 % K₂O, rendement LED,
- `2Δ(0)/k_BT_c = 3,53`, gap `E_g` des semi-conducteurs.

## 5. Limites — ce que ce dossier ne revendique pas

1. **Rien n'est mesuré ici.** Les 54 équations sont des fermetures d'identité : constantes SI
   exactes, algèbre, bilans de matière et d'énergie. Elles sont *contrôlées*
   (`C01…C54`, 54/54 à chaque exécution), pas expérimentées.
2. **Aucune de ces valeurs n'est une preuve d'optimabilité ni d'abondance atteignable.** Le
   mot « abondance » désigne un budget chiffré sous hypothèses nommées, pas une promesse.
3. **Le périmètre est borné** : disque actuator pour Betz, solution idéale pour Raoult et van
   't Hoff, régime céréalier simple pour EQ-14 agriculture, corps noir à 5772 K pour le spectre.
   Changer l'hypothèse change le nombre ; la table ci-dessus dit laquelle.
4. Les noms marqués **LIGNÉE** ne sont pas des auteurs de nos chiffres. Retirer un nom de
   lignée ne changerait aucun résultat — c'est précisément le critère de ce statut.

## 6. Comment revérifier

```bash
cd ZENODO_DEPOT_ALMIZAN/ABONDANCE
py -3 electricite_abondance.py            # 21 équations, 21 contrôles
py -3 eau_abondance.py                    # 15 équations, 15 contrôles
py -3 agriculture_abondance.py            # 18 équations, 18 contrôles
py -3 generer_abondance.py                # 54 équations, 54/54, 31 artefacts
py -3 -m unittest tests.test_electricite_abondance tests.test_eau_abondance \
              tests.test_agriculture_abondance          # 107 tests, OK
```

Deux gardes bloquent la publication à la génération :

- les nombres affichés dans les trois langues doivent être dérivés des modules
  (`verifier_nombres`, tolérance `max(1e-9, |v|·1e-6)`) — un chiffre tapé à la main dans une
  page lève `ValueError` ;
- un mot arabe à moitié translittéré ne passe pas (`_verifier_mixte`, motif
  `[\u0621-\u064a\u064f-\u0652]{4,}[A-Za-z]{4,}`) — lève `SystemExit`.

Les noms propres des fils conducteurs et le texte des sources ne sont **pas** dans le pool de
nombres : ils ne sont pas des résultats.

**Fins de ligne.** Les trois `.csv` sortent en BOM UTF-8 + CRLF (Excel français), écrits en
octets imposés. Le dépôt normalise les blobs en LF (`core.autocrlf=true`, comme pour tout le
reste du dépôt) et le manifeste scelle ces octets-LF ; les `.csv` sont en plus marqués
`text eol=crlf` dans `.gitattributes`, donc un clone ou une archive — même tentée avec
`git -c core.autocrlf=false archive` — rendent le CRLF annoncé plutôt qu'un LF hors Windows.
Les empreintes du manifeste restent calculées sur le blob (`git cat-file blob HEAD:CHEMIN`),
pas sur le fichier de l'arborescence de travail.
