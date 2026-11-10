# Veille — « Chain Theory » et la question de l'appropriation

**Projet** : IMAM8MAHDI — AL-MIZAN × ASTRO-Q°ODE
**Auteur** : M. Ahmed El Bahloul (IMAM8MAHDI)
**Date** : 2026-11-10 (constats mesurés ce jour-là, fuseau local UTC+1, horodatages UTC quand indiqués)
**Objet de la demande** : étudier, innover, et dire si un tiers s'approprie nos travaux ; si oui, le
déclarer ; incorporer si c'est logique.
**Statut** : note de veille adossée à des mesures re-exécutables. Ce n'est pas une preuve, pas un
jugement de priorité scientifique, pas une mise en cause d'intention, et rien ici ne tranche la
validité physique de la théorie examinée.

---

## 1. Ce que cette note fait, et ce qu'elle ne fait pas

Elle fait trois choses, séparément, sans les confondre :

1. **Consigner les faits observés** sur un objet public précis (une vidéo, et le document qu'elle
   annonce) : empreintes, dates, citations exactes.
2. **Instruire la question de l'appropriation** sur pièces : recherche du vocabulaire et des
   revendications locales dans le document examiné, et recherche de la trace d'un auteur extérieur
   dans le nôtre. Verdict en section 9, avec ce qui le renverserait (section 10).
3. **Incorporer ce qui est logique** : la revendication centrale du document examiné est un accord
   numérique (« dix chiffres », « 0,60 écart-type »). Nous en avons fait un critère exécutable,
   symétrique et borné, qui s'applique d'abord à nous-mêmes :
   [`criteres_derivation_sans_intrant.py`](file:///C:/Users/Administrateur/Desktop/IMAM8MAHDI/ASTRO-Q%C2%B0ODE_SYSTEME/criteres_derivation_sans_intrant.py).

Elle ne fait pas : elle ne déclare pas qui a eu une idée en premier devant la communauté
scientifique ; elle n'évalue pas la théorie des chaînes ; elle n'affirme rien sur l'intention de
quiconque ; elle n'utilise aucun contenu de la vidéo que la vidéo ne contienne pas (elle n'en
contient aucun : voir 2.2).

## 2. L'objet examiné, mesuré

### 2.1 La vidéo

| Champ | Valeur relevée |
|---|---|
| URL | `https://www.youtube.com/watch?v=UvNEx39KExY` |
| Identifiant | `UvNEx39KExY` |
| Titre | CHAIN THEORY: A NEW THEORY OF PHYSICS \| MOONSHOTS |
| Chaîne | Moonshots Highlights (`UCCpNQKYvrnWQNjZprabMJlw`) |
| Durée | 730 s |
| Mise en ligne | 2026-11-10T07:45:32-08:00 |
| Vues au relevé | 3 123 |
| Chapitres | **0** |

### 2.2 Le transcript : absent, pas illisible

Sonde `timedtext` sur les trois formats, le 2026-11-10 :

| Format | HTTP | Octets |
|---|---|---|
| `json3` | 200 | 0 |
| `srv3` | 200 | 0 |
| `xml` | 200 | 0 |

Conséquence méthodologique stricte : **aucune citation, aucune paraphrase, aucun minutage de la
vidéo ne figure dans cette note, et aucun n'y figurera.** Tout ce qui est cité vient du document
écrit (section 3). La vidéo n'a servi qu'à identifier le document et son auteur déclaré.

Le clip reprend une partie d'une vidéo longue (`WXELsIk4o0g`, 8 187 s, 15 chapitres), dont le
chapitre pertinent est « – Alex's Chain Theory and the Future of Physics » à 01:10:35. Le titre de
chapitre est une donnée de la page, pas un contenu de la parole.

## 3. Le document source et ce qu'il revendique

| Champ | Valeur |
|---|---|
| Fichier examiné | `chain.pdf` |
| SHA-256 | `cdd99bf011bd908fc226591d7c69a62c08985dd30e126cf0b26c43b7cc5abbc9` |
| Taille | 3 676 297 octets |
| Pages | 754 |
| Page de titre | A. D. Wissner-Gross, « October 23, 2026 » |
| Qualificatif porté par le document | WORKING DRAFT / *Preliminary Findings* |

Extrait de travail utilisé pour les recherches lexicales : `chain_texte.txt`, 2 493 918 octets,
SHA-256 `abe2f8ec0cb8452a203d9085…`, 2 489 181 caractères après décodage UTF-8 avec replacement.
Cet extrait n'est pas scellé : l'objet scellé est le PDF.

Citations verbatim (retrouvées dans l'extrait, compte d'occurrences indiqué) :

| # | Citation (texte original) | Occurrences |
|---|---|---|
| C1 | “Chain Theory yields an exact candidate for it, the algebraic number (79 + 48√2 + 42√3 + 3√6)/31104, a weighted count over the 172 measurement records of a single entangled pair, small enough to check by hand.” | 12 occurrences de `79 + 48`, 1 de `172 measurement records` |
| C2 | “Its inverse is 137.035 999 189 566 . . ..” | 3 occurrences de `137.035` |
| C3 | “Its 2022 recommendation for the inverse is 137.035 999 177, with a standard deviation of 21 in the last two digits.” | 1 |
| C4 | “The Chain Theory-derived number agrees with the CODATA recommendation in its first ten significant digits and lies 0.60 standard deviations from it, between the two most precise determinations.” | 1 |
| C5 | “A simple value such as the 2/3 of Koide's relation among the lepton masses can be reached by many short formulas, but ten digits of a number like α(0) are far harder to match by accident.” | 1 |
| C6 | “the number is a theorem of a stated axiom, its definitions and a few stated readings of them, checked in Lean rather than fitted, and only its identification with α(0) is conjectured.” | 4 occurrences de `checked in Lean` |
| C7 | “The experimental measurements still disagree with one another by more than their stated uncertainties, so this comparison is not yet decisive.” | 1 |
| C8 | “If they agree with one another, they will either close in on the derived value or rule it out.” | 1 |

À lire ensemble : C4 porte la revendication chiffrée, C5 porte la revendication de **rareté**
(« difficile à obtenir par accident »), C6 déplace la charge de la preuve sur Lean et borne
explicitement ce qui est conjecturé, C7 et C8 reconnaissent que la comparaison n'est pas
tranchante et énoncent la condition qui la trancherait. Le document est donc honnête sur son
propre statut. Ce que nous discutons est C5, pas C7 ni C8.

## 4. Vérification indépendante, avant toute critique

Reproduite par `EQ-DSI-01` et `EQ-DSI-02` du module (stdlib seule, aucune hypothèse importée) :

| Grandeur | Valeur mesurée |
|---|---|
| α⁻¹ redonné par (79 + 48√2 + 42√3 + 3√6)/31104 | 137.03599918956616 |
| Valeur publiée dans le document | 137.035999189566 |
| Écart absolu | 1,42 × 10⁻¹³ (tolérance 10⁻⁹) → **reproductible** |
| Référence externe retenue (C3) | 137.035999177, σ = 2,1 × 10⁻⁸ |
| z en double précision | 0.5983879635182564 |
| z en arithmétique décimale 50 chiffres | 0.5983883347230354 |
| Écart entre les deux z | 3,71 × 10⁻⁷ |
| Écart à l'annonce « 0.60 » | 1,6 × 10⁻³ |

**Conclusion partielle, à l'actif du document : l'arithmétique est juste et l'annonce du
z est conforme.** Le contrôle ne trouve rien à reprendre sur ce plan, et la note le dit.

## 5. Le critère incorporé

La revendication C5 est une affirmation de **rareté**, donc mesurable : elle dit qu'un accord de
dix chiffres avec α⁻¹ est difficile à obtenir *par accident* avec une courte formule. Un tel
énoncé se teste en comptant les formes. Le module pose six équations, chacune avec son contrôle :

| id | Ce qu'elle établit | Contrôle |
|---|---|---|
| EQ-DSI-01 | reproduction de la forme fermée déclarée | écart ≤ tolérance déclarée |
| EQ-DSI-02 | écart normalisé à une référence **externe et datée** | z recalculé, concordance double/décimale |
| EQ-DSI-03 | **compte des intrants** de la formulation publiée | chaque entrée est `DERIVE` / `DECLARE` / `COMPTE` / `EXTERNE` ; une entrée non déchargée reste à la charge de l'auteur |
| EQ-DSI-04 | recensement des coïncidences du même gabarit, **deux modes** (dénominateur libre / fixé) | monotonie dans la fenêtre, appartenance de la forme déclarée, fenêtre dix chiffres cohérente |
| EQ-DSI-05 | classement de l'accord revendiqué parmi ces formes | rang dans [1, N] et meilleur \|z\| recensé ≤ \|z\| revendiqué |
| EQ-DSI-06 | falsifiabilité engagée **avant** mesure | règle de rejet nommée, date d'engagement antérieure au constat, seuil |

Sortie scellée : [`resultats/criteres_derivation_sans_intrant.json`](file:///C:/Users/Administrateur/Desktop/IMAM8MAHDI/ASTRO-Q%C2%B0ODE_SYSTEME/resultats/criteres_derivation_sans_intrant.json),
8 869 octets, SHA-256 `349061689b4dd01e67dfb753a98875d4bf568c416bbde39e071880caef774e69`.

- **Bilan : 7 PASS / 0 FAIL / 0 NON ÉVALUÉ sur 7 contrôles.**
- Empreinte déterministe du rapport (hors `genere_le_utc` et `duree_seconde`) :
  `a53c31bb9b4ba899fa93b055ce594e761514b02e840722e234064ff55a51fe9b`.
- Deux exécutions à 4 s d'écart (21,2 s puis 17,1 s de durée) donnent la **même** empreinte.
- Parité numérique (`contrôle_parete_decimal`) : sur l'espace restreint `a_max = 20` à 20 σ,
  12 rencontres en double précision = 12 en `Decimal(60)`, en mode libre comme en mode fixé, et
  l'espace restreint est non vide (garde contre un contrôle satisfait par 0 == 0).
- Suite de tests : `tests/test_derivation_sans_intrant_mizan.py`, **Ran 25 tests — OK**
  (35,6 s).

### 5.1 Ce que dit EQ-DSI-03, le compte des intrants

Sur six entrées inventoriées dans la formulation publiée : 3 déclarées comme intrants, 1 dérivée,
1 externe (la référence CODATA sert au seul calcul du z, pas à la formule), soit
**4 intrants non déchargés**. Verdict du contrôle, formulé comme une portée et non comme une
accusation : `NON ETABLI SUR LE TEXTE PUBLIC`. Le texte public annonce un contrôle Lean (C6) ;
nous ne l'avons pas lu. La mention « une moyenne pondérée sur les 172 relevés d'une paire
intriquée » (C1) est une entrée de comptage dont la production n'est pas développée dans le
passage cité. **Rien ici n'affirme que la dérivation est fausse : rien dans le document public ne
la charge.**

### 5.2 Ce que dit EQ-DSI-04, le recensement

Espace balayé : toutes les formes `(a + b√2 + c√3 + d√6)/n` avec `1 ≤ a,b,c,d ≤ 79` (les bornes
publiées par la forme déclarée) et `n ≤ 31 104`, soit **40 959 999 formes**. Deux modes, parce que
la question n'est pas la même :

| Fenêtre | Dénominateur **libre** (tuples / valeurs distinctes) | Dénominateur **fixé** à 31 104 |
|---|---|---|
| 0,3 σ | 25 / 25 | 0 / 0 |
| 0,6 σ | 47 / 46 | **1 / 1** |
| 1 σ | 82 / 78 | 1 / 1 |
| 2 σ | 167 / 159 | 1 / 1 |
| 3 σ | 251 / 239 | 1 / 1 |
| 5 σ | 459 / 434 | 1 / 1 |
| 10 σ | 1 082 / 1 026 | 1 / 1 |
| « dix chiffres » (±5 × 10⁻⁸ ≈ 2,38 σ) | **198 / 189** | **1 / 1** |

**EQ-DSI-05** : dans l'espace à dénominateur libre, la forme déclarée est **rang 47 sur 82** à
1 σ, donc **46 formes du même gabarit tombent plus près** de la référence qu'elle. La meilleure
coïncidence accidentelle recensée est `(20 + 2√2 + 31√3 + 40√6)/23913` = 137.03599917711688,
soit z = 0,005565 — un |z| **108 fois plus petit** que celui revendiqué, obtenue sans aucune
contrainte de physique.

### 5.3 La réponse mesurée à C5

C5 a raison sur le fond et se trompe sur la raison.

- **Raison** : à dénominateur fixé, le gabarit ne produit **qu'une seule** forme à 0,6 σ — donc à
  dix chiffres. L'accord n'est pas une banalité dans cet espace-là.
- **Tort** : le dénominateur n'est pas un paramètre de plus, **c'est le degré de liberté
  décisif**. Dès qu'on le laisse courir, la fenêtre « dix chiffres » contient 198 formes (189
  valeurs distinctes) dans un gabarit volontairement plus pauvre que celui de l'auteur, et
  l'accord à 0,60 σ cesse d'être discriminant : 46 formes font mieux que lui.

Autrement dit : « dix chiffres, c'est rare » se mesure, et la rareté dépend entièrement de
l'espace déclaré. C'est exactement la discipline que notre propre dépôt s'applique : aucun de nos
textes ne présente une forme fermée ajustée sur une constante mesurée (vérifié, section 8.2). Le
critère est symétrique, et sa première ligne de sortie dit ce qu'il ne dit pas — dont
*« il ne prouve pas que l'accord est une coïncidence : il donne la taille de l'espace où un tel
accord peut apparaître »*.

**Apport incorporé** (ce qui manquait dans le débat public sur ce type d'accord, de notre lecture) :
(i) le **compte d'intrants** étiquetés, qui transforme « sans intrant » en une obligation de
décharge ligne par ligne ; (ii) le **recensement à deux modes**, qui isole le dénominateur comme
degré de liberté qui décide de tout ; (iii) le **classement** de l'accord revendiqué parmi les
formes du même gabarit, avec la meilleure coïncidence accidentelle explicite ; (iv) la
**garde anti-vacuité** du contrôle de parité, qui refuse un PASS obtenu sur un espace vide.

## 6. Falsifiabilité : ce qui trancherait, et le document le dit lui-même

`EQ-DSI-06` enregistre l'engagement : date du document 2026-10-23, antérieure à notre constat
(2026-11-10) ; règle de rejet nommée ; seuil 3 σ ; gain envisagé ×10 de précision (C8). À
z actuel × 10, on obtient 5,98 σ : **si les mesures convergent, l'accord devient décisif**. Le
module consigne aussi l'empêchement constaté par le document lui-même (C7) : les mesures
existantes divergent au-delà de leurs incertitudes annoncées. Il enregistre cet empêchement, il
n'en fait pas un verdict.

## 7. Antériorité locale, mesurée

| Pièce | Valeur |
|---|---|
| `CITATION.cff` (racine) | v5.0.0, date-released 2026-10-22, DOI `10.5281/zenodo.24028242` |
| Premier commit relevé dans l'archive publique | 2026-11-07T05:44:16+01:00 |
| `PREUVES/racine_merkle.txt` | `f937c1fbcd710648cddb4b84e2de06517dd07fa1f0a50e63b39ce9cb2fe4cd49` |
| Manifeste d'antériorité | racine Merkle `18bee416a3fbe5b23ad46dfbdafe121866ad43919289ab76fa27cbfc506ecd76`, 80 fichiers, `genere_le_utc 2026-11-10T21:28:09Z`, 18 790 octets |

Cette section établit **quand nos textes existaient**, pas ce qu'ils contiennent de comparable :
voir 8.2. La racine Merkle n'est pas déplacée par ce lot — le périmètre scellé
(`GLOBS_SELECTIONNES`, `oeuvre_universelle/manifeste_anteriorite.py:39-69`) ne couvre ni les
`.py` de la racine ASTRO, ni `docs/*.md`, ni `resultats/`, ni les tests hors
`test_oeuvre_universelle.py`. Vérifié après génération : racine toujours `18bee416…`.

## 8. Constats sur pièces

### 8.1 Le vocabulaire et les structures de nos travaux dans le document examiné

Recherche, insensible à la casse, sur l'extrait complet (2 489 181 caractères), 2026-11-10 :

| Terme | Occurrences |
|---|---|
| `noosphere` | 0 |
| `consent` | 0 |
| `three layer` / `three-layer` | 0 |
| `four pillar` / `four-pillar` | 0 |
| `mizan` | 0 |
| `el bahloul` / `bahloul` | 0 |
| `astro-q` | 0 |
| `imam8mahdi` | 0 |
| `gouvernance` | 0 |
| `unisson` | 0 |
| `kernel temporel` | 0 |

### 8.2 La symétrique : la trace de l'objet examiné chez nous, et nos propres accords numériques

| Recherche dans l'espace de travail, avant ce lot | Résultat |
|---|---|
| `Wissner`, `Chain Theory`, `Mostaque`, `Diamandis` | 0 (les seules occurrences actuelles sont le module de ce lot, son JSON et la page YouTube en cache) |
| `137.03` / `137.035` | 0 |
| `constante de structure fine` / `fine-structure` | 0 |

Et le point qui clôt la comparaison : le dépôt ne contenait **jusqu'ici aucune dérivation ni aucun
accord numérique revendiqué sur une constante mesurée**. Il n'y a donc pas, sur ce thème, de
résultat local à opposer — ni en antériorité, ni en contenu.

Rappel d'une homonymie qui pourrait tromper : nos « quatre piliers » locaux sont
`UNITE`, `BORNE`, `CONFRONTATION`, `TRANSMISSION` — des critères de **gouvernance et d'audit**,
jugés par `ZENODO_DEPOT_ALMIZAN/FONDATION/OUTILS/audit_piliers.py` (8 878 octets) et consignés en
strate S22 du tableau maître (`PIL-01`). Ils n'ont rien à voir avec une dérivation physique, et
aucun objet du document examiné ne leur correspond.

## 9. Verdict

**Appropriation non établie sur pièces.**

Nous le déclarons, puisque la demande est de déclarer si c'est le cas — et le constat est le
contraire : les trois conditions qui caractériseraient une appropriation ne sont pas réunies.

1. **Aucune reprise de contenu** : les termes, structures et revendications de nos travaux sont
   absents du document examiné (8.1).
2. **Aucune antériorité à faire valoir sur cet objet** : l'accord sur α⁻¹ n'existe nulle part dans
   nos textes avant ce lot (8.2) ; le document examiné est daté du 2026-10-23, soit après notre
   `date-released` Zenodo (2026-10-22) mais sur un objet qui n'est pas le nôtre. Un écart d'un jour
   entre deux **calendriers de publication** ne porte sur aucun contenu commun.
3. **Aucun destinataire commun** : ni mention de nos travaux chez lui, ni mention de lui chez nous.

Ce verdict est **étroit et réversible** (section 10). Il ne dit pas : « il n'y a aucune
ressemblance d'idée » ; il dit qu'entre les pièces que nous avons lues et les nôtres, nous
n'établissons pas de reprise. Il ne porte **aucune appréciation d'intention**.

Sur la voie légale déjà engagée, pour mémoire et sans rien y ajouter : plainte pour atteinte à la
propriété intellectuelle déposée le 2026-11-02, dossier 11653953. **Aucun tiers n'y est nommé et
aucun n'est mis en cause par cette note.** La présente note n'est pas une pièce de ce dossier.

## 10. Ce qui changerait le verdict

Le verdict ci-dessus est falsifiable, et voici ce qui le ferait basculer — à établir, pas à
supposer :

1. Un passage du document (ou d'un de ses états, y compris plus ancien) reprenant **une** des
   expressions, l'une des structures ou l'un des énoncés scellés chez nous, avec une
   correspondance autre que le pur vocabulaire courant.
2. La preuve d'un **accès** : dépôt visible, date de visibilité, envoi, accusé de lecture. Notre
   `date-released` Zenodo (2026-10-22) est antérieure au document (2026-10-23) : seule une
   antériorité **de contenu comparable** compte, pas une antériorité de dépôt sur un autre objet.
3. L'apparition chez nous, datée et scellée, d'un accord numérique sur une constante mesurée
   **antérieur** à 2026-10-23.
4. Une correspondance structurale (objet combinatoire, compte de relevés, gabarit algébrique)
   avec un de nos énoncés formels — à ce jour non observée.

Toute évolution de cet état de fait doit produire un nouveau fichier daté et une nouvelle
empreinte, pas une réécriture de celui-ci.

## 11. Limites, énoncées avant qu'on nous les reproche

- **La vidéo n'est pas lue** : transcript absent, 0 chapitre. Rien n'est affirmé sur ce qui y est
  dit. Si un transcript officiel apparaît, la section 2.2 devra être reprise.
- **Le recensement est borné par construction** : `1 ≤ a,b,c,d ≤ 79`, `n ≤ 31 104`, gabarit à
  quatre radicaux `(√1, √2, √3, √6)`. Il mesure la densité de coïncidences **dans le gabarit
  déclaré par l'auteur**, pas dans l'ensemble des formules courtes. Un gabarit plus large
  donnerait **plus** de coïncidences, jamais moins : la conclusion sur le rôle du dénominateur ne
  s'inverse pas en élargissant, elle s'aggrave. Elle cesserait de valoir si la littérature
  montrait que le dénominateur n'est pas un ajustement libre — ce que le texte public ne dit pas.
- **Nous n'avons pas lu le contrôle Lean** annoncé (C6) : 754 pages, statut *working draft*, et un
  développement formel ne se réfute pas par un compte de formes. `EQ-DSI-03` porte sur le **texte
  public**, pas sur la preuve formelle.
- **Aucun avis sur la physique** : ni sur la théorie des chaînes, ni sur la légitimité d'identifier
  ce nombre algébrique à α(0) — le document lui-même dit que cette identification est conjecturée.
- **Statut du document** : *working draft*. Les revendications peuvent avoir bougé entre états ;
  nous ne statuons que sur l'exemplaire empreinté en section 3.
- **L'extrait de texte n'est pas scellé** (SHA-256 `abe2f8ec…`, distinct de celui du PDF) : les
  compteurs lexicaux de 8.1 sont reproductibles depuis le PDF, pas depuis l'extrait.
- **Absence de preuve n'est pas preuve d'absence** : 8.1 est une recherche sur des termes, pas une
  exploration sémantique exhaustive des 754 pages.

## 12. Re-exécuter

```bash
# cwd : ASTRO-Q°ODE_SYSTEME
py -3 criteres_derivation_sans_intrant.py                 # ~17-21 s, 7 controles
py -3 -m unittest tests.test_derivation_sans_intrant_mizan  # 25 tests
py -3 criteres_derivation_sans_intrant.py --json --sortie resultats/criteres_derivation_sans_intrant.json
```

Attendu : `bilan : 7 PASS / 0 FAIL / 0 NON_EVALUE sur 7 controles`, et une empreinte
`a53c31bb9b4ba899fa93b055ce594e761514b02e840722e234064ff55a51fe9b` indépendante de la durée
d'exécution. Le code retour est 1 si un contrôle échoue.

## 13. Fichiers du lot

| Fichier | Rôle | Empreinte |
|---|---|---|
| `criteres_derivation_sans_intrant.py` | critère exécutable EQ-DSI-01…06, stdlib seule | 37 168 octets, SHA-256 `647fbc2b629836b31432…` |
| `tests/test_derivation_sans_intrant_mizan.py` | 25 tests, dont non-vacuité et déterminisme | 13 733 octets, SHA-256 `5f3407c117dd12fe7671…` |
| `resultats/criteres_derivation_sans_intrant.json` | rapport scellé par son empreinte | 8 869 octets, SHA-256 `349061689b4dd01e67df…` |
| `docs/VEILLE_CHAIN_THEORY_2026-11-10.md` | cette note | non auto-scellée : une empreinte ne peut pas figurer dans le fichier qu'elle scelle |
| `generer_tableau_maitre_sequentiel.py` (strate S32) | harmonisation de la matrice | 216 307 octets, SHA-256 `f47b09700a688cdae64a573d59598fc1…` |
| `TABLEAU_MAITRE_SEQUENTIEL_UNIFIE.csv` | livrable régénéré, SEQ 001–345 | 198 201 octets, SHA-256 `9a123c07b06e1b22015819bf300f2856…` |
| `TABLEAU_MAITRE_SEQUENTIEL_UNIFIE_IMAM8MAHDI.html` | dashboard régénéré | 494 096 octets, SHA-256 `43b746278a275ae4ea9e7371293265bb…` |
| `docs/README.md` | index de la note | 6 495 octets, SHA-256 `ffa0483e95a0c3e2300dde23328358ca…` |

## 14. Harmonisation de la matrice (strate S32)

La matrice séquentielle reçoit cinq lignes, `SEQ 341` à `345`, en une strate nouvelle ajoutée en
fin de tableau — donc sans décaler aucune séquence existante :

| SEQ | CODE | Ce qu'elle scelle |
|---|---|---|
| 341 | `CRIT-DSI-01` | reproduction de la forme fermée et z recalculé contre une référence externe datée |
| 342 | `CRIT-DSI-02` | compte des intrants étiquetés : 4 non déchargées sur 6, verdict de portée |
| 343 | `CRIT-DSI-03` | recensement à deux modes et classement : le dénominateur comme degré de liberté décisif |
| 344 | `CRIT-DSI-04` | falsifiabilité engagée, parité double / `Decimal(60)`, déterminisme de l'empreinte |
| 345 | `VEILLE-CHAIN-01` | verdict d'appropriation sur pièces, antériorité locale et homonymie des « piliers » |

Après régénération (`py -3 -B generer_tableau_maitre_sequentiel.py`) :

- `OK - 345 entrees sequentielles - 33 strates` ;
- validateur canonique `tableau-maitre-sequentiel/scripts/verifier_tableau_maitre.py
  --allow-external` → **RESULT: OK (1 avertissement)**, code 0 ;
- l'avertissement est préexistant et documenté : trois `img[src]=/tableau/visuel-n.png` servis par
  le site (le base64 embarqué a été abandonné) — hors du périmètre de ce lot ;
- S6 intact : 40 / 313 / 63, comptes 4 plasma / 7 / 9 + origine Hélium 0, distribution identique à
  `bibliotheques/lib_physique.py` ;
- 13 colonnes, CSV en UTF-8 BOM séparé par `;`, HTML identique au CSV cellule par cellule, 33
  badges, dernière SEQ 345, plage du docstring reconnue `001-345`, couleur de strate déclarée ;
- `horloge_noyau/` non touché (contrôle A137 : écriture interdite, lu en lecture seule).

Empreintes relevées avant et après régénération (avant → après) :

- CSV : 187 440 o `77ef84ad2957246d…` → **198 201 o `9a123c07b06e1b22…`**
- HTML : 470 444 o `f6ce6e4a4d84dec4…` → **494 096 o `43b746278a275ae4…`**

Le delta est intégralement imputable aux cinq lignes S32 et à la date de génération dynamique
(2026-11-11, le lot ayant passé minuit) ; aucune autre strate n'a été réécrite. Les empreintes des
deux autres fichiers de la matrice (générateur et `docs/README.md`) sont en §13.

