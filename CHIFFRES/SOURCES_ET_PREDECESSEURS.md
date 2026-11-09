# SOURCES ET PRÉDÉCESSEURS — dossier CHIFFRES

**Licence** : GPL-3.0-only OR AGPL-3.0-only (double licence, voir `LICENSE.md` à la racine du dépôt).

**Auteur** : M. Ahmed EL BAHLOUL (IMAM8MAHDI) — développement assisté par IA générative,
résultats relus et dirigés par l'auteur humain.

**Périmètre** : `generer_chiffres.py` (3 productrices de décimales certifiées, 2 voies
indépendantes par constante) et `chiffres_pi.py` (17 équations, 17 contrôles, 108 cellules
pré-déclarées), `tests/test_chiffres.py` (32 tests). Domaine des tests `n = 20 000`, domaine
publicé `n = 10^6` avec artefacts (`artefacts/*.json`, `artefacts/confrontation.csv`).

Ce fichier répond à une seule question : **qui a posé la brique, et qu'est-ce que ce dossier
en fait vraiment.** Chaque nom cité est rangé dans un des trois statuts ci-dessous, et le
troisième est écrit noir sur blanc.

## 1. Règle d'attribution — trois statuts

| Statut | Ce que ça veut dire | Ce que ça ne veut pas dire |
|---|---|---|
| **CALCULÉE** | la loi est écrite dans le module, son résultat est chiffré, et un contrôle `Cnn` la re-vérifie à chaque exécution, sans emprunt de mesure | aucune preuve de normalité, jamais |
| **DÉCLARÉE** | la valeur ou l'identité vient de la littérature ; le module en vérifie la **cohérence** (entiers, bornes, unités), pas la valeur elle-même | aucun mérite d'auteur pour ce dossier |
| **LIGNÉE** | le nom figure dans la filiation intellectuelle ; **aucune des 17 équations ne repose sur lui** | ce n'est pas une revendication de paternité d'un résultat chiffré |

## 2. Ce que la vidéo a fourni — et ce qu'elle n'a pas fourni

Mesure reproductible avec `scripts/extraire_chapitres_youtube.py` (Skill
`extraire-chapitres-youtube-sans-transcript`). Sortie verbatim, consignée dans
`chiffres_pi.VIDEO` et reprise dans `artefacts/predictions.json` :

```
titre            : What Is Actually Hiding in the Digits of Pi?
auteur           : Euclidea
id               : M90ZAVojI30
url              : https://www.youtube.com/watch?v=M90ZAVojI30
duree_s          : 854
horodatage_utc   : 2026-11-08T23:43:25Z
transcript       : absent — timedtext 0 octet en json3, srv3 et xml
```

Les dix chapitres horodatés, repris **tels quels** (titre et `debut`), sont le seul apport de
la vidéo ; chacun rattache au moins une équation (`equations[i].chapitre`) :

| `debut` | Titre du chapitre | Équation rattachée |
|---|---|---|
| 0:00 | Five digits at position 16470 | EQ-09 |
| 1:33 | Where position one is | EQ-05 |
| 2:57 | Ninety thousand candidates | EQ-10 |
| 4:17 | Zero point nine every time | EQ-08 |
| 5:37 | Matches by length | EQ-13 |
| 7:03 | The running total | EQ-11 |
| 8:22 | Three ways to count | EQ-12 |
| 9:39 | The same search in e and root two | EQ-16 |
| 11:02 | Every short string shows up | EQ-14, EQ-15 |
| 12:46 | A pattern nobody has proven | EQ-17 |

Avertissements renvoyés par la sonde, repris tels quels :

```
aucun en-tete de chapitres : horodatages pris dans toute la description
timedtext repond sans contenu : le transcript est tenu pour absent
```

**Conséquence, appliquée sans exception** : la vidéo a fourni des *thèmes* et leurs
horodatages. Elle n'a fourni **aucune citation, aucun chiffre, aucune méthode**. Aucun nombre
de ce dossier ne vient d'elle, et aucune phrase de nos artefacts n'est présentée comme tirée
de sa bande-son. Le titre « Five digits at position 16470 » n'est pas la source du chiffre
16470 : `C09` et `test_point_de_feynman_et_position_16470` le recalculent à partir des
décimales produites par le module. Le dernier chapitre, « A pattern nobody has proven », est
pris au mot : `EQ-17` n'affiche qu'une confrontation bornée, jamais une preuve.

## 3. Table des 17 équations

| EQ | Ce qui est calculé | Prédécesseur | Statut |
|---|---|---|---|
| 01 | π à `n` décimales par Chudnovsky, splitting binaire, encadrement entier + `LONGUEUR_ANCRE` = 50 décimales publiées recoupées (`C01`) | Chudnovsky et Chudnovsky (1989) ; Brent (complexité du produit) | DÉCLARÉE (l'identité) / CALCULÉE (alternance, contraction, plancher, ancre) |
| 02 | Seconde voie : π = 16·arccot 5 − 4·arccot 239, bornes alternées en rationnels, accord chiffre à chiffre avec EQ-01 | Machin (1706) ; Gregory (1671) et Leibniz (1673) pour la série d'arctangente | CALCULÉE |
| 03 | e à `n` décimales par Σ1/k!, queue `< 1/(m·m!)` et `Q = m!` revérifié en entiers | Euler (1748) | CALCULÉE (la borne de queue est éprouvée ici) |
| 04 | √2 par `w = ⌊√2·10ⁿ⌋` : `w² ≤ 2·10^{2n} < (w+1)²`, contrôle croisé avec la racine décimal exacte de la bibliothèque | Hippase / les pythagoriciens (irrationalité) ; tablette YBC 7289 (approximation sexagésimale) — aucun des deux n'intervient dans le calcul | CALCULÉE / LIGNÉE (les deux noms) |
| 05 | Convention d'indexage assumée : position 1 = première décimale ; l'autre convention décale de exactement 1 | — (convention, pas un résultat) | CALCULÉE |
| 06 | `predire(n)` ne lit aucun chiffre : table reproductible bit à bit, définie à `n = 0` | — (méthode : pré-déclaration avant mesure) | CALCULÉE |
| 07 | Fréquences des dix chiffres, Σ comptes = `n`, χ²(9) dans l'intervalle annoncé | Pearson (1900) pour la statistique ; Wilson et Hilferty (1931) pour l'intervalle en racine cubique | CALCULÉE / DÉCLARÉE (l'approximation Wilson–Hilferty, qui n'est pas le quantile exact) |
| 08 | `E[#auto-localisés de classe k] = 9·10^{k−1}·10^{−k} = 9/10` en fractions exactes, `k = 1..20` | — (arithmétique élémentaire, formulée ici) | CALCULÉE |
| 09 | Positions où le numéro s'écrit à sa propre place ; 16470 revérifié dans π | — (définition locale au dossier) | CALCULÉE |
| 10 | Candidats par classe : 90 000 pour la classe 5 dès que le domaine le permet | — (dénombrement) | CALCULÉE |
| 11 | Cumul par pas déclaré (`PAS_CUMUL = 10`) et seuil de Bonferroni sur les 3×points testés | Bonferroni (1936), Cetoni (1925) | CALCULÉE (courbe) / DÉCLARÉE (la correction multiple) |
| 12 | Trois voies de comptage : analytique, Monte-Carlo (`GRAINE = 20261109`), rejeu ; rapport des écarts-types dans la bande `√n` déclarée | Metropolis, Ulam et von Neumann (1949) pour la méthode ; de Moivre et Laplace pour l'échelle `√n` | CALCULÉE / LIGNÉE (noms de la méthode) |
| 13 | Longueurs de runs : espérance `1 + 0,9(n−1)` et bilan des queues, variance **calibrée** `κ` (pas supposée) | Wald et Wolfowitz (1940) — leur test n'est **pas** utilisé ici | CALCULÉE / LIGNÉE |
| 14 | Occulence (mots distincts de longueur `k`) : espérance exacte par inclusion et variance simulée | — | CALCULÉE / SIMULÉE (`κ` mesuré, `KAPPA_BANDE = [0, 1,35]`) |
| 15 | Cinq sondes déclarées (`12345`, `54321`, `00000`, `999999`, `0123456789`) : intervalle Poisson sur le **nombre** de présences, pas sur leur place | Poisson (1837) pour la loi des petits comptes ; l'anecdote du « point de Feynman » (six 9 à 762) est folklore de cours, sans auteur vérifié | CALCULÉE / DÉCLARÉE (l'anecdote) |
| 16 | Déiance `G²` auto-localisée sur `3·KMAX` degrés de liberté, dans l'intervalle χ² annoncé | Fisher (test G, 1932) | CALCULÉE |
| 17 | Verdict global : nombre d'exclusions ≈ Poisson(`α` × cellules), `α = 0,001` déclaré avant mesure | Borel (1909) pour la notion de normalité — jamais établie pour π, e ou √2 | CALCULÉE (sur domaine fini) / LIGNÉE (Borel) |

**Noms de lignée pure**, sans aucune équation qui repose sur eux : **Borel (1909)**,
**Sierpiński (1917)** et **Champernowne (1933)** (premiers nombres explicitement normaux),
**Copeland et Erdős (1937)**, **Wall (1949)** (normalité dans toutes les bases),
**Bailey, Borwein et Plouffe (1995)** (extraction des chiffres d'hexadécimale de π — formule
BBP : **aucune** de nos deux voies ne l'utilise), **Plouffe (1996, BBP–Lecoutre–Plouffe,
chiffres décimaux de √2 par expérimentation)**. Les retirer ne changerait un seul de nos
chiffres : c'est précisément le critère du statut.

## 4. Où sont les valeurs déclarées

Toute valeur déclarée porte la mention `déclaré` à la ligne de la constante :
`GARDE = 40`, `ALPHA = 0,001`, `Z_SEUIL = 3,2905267314918953`, `GRAINE = 20261109`,
`PAS_CUMUL = 10`, `LIMITE_POISSON_EXACT = 500`, `MIN_LAMBDA_RAPPORT = 1`,
`BANDE_RAPPORT = [0,5 ; 2,0]`, `KAPPA_BANDE = [0 ; 1,35]`, `LONGUEUR_ANCRE = 50`,
`CHIFFRES_DE_REFERENCE` (50 décimales publiées des trois constantes), et les trois entiers
`A = 13591409`, `B = 545140134`, `C = 640320` de l'identité de Chudnovsky.

## 5. Une correction réelle, consignée

La constante `CHIFFRES_DE_REFERENCE["racine2"]` était fausse depuis sa première écriture :
`…9807859109969759585` au lieu de `…9807856967187537694`. Les deux chaînes divergent au
38ᵉ chiffre (les 37 premiers sont communs), et la queue erronée ne correspond à aucun
développement recoupé ici (π, e, √2, √3, √2 000 chiffres en interne, `Decimal` à 2 100
chiffres). Les décimales **produites** par `decimales_racine2` n'ont jamais été fausses — seule
la constante citée l'était, et rien ne la confrontait. Correction : la constante est maintenant
comparée aux chiffres produits (`C01`, `ancre = 3/3`) et recalculée par une troisième voie
indépendante dans les tests (`test_ancre_racine2_par_decimal`, `decimal.Decimal(2).sqrt()`).
Un test qui reprend une valeur publiée sans la recroiser à une source hors du fichier est une
valeur tapée à la main, pas un contrôle.

## 6. Limites — ce que ce dossier ne revendique pas

1. **Aucune preuve de normalité.** `EQ-17` et les 108 cellules confrontent des lois calculées
   à des mesures sur un domaine fini déclaré (`n = 20 000` en test, `10^6` publié). Un
   résultat conforme ne prouve pas que π est normal ; un résultat discordant ne prouverait pas
   qu'il ne l'est pas. C'est le sens du chapitre 12:46, « A pattern nobody has proven ».
2. **Le domaine fini est le domaine.** Les seuils (`Z_SEUIL`, bandes `κ` et rapport) sont
   déclarés avant mesure ; ils sont arbitraires mais publics, donc re-jouables à l'identique.
3. **`κ` est simulé, pas prouvé.** Pour les runs et l'occulence, la variance Monte-Carlo
   remplace une variance supposée : `C14` borne le rapport à `[0 ; 1,35]` sans le justifier
   ailleurs que par la bande déclarée.
4. **L'intervalle χ² est une approximation** (Wilson–Hilferty 1931), pas le quantile exact.
5. **Les 50 chiffres publiés sont une ancre, pas une autorité** : ils ne font que 50 chiffres,
   et leur seul rôle est de coincer une régression d'implémentation, comme §5 en donne le cas.

## 7. Comment revérifier

```bash
cd ZENODO_DEPOT_ALMIZAN/CHIFFRES
py -3 chiffres_pi.py                     # domaine court 20 000 — 17/17 contrôles, rc=0
py -3 chiffres_pi.py 1000000 --ecrit     # domaine publié + 5 artefacts, ~3 min
cd CHIFFRES && py -3 -m unittest tests.test_chiffres    # 32 tests, OK
```

`generer_chiffres.py` s'exécute seul (`py -3 generer_chiffres.py`) et rend les deux voies
indépendantes par constante ; `chiffres_pi.py` les consomme et ne les relit pas. Les artefacts
`mesures.json` portent l'ancre (`certificats.*.ancre_publiee`) ; `confrontation.csv` sort en
BOM UTF-8 + `;` + virgule décimale (Excel français), 109 lignes = en-tête + 108 cellules.

**Fins de ligne.** Le dépôt normalise les blobs en LF (`core.autocrlf=true`) et le manifeste
scelle ces octets-LF (`git cat-file blob HEAD:CHEMIN | sha256sum`), pas le fichier de l'arbre
de travail. `confrontation.csv` est en plus marqué `text eol=crlf` dans `.gitattributes` :
clone et archive rendent partout le CRLF que le format « Excel français » annonce, y compris
sous `git -c core.autocrlf=false archive --format=zip`. Le fichier lui-même est écrit en octets
imposés (`write_bytes`) : un `write_text` en mode texte laisse le système traduire les fins de
ligne, ce qui rendait un CSV LF hors Windows alors que le test, lui, attend le CRLF annoncé.
