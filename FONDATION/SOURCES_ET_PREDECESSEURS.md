# SOURCES ET PRÉDÉCESSEURS — dossier FONDATION

**Licence** : GPL-3.0-only OR AGPL-3.0-only (double licence, voir `LICENSE.md` à la racine du dépôt).

**Auteur** : M. Ahmed EL BAHLOUL (IMAM8MAHDI) — développement assisté par IA générative,
résultats relus et dirigés par l'auteur humain.

**Périmètre** : `fondation_base.py` (18 équations, 18 contrôles, registre de 14 grandeurs,
prédiction gelée à 14 variables libres), `tests/test_fondation.py` (45 tests),
`OUTILS/audit_piliers.py` (audit des quatre piliers, parc entier) et
`SIMULATIONS/simuler_kaons.py` (5 validations de comptage, 20 000 tirages, graine 20261109).
Artefacts : `artefacts/{base,etat,gel,confrontation,inventaire}.json` et
`artefacts/confrontation.csv`.

Ce dossier est la **base** du parc : il ne prétend pas ajouter une physique, il énonce les
quatre règles que toute équation du dépôt doit tenir, et il les applique d'abord à lui-même.
Il répond à la même question que les autres dossiers de sources : **qui a posé la brique, et
qu'est-ce que ce dossier en fait vraiment.**

## 1. Règle d'attribution — quatre statuts

| Statut | Ce que ça veut dire | Ce que ça ne veut pas dire |
|---|---|---|
| **CALCULÉE** | la loi est écrite dans le module, son résultat est chiffré, et un contrôle `Cnn` la re-vérifie à chaque exécution | aucune valeur publique n'est produite par ce calcul |
| **DÉCLARÉE** | la valeur vient d'une source publique ; le module en vérifie la **cohérence** (unités, clôtures, intervalles), pas la valeur elle-même | aucun mérite d'auteur pour ce nombre |
| **LIGNÉE** | le nom figure dans la filiation intellectuelle ; **aucune des 18 équations ne repose sur lui** | ce n'est pas une revendication de paternité d'un résultat chiffré |
| **POSÉE HORS MATRICE** | l'énoncé est déclaré comme source de la régularité ; il n'entre dans aucun calcul et porte `nombres_fournis_par_l_axiome = 0` | aucune équation ne le prouve, aucune mesure ne le confirme ni ne l'infirmé |

## 2. Ce que la vidéo a fourni — et ce qu'elle n'a pas fourni

Mesure reproductible avec `scripts/extraire_chapitres_youtube.py` (Skill
`extraire-chapitres-youtube-sans-transcript`). Sortie verbatim, consignée dans
`fondation_base.SOURCE` et reprise dans `artefacts/base.json` :

```
titre            : Le CERN a Enfin Détecté un Événement que la Science Attendait depuis 40 Ans
chaine           : Nocturne
id               : 5pP1e69T3HQ
url              : https://www.youtube.com/watch?v=5pP1e69T3HQ
duree_s          : 8018
chapitres_publics: 0
transcript       : absent — timedtext 0 octet en json3, srv3 et xml
description      : 1908 caractères mesurés, deux premiers paragraphes recopiés mot pour mot
mesure_le        : 2026-11-09T01:44:02Z (revérifiée 2026-11-09T01:55:04Z : mêmes valeurs)
```

Avertissements renvoyés par la sonde, repris tels quels :

```
aucun en-tete de chapitres : horodatages pris dans toute la description
aucun chapitre horodate dans la description
timedtext repond sans contenu : le transcript est tenu pour absent
```

Cette vidéo n'a **aucun chapitre horodaté** et **aucune transcription accessible** : le
dossier ne peut donc pas lui rattacher un minutage. À la place, `SOURCE["extraits_description"]
` contient dix passages de la **description**, et `C04` (`discipline_sources()`) vérifie à
chaque exécution que chacun est bien une sous-chaîne du texte mesuré, et que la page ne rend
**aucun** horodatage citable :

| Extrait (sous-chaîne de la description mesurée) | Équation qui le prend en charge |
|---|---|
| « En septembre 2024, l'expérience NA62 du CERN a annoncé l'observation » | EQ-13 |
| « un kaon chargé qui se transforme en un pion et deux neutrinos invisibles » | EQ-08 |
| « suivre des centaines de millions de particules par seconde » | EQ-16 |
| « écarter des milliards de désintégrations ordinaires qui lui ressemblent » | EQ-08, EQ-15 |
| « franchir le seuil des cinq sigma » | EQ-12 |
| « la découverte du kaon dans les rayons cosmiques des années 1940 » | EQ-02 (racine externe) |
| « le modèle standard rend cette désintégration presque impossible » | EQ-06, EQ-10 |
| « les expériences de Brookhaven n'en ont capté que quelques événements en deux décennies » | EQ-17 |
| « en étudiant les kaons en plein vol » | EQ-16 |
| « ce que ce résultat nous apprend sur la physique au-delà du modèle standard » | EQ-18 |

**Conséquence, appliquée sans exception** : la vidéo a fourni un *thème* et une *formulation*.
Elle n'a fourni **aucun chiffre, aucune citation, aucun minutage, aucune méthode**. Aucun
nombre de ce dossier ne vient d'elle : les dix-huit grandeurs du registre viennent des
quatre publications et communiqués listés au §4. Les remerciements, appels à s'abonner et la
liste de sources de la description sont écartés du texte retenu, et la chaîne elle-même donne
ses deux sources principales — arXiv:2103.15389 et arXiv:2605.02415 — qui sont deux des
quatre comparateurs publics du dossier.

## 3. Table des 18 équations

| EQ | Ce qui est calculé | Prédécesseur | Statut |
|---|---|---|---|
| 01 | L'axiome est posé et son effet est borné : zéro nombre fourni, une seule interdiction (ne pas déclarer deux fois la même grandeur avec deux valeurs) | — (énoncé de l'auteur, voir `AXIOME.auteur`) | POSÉE HORS MATRICE |
| 02 | Tout nœud sans prédécesseur interne est fondé sur une source déclarée hors du dossier : 1 racine, 18 aretes vers l'extérieur | — (structure du dossier) | CALCULÉE |
| 03 | Le graphe `NOEUDS` est un DAG : acyclique, 18 nœuds atteignables, zéro auto-référence, tri topologique de Kahn | Kahn (1962) pour l'algorithme de tri | CALCULÉE |
| 04 | Discipline de source : chaque nombre a une source publique, douze cases pilier × couche sont habitées, les dix extraits de la description sont des sous-chaînes du texte mesuré, 0 horodatage prêté à la chaîne Nocturne | Nocturne (5pP1e69T3HQ) — thème seulement | CALCULÉE |
| 05 | Transmission : `imports ⊆ stdlib ∪ locaux`, ici et dans les cinq modules principaux du parc (tiers : aucun) | — (contrainte d'outillage) | CALCULÉE |
| 06 | Registre des grandeurs : 14 entrées, 14 noms uniques, 0 doublon en conflit, unités non vides partout, `hors_declare = []` | Buras et al. (2015) ; NA62 (2021, 2024, 2026) ; home.cern (2024) | CALCULÉE (le registre) / DÉCLARÉE (les valeurs) |
| 07 | La fonction de prédiction ne reçoit aucune clé du comparateur : `signature(prediction_gel) = ['declares']`, et le drapeau `a_lu_le_comparateur` se lève dès qu'une clé interdite entre | — (pratique de l'analyse en aveugle, telle que NA62 la déclare pour sa propre analyse) | CALCULÉE |
| 08 | Nombre de désintégrations ordinaires par désintégration rare : `1/BR − 1` ; SM `1.19048e+10 ∈ [1.06383e+10, 1.35135e+10]`, et le communiqué arrondi `9 999 999 999` donne un taux implicite de `1e-10` | communiqué home.cern 2024-09-25 (« the other 9 999 999 999 decays ») | DÉCLARÉE / CALCULÉE (l'intervalle) |
| 09 | Clôture de l'acceptance : `A·ε = N_signal/(N_K × BR_SM)` ; 4,4144 % (2016-18) contre 4,1377 % (2021-22), `N` recalculé 10,0119 contre 10,01 publié (écart 0,0192 %) | NA62 2021 (arXiv:2103.15389) | DÉCLARÉE (les trois publiés) / CALCULÉE (la fermeture) |
| 10 | Prédiction gelée : `N_signal 2016-18 = 10,0119` contre `12,97` publié, écart `+0,7166 σ` | NA62 2021 (arXiv:2103.15389) | CALCULÉE / DÉCLARÉE (l'incertitude du comparateur) |
| 11 | Signification Li–Ma 2021 : 3,9852 σ contre 3,3975 σ publié (écart +0,5877), les deux sous 5 σ | Li et Ma (1981, ApJ 272, 317) | CALCULÉE / DÉCLARÉE (le fond publié) |
| 12 | Seuil communautaire : événements requis `25,0624` contre `33,00` publié, marge 7,9376 | — (convention des cinq sigma, déclarée par la communauté) | DÉCLARÉE (le seuil) / CALCULÉE (l'arithmétique) |
| 13 | Confrontation 2024 : notre `z` par addition en quadrature `∈ [1,3340, 1,4546]` contre le `1,7` déclaré par NA62 — les intervalles à un sigma **ne se recouvrent pas** | NA62 2024 (arXiv:2412.12015, JHEP 02 (2025) 191) | CALCULÉE (la quadrature, hypothèse nôtre) / DÉCLARÉE (le 1,7) |
| 14 | Confrontation 2026 : `BR 9,6e-11`, notre `z = 0,5589` (branche basse 0,5828) — sous 1 σ | NA62 2026 (arXiv:2605.02415, MPP-2026-83) — prépublication | DÉCLARÉE / CALCULÉE |
| 15 | Budget de fond : réjection requise `3,841e+11` contre la chaîne annoncée μ × π⁰ `1e+15` — marge `+3,416` ordres de grandeur | NA62 2026 (ordres de grandeur de réjection) | DÉCLARÉE (les facteurs) / CALCULÉE (le quotient) |
| 16 | Géométrie du faisceau : `0,0004753`, soit un kaon sur 2 104 produits à `6e+07` K⁺/s | home.cern 2024-09-25 (le communiqué ne donne ni temps mort ni acceptance du faisceau) | SIMULÉ |
| 17 | Loi en `√N` : gain prévu `1,5951` contre gain mesuré `1,4866` (rapport 0,9320) ; incertitudes relatives 2021 `0,3448` vs `0,3774`, 2024 `0,2164` vs `0,2538` | de Moivre, Laplace, Poisson (1837) pour les lois de comptage | CALCULÉE / DÉCLARÉE (les incertitudes publiées) |
| 18 | Limite de la base : cinq conditions de chute et quatre choses non prouvées, écrites noir sur blanc | — (auto-contrainte du dossier) | SPÉCIFIÉ |

**Noms de lignée pure**, sans aucune équation qui repose sur eux : **Rochester et Butler
(1947)** pour la découverte des rayons cosmiques à particule V (la vidéo parle des années
1940 ; aucun nombre de ce dossier n'en vient), **Gell-Mann et Nishijima (1953)** pour
l'étrangeté, **Glashow, Iliopoulos et Maiani (1970)** et **Gaillard et Lee (1976)** pour la
théorie de la désintégration — le dossier ne lit pas leurs articles, il lit la valeur `8,4 ×
10⁻¹¹` que la revue de 2015 en déduit. **Aucun chiffre de Brookhaven n'entre ici** : la vidéo
évoque « quelques événements en deux décennies », nous n'avons pas revérifié leurs
publications, donc nous n'en citons aucun nombre. Les retirer tous ne changerait un seul de
nos résultats : c'est précisément le critère du statut.

## 4. Où sont les valeurs déclarées

Les quatorze grandeurs du registre, avec leur source, telles que `registre_grandeurs()` les
rend (aucune sans unité, aucune non numérique, aucun doublon en conflit) :

| Grandeur | Valeur | Unité | Source |
|---|---|---|---|
| `BR_sm` | 8,4e-11 | 1 | Buras et al., JHEP 11 (2015) 33 — arXiv:1503.02693 |
| `dBR_sm` | 1,0e-11 | 1 | même source |
| `N_K_2016_2018` | 2,7e12 | désintégrations | arXiv:2103.15389 |
| `SES_2016_2018` | 0,839e-11 | 1 | arXiv:2103.15389 |
| `N_K_2021_2022` | 2,85e12 | désintégrations | arXiv:2412.12015 |
| `SES_2021_2022` | 8,48e-12 | 1 | arXiv:2412.12015 |
| `secondaires_par_s` | 1,0e9 | 1/s | home.cern 2024-09-25 |
| `fraction_K_plus` | 0,06 | 1 | home.cern 2024-09-25 |
| `annees_prises_2016_2018` | 3,0 | an | arXiv:2103.15389 |
| `rejection_mu` | 1,0e7 | 1 | arXiv:2605.02415 — ordre de grandeur |
| `rejection_pi0` | 1,0e8 | 1 | arXiv:2605.02415 — ordre de grandeur |
| `rejection_autres_canaux` | 1,0e4 | 1 | arXiv:2605.02415 — ordre de grandeur |
| `seuil_observation` | 5,0 | sigma | déclaré par la communauté |
| `z_declare_2024` | 1,7 | sigma | arXiv:2412.12015 |

Les comparateurs publics (lus **après** le gel de la prédiction, digest `242389d1…`) sont dans
`artefacts/gel.json` : `NA62_2021` (20 candidats, fond 7,03, BR 1,06e-10, « evidence à 3,4
sigma »), `NA62_2024` (51 candidats, fond 18,0, BR 1,3e-10, « observation au-delà de 5
sigma »), `NA62_2026` (BR 2016-2024 9,6e-11, « accord avec le modèle standard à moins de 1
sigma ») et `CERN_2024`.

## 5. Ce que la base ajoute au parc

Les quatre piliers ne valent pas seulement ici : `OUTILS/audit_piliers.py` les applique à
tous les modules d'équations du dépôt. À l'issue de cette application, l'audit `--tous
--rigide` rend **CONFORME** sur les cinq modules, soit **89 équations et 89 contrôles**
(ABONDANCE 54, CHIFFRES 17, FONDATION 18) :

```
FONDATION\fondation_base.py            — 18 équations, 18 contrôles — CONFORME
CHIFFRES\chiffres_pi.py                — 17 équations, 17 contrôles — CONFORME
ABONDANCE\electricite_abondance.py     — 21 équations, 21 contrôles — CONFORME
ABONDANCE\eau_abondance.py             — 15 équations, 15 contrôles — CONFORME
ABONDANCE\agriculture_abondance.py     — 18 équations, 18 contrôles — CONFORME
```

Le travail effectif a porté sur P2 BORNE : 11 équations de CHIFFRES et les 54 d'ABONDANCE ne
portaient pas de clause de limite au niveau de l'équation. Elles en portent une aujourd'hui,
écrite pour chacune, jamais revalidée par copier-coller. Un pilier devient exigeant quand il
coûte des phrases, pas quand il est annoncé.

## 6. Limites — ce que ce dossier ne revendique pas

1. **Aucune preuve d'aucune physique.** Ce dossier calcule l'arithmétique de comptage d'une
   expérience publique. Il ne dérive pas le modèle standard, ne propose aucun mécanisme
   au-delà, et ne tranche pas la question ouverte par NA62 elle-même.
2. **La prédiction gelée n'est pas une mesure.** `EQ-10` confronte 10,0119 à 12,97 publié ;
   l'écart `+0,7166 σ` est un accord, pas une découverte, et notre incertitude est celle que
   NA62 déclare — nous ne reconstruisons pas sa vraisemblance.
3. **Le désaccord 2024 est nôtre autant que le leur.** `EQ-13` fait une hypothèse déclarée
   (addition en quadrature) que NA62 ne fait pas ; les intervalles à un sigma ne se
   recouvrent pas, et ce fait est un contrôle de méthode, pas une critique de leur résultat.
4. **`EQ-16` est SIMULÉ.** La fraction d'un kaon sur 2 104 est bornée inférieurement : tout
   temps mort réel la rend plus grande, et le communiqué ne donne ni le temps utile ni
   l'acceptance du faisceau.
5. **`arXiv:2605.02415` est une prépublication.** `EQ-14` et `EQ-15` peuvent bouger ; le
   dossier l'écrit dans la limite de ces deux équations.
6. **L'axiome ne prouve rien.** `EQ-01` porte `nombres_fournis_par_l_axiome = 0` : aucun
   nombre du dossier n'a l'axiome pour source. Il interdit seulement de déclarer deux fois la
   même grandeur avec deux valeurs — ce que le registre vérifie (`0` doublon en conflit).
7. **La validation Monte-Carlo teste l'arithmétique, pas le détecteur.**
   `SIMULATIONS/simuler_kaons.py` rend cinq verdicts verts (V1 à V5) sur des lois de comptage
   à fond connu ; un désaccord de 5 écarts-types invaliderait la validation, pas la nature.

## 7. Comment revérifier

```bash
cd ZENODO_DEPOT_ALMIZAN
py -3 FONDATION/fondation_base.py                     # 18/18 contrôles, rc=0
py -3 -m unittest FONDATION.tests.test_fondation      # 45 tests, OK
py -3 FONDATION/OUTILS/audit_piliers.py --tous --rigide   # 5 modules CONFORME, rc=0
py -3 FONDATION/SIMULATIONS/simuler_kaons.py          # V1..V5 verts, rc=0
```

`fondation_base.py` n'écrit ses artefacts que sur demande explicite (`--ecrit`) ; sans
l'option, il rend le verdict complet sur la sortie standard. Aucun import tiers : la stdlib
seule (`__future__`, `hashlib`, `inspect`, `json`, `math`, `pathlib`, `re`, `sys`, `typing`).

**Fins de ligne.** Le dépôt normalise les blobs en LF (`core.autocrlf=true`) : l'archive
Zenodo contient la variante LF. Les empreintes du manifeste sont calculées sur le blob
(`git cat-file blob HEAD:CHEMIN | sha256sum`), pas sur le fichier de l'arborescence de travail.
