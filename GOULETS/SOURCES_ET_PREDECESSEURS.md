# SOURCES ET PRÉDÉCESSEURS — dossier GOULETS

**Licence** : GPL-3.0-only OR AGPL-3.0-only (double licence, voir `LICENSE.md` à la racine du dépôt).

**Auteur** : M. Ahmed EL BAHLOUL (IMAM8MAHDI) — développement assisté par IA générative,
résultats relus et dirigés par l'auteur humain.

**Périmètre** : `goulets_base.py` (10 équations EQ-01…EQ-10, 10 contrôles C01…C10, certificat à
racine Merkle), `tests/test_goulets.py`, six fichiers dans `sources/` tableés par
`sources/EMPREINTES.json`. Artefacts dans `artefacts/` : `certificat.json`, `cadence.csv`,
`bornes.csv`, `figures/bornes.svg` — les deux CSV en UTF-8 BOM, séparateur `;`, CRLF, virgule
décimale.

**Le module n'appelle aucun réseau et ne publie rien.** Il relit six instantanés pris le
2026-11-10 (date UTC) et en recalcule les bornes, en bibliothèque standard seule.

## 1. La demande, et ce qui l'a remplacée

La demande consignée était : « étudier et poser les équations pour résoudre les goulots
d'étranglement et être inarrêtable ». Le mot « inarrêtable » n'a pas de définition falsifiable :
il n'est repris nulle part comme revendication. Il est remplacé par quatre bornes datées,
chacune avec la condition qui la rompt (table complète dans `artefacts/bornes.csv`) :

| Borne | Valeur consignée | Nature | Rompue si |
|---|---|---|---|
| durée par vidéo | 900 s | déclaré (seuil attaché au verrou du compte) | une vidéo publiée dépasse 900 s |
| capacité de publication | 99 publications/jour | déclaré (barème : 10 000 unités, 101 unités par publication, 100 appels d'expédition) | le fournisseur modifie son barème ou son allocation projet |
| plafond réellement observé | 10 publications/jour | mesuré (jour le plus haut, avec refus ce jour-là) | un jour publie davantage sans refus, ou le plafond est relevé |
| marge matérielle | 436 vidéos du gabarit moyen | mesuré (instantané d'hôte, propre à cette machine) | l'espace libre descend sous un gabarit moyen |

À ces quatre bornes s'ajoute la cadence tenue : 1,352941 publication par jour
(23 vidéos sur 17 jours d'emprise, fuseau du Pacifique), soit 13,5 % du plafond observé et
1,4 % de la capacité déclarée. Le dossier consigne ce rapport ; il n'en déduit aucune recette
d'audience et n'affirme pas que la chaîne est arrêtable ou inarrêtable.

## 2. Les six instantanés, et d'où vient chacun

| Fichier | Provenance | Ce qu'il nourrit |
|---|---|---|
| `sources/youtube.json` | `channels.list(mine=True)` puis `playlistItems.list` sur la playlist d'expédition, puis `videos.list` par paquets de 50 — lecture seule | EQ-02, EQ-03, EQ-04, EQ-08, C02…C04, C08 |
| `sources/quotas_declares.json` | texte publié du barème de coûts, recopié verbatim le jour de la prise | EQ-05, C05 |
| `sources/plafond_chaine.json` | lignes du journal local de l'opérateur portant la raison renvoyée par l'API, rapprochées des publications lues sur la chaîne | EQ-06, C06 |
| `sources/backlog_local.json` | fichiers `.mp4` de trois dossiers locaux : taille par `stat()`, durée lue dans la boîte `mvhd` en remontant l'arborescence des boîtes | EQ-09, C09 |
| `sources/disque.json` | `GetDiskFreeSpaceExW` sur le lecteur de production, instantané propre à cet hôte | EQ-09, C10 |
| `sources/video_source.json` | oEmbed de la vidéo qui a donné le thème : titre, auteur, durée, horodatages de la description | `video_source` du certificat |
| `sources/EMPREINTES.json` | table dressée à la capture : SHA-256 de chaque fichier, puis racine sur la concaténation triée « nom + empreinte » | EQ-01, C01 |

Aucun nom de fichier ne porte de date : le nom entre dans `MANIFESTE_SHA256.txt`, et le sceau du
dépôt ne doit porter aucune date — `DECLARATION/declaration_base.py → sceau_contenu() → C04`
compte les motifs `20\d\d-\d\d-\d\d` dans le texte du manifeste et rougit dès qu'un seul y
apparaît. La date de prise reste consignée à l'intérieur de chaque instantané, champ
`mesure_le_utc`, et dans `horodatage_utc` de la table d'empreintes ; le renommage du
11 novembre 2026 n'a changé ni un octet des six fichiers (SHA-256 et tailles repris tels quels
dans `EMPREINTES.json`), ni un nombre du certificat.

`git` ne doit pas retoucher les fins de ligne de ces fichiers : `.gitattributes` verrouille
`GOULETS/sources/*.json` en `eol=lf`, faute de quoi un clone
Windows hacherait des octets différents et C01 rougirait pour une raison absente des données.

## 3. Ce que la prise établit — et ce qu'elle laisse ouvert

| | Établi par ces octets | Non établi |
|---|---|---|
| Verrou de durée | `longUploadsStatus = "allowed"` à la date de prise : la levée du seuil de 15 minutes est effective sur cette chaîne | qu'elle tienne encore demain : c'est un instantané, pas un état permanent |
| Barème | 1 unité par `videos.insert`, 50 par `videos.update`, 50 par `thumbnails.set`, 10 000 unités et 100 appels d'expédition par jour, réinitialisation « at midnight Pacific Time (PT) » | l'allocation réellement accordée à CE projet : le dépôt ne la lit pas, il applique le barème publié |
| Plafond effectif | 10 publications le 2026-11-10 (Pacifique), refus `uploadLimitExceeded` consigné ce jour-là ; 9,9 fois sous la capacité calculée | sa loi temporelle : un refus est consigné le 2026-11-08, jour de **zéro** publication. Un compteur qui se remet à minuit heure du Pacifique ne rend pas compte de ce jour-là. Le dossier marque `loi_temporele_etablie = False` et n'invente pas la règle |
| Fuseaux | les deux histogrammes (UTC et Pacifique) ont les mêmes comptes quotidiens et un pic à 10 ; leurs libellés de jour diffèrent de deux dates | la moindre supériorité d'un calendrier sur l'autre : c'est le fuseau que le fournisseur déclare pour sa réinitialisation qui est utilisé |
| Diffusion | 48 vues, 23 vidéos, 1 abonné à la date de prise ; rapport 48/23 = 2,086957 vues par publication | toute causalité, toute prévision, tout conseil : le rapport est un compteur, pas un indicateur de qualité |
| Matériel | 35 434 115 072 o libres sur le lecteur de production, gabarit moyen 81 269 225 o → 436 vidéos | une valeur portable : un autre hôte rend un autre chiffre, et les vidéos publiées ne libèrent pas l'espace local |

Les horodatages du journal de l'opérateur sont **locaux**, pas serveur : ils situent un refus dans
la journée du fournisseur, ils ne datent pas la réponse de l'API. Le compte de lignes du journal
n'est pas un compte de refus distincts — la même raison recopiée dans plusieurs messages d'une
même session produit plusieurs lignes. C'est écrit dans l'instantané (`avertissement`) et repris
dans la limite de EQ-06.

## 4. Règle d'attribution — quatre statuts

| Statut | Ce que ça veut dire | Ce que ça ne veut pas dire |
|---|---|---|
| **OPÉRATIONNEL** | le nombre sort d'octets publiés dans `sources/` et un contrôle le re-mesure par une écriture différente (table de bornes d'heure d'été écrite en dur, digestion par blocs, `Fraction`, entiers) | que la mesure était juste au moment de la prise : l'empreinte atteste l'octet, pas le geste |
| **SPÉCIFIÉ** | la capacité de 99 publications/jour est calculée d'après le barème publié par le fournisseur | une mesure : c'est une borne de conception, et le plafond observé est 9,9 fois plus bas |
| **SIMULÉ** | l'horizon (78 fichiers ÷ la cadence, 78 ÷ le plafond) est une projection linéaire de deux nombres mesurés | une prédiction : elle suppose λ constant et le plafond non abaissé |
| **CITÉ** | la vidéo qui a donné le thème est nommée avec son auteur, sa durée et ses chapitres | une citation : le transcript n'a pas été sondé, aucune phrase n'est reproduite ni résumée |

## 5. Filiation intellectuelle — aucune équation n'en dépend pour un chiffre

- Ralph C. Merkle, *A Digital Signature Based on a Conventional Encryption Function*, CRYPTO '87
  (1988) : la forme de l'arbre dont la racine scelle les dix nœuds d'équation.
- John D. C. Little, *A Conservation Law for a One-Sample Queueing System*, Ops. Res. 9 (1961) :
  le rapport débit / file / délai que la projection d'horizon utilise à l'envers (nombre ÷ cadence),
  sans en emprunter aucune hypothèse de stabilité.
- Uniform Time Act (1966, tel qu'amendé) et la règle civile américaine qui en découle : deuxième
  dimanche de mars, premier dimanche de novembre. Le module la réécrit lui-même, sans `tzdata`.
- Documentation publique de la YouTube Data API v3 : le barème de coûts et la réinitialisation
  « at midnight Pacific Time (PT) », recopiés verbatim dans `quotas_declares.json`.
- ISO/IEC 14496-12 (boîtes `moov`/`mvhd`) : la structure d'en-tête MP4 dont la durée est lue.

Aucun de ces travaux ne fonde un chiffre d'AL-MIZAN, et aucun chiffre de ce dossier ne leur est
attribué comme résultat : ils disent d'où viennent les formes de calcul.

## 6. Ce que ce dossier ne dit pas

1. Il ne revendique pas l'inarrêtabilité : le mot n'apparaît que comme citation de la demande, et
   le test le vérifie champ par champ dans le certificat.
2. Il n'établit pas la loi temporelle du plafond : un jour de refus à zéro publication contredit
   l'hypothèse d'un compteur remis à minuit, et le dossier le consigne plutôt que de l'expliquer.
3. Il ne prouve rien sur AL-MIZAN : `predictions_al_mizan_testees = 0`.
4. Il n'appelle pas le réseau : `reseau_appelle_par_ce_module = False` ; ni `urllib`, ni `socket`,
   ni `googleapiclient`, ni `ctypes` dans le module (contrôlé par AST dans les tests) — la capture
   a été faite hors dépôt, puis gelée dans `sources/`.
5. Il ne consigne aucun jeton : `jetons_consignes = 0` ; les instantanés ne portent que des
   compteurs publics, des durées, des identifiants publics et des dates. Aucun chemin d'hôte
   n'est écrit dans ce qui est publié.
6. Il ne donne aucune recette d'audience et ne promet aucune croissance.
7. Il ne titre aucune preuve : le vocabulaire « prouvé / démontré / certifié / garanti /
   universel / 100 % » est absent du certificat, et le test le vérifie chaîne par chaîne.

## 7. Relancer

```bash
cd ZENODO_DEPOT_ALMIZAN
py -3 -B GOULETS/goulets_base.py                    # attendu : CONTROLES 10/10
py -3 -B GOULETS/goulets_base.py --ecrit --json     # + certificat.json, CSV et SVG
py -3 -m unittest GOULETS.tests.test_goulets -v     # suites de relecture et de non-vacuité
py -3 -B FONDATION/OUTILS/audit_piliers.py GOULETS/goulets_base.py   # attendu : CONFORME
```

Le module est déterministe : deux relances rendent la même racine Merkle, et la table
`sources/EMPREINTES.json` refuse tout fichier hors table. Pour re-prendre les instants, il faut
un hôte YouTube, les quatre dossiers locaux et le journal de session de l'opérateur : rien de
cela n'est dans le dépôt, et c'est volontaire.
