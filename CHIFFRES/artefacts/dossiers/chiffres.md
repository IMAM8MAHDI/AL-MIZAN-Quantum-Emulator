# CHIFFRES — 108 cellules fermées avant la mesure

**Auteur** : M. Ahmed EL BAHLOUL (IMAM8MAHDI)  
**Licence** : GPL-3.0-only OR AGPL-3.0-only  
**Module** : `chiffres_pi.py` — 17 équations, 17/17 contrôles reçus.

## Chemin

### La source mesurée, et ce qu'elle ne donne pas
Le point de départ est une page YouTube mesurée octet pour octet, citée comme une référence bibliographique : « What Is Actually Hiding in the Digits of Pi? » (chaîne Euclidea, identifiant M90ZAVojI30, durée déclarée 854 s). Elle rend dix chapitres horodatés, mais timedtext renvoie 0 octet en json3, srv3 et xml : le transcript est tenu pour absent. Le dossier n'en tire aucune citation, aucun chiffre, aucune méthode ; il en retient dix thèmes, chacun rattaché à une équation.

### Le domaine est clos avant la mesure
n = 1000000 chiffres par constante, KMAX = 6 classes, RMAX = 7 longueurs de runs, ALPHA = 0.001, GRAINE = 20261109, PAS_CUMUL = 10, cinq sondes de recherche : tout est écrit dans le module avant que la moindre décimale ne soit produite. Les 108 cellules de la confrontation sont énumérées par `predire(n)`, qui ne lit aucun chiffre.

### Les décimales viennent d'un certificat, pas d'un arrondi
Chaque voie principale rend un encadrement exact aux deux bornes et vérifie que les deux bornes ont la même partie entière à l'échelle demandée : les chiffres sont forcés. Le module porte même une correction consignée — la constante d'ancre de √2 avait été recopiée fausse, divergeant au 38ᵉ chiffre ; rien ne la confrontait, désormais C01 le fait.

### Deux voies indépendantes se recoupent
Chudnovsky contre Machin pour π, la série des factorielles contre la somme terme à terme pour e, la racine carrée entière contre Newton pour √2. L'accord chiffre à chiffre atteste que le générateur ne dérive pas ; il n'ajoute rien de neuf sur les constantes elles-mêmes.

### La confrontation borne le rejet, elle ne prouve pas
108 cellules, un seuil bilatère de 0.001 déclaré d'avance, une déiance sommée sur 18 degrés de liberté et un verdict global Poisson sur le nombre d'exclusions. Une cellule est exclue sur 108, là où 0.108 étaient attendues, p = 0.2047 : CONTENU. Ce résultat ne dit pas que π est normal ; il dit que, sur ce domaine, rien ne force à le traiter autrement qu'une suite uniforme.

### La limite est écrite dans le module
`EQ-17` ne porte pas la mention « preuve » : le statut de tout ce dossier est une confrontation sur domaine fini. La normalité simple de π, e et √2 reste ouverte depuis Borel 1909 ; aucune des lignes calculées ici ne s'avance au-delà du domaine déclaré, et le dernier chapitre de la vidéo, « A pattern nobody has proven », est pris au mot.

## Équations

### EQ-01 — π certifié par splitting binaire de Chudnovsky

`π = 426880·√10005 / Σ(−1)ᵏ(6k)!(A+Bk)/((3k)!(k!)³C³), splitting binaire`

> 1000000 décimales certifiées · 71434 termes · marge 40 chiffres de garde

*Statut* : OPÉRATIONNEL · *chemin* : `chiffres_pi.py → generer_chiffres.decimales_pi() → C01`

### EQ-02 — Seconde voie pour π : la formule de Machin

`π = 16·arccot 5 − 4·arccot 239 (Machin 1706), bornes alternées`

> accord sur 500 chiffres · premier désaccord None

*Statut* : OPÉRATIONNEL · *chemin* : `chiffres_pi.py → generer_chiffres.pi_par_machin() → C02`

### EQ-03 — e certifié par la série des inverses de factorielles

`e = Σ 1/k!, queue < 1/(m·m!) avec m·m! > 10^(n+40)`

> 1000000 décimales certifiées · m = 205029 · Q = m! vérifié True

*Statut* : OPÉRATIONNEL · *chemin* : `chiffres_pi.py → generer_chiffres.decimales_e() → C03`

### EQ-04 — √2 par une seule inégalité entière

`w = ⌊√2·10ⁿ⌋ éprouvé par w² ≤ 2·10²ⁿ < (w+1)²`

> 1000000 décimales, preuve True · voie Newton True

*Statut* : OPÉRATIONNEL · *chemin* : `chiffres_pi.py → generer_chiffres.decimales_racine2() → C04`

### EQ-05 — Une convention d'indexage, assumée et écrite

`position 1 = première décimale ; l'autre convention décale de 1`

> première décimale de π = 1 et elle est en position 1 ; 16470 auto-localisé : True

*Statut* : OPÉRATIONNEL · *chemin* : `chiffres_pi.py → convention_indexage() → C05`

### EQ-06 — H0 posée, et 108 cellules closes avant la mesure

`H0 : décimales i.i.d. uniformes sur {0,…,9}`

> 108 cellules déclarées · ALPHA = 0.001 · z seuil 3.290527 · 0.108 exclusion(s) attendue(s)

*Statut* : SPÉCIFIÉ · *chemin* : `chiffres_pi.py → predire() → C06`

### EQ-07 — Dix chiffres comptés, un χ² lu dans un intervalle

`E[compte] = n/10, σ = √(0,09n), χ²(9) : 9 ± √18, intervalle Wilson–Hilferty`

> π χ² 5.5091 · e 9.5057 · √2 16.6573 dans [0.866, 29.914]

*Statut* : OPÉRATIONNEL · *chemin* : `chiffres_pi.py → mesurer_frequence() → C07`

### EQ-08 — Une régularité exacte : 9/10, classe après classe

`λ_k = 9·10^(k−1) · 10^(−k) = 9/10`

> exact en fractions pour k = 1..20 : 9/10

*Statut* : OPÉRATIONNEL · *chemin* : `chiffres_pi.py → esperance_auto_local() → C08`

### EQ-09 — Les positions qui s'écrivent à leur propre place

`p tel que la lecture en p redonne p`

> π : [1, 16470, 44899] … 3 au total

*Statut* : OPÉRATIONNEL · *chemin* : `chiffres_pi.py → positions_auto_local() → C09`

### EQ-10 — Comptes par classe de longueur, sous loi de Poisson

`compte par classe de longueur, Poisson(λ_k) indépendante du nombre de chiffres`

> π k1:1/0.9000∈(0, 5), k2:0/0.9000∈(0, 5), k3:0/0.9000∈(0, 5), k4:0/0.9000∈(0, 5), k5:2/0.9000∈(0, 5), k6:0/0.9000∈(0, 5)

*Statut* : OPÉRATIONNEL · *chemin* : `chiffres_pi.py → classes_auto_local() → C10`

### EQ-11 — Une courbe cumulative, un seuil de Bonferroni

`E[N(x)] = Σ_{k'<k}λ_k' + (x − 10^(k−1) + 1)·10^(−k)`

> cumul sur 10 points déclarés · |z| maximal 1.842 contre le seuil de Bonferroni 4.149

*Statut* : OPÉRATIONNEL · *chemin* : `chiffres_pi.py → mesurer_cumul() → C11`

### EQ-12 — Trois voies de comptage sur une graine déclarée

`analytique / Monte-Carlo (MT19937, graine déclarée) / balayage direct`

> à n_sim = 100000 : simulé 4.650 ± 2.102 vs analytique 4.500

*Statut* : OPÉRATIONNEL · *chemin* : `chiffres_pi.py → calibrage() → C12`

### EQ-13 — Runs de chiffres identiques, compte sur compte

`E[run de longueur r] = (n−r−1)·0,81·10^(−(r−1)) + 1,8·10^(−(r−1))`

> π r1:809776/810000.2, r2:81256/80999.9, r3:7976/8100.0, r4:830/810.0, r5:77/81.0, r6:12/8.1, r7:1/0.8

*Statut* : OPÉRATIONNEL · *chemin* : `chiffres_pi.py → mesurer_runs() → C13`

### EQ-14 — Occulence : tout mot court apparaît, sur ce domaine

`E[k-présentes] = 10^k·(1 − (1 − 10^(−k))^m)`

> π k1:10/10, k2:100/100, k3:1000/1000, k4:10000/10000, k5:99992/99995, k6:631548/632119

*Statut* : OPÉRATIONNEL · *chemin* : `chiffres_pi.py → mesurer_occulence() → C14`

### EQ-15 — Cinq sondes déclarées, lues avant tout commentaire

`T ~ géométrique(10^(−L)) ; u = P(T ≤ t) doit suivre une uniforme`

> π 12345:49702, 54321:64224, 00000:17534, 999999:762, 0123456789:None

*Statut* : OPÉRATIONNEL · *chemin* : `chiffres_pi.py → mesurer_attentes() → C15`

### EQ-16 — Une déiance sommée sur les trois constantes

`G² = 2Σ[x·ln(x/λ) + λ − x] ~ χ²(3·KMAX)`

> G² = 21.036 sur 18 ddl, [4.33, 44.61] → CONTENU

*Statut* : OPÉRATIONNEL · *chemin* : `chiffres_pi.py → deviance_auto_local() → C16`

### EQ-17 — Un verdict borné : CONTENU, et rien de plus

`rejet si p < 0.001 ; global : Poisson(α·cellules) sur le nombre d'exclusions`

> 1 exclues sur 108 (attendu 0.11), p = 0.2047 → CONTENU

*Statut* : OPÉRATIONNEL · *chemin* : `chiffres_pi.py → confronter() → C17`

## Contrôles numériques

| ID | Contrôle | Attendu | Obtenu | État |
|---|---|---|---|---|
| C01 | certificat de π : alternance, contraction, plancher forcé ; et les 50 décimales publiées des trois sont rendues sans désaccord | True True True et 50/50 conformes | True True True ; ancre = 3/3 et 50 chiffres comparés ; désaccords = aucun | reçu |
| C02 | Machin rend les mêmes chiffres que Chudnovsky | identique + certifié | True/True | reçu |
| C03 | certificat de e et Q = m! exact | True True | True/True | reçu |
| C04 | √2 prouvé par les carrés et concordant avec Newton | True True | True/True | reçu |
| C05 | convention d'indexage : décalage exactement 1, position 1 = 1 | 1 ; décalage 1 | 1 ; 1 | reçu |
| C06 | predire(n) ne lit aucun chiffre : table identique, définie à n = 0 | identique et n=0 défini | identique=True, n0=True | reçu |
| C07 | Σ comptes = n, chaînes pures, χ²(9) dans l'intervalle des trois | True | True | reçu |
| C08 | algèbre du 0,9 exacte en fractions, k = 1..20 | True | True | reçu |
| C09 | chaque position rendue relit bien son propre numéro | True | True | reçu |
| C10 | candidats de classe 5 = 90 000 dès que le domaine le permet, et classes cohérentes avec la liste | 90000 (n ≥ 100005) | 90000, n = 1000000 | reçu |
| C11 | cumul auto-local : grille annoncée retrouvée, courbe croissante, |z| sous le seuil de Bonferroni | grille et ≤ 4.149 | 1.842 monotone=True grille=True | reçu |
| C12 | trois voies de comptage : simulé ≈ analytique à ±3 σ de la moyenne, rapports d'écarts-types dans la bande √n | Δ ≤ 0.4460 et 0.5 ≤ rapport ≤ 2.0 | Δ = 0.1500 ; rapports = [0.785, 1.119, 1.11, 1.133, 0.929, 1.007] | reçu |
| C13 | bilan des runs : comptés + queue = 1 + 0,9(n−1) | ≤ 3√(0,09n) = 900.0 | 72.0 | reçu |
| C14 | variances simulées dans la bande κ déclarée (occulence et runs) ; moyenne simulée ≈ analytique | 0.0 ≤ κ ≤ 1.35 ; |Δ| ≤ 632.1 | κ=[0.81, 0.539, 0.425, 0.806, 0.936, 0.988, 0.996] Δ=9.53 | reçu |
| C15 | les cinq sondes déclarées : le nombre de celles qu'on retrouve tombe dans l'intervalle Poisson de leurs probabilités de présence | [2, 23] (λ = 10.896) | 11 sur 15 | reçu |
| C16 | G² auto-local dans l'intervalle χ²(3·KMAX) | [4.33, 44.61] | 21.036 | reçu |
| C17 | verdict global : exclusions ~ Poisson(α·cellules) | p ≥ 0.001 | 0.2047 (1/108) | reçu |

## Source

```
{
  "module": "chiffres_pi.py",
  "video": {
    "url": "https://www.youtube.com/watch?v=M90ZAVojI30",
    "id": "M90ZAVojI30",
    "titre": "What Is Actually Hiding in the Digits of Pi?",
    "auteur": "Euclidea",
    "duree_s": 854,
    "horodatage_utc": "2026-11-08T23:43:25Z",
    "transcript": "absent — timedtext 0 octet en json3, srv3 et xml",
    "outils": "scripts/extraire_chapitres_youtube.py (Skill extraire-chapitres-youtube-sans-transcript)",
    "chapitres": [
      [
        "0:00",
        "Five digits at position 16470"
      ],
      [
        "1:33",
        "Where position one is"
      ],
      [
        "2:57",
        "Ninety thousand candidates"
      ],
      [
        "4:17",
        "Zero point nine every time"
      ],
      [
        "5:37",
        "Matches by length"
      ],
      [
        "7:03",
        "The running total"
      ],
      [
        "8:22",
        "Three ways to count"
      ],
      [
        "9:39",
        "The same search in e and root two"
      ],
      [
        "11:02",
        "Every short string shows up"
      ],
      [
        "12:46",
        "A pattern nobody has proven"
      ]
    ]
  },
  "domaine": {
    "n": 1000000,
    "n_sim": 100000,
    "n_sim2": 50000,
    "repiliques": 200,
    "graine": 20261109,
    "alpha": 0.001,
    "z_seuil": 3.2905267314918953,
    "kmax": 6,
    "rmax": 7
  },
  "outils": {
    "generation": "generer_chiffres.py",
    "confrontation": "chiffres_pi.py"
  }
}
```

## Valeurs déclarées

```
{
  "n": 1000000.0,
  "GARDE": 40.0,
  "A_CHUD": 13591409.0,
  "B_CHUD": 545140134.0,
  "C_CHUD": 640320.0,
  "LONGUEUR_ANCRE": 50.0,
  "ALPHA": 0.001,
  "Z_SEUIL": 3.2905267314918953,
  "KMAX": 6.0,
  "RMAX": 7.0,
  "PAS_CUMUL": 10.0,
  "GRAINE": 20261109.0,
  "n_sim": 100000.0,
  "repiliques": 200.0,
  "LIMITE_POISSON_EXACT": 500.0,
  "KAPPA_BANDE": 1.35,
  "BANDE_RAPPORT": 2.0,
  "MIN_LAMBDA_RAPPORT": 1.0
}
```

> Document calculé, non écrit à la main : régénérer le module régénère la page.
