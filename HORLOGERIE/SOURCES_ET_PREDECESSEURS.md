# SOURCES ET PRÉDÉCESSEURS — dossier HORLOGERIE

**Licence** : GPL-3.0-only OR AGPL-3.0-only (double licence, voir `LICENSE.md` à la racine du dépôt).

**Auteur** : M. Ahmed EL BAHLOUL (IMAM8MAHDI) — développement assisté par IA générative,
résultats relus et dirigés par l'auteur humain.

**Périmètre** : `horlogerie.py` (15 équations, 15 contrôles, certificat à six sous-scellés),
`verifier_certificats.py` (16 contrôles V01–V16, zéro import du dépôt),
`calibrer_horloge_almizan.py` (mesure τ = T/N), `laboratoire.py` (5 contrôles L01–L05 :
trajectoire entière x+y+z−k·dt, repère à quatorze coordonnées, écart-type d'Allan),
`tests/test_horlogerie.py` et `tests/test_laboratoire.py` (64 tests au total).
Artefacts : `artefacts/certificats.json` (19 159 o) et
`artefacts/confrontation_astronomique.csv` (823 o, UTF-8 BOM, `;`, CRLF, virgule), plus les
quatre livrables du laboratoire — `laboratoire.json` (7 147 o),
`trajectoire_laboratoire.csv` (34 165 o), `stabilite_laboratoire.csv` (331 o) et
`trajectoire_laboratoire.svg` (18 775 o) — même format Excel français, et aucun nombre d'hôte.

Le dossier répond à une objection adressée à AL-MIZAN le 2026-11-09 :

> « dx + dy + dz = dt est arithmétiquement exact, mais 365,25 / 354 / 360 jours ne sont pas des
> périodes astronomiques mesurées ; et écrire dt ≈ 135 097 021,3359375 Hz suppose une période de
> 7,4 ns que la machine ne respecte pas. »

Il ne cherchait pas à réfuter l'objection. Il cherchait à ce que **n'importe qui** puisse
trancher sans nous croire : c'est le contenu exact des deux fichiers `horlogerie.py` et
`verifier_certificats.py`, et le sens des verdicts ci-dessous est laissé tel qu'il tombe.

## 1. Règle d'attribution — quatre statuts

| Statut | Ce que ça veut dire | Ce que ça ne veut pas dire |
|---|---|---|
| **CALCULÉE** | le nombre sort des seules semences du dépôt par une formule écrite dans `horlogerie.py`, et un contrôle `Cnn` le re-vérifie en entiers | aucune portée physique : rien ici n'affirme qu'AL-MIZAN prédit une période du ciel |
| **DÉCLARÉE** | la valeur vient d'une source publique nommée ; le certificat en vérifie l'**accord avec sa propre décimale citée** (V16), pas la justesse astronomique | aucun mérite d'auteur pour ces éphémérides |
| **MESURÉE** | τ = T/N sort de `calibrer_horloge_almizan.py` sur la machine de qui l'exécute ; il est explicitement **hors scellement** | aucune constante : la valeur change d'un ordinateur à l'autre, et c'est précisément l'argument |
| **LIGNÉE** | le nom figure dans la filiation intellectuelle du dossier ; **aucun des 15 EQ n'en dépend pour un chiffre** | pas une revendication de paternité d'un résultat chiffré |

## 2. Ce que la vidéo a fourni — et ce qu'elle n'a pas fourni

Mesure reproductible avec `scripts/extraire_chapitres_youtube.py` (Skill
`extraire-chapitres-youtube-sans-transcript`). Sortie verbatim, consignée dans
`horlogerie.SOURCE` et reprise dans `artefacts/certificats.json → attribution` :

```
titre            : AI Proved His 18-Year-Old Conjecture. He Hasn't Understood It Yet.
chaine           : Adem B10
id               : qa8IsnneG0c
url              : https://www.youtube.com/watch?v=qa8IsnneG0c
duree_s          : 593
chapitres_publics: 8
transcript       : absent — timedtext 0 octet en json3, srv3 et xml
mesure_le        : 2026-11-09T15:32:44Z
```

Avertissements renvoyés par la sonde, repris tels quels :

```
aucun en-tete de chapitres : horodatages pris dans toute la description
timedtext repond sans contenu : le transcript est tenu pour absent
```

Les huit chapitres, recopiés mot pour mot (dernier : 8:58 ≤ 9:53, horodatages strictement
croissants) :

| Début | Titre verbatim |
|---|---|
| 0:00 | "I believe the proof is correct" |
| 1:08 | Cups, looks and a quantum computer |
| 2:15 | The dial and the switch that matters |
| 3:23 | The 2019 proof that failed |
| 3:58 | Reason one: the Lean certificate |
| 5:12 | Reason two: the humans |
| 6:12 | Is quantum supremacy dead? |
| 8:58 | How Aaronson feels |

**Ce que la vidéo n'a pas fourni** — et que ce dossier ne lui prête donc pas :

- aucun transcript : donc **aucune citation**, aucune phrase attribuée à la bande-son ;
- aucun nombre : ni borne, ni délai, ni taux de réussite d'une preuve automatique ;
- aucune mention d'AL-MIZAN, que la vidéo ne nomme pas.

**Ce qui en vient** est une seule décision de forme, énoncée dans `SOURCE` comme étant d'ici :
séparer celui qui produit la preuve de celui qui la vérifie. D'où deux fichiers, et un
vérificateur qui n'importe **aucun** module du dépôt (`imports_de` le prouve : `autres: []`).

## 3. Les six références du ciel, et ce qu'elles engagent

Chacune porte `jours` (fraction exacte utilisée dans le calcul) et `decite` (la décimale telle
que l'écrit la source). V16 et C15 exigent que les deux tombent d'accord, en entiers.

| id | jours | decite | nature | source |
|---|---|---|---|---|
| `annee_julienne` | 1461/4 | 365,25 | définition exacte | UAI, Résolution B2 (2009) : 365,25 j = 31 557 600 s |
| `annee_tropique` | 1826211/5000 | 365,2422 | éphéméride mesurée | NASA Glenn Research Center, Planetary Fact Sheet — Earth |
| `annee_tropique_2000` | 36524219/100000 | 365,24219 | éphéméride mesurée | Wikipedia, Tropical year (jours d'éphéméride à l'équinoxe J2000) |
| `lunaison` | 2953059/100000 | 29,53059 | éphéméride mesurée | Explanatory Supplement to the Astronomical Almanac, mois synodique moyen |
| `lunaisons_12` | 8859177/25000 | 354,36708 | éphéméride mesurée | 12 × la ligne précédente |
| `annee_lunaire_civile` | 354 | 354 | convention de calendrier | année lunaire de douze mois de 29 ou 30 jours |

### Correction du 2026-11-09, écrite ici plutôt qu'effacée

La première version de ce fichier portait `lunaisons_12 = 8884173/25000`, soit **355,36692 j**,
alors que sa propre source écrit 354,36708 j. L'erreur changeait l'écart Lune-lunaisons de
−31 715,712 s/an à −118 101,888 s/an sans changer le verdict : le certificat restait cohérent
avec lui-même et incohérent avec sa citation. Elle est corrigée, et la garde est devenue un
contrôle : **C15** côté production, **V16** côté vérificateur, plus un test qui réécrit la
fraction fautive, **re-scelle le certificat**, et exige que V16 tombe quand même
(`test_la_copie_fautive_du_2026_11_09_est_refusee_meme_rescellee`). L'empreinte du gel a changé
avec la correction ; `SEUILS["correction_apportee"]` le dit dans le fichier même.

## 4. Ce que le dossier conclut — y compris quand cela ne l'arrange pas

Identité d'horloge, en entiers, relisible sans le dépôt :

```
dx = 6 403 563/128        = 50 027,8359375
dy = 93 987/2             = 46 993,5
dz = 135 000 000          (dz_brut = 3 888 000 000 ; dz_brut/dz = 144/5)
dt = dx + dy + dz = 17 292 418 731/128 = 135 097 021,3359375
gcd(17 292 418 731, 128) = 1, numérateur impair ⇒ 2^7 est le plus petit dénominateur possible
```

Verdicts astronomiques, seuils gelés **avant** lecture (≤ 60 s/an CONFORME, ≤ 3 600 s/an
ÉCART SIGNALÉ, au-delà HORS TOLÉRANCE) :

| Cycle | Pire verdict | Déclaré face à | Écarts effectifs |
|---|---|---|---|
| Soleil (365,25 j) | ÉCART SIGNALÉ | `annee_tropique` | +673,92 s/an (tropique), +674,784 s/an (J2000), 0 contre l'année julienne |
| Lune (354 j) | HORS TOLÉRANCE | `lunaisons_12` | −31 715,712 s/an (≈ 8 h 49 min), −971 326,08 s/an contre l'année tropique |
| Terre (360 j) | HORS TOLÉRANCE | `annee_julienne` | −453 600 s/an (julienne), −452 926,08 s/an (tropique), +486 684,288 s/an (lunaisons) |

`face_a` est la première paire au pire verdict, à égalité de sévérité : pour la Terre, le plus
grand écart sur éphéméride **mesurée** est +486 684,288 s/an (douze lunaisons), et c'est ce
nombre que le certificat publie sous `ecart_max_s`.

Sur les **six** comparaisons à une éphéméride mesurée, aucune ne passe sous les 60 s/an. En
revanche 365,25 j tombe exactement sur l'année julienne (définition de l'UAI) et 354 j
exactement sur l'année lunaire civile : **ce sont des calendriers, pas des mesures.** La
sensibilité testée sous 29,530588 d ne change aucun verdict.

Lecture de l'unité, séparée en trois énoncés que le fichier ne confond jamais :

1. `dt = 17 292 418 731/128` — **exact**, indépendant de tout ordinateur ;
2. `1/dt = 7,40208770046351475896… ns` sur 40 rangs — conséquence **conditionnelle** de
   l'hypothèse « dt est une fréquence », statut SPÉCIFIÉ ;
3. τ mesuré ici = **941,9 ns/tick** (min 878,54, max 1 416,18, écart absolu médian 27,08 ;
   5 séries de 5 000 ticks, Python 3.14.7, Windows 11) — soit ≈ 127 × la période de 2. La
   machine d'un contradicteur a rendu ≈ 420 ns/tick : la grandeur change du simple au double
   selon l'hôte, donc ce n'est pas une fréquence. **Une constante physique ne change pas d'un
   ordinateur à l'autre ; le temps par tick, si.**

Unité retenue dans le certificat : **cycle logique** (`budget de comptes` adimensionnel), et
`resultats/run_cycle_solaire_lunaire_terrestre_*.json → pulsation_dt_hz` est relevé comme un
champ nommé « hz » rempli par la constante du noyau, non par un compteur de cycles par seconde.

## 5. prédécesseurs dans le dépôt — ce que ce dossier lit, sans rien écrire

| Fichier | Ce qu'il donne | Ce que HORLOGERIE en fait |
|---|---|---|
| `bibliotheques/lib_temporelle.py` | `CLOCK_DX_SOLEIL`, `CLOCK_DY_LUNE`, `CLOCK_DZ_TERRE`, `CLOCK_DZ_TERRE_BRUT`, `CLOCK_DT_KERNEL`, `HorlogeKernelTemporelle.consommer_tick` | les cinq constantes sont recalculées en rationnels et comparées bit à bit (C13) ; le tick sert d'objet de mesure (C12) |
| `bibliotheques/lib_informe.py` | `_SEMENCES_ASTRES`, `produit_quatre_niveaux`, `calculer_cycles_trinite_depuis_zero()` | les douze semences sont relues par nom de clé, la formule est **réécrite** dans le vérificateur au lieu d'être importée |
| `horloge_noyau/actes/almizan_acte_a134_*.json`, `..._a136_*.json` | les chaînes « ≈ … Hz » et `constantes_deduites` | citées verbatim dans `unites.lectures_rencontrees`, en **lecture seule** : la capsule `horloge_noyau/` n'est jamais modifiée |
| `FONDATION/OUTILS/audit_piliers.py` | la grammaire des quatre piliers | appliquée à `HORLOGERIE/horlogerie.py` : 15/15 équations, 15/15 contrôles, CONFORME sous `--rigide` |

## 6. Utilisation

```bash
cd ZENODO_DEPOT_ALMIZAN

# 1. produire le certificat et ses artefacts (rc=0 si les 15 contrôles sont verts)
PYTHONIOENCODING=utf-8 py -3 HORLOGERIE/horlogerie.py --ecrit

# 2. le relire SANS faire confiance à celui qui l'a produit
PYTHONIOENCODING=utf-8 py -3 HORLOGERIE/verifier_certificats.py
PYTHONIOENCODING=utf-8 py -3 HORLOGERIE/verifier_certificats.py --importes   # autres: []

# 3. mesurer τ = T/N sur SA machine (hors scellement, jamais dans le certificat)
PYTHONIOENCODING=utf-8 py -3 HORLOGERIE/calibrer_horloge_almizan.py --ticks 10000 --series 7
PYTHONIOENCODING=utf-8 py -3 HORLOGERIE/calibrer_horloge_almizan.py --ticks 10000 --series 7 \
    --sortie calibrage_almizan.csv

# 4. faire tourner le laboratoire : trajectoire, repère, stabilité, écran en direct
PYTHONIOENCODING=utf-8 py -3 HORLOGERIE/laboratoire.py --pas 4096
PYTHONIOENCODING=utf-8 py -3 HORLOGERIE/laboratoire.py --en-direct --secondes 20 --ticks 50000
PYTHONIOENCODING=utf-8 py -3 HORLOGERIE/laboratoire.py --ecrit        # les quatre livrables

# 5. rejouer les 64 tests du dossier, puis l'audit des piliers
PYTHONIOENCODING=utf-8 py -3 -m unittest HORLOGERIE.tests.test_horlogerie -v
PYTHONIOENCODING=utf-8 py -3 -m unittest HORLOGERIE.tests.test_laboratoire -v
PYTHONIOENCODING=utf-8 py -3 FONDATION/OUTILS/audit_piliers.py HORLOGERIE/horlogerie.py --rigide
```

Codes de sortie : `horlogerie.py` 0 si tous les contrôles sont verts, 1 sinon ;
`verifier_certificats.py` 0 conforme, 1 non conforme ou fichier illisible, 2 usage invalide ;
`calibrer_horloge_almizan.py` refuse `--ticks < 100` ou `--series < 3` avec rc=2 ;
`laboratoire.py` 0 sur « LABORATOIRE CONFORME », 1 si un contrôle L01–L05 tombe.

## 7. Limites du dossier

1. le certificat porte l'arithmétique des nombres **déclarés**, jamais leur valeur de prévision ;
2. les semences (8766 h, 8496 h, 8640 h) viennent du dépôt : le certificat montre qu'elles
   produisent exactement les constantes publiées, pas qu'elles décrivent le ciel ;
3. les références astronomiques sont des valeurs publiques **moyennes** ; rien n'est recalculé
   depuis une éphéméride du jour, et les écarts ne prédisent aucune date réelle ;
4. le rythme d'exécution est absent du fichier scellé — il dépend de la machine, et sa
   faiblesse (changer d'hôte) est l'argument qui écarte la lecture en hertz, pas une preuve
   d'horlogerie ;
5. la vidéo `qa8IsnneG0c` n'a fourni que ses huit titres horodatés : aucun chiffre, aucune
   citation, aucun résultat d'aucune preuve formelle (Lean, Coq, autre) n'est repris d'elle.
