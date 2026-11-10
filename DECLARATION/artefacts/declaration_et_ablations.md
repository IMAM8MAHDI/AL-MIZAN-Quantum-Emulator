# DECLARATION — antériorité accessible, paternité non instrumentée

**Départ** quatre déclarations de l'auteur et une consigne d'avis externe, consignées dans `SOURCE` ; aucune n'est reprise comme preuve, toutes sont comptées.

| demande de l'auteur | instrument qui l'étayerait | mesuré | statut |
|---|---|---|---|
| preuves d'antériorité | sceau SHA-256 du dépôt | 240 entrées, 0 date à l'intérieur, 0 identifiant de commit | OPÉRATIONNEL |
| antériorité par un tiers | RFC 3161 / TSA / eIDAS / coffre-fort / e-Soleau | 0 instrument sur disque, 31 mentions textuelles dont 12 lignes d'absence | OPÉRATIONNEL |
| dépôt public horodaté | commits git, blocs de signature | 1/81 portent gpgsig, 0 vérifiée(s) faute de clé publique, du 2026-11-07T06:05:23+01:00 au 2026-11-10T09:21:16+01:00 | OPÉRATIONNEL |
| « j'ai commencé par les fractales » | trace fractale datée dans l'archive | 10 occurrences, 3 fichiers, première trace fractale 2026-11-07T05:44:16+01:00 contre 2026-11-07T05:44:16+01:00 pour le dépôt ; première trace fractale = plus ancienne du dépôt : True | OPÉRATIONNEL |
| « j'ai éduqué les IA » | poids fins, dataset d'alignement, journal d'entraînement | 0 instrument, 0 mention du verbe dans l'archive | SIMULÉ — déclaratif |
| mérite contre l'automate | partage mesuré des commits et des fichiers | 63 commits humains / 18 d'automate (77.78 % / 22.22 %) ; 65 fichiers touchés par l'automate seul, dont 0 portant une borne écrite | OPÉRATIONNEL |
| chaîne de publication | Zenodo et CITATION.cff relus | version 3.3.0, 11 identifiants distincts, 320 mentions de DOI, résolution en ligne non testée ici | OPÉRATIONNEL |
| équations publiables | sceau par module | 12/12 modules dans le sceau, 0 équations hors publication prouvable | OPÉRATIONNEL |

## Les trois ablations exécutées

1. **Retrancher la borne.** Sur `CONTINUITE/continuite_base.py`, 15 limites d'au moins 40 caractères effacées : P2 passe de tenu True à tenu False, et les nombres rendus sont inchangés : True. Un nombre sans borne n'est pas plus faux — il ne borne plus rien.
2. **Retrancher le chemin et le statut.** Sur `CONTINUITE/continuite_base.py`, 15 équations sans chemin et 15 statuts inconnus : les 15/15 contrôles du module restent verts, la grille de l'auditeur rouge (True). Ce que l'automate produit ne se déclare pas lui-même.
3. **Retrancher la provenance.** 57 lectures du bloc SOURCE se font dans les fonctions de rendu, 18 dans des fonctions de mesure (DECLARATION/declaration_base.py, FONDATION/fondation_base.py, GUERRE/guerre_base.py). Effacer l'attribution ne change pas la racine Merkle : False ; y injecter un nombre la change : True.

## Ce que la mesure corrige dans la demande

1. Un dépôt — Zenodo, GitHub, un sceau SHA-256 — atteste une **date d'accessibilité** d'un contenu, pas une paternité ni une priorité d'invention. Une idée, un concept ou une fractale ne se déposent pas : seule leur expression se diffuse et se date.
2. L'ordre demandé (« verrouiller avant d'exposer ») est déjà tenu à l'envers par les faits : l'exposition est publique depuis le premier dépôt. Ce dossier date cette exposition au lieu de la nier.
3. L'ablation ne montre pas que l'automate ne produit rien : elle montre que ce qu'il produit reste vérifiable et borné par des règles écrites ailleurs, et que ces règles, une fois retirées, laissent les mêmes nombres dire n'importe quoi.

## Limites ouvertes

- aucun instrument d'horodatage qualifié (RFC 3161, TSA, eIDAS, cachet) n'est dans l'archive : 0 fichier — ce dossier ne peut pas en produire un
- 1 commit sur 81 porte un bloc gpgsig (clé B5690EEEBB952194) et 0 est vérifiée : faute de clé publique au trousseau, aucun commit ne rend ce dépôt probant par signature
- le sceau ne porte aucune date : 0 date dans 240 entrées — dater un contenu demande un tiers de confiance, pas un hash
- les dates ne voyagent pas avec l'archive : lue d'ici, cette couche compte 81 commit(s) dans l'histoire git et 88 ligne(s) au journal local ; extraite par « git archive » hors de tout dépôt, elle n'en compte aucun et doit le dire — EQ-01 nomme la source, C01, C02, C03 et C09 exigent le zéro honnête dans ce second cas
- aucune trace d'éducation des IA dans l'archive : 0 instrument (poids fins, dataset, journal, config) — la demande reste déclarée
- le dossier de preuves externe est cité 0 fois dans l'archive et n'y est pas scellé : sa valeur probante ne se transmet pas avec le ZIP
- 4/4 antécédents vidéo sont nommés dans l'archive ; aucun n'y porte de date mesurable
- la résolution en ligne des 11 identifiants Zenodo comptés n'est pas faite ici : ce module ne fait aucune requête réseau
- 100 fichiers de l'archive sont hors du sceau, dont 0 équations de modules non scellés
- la date d'auteur la plus ancienne (2026-11-07T05:44:16+01:00) est signée devin@cognition.ai et la première trace fractale (2026-11-07T05:44:16+01:00) devin@cognition.ai : la plus vieille date du dépôt n'attribue pas l'idée à un humain
- le classifieur statue ligne à ligne : 19 lignes affirmatives sur les mentions d'horodatage, dont des clés de fichiers qui nomment l'instrument sans l'employer — le mot compte, il ne prouve pas

**antériorité accessible, paternité non instrumentée** : ce dossier date et retranche ; il ne certifie personne.

