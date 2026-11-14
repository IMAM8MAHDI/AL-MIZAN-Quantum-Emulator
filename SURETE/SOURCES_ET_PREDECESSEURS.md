# SOURCES ET PRÉDÉCESSEURS — dossier SURETE

**Licence** : GPL-3.0-only OR AGPL-3.0-only (double licence, voir `LICENSE.md` à la racine du dépôt).

**Auteur** : M. Ahmed EL BAHLOUL (IMAM8MAHDI) — développement assisté par IA générative,
résultats relus et dirigés par l'auteur humain.

**Périmètre** : `surete_bornee_base.py` (13 équations EQ-01…EQ-13, 13 contrôles C01…C13,
certificat à racine Merkle), `tests/test_surete_bornee.py` (46 tests), artefact
`artefacts/certificat.json`. Bibliothèque standard seule, aucun appel réseau, aucune
écriture hors de `artefacts/` et hors du `--ecrit`.

**Statut des résultats** : 7 OPÉRATIONNEL, 4 SIMULÉ, 2 SPÉCIFIÉ. Aucun chiffre de ce
dossier n'est une mesure d'un produit réel. Le verdict du module est
`BORNE ÉCRITE, GARANTIES TRIÉES, AUCUNE PREUVE`.

## 1. La demande, et ce qui l'a remplacée

Le point de départ est une vidéo franceinfo dont le titre public porte une proposition
sur la borne de ce qu'une sécurité informatique peut promettre : « Panne chez Microsoft :
"L'informatique ne sera jamais sécurisée à 100%" (Damien Bancal) »
(`AcoshabaQyg`, 1 366 s, titre et durée repris d'oEmbed et de la page watch).

La sonde a mesuré, le 2026-11-13T23:44:50Z : **0 chapitre horodaté** dans la description
et **0 octet** renvoyés par timedtext en `json3`, `srv3` et XML. Sans transcript, aucune
phrase n'est attribuable à la bande-son. Ce dossier ne cite donc personne, ne numérote
rien d'une vidéo, et n'attribue rien à la personne nommée dans le titre.

La demande initiale — répondre à cette vidéo de façon à « rendre ces géants obsolètes » —
a été requalifiée avant écriture, pour deux raisons falsifiables :

1. **l'obsolescence d'une entreprise n'est pas une propriété décidable** par un calcul
   local : elle dépend d'un marché, d'une base installée et d'une date, trois choses
   qu'aucune équation de ce dossier ne mesure ;
2. **l'obsolescence d'un énoncé de garantie l'est** : dire qu'une garantie est intenable
   ne demande que de lire ce qu'elle annonce. D'où EQ-09, qui pose le critère
   `tenable(g) ⟺ (borne de fuite annoncée > 0) et (procédure publique en temps borné)`.

Le critère est ensuite **retourné contre ce dépôt** (EQ-13, C13) : les trois garanties
absolues écrites en G1, G2, G3 sont disqualifiées par le même calcul, et la limite
globale du dossier est publiée avec ses résultats. Une règle qui ne s'applique qu'aux
autres n'est pas une règle.

## 2. Les treize équations, et d'où vient chacune

| Éq. | Objet | Source du contenu |
|---|---|---|
| EQ-01 | indécidabilité d'une propriété non triviale | théorème de Rice (1953), **cité, non redémontré** |
| EQ-02 | énumération effective d'un domaine fini | forme fermée Σ_{n≤K} 2ⁿ = 2^(K+1) − 1, recomptée état par état |
| EQ-03 | défauts exploitables attendus | loi de Poisson ; surfaces `déclarées`, aucune ligne de code comptée |
| EQ-04 | fenêtre d'exposition d'un correctif | chaîne en trois tranches déclarées (7 + 5 + 3 jours) |
| EQ-05 | part non divulguée | arithmétique d'intervalles : `[a;b] + [c;∞) = [a+c;∞)` |
| EQ-06 | fuite d'une chaîne de couches | modèle à deux branches, `p` et `β` déclarés |
| EQ-07 | décroissance et plancher de cette fuite | conséquence exacte d'EQ-06 en rationnels, sur N = 1…40 |
| EQ-08 | disponibilité | identité `(1−A)·T = T·MTTR/(MTBF+MTTR)`, MTBF/MTTR déclarés |
| EQ-09 | critère sur un énoncé de garantie | définition posée ici, sur six énoncés écrits ici |
| EQ-10 | coût de re-jouée pour un tiers | AST du fichier lui-même : imports, lectures, modules réseau |
| EQ-11 | registre consigné | instantané de `DECLARATION/artefacts/certificat.json`, recopié dans `PARAMETRES` |
| EQ-12 | socle de 313 000 000 000 000 poids | valeur d'adressage de `reseau_poids_sparse_mizan.py` (313T) ; 313 premier par test de division |
| EQ-13 | auto-application | le critère d'EQ-09 appliqué aux énoncés de ce module |

Aucune de ces lignes ne vient de la vidéo. La vidéo a fourni un **thème** — la borne de
ce qui est promettable — et rien d'autre ; c'est consignée dans `SOURCE` sous
`ce_que_le_titre_fournit` et `ce_que_la_video_n_a_pas_fourni`.

## 3. Ce que la prise établit — et ce qu'elle laisse ouvert

Établi, c'est-à-dire recalculable par une autre route à chaque exécution :

- le compte énuméré (131 071 états pour K = 16) rejoint la forme fermée 2¹⁷ − 1, et le mot
  critique `0000000000000000` change le verdict d'une machine à l'autre : la propriété
  d'EQ-01 est bien non triviale **sur ce domaine** ;
- `P₀ = e^(−N)` est retrouvé par trois voies (exponentielle, limite `(1 − N/n)ⁿ`, série de
  Taylor 60 termes) et les quatre issues de deux couches font exactement la probabilité un ;
- la fuite d'EQ-06 est strictement décroissante sur quarante rangs exacts et sa pente en
  logarithme ressort de la régression ;
- l'identité d'EQ-08 tient en rationnels exacts, et l'approximation usuelle `T·MTTR/MTBF`
  **majore** le temps perdu (2,000000 h contre 8760/4381 h) — ce que l'énoncé courant
  n'ose pas affirmer ;
- `313 000 000 000 000` a quinze chiffres, se factorise en 313 × 10¹² et 313 n'a aucun
  diviseur jusqu'à ⌊√313⌋ = 17 ;
- le registre consigné ne se contredit pas compte à compte (15 modules, somme 232 pour un
  total publié de 232) ;
- ce module ne lit aucun fichier extérieur à lui-même, n'importe que la standard library
  (11 racines) et n'appelle aucun module réseau.

Laissé ouvert, et écrit dans chaque `limite` :

- **le coût d'une panne réelle** : aucun chiffre de ce dossier ne vient d'un incident,
  d'un effectif ou d'un prix ; EQ-03 et EQ-04 portent sur des ordres de grandeur déclarés.
- **le vrai `β` d'une architecture** : EQ-07 montre que le plancher ne s'annule pas dans le
  modèle ; un `β` réellement nul est indéterminable par échantillon fini.
- **le complément du domaine** : épuiser 131 071 états prouve l'absence de contredit *dans*
  ce domaine, rien au-dehors — c'est précisément la place que laisse le théorème de Rice.
- **la valeur de ce qui est garanti** : EQ-09 statue sur la forme d'une promesse, jamais sur
  son utilité, et ne dit rien d'une équipe ni d'une entreprise.

## 4. Règle d'attribution — quatre statuts

- **OPÉRATIONNEL** : le chiffre sort d'un calcul que la machine refait à chaque exécution
  (compte énuméré, identité rationnelle, décompte d'AST, test de primalité).
- **SIMULÉ** : le calcul est exact mais ses entrées sont des paramètres déclarés de
  `PARAMETRES` (surfaces de code, durées de chaîne, `p`, `β`, MTBF, MTTR).
- **SPÉCIFIÉ** : l'énoncé est posé et exploité symboliquement, sans évaluation d'un produit
  (le critère d'EQ-09, l'addition d'un intervalle non majoré d'EQ-05).
- **CITÉ** : un résultat de la littérature, nommé et daté, dont le dossier ne revendique
  pas la démonstration. ici : Rice (1953).

Un calcul n'est jamais présenté comme une mesure. Neuf marqueurs de prétention absolue
forment une liste fermée (`MARQUEURS_ABSOLUS` : `100 %`, `infaillible`, `invuln`,
`aucune faille`, `complete`, `garanti a`, `zero risque`, `sûre`, `certain`) et sont
scannés dans les résultats publiés de ce module ; C13 rougit si l'un d'eux y entre.

## 5. Filiation intellectuelle — aucune équation n'en dépend pour un chiffre

- **Rice, 1953** — indécidabilité de toute propriété extensionale non triviale des
  langages récursivement énumérables. EQ-01 l'énonce et en déduit ce qu'elle autorise
  (EQ-02, un domaine fini) ; la démonstration n'est pas rejouée ici.
- **Poisson** — la loi `P₀ = e^(−N)` d'EQ-03 est la probabilité zéro événement d'une loi de
  Poisson d'espérance N, écrite à la main avant d'être comparée à `defauts_tcb()`.
- **Arithmétique d'intervalles** — R. E. Moore, *Interval Analysis*, Prentice-Hall, 1966,
  pour la nomination. EQ-05 n'utilise qu'une règle : un majorant absent se propage par
  addition.
- **Rang des couches** : le modèle `s = p·β`, `a = (p − s)/(1 − s)` d'EQ-06 est une écriture
  à deux branches posée dans ce dossier, pas une formule empruntée à un tiers. Sa décroissance
  (EQ-07) en est une conséquence algébrique.
- **`MTBF/(MTBF+MTTR)`** — formule d'ingénierie de la disponibilité ; EQ-08 en vérifie
  l'identité et non la validité comme argument de sécurité, ce que sa `limite` refuse.
- **313T** — la capacité d'adressage reprise d'EQ-12 vient du socle de poids de ce dépôt,
  pas de la vidéo ; son nombre est consigné dans `PARAMETRES` et non deviné.

Le module ne déclare qu'une référence extérieure dans ses nœuds
(`NOEUDS["EQ-01"]["externe"]`, Rice 1953 ; `EQ-03`, `EQ-05` et `EQ-08` portent `None`).
Les autres nominations de cette section sont éditoriales — elles nomment une loi ou une
formule d'usage, sans intervenir dans aucun champ haché ni dans aucun contrôle.

## 6. Ce que ce dossier ne dit pas

- Il ne nomme aucun acteur de la vidéo et n'affirme que quelqu'un ait dit quoi que ce soit.
- Il ne conclut pas que Microsoft, un autre éditeur ou une autre personne serait obsolète,
  et ne le pourrait pas : EQ-09 porte sur des énoncés, pas sur des entreprises.
- Il n'apporte **aucune preuve mathématique** d'aucune propriété d'aucun système. Le verdict
  du module est `AUCUNE PREUVE`, et la racine Merkle ne scelle que des énoncés.
- Il ne mesure rien d'un incident réel : ni coût, ni durée, ni effectif, ni taux.
- `PARAMETRES["registre_consigne"]` est un **instantané** recopié pour que le module reste
  exécutable hors du dépôt. C11 prouve la cohérence interne de cet instantané ; le test
  `test_instantane_confronte_au_parc_vivant` est seul à confronter le chiffre au parc réel,
  et il rougit si le parc bouge sans que l'instantané suive.

## 7. Relancer

```bash
cd ZENODO_DEPOT_ALMIZAN
PYTHONIOENCODING=utf-8 py -3 -B SURETE/surete_bornee_base.py            # 13/13, racine, verdict
PYTHONIOENCODING=utf-8 py -3 -B SURETE/surete_bornee_base.py --ecrit    # artefacts/certificat.json
PYTHONIOENCODING=utf-8 py -3 -B -m unittest SURETE.tests.test_surete_bornee -v
PYTHONIOENCODING=utf-8 py -3 -B FONDATION/OUTILS/audit_piliers.py SURETE/surete_bornee_base.py --rigide
PYTHONIOENCODING=utf-8 py -3 -B FONDATION/OUTILS/audit_piliers.py --tous --rigide
```

Attendu, mesuré le 2026-11-14 : `CONTROLES 13/13 · EQUATIONS 13`, racine
`c41de72882b7568101def098bdb1c67b59015db85098a6027204d2eb208198f0`, 46 tests `OK`,
audit CONFORME sur les quatre piliers, et 15 dossiers CONFORME en `--tous`.

La racine ne dépend que des cinq champs hachés par équation
(`id`, `formule`, `resultat`, `statut`, `limite`) : retoucher un texte de contrôle ne la
fait pas bouger. Une exécution sur une autre machine change les durées relevées dans
`mesure`, jamais la racine.
