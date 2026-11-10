# FONDATION — une base, quatre piliers, une limite

**Auteur** : M. Ahmed EL BAHLOUL (IMAM8MAHDI)  
**Licence** : GPL-3.0-only OR AGPL-3.0-only  
**Module** : `fondation_base.py` — 18 équations, 18/18 contrôles reçus.

## Chemin

### La source mesurée, et ses absences
Le point de départ est une page YouTube mesurée octet pour octet, citée ici comme une référence bibliographique : son titre « Le CERN a Enfin Détecté un Événement que la Science Attendait depuis 40 Ans » (chaîne Nocturne, identifiant 5pP1e69T3HQ, durée déclarée 8018 s). Elle ne rend que du JavaScript d'amorçage, sa description ne porte aucun chapitre horodaté, donc aucun minutage citable, et timedtext renvoie 0 octet : le transcript est tenu pour absent. Le dossier ne cite aucune phrase de la vidéo, n'en reprend aucun instant, n'en tire aucun chiffre ; il n'en retient qu'un thème, la désintégration rare K⁺ → π⁺ νν̄.

### L'axiome est posé, il ne prouve rien
EQ-01 énonce l'Un, posé HORS MATRICE et attribué à M. Ahmed EL BAHLOUL (IMAM8MAHDI). Le module porte explicitement `nombres_fournis_par_l_axiome = 0` : aucune équation ne dérive de l'axiome, aucune mesure du CERN ne le confirme ni ne l'infirme, et la physique de ce dossier ne suit pas une théologie. Ce que l'axiome engage est une seule contrainte vérifiable : ne pas déclarer deux fois la même grandeur avec deux valeurs.

### Quatre piliers qui sont des contrôles
Unité, Borne, Confrontation, Transmission ne sont pas des décorations : chacun est repris par des contrôles exécutés à chaque exécution, et `OUTILS/audit_piliers.py` les applique aux autres modules du dépôt. Un pilier devient exigeant quand il coûte des phrases et des échecs possibles, pas quand il est annoncé.

### Le graphe s'arrête quelque part
EQ-02 et EQ-03 exigent qu'un nœud sans prédécesseur interne nomme une source déclarée hors du dossier, et que le graphe reste acyclique. La chaîne de dérivation butte donc sur une source posée, jamais sur elle-même : c'est la forme opératoire de l'axiome, et elle ne dit rien de la vérité des nombres.

### Une prédiction gelée avant la lecture
EQ-07 gèle la prédiction sur un dictionnaire de valeurs déclarées et vérifie, par l'inspection de la signature, qu'aucune clé du comparateur n'y entre ; le drapeau de contamination se lève dès qu'on en injecte une. EQ-10 peut alors confronter 10,0119 événements à l'excès publié sans avoir lu le résultat d'avance.

### La confrontation : 2021, 2024, 2026 et le communiqué
EQ-08 à EQ-17 lisent quatre sources publiques. Le dossier écrit ce qui concorde (l'acceptance ferme, l'excès à 0,7166 σ de la prédiction gelée), ce qui ne concorde pas (les intervalles à un sigma de 2024 ne se recouvrent pas sous notre hypothèse de quadrature), et ce qui se referme (l'écart 2026 passe sous 1 σ). Aucun de ces écarts n'est présenté comme une découverte ni comme une réfutation de NA62.

### Ce que SPÉCIFIÉ et SIMULÉ veulent dire
Deux équations portent SPÉCIFIÉ — l'axiome posé et la limite écrite — et une porte SIMULÉ : la fraction géométrique du faisceau, bornée inférieurement parce que le communiqué ne donne ni le temps utile ni l'acceptance du faisceau. Ces mots apparaissent dans les trois langues sur chaque page ; aucun résultat simulé n'est promu en affirmation.

### Écrire sa propre réfutation
EQ-18 termine le dossier par sa propre chute : cinq conditions qui l'invalident, quatre choses qu'il ne prouve pas, et dix-huit limites d'équation non vides. Un calcul fini ne fonde pas une assertion universelle ; il peut montrer que la discipline tient sur des nombres publics. C'est tout ce que ce dossier revendique.

## Équations

### EQ-01 — L'axiome posé hors matrice

`AX : la régularité d'un système fini n'appartient pas à ce système`

> Il n'y a de dieu que Allah — posé HORS MATRICE. — SPÉCIFIÉ — posé, jamais dérivé, jamais réfuté par ce dossier

*Statut* : SPÉCIFIÉ · *chemin* : `fondation_base.py → eq01_axiome() → C01`

### EQ-02 — Tout nœud sans prédécesseur interne est fondé dehors

`∀ nœud sans prédécesseur interne, une source déclarée hors du dossier`

> 1 racine : EQ-01 — fondée dehors : True ; 18 aretes vers l'exterieur

*Statut* : OPÉRATIONNEL · *chemin* : `fondation_base.py → graphe_dependances() → C02`

### EQ-03 — Le graphe est un DAG

`DAG : acyclique, toutes racines atteignables, zéro auto-référence`

> acyclique=True · nœuds=18 · atteignables=18 · auto-références=[]

*Statut* : OPÉRATIONNEL · *chemin* : `fondation_base.py → graphe_dependances() → C03`

### EQ-04 — Discipline de source et parc compté

`chaque nombre ⇒ source publique ; douze cases pilier × couche habitées ; chaque extrait de la chaîne ⇒ sous-chaîne du texte mesuré`

> 4 sources publiques · ABONDANCE 54eq/54c/107t · CHIFFRES 17eq/17c/32t · FONDATION 18eq/18c/45t · HORLOGERIE 15eq/15c/64t · CONTINUITE 15eq/15c/23t · REDACTION 16eq/16c/32t · CONSTRUCTION 16eq/16c/42t · VERROUS 16eq/16c/51t · DECLARATION 16eq/16c/31t · GUERRE 16eq/16c/56t · 10 extraits verbatimes · 0 horodatage cité

*Statut* : OPÉRATIONNEL · *chemin* : `fondation_base.py → eq04_confrontation_et_parc() → C04`

### EQ-05 — Bibliothèque standard seule, ici et dans le parc

`imports ⊆ stdlib ∪ modules locaux — ici et dans tout le parc`

> ici ['__future__', 'hashlib', 'inspect', 'json', 'math', 'pathlib', 're', 'sys', 'typing'] ; tiers ici [] ; tiers du parc {'ABONDANCE': [], 'CHIFFRES': [], 'FONDATION': [], 'HORLOGERIE': [], 'CONTINUITE': [], 'REDACTION': [], 'CONSTRUCTION': [], 'VERROUS': [], 'DECLARATION': [], 'GUERRE': [], 'code': [], 'bibliotheques': []}

*Statut* : OPÉRATIONNEL · *chemin* : `fondation_base.py → imports_de(), imports_parc() → C05`

### EQ-06 — Un registre, une valeur par grandeur

`|registre| = noms uniques · aucun doublon en conflit · unité non vide partout`

> 14 entrées, 14 noms uniques, doublons []

*Statut* : OPÉRATIONNEL · *chemin* : `fondation_base.py → registre_grandeurs() → C06`

### EQ-07 — La prédiction est gelée avant la lecture du comparateur

`signature(prediction) ∩ clés_comparateur = ∅ · digest stable`

> signature=['declares'] · digest=242389d120565971… · drapeau sous contamination True

*Statut* : OPÉRATIONNEL · *chemin* : `fondation_base.py → prediction_gel() → C07`

### EQ-08 — Désintégrations ordinaires par désintégration rare

`N_ordinaires = 1/BR − 1, intervalle par les deux branches d'incertitude`

> SM 1.19048e+10 ∈ [1.06383e+10, 1.35135e+10] ; communiqué 9999999999 ⇒ taux implicite 1e-10 ; intervalle 2024 [6.135e+09, 1e+10]

*Statut* : OPÉRATIONNEL · *chemin* : `fondation_base.py → intervalle_ordinaires() → C08`

### EQ-09 — L'acceptance ferme sur des chiffres publiés

`A·ε = 1/(N_K·SES) puis N = N_K·BR_sm·A·ε`

> A·ε 2016-18 4.4144% · 2021-22 4.1377% (rapport 0.9373) · N calculé 10.0119 vs publié 10.01 (écart 0.0192%)

*Statut* : OPÉRATIONNEL · *chemin* : `fondation_base.py → acceptance(), eq09_cloture_acceptance() → C09`

### EQ-10 — Prédiction gelée contre l'excès publié en 2021

`N gelé = 10,01 contre excès publié (candidates − fond)`

> prévu 10.0119 · publié 12.97 · écart +0.7166 σ

*Statut* : OPÉRATIONNEL · *chemin* : `fondation_base.py → prediction_gel() → eq10_prediction_gelee() → C10`

### EQ-11 — Signification Li–Ma sur les chiffres 2021

`z(20 | 7,03) par Li–Ma contre z implicite de la p-value publiée`

> Li–Ma 3.9852 σ · publié 3.3975 σ · écart +0.5877 · les deux sous 5 σ : True

*Statut* : OPÉRATIONNEL · *chemin* : `fondation_base.py → signification_lima(), z_de_p_seuil() → C11`

### EQ-12 — Ce que cinq sigma coûtent en événements

`excès requis pour z = 5 à fond connu, contre excès publié 2024`

> requis 25.0624 · publié 33.00 · marge 7.9376 · Li–Ma 6.3426 vs publié 5.0690

*Statut* : OPÉRATIONNEL · *chemin* : `fondation_base.py → evenements_requis() → C12`

### EQ-13 — Confrontation 2024 : notre z contre le leur

`z = (BR_obs − BR_sm)/√(σ_obs² + σ_sm²), sur les deux branches`

> z ∈ [1.3340, 1.4546] · NA62 déclare 1.7 · chevauchement à 1 σ : False

*Statut* : OPÉRATIONNEL · *chemin* : `fondation_base.py → eq13_confrontation_2024() → C13`

### EQ-14 — Confrontation 2026 : l'écart se referme

`même formule, chiffres 2016-2024 de la mise à jour 2026`

> BR 9.6e-11 · z = 0.5589 (branche basse 0.5828) · sous 1 σ : True

*Statut* : OPÉRATIONNEL · *chemin* : `fondation_base.py → eq14_confrontation_2026() → C14`

### EQ-15 — Budget de fond contre chaîne de rejets

`suppression totale requise = N_K/fond, contre la chaîne de rejets publiée`

> requise 3.841e+11 · chaîne μ×π⁰ 1e+15 · marge +3.416 ordres

*Statut* : OPÉRATIONNEL · *chemin* : `fondation_base.py → eq15_budget_fond() → C15`

### EQ-16 — Géométrie du faisceau : une borne inférieure simulée

`fraction = N_K / (secondaires/s × 6 % × 3 ans × 3,15576·10⁷ s)`

> 0.0004753 — un kaon sur 2104 produits · 6e+07 K⁺/s

*Statut* : SIMULÉ · *chemin* : `fondation_base.py → eq16_geometrie() → C16`

### EQ-17 — Erreur de comptage contre erreur publiée

`σ_Poisson = √(s+b)/s contre erreur relative publiée, deux périodes`

> 2021 0.3448 vs 0.3774 · 2024 0.2164 vs 0.2538 · √N prévu 1.5951 vs mesuré 1.4866

*Statut* : OPÉRATIONNEL · *chemin* : `fondation_base.py → eq17_loi_racine_n() → C17`

### EQ-18 — La limite est le produit

`liste des réfutations internes et des non-preuves`

> 5 conditions de chute, 4 choses non prouvées

*Statut* : SPÉCIFIÉ · *chemin* : `fondation_base.py → eq18_limite_de_la_base() → C18`

## Contrôles numériques

| ID | Contrôle | Attendu | Obtenu | État |
|---|---|---|---|---|
| C01 | l'axiome est posé hors matrice et ne fournit aucun nombre | hors_matrice True · 0 nombre · quatre piliers engendrés | True · 0 · ['P1 UNITE', 'P2 BORNE', 'P3 CONFRONTATION', 'P4 TRANSMISSION'] | reçu |
| C02 | la racine unique du graphe est fondée sur une source extérieure | racines = ['EQ-01'] et fondée dehors True | ['EQ-01'] · True | reçu |
| C03 | graphe acyclique, dix-huit nœuds atteignables, zéro auto-référence | acyclique et atteignables = 18 | acyclique=True atteignables=18 self=[] couches vides=[] | reçu |
| C04 | les douze cases pilier × couche sont habitées ; chaque dossier du parc déclare autant de contrôles que d'équations et porte ses tests ; la chaîne est citée mot pour mot et n'est jamais minutée | aucune case vide · eq = c > 0 et tests > 0 par dossier · extraits verbatimes · 0 horodatage · 0 octet de transcript | aucune · 4 sources · ABONDANCE 54/54 et 107t · CHIFFRES 17/17 et 32t · FONDATION 18/18 et 45t · HORLOGERIE 15/15 et 64t · CONTINUITE 15/15 et 23t · REDACTION 16/16 et 32t · CONSTRUCTION 16/16 et 42t · VERROUS 16/16 et 51t · DECLARATION 16/16 et 31t · GUERRE 16/16 et 56t · extraits tous retrouvés · horodatages [] | reçu |
| C05 | aucun import tiers, ici ni dans le parc | listes vides | ici [] · parc {'ABONDANCE': [], 'CHIFFRES': [], 'FONDATION': [], 'HORLOGERIE': [], 'CONTINUITE': [], 'REDACTION': [], 'CONSTRUCTION': [], 'VERROUS': [], 'DECLARATION': [], 'GUERRE': [], 'code': [], 'bibliotheques': []} | reçu |
| C06 | registre clos : une valeur par grandeur, unité non vide, registre = DECLARE | 0 doublon · 0 unité vide · entrées = noms uniques · hors_declare et declare_sans_entree vides | [] · [] · 14/14 · ∅ · ∅ | reçu |
| C07 | la prédiction ne voit aucune clé du comparateur et ne change pas | intersection vide · digest inaltéré · drapeau levé sous contamination | ∅ · 242389d12056… · True · inaltéré True | reçu |
| C08 | le compte communiqué est l'arrondi 10⁻¹⁰ ; il tombe dans l'intervalle mesuré 2024 — et l'intervalle du modèle standard ne le contient pas | taux implicite = 1,0e-10 · 2024 True · SM écrit tel quel | taux 1e-10 · 2024 True · SM (arrondi hors domaine) False | reçu |
| C09 | les deux Acceptations concordent et le N calculé ferme sur le publié | écart relatif ≤ 1 % · rapport d'acceptations dans [0,9 ; 1,1] | écart 0.0192% · rapport 0.9373 | reçu |
| C10 | l'excès publié reste à moins de 2 σ de la prédiction gelée | |écart| ≤ 2 σ | +0.7166 σ | reçu |
| C11 | 2021 : les deux calculs disent evidence, aucun ne dit observation | max(z) < 5 et Li–Ma > publié | 3.9852 · 3.3975 | reçu |
| C12 | 2024 : l'excès publié dépasse le nombre d'événements requis pour 5 σ | marge > 0 et les deux z > 5 | requis 25.0624 · publié 33.00 · marge 7.9376 | reçu |
| C13 | 2024 : nos z restent sous le z déclaré par NA62, non-chevauchement écrit | max(z) < 1,7 et chevauchement False | z 1.3340/1.4546 · False | reçu |
| C14 | 2026 : l'écart au modèle standard passe sous 1 σ | z < 1 sur les deux branches | 0.5589 · 0.5828 | reçu |
| C15 | la chaîne de rejets publiée est au moins à la hauteur du fond annoncé | marge en ordres de grandeur > 0 | requise 3.841e+11 · chaîne 1e+15 · +3.416 | reçu |
| C16 | fraction des kaons produits qui désintègrent dans le volume utile | 0 < fraction < 1 | 0.0004753 (un sur 2104) | reçu |
| C17 | les deux périodes publient une erreur au-dessus du seul Poisson, et le gain mesuré reste SOUS la loi √N | surcroîts > 0 · gain mesuré < gain prévu | +0.0326 · +0.0374 · 1.4866 < 1.5951 | reçu |
| C18 | la limite est écrite : cinq réfutations, quatre non-preuves, dix-huit limites d'équation non vides | ≥ 4 conditions et ≥ 3 non-preuves et 18/18 limites | 5 · 4 · 18/18 | reçu |

## Source

```
{
  "titre": "Le CERN a Enfin Détecté un Événement que la Science Attendait depuis 40 Ans",
  "chaine": "Nocturne",
  "video_id": "5pP1e69T3HQ",
  "url": "https://www.youtube.com/watch?v=5pP1e69T3HQ",
  "duree_s": 8018,
  "chapitres_publics": 0,
  "transcript": "absent (timedtext : 0 octet en json3, srv3 et xml)",
  "mesure_le": "2026-11-09T01:44:02Z",
  "outils": "scripts/extraire_chapitres_youtube.py (Skill extraire-chapitres-youtube-sans-transcript)",
  "avertissements_sonde": [
    "aucun en-tete de chapitres : horodatages pris dans toute la description",
    "aucun chapitre horodate dans la description",
    "timedtext repond sans contenu : le transcript est tenu pour absent"
  ],
  "sonde_transcript_octets": {
    "json3": 0,
    "srv3": 0,
    "xml": 0
  },
  "description_mesuree_caracteres": 1908,
  "description_retenue": "les deux premiers paragraphes, recopiés mot pour mot ; les paragraphes suivants sont des remerciements, des appels à s'abonner et la liste des sources",
  "description_verbatim": "En septembre 2024, l’expérience NA62 du CERN a annoncé l’observation d’une des désintégrations les plus rares jamais mesurées : un kaon chargé qui se transforme en un pion et deux neutrinos invisibles. Pour la trouver, les physiciens ont dû suivre des centaines de millions de particules par seconde et écarter des milliards de désintégrations ordinaires qui lui ressemblent. Ils ont ainsi rassemblé assez d’événements pour franchir le seuil des cinq sigma, celui qui transforme un simple indice en véritable découverte.\n\nDans ce documentaire, on remonte à la découverte du kaon dans les rayons cosmiques des années 1940. On voit pourquoi le modèle standard rend cette désintégration presque impossible, et comment les expériences de Brookhaven n’en ont capté que quelques événements en deux décennies. On découvre aussi comment le CERN a fini par réussir en étudiant les kaons en plein vol. On regarde enfin ce que ce résultat nous apprend sur la physique au-delà du modèle standard, et ce qu’il laisse encore sans réponse.",
  "extraits_description": [
    "En septembre 2024, l’expérience NA62 du CERN a annoncé l’observation",
    "un kaon chargé qui se transforme en un pion et deux neutrinos invisibles",
    "suivre des centaines de millions de particules par seconde",
    "écarter des milliards de désintégrations ordinaires qui lui ressemblent",
    "franchir le seuil des cinq sigma",
    "la découverte du kaon dans les rayons cosmiques des années 1940",
    "le modèle standard rend cette désintégration presque impossible",
    "les expériences de Brookhaven n’en ont capté que quelques événements en deux décennies",
    "en étudiant les kaons en plein vol",
    "ce que ce résultat nous apprend sur la physique au-delà du modèle standard"
  ],
  "sources_citees_par_la_chaine": [
    "Collaboration NA62, Measurement of the very rare K+→π+νν̄ decay (2021) — https://arxiv.org/pdf/2103.15389",
    "Collaboration NA62, Recent Results from NA62 in Kaon and Dump Mode (2026) — https://arxiv.org/pdf/2605.02415"
  ],
  "ce_que_la_video_n_a_pas_fourni": [
    "aucun chapitre horodaté (donc aucun minutage citable)",
    "aucun transcript (donc aucune citation, aucune phrase attribuée à la bande-son)",
    "aucun chiffre : les nombres de ce dossier viennent des publications arXiv et du communiqué CERN, jamais de la vidéo"
  ]
}
```

## Valeurs déclarées

```
{
  "BR_sm": 8.4e-11,
  "dBR_sm": 1e-11,
  "N_K_2016_2018": 2700000000000.0,
  "SES_2016_2018": 8.39e-12,
  "N_K_2021_2022": 2850000000000.0,
  "SES_2021_2022": 8.48e-12,
  "secondaires_par_s": 1000000000.0,
  "fraction_K_plus": 0.06,
  "annees_prises_2016_2018": 3.0,
  "rejection_mu": 10000000.0,
  "rejection_pi0": 100000000.0,
  "rejection_autres_canaux": 10000.0,
  "seuil_observation": 5.0,
  "z_declare_2024": 1.7
}
```

> Document calculé, non écrit à la main : régénérer le module régénère la page.
