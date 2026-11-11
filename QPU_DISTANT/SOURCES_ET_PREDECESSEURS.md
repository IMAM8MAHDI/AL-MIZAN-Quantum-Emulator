# SOURCES ET PRÉDÉCESSEURS — dossier QPU_DISTANT

**Licence** : GPL-3.0-only OR AGPL-3.0-only (double licence, voir `LICENSE.md` à la racine du dépôt).

**Auteur** : M. Ahmed EL BAHLOUL (IMAM8MAHDI) — développement assisté par IA générative,
résultats relus et dirigés par l'auteur humain.

**Périmètre** : `qpu_distant_base.py` (10 équations EQ-01…EQ-10, 10 contrôles C01…C10,
certificat à racine Merkle), `tests/test_qpu_distant.py` (28 tests), six fichiers dans
`sources/` dont cinq publiés et tableés par `sources/EMPREINTES.json`. Artefacts :
`artefacts/certificat.json` (11 922 o), `artefacts/compteurs.csv` (87 o),
`artefacts/frontieres.csv` (350 o), `artefacts/figures/frontieres.svg` (1 533 o) — les deux CSV
en UTF-8 BOM, séparateur `;`, CRLF, virgule décimale.

**Le module n'appelle aucun réseau et n'exécute aucun qubit.** Il relit, en bibliothèque
standard seule, un job déjà rendu par IBM Quantum le 2026-11-10, et en recalcule les nombres.

## 1. Ce que ce dossier établit — et ce qu'il laisse ouvert

| | Établi | Non établi |
|---|---|---|
| Donnée | 256 tirages d'un circuit à 2 bits sur `ibm_marrakesh`, recomptés depuis le `BitArray` publié : `00`=126, `01`=22, `10`=0, `11`=108 | la moindre généralisation : une exécution, une paire de qubits |
| Parité | p = 234/256 = 0,9140625, σ de tirage 0,01751698351040244 | que p vaille pour un autre circuit |
| Asymétrie | `01` contre `10` : test exact conditionné à 22, valeur p = 2·(½)²² = 4,76837158203125e-07 | l'origine physique de cette asymétrie |
| Bornes | deux enveloppes `1 − 2·Σε` : 0,9114309996674055 (support réel, reçue) et 0,9258965410524731 (médiane machine, non reçue) | un modèle de bruit : l'inégalité triangulaire ne simule pas le bruit corrélé |
| Statut | `qubit_physique_local = False` reste **faux** : ce tirage n'a rien exécuté ici | rien sur AL-MIZAN : 0 prédiction d'AL-MIZAN testée par ce dossier |

Les deux enveloppes ne sont jamais fusionnées. Le verdict de la médiane machine — non reçu, à
−0,6755752807237312 σ — est écrit tel quel : cette exécution-là l'aurait falsifiée.

## 2. Chaîne de reproduction, et ce qu'elle ne reproduit pas

```
job-dbpkmr0ou4as73ctrm80.zip (2 706 o, SHA-256 7a137a17fe6b243c…)      ATTESTÉ, non publié
   ├── info.json  →  sources/info_netoyee.json      SHA-256 ec40fe3239972cb5…  publié
   │                  (champ user_id retiré, remplacé par son préfixe d'empreinte)
   ├── result.json →  sources/result.json            SHA-256 417f4d7eabfa78e1…  publié verbatim
   └── bloc QPY (6 277 o décompressés)  →  SHA-256 fab40a5c0d459de2…
                                          lié à sources/portes_transpilees.json
```

Trois états, à ne pas confondre :

1. **Reproductible ici** : les compteurs (décodage `.npy` à la main), la parité, l'asymétrie,
   la simulation d'unité, les deux enveloppes, les deux empreintes internes (`empreinte_parc`,
   `empreinte_support`) et l'empreinte du bloc QPY, recalculée depuis `info_netoyee.json`
   par `zlib` + `base64` — sans qiskit.
2. **Attesté, non reproductible** : le SHA-256 du zip d'origine. Il est porté par le registre
   scellé, mais les fichiers publiés ne le recalculent pas : ils ignorent le `user_id` retiré.
   Le contrôle C04 compte les occurrences du motif de compte dans les fichiers publiés —
   attendu zéro, obtenu zéro.
3. **Extraction hors dépôt** : `portes_transpilees.json` (12 portes transpilées, registre de
   156 fils) a été produit par `qiskit.qpy.load` dans l'environnement d'exécution, puis écrit
   en JSON et lié à l'archive par l'empreinte du bloc QPY. Le dépôt ne rejoue pas qiskit : il
   vérifie le lien.

## 3. Les fichiers sources du dossier, et d'où ils viennent

| Fichier | Provenance | Contrôle |
|---|---|---|
| `sources/info_netoyee.json` | archive du fournisseur, champ `user_id` retiré | C01, C03, C04 |
| `sources/result.json` | membre verbatim de l'archive du fournisseur | C02, C05, C06 |
| `sources/portes_transpilees.json` | extraction qiskit hors dépôt, liée au bloc QPY | C03, C07 |
| `sources/calibration_ibm_marrakesh.json` | snapshot public du calibrage de la machine, lu en lecture seule par `ASTRO-Q°ODE_SYSTEME/constantes_ibm.py` | C09 (`empreinte_parc`), EQ-07 |
| `sources/support_ibm_marrakesh_0-1.json` | sonde en lecture seule du support 0-1 par `ASTRO-Q°ODE_SYSTEME/sonde_support_ibm.py` (0 tirage, 0 coût) | C09 (`empreinte_support`), EQ-08 |
| `sources/EMPREINTES.json` | table dressée lors de la rédaction du dossier | C01 |

Les deux snapshots portent leur propre empreinte interne, et cette empreinte se recalcule à
partir des octets publiés : la règle est celle des scripts qui les ont écrits
(`sha256(json.dumps(corps_sans_le_champ_d_empreinte, sort_keys=True, ensure_ascii=False))`),
redémontrée dans `tests/test_qpu_distant.py::test_08`, pas déléguée au module. Les nombres
de la confrontation sont ceux de
`ASTRO-Q°ODE_SYSTEME/resultats_ibm/audit_dbpkmr0ou4as73ctrm80.json`, redits littéralement dans
`AUDIT` au début du fichier de tests : le dépôt scellé ne dépend d'aucun fichier hors dépôt.

Les deux snapshots de machine (`calibration_…`, `support_…`) ont été réécrits le 11 novembre 2026
pour retirer un CRLF que l'écriture Windows y avait ajouté : les octets publiés sont depuis
exactement ceux que le fournisseur rend, en LF — 11 843 et 1 387 octets, que la table
`EMPREINTES.json` consigne et que C01 re-hache à chaque exécution. `.gitattributes` verrouille
`QPU_DISTANT/sources/*.json` en `eol=lf` pour qu'un clone ou une `git archive` ne réintroduce
pas la même dérive. Aucun nombre de la confrontation n'en change : le JSON relu reste identique
champ par champ, et la racine du dossier reste `011827d24081c8f2…`.

Les deux mêmes fichiers ont été renommés le 11 novembre 2026 sans leur suffixe date
(`…_2026-11-10T1647Z.json` → `calibration_ibm_marrakesh.json`,
`…_2026-11-10T2057Z.json` → `support_ibm_marrakesh_0-1.json`) : un nom de fichier entre dans
`MANIFESTE_SHA256.txt`, or le sceau du dépôt ne porte aucune date — c'est ce que mesure
`DECLARATION/declaration_base.py → sceau_contenu() → C04`, qui rougissait à 8 dates pour ces
deux noms et les six de `GOULETS/`. L'horodatage du fournisseur n'est pas perdu pour autant : il
reste dans le contenu des deux snapshots, dans `horodatages_des_sources` du certificat et dans la
table d'empreintes. Les octets des deux fichiers, eux, n'ont pas bougé d'un octet — C01 re-hache
les mêmes SHA-256 qu'avant le renommage.

## 4. Règle d'attribution — quatre statuts

| Statut | Ce que ça veut dire | Ce que ça ne veut pas dire |
|---|---|---|
| **OPÉRATIONNEL** | le nombre sort d'octets publiés et un contrôle le re-mesure par une écriture différente (`divmod`, `Fraction`, digestion par blocs) | rien qui ait été exécuté par ce dépôt : le tirage est celui du fournisseur |
| **SPÉCIFIÉ** | la valeur est une borne de conception (médiannes de la machine entière, table d'erreurs du support) | un modèle du bruit de CE circuit |
| **SIMULÉ** | l'unité d'état recalculate en `complex` pur rend [0,5 ; 0 ; 0 ; 0,5] | une exécution : la simulation prouve la prédiction, pas la machine |
| **LIGNÉE** | le nom figure dans la filiation intellectuelle ; aucune équation du dossier n'en dépend pour un chiffre | une revendication de paternité d'un résultat chiffré |

## 5. Filiation intellectuelle — aucune équation n'en dépend pour un chiffre

- John S. Bell, *On the Einstein Podolsky Rosen Paradox*, Physics **1**, 195 (1964) ; et
  Artur K. Ekert, *Quantum Cryptography Based on Bell's Theorem*, Phys. Rev. Lett. **67**, 661
  (1991) : la raison pour laquelle une corrélation `01`/`10` asymétrique est une question, pas
  un détail.
- Michael A. Nielsen et Isaac L. Chuang, *Quantum Computation and Quantum Information*,
  Cambridge University Press (2000) : la forme du budget d'erreurs — une fidélité bornée par la
  somme des erreurs de porte, inégalité triangulaire. C'est la règle `1 − 2·Σε` jouée ici, et
  rien de plus.
- Charles H. Bennett, Gilles Brassard, Claude Crépeau, Richard Jozsa, Asher Peres et
  William K. Wootters, *Teleporting an Unknown Quantum State via Dual Classical and EPR
  Channels*, Phys. Rev. Lett. **76** (1996) : la famille de protocoles dont le circuit du job
  est un membre appauvri (une paire, deux bits de lecture).
- Documentation publique de calibration d'IBM Quantum : les tables de fidélité de porte et les
  médiannes de machine qui alimentent les deux enveloppes, lues en lecture seule.

Aucun de ces travaux ne fonde un chiffre d'AL-MIZAN, et aucun chiffre de ce dossier ne leur est
attribué comme résultat : ils disent d'où viennent les formes de calcul.

## 6. Ce que ce dossier ne dit pas

1. Il ne prouve rien sur AL-MIZAN : `predictions_al_mizan_testees = 0`.
2. Il n'exécute rien localement : `executions_locales = 0`, `qubit_physique_local = False`.
3. Il n'appelle pas le réseau : `reseau_appelle_par_ce_module = False` ; le module ne contient
   ni `urllib`, ni `socket`, ni `requests`, ni `subprocess` (contrôlé par AST dans les tests).
4. Il ne publie pas d'identifiant de compte : seul le préfixe SHA-256 en 12 rangs circule.
5. Il ne titre aucune preuve : le vocabulaire « prouvé / démontré / certifié / garanti /
   universel / 100 % » est absent du certificat, et le test le vérifie chaîne par chaîne.
6. Il ne remplace pas l'audit local : l'archive brute reste hors dépôt, et son SHA est attesté
   sans être reproductible — c'est écrit dans le certificat, pas masqué.

## 7. Relancer

```bash
cd ZENODO_DEPOT_ALMIZAN
py -3 -B QPU_DISTANT/qpu_distant_base.py            # attendu : CONTROLES 10/10
py -3 -B QPU_DISTANT/qpu_distant_base.py --ecrit --json
py -3 -m unittest QPU_DISTANT.tests.test_qpu_distant -v   # attendu : 28 tests OK
```

Le module est déterministe : deux relances rendent la même racine Merkle
(`011827d24081c8f2…`), et la table `sources/EMPREINTES.json` refuse tout fichier hors table.
