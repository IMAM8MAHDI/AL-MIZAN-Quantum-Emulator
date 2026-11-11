# COMMUNIQUÉ DE PRESSE

## POUR DIFFUSION IMMÉDIATE

---

# Un chercheur français publie un émulateur quantique open source avec certificats mathématiques scellés pour les problèmes du millénaire

**Valence, France — 9 novembre 2026** — M. Ahmed EL BAHLOUL, chercheur indépendant de l'initiative IMAM8MAHDI, annonce la publication de **AL-MIZAN v3.2.2**, un émulateur quantique complet implémenté en Python pur sans aucune dépendance externe, accompagné de certificats mathématiques cryptographiquement scellés pour la vérification bornée de problèmes du millénaire.

### Une architecture sans précédent

AL-MIZAN unifie en un seul paquetage open source (licence AGPL-3.0/GPL-3.0) :

- **Simulation quantique complète** : vecteur d'état (16 qubits), matrice densité (8 qubits), code de correction d'erreur Steane [[7,1,3]], extrapolation à bruit nul (ZNE Richardson), et générateur de layout GDSII pédagogique.
- **Certificats mathématiques scellés SHA-256** : vérification bornée de la conjecture du Point Carré (PC-1 à PC-6 vérifiés par exhaustion sur le domaine fini déclaré), théorème de Turing sur la bande de Riemann ≤100 (29 zéros non triviaux certifiés sur Re=½ par arithmétique d'intervalles), et vérification de la conjecture BSD sur trois courbes elliptiques nommées.
- **Contraintes d'honnêteté strictes** : chaque artefact porte sa borne de calcul explicite. Aucun problème ouvert du millénaire n'est revendiqué comme résolu.

### Des résultats reproductibles

Le paquetage d'émulation quantique passe **53 tests unitaires et d'intégration avec un taux de réussite de 100%** (0 ignoré), couvrant la préparation d'états, les opérations de portes, les permutations, les métriques d'intrication, l'échantillonnage de Born, les modèles de bruit (trajectoire et Kraus), l'analyse QASM, les algorithmes Deutsch-Jozsa/téléportation/QPE, les bornes variationnelles VQE, la factorisation de Shor, l'encodage GDSII, les règles DRC, l'extrapolation ZNE, le code Steane, et l'arbre des sept problèmes du millénaire. Le dépôt complet — émulateur, horloge du noyau, et les douze dossiers d'équations ABONDANCE, CHIFFRES, FONDATION, HORLOGERIE, CONTINUITE, REDACTION, CONSTRUCTION, VERROUS, DECLARATION, GUERRE, QPU_DISTANT et GOULETS — en compte **654, tous verts** (53 + 10 + 107 + 32 + 45 + 64 + 23 + 32 + 42 + 62 + 37 + 56 + 28 + 38), et ses 219 équations sont notées par un seul outil, `FONDATION/OUTILS/audit_piliers.py --tous --rigide`, qui rend 14 modules CONFORME et sort sur code 0 (mesure du 11 novembre 2026).

### Pourquoi c'est important

« Les revendications publiques sur le calcul quantique résolvant les problèmes du millénaire manquent souvent de reproductibilité et de périmètre clair, » explique M. EL BAHLOUL. « AL-MIZAN propose une architecture de certificats où chaque théorème porte un sceau SHA-256, des bornes de domaine explicites, et des déclarations honnêtes de limitations. C'est un modèle pour les mathématiques computationnelles rigoureuses. »

Le logiciel fonctionne sur tout environnement Python 3.10+ sans accès matériel QPU, le rendant adapté à l'enseignement, au prototypage rapide, et aux mathématiques computationnelles transparentes.

### Disponibilité

- **GitHub** : https://github.com/IMAM8MAHDI/AL-MIZAN-Quantum-Emulator
- **Zenodo (archive peer-reviewed)** : https://doi.org/10.5281/zenodo.24028242 — DOI de concept, c'est la référence citable, il résout toujours vers la dernière version déposée
- **Dernière version** : v3.3.2, https://doi.org/10.5281/zenodo.24122287 (11 novembre 2026) — `criteres_derivation_sans_intrant.py` : six équations EQ-DSI-01..06 qui décident si une forme fermée offerte pour une constante mesurée relève de la dérivation ou de la coïncidence ; sur la forme examinée (79 + 48√2 + 42√3 + 3√6)/31104 la reproduction vaut 1,42 × 10⁻¹³ et l'écart normalisé z = 0,5983879635182564 contre CODATA 2022, le recensement exact des 40 959 999 formes a + b√2 + c√3 + d√6 sur n ≤ 31 104 rendant cette forme 47ᵉ à 0,6σ ; verdict borné au texte public examiné, sans jugement d'intention. Sa suite de 25 tests est la treizième documentée et portait le total à 588, le manifeste passant de 245 à 249 entrées scellées sur le HEAD `c9b7fbd` ; contrôle fait dans l'archive re-téléchargée : 250 membres, 233 re-hachages exacts, 16 CSV conformes après seuls fins de ligne, 0 divergent. **En préparation, v3.4.0** ajoute `QPU_DISTANT/` (10 équations, 10 contrôles : le job `dbpkmr0ou4as73ctrm80` joué sur `ibm_marrakesh`, 256 tirs sur le support [0,1], relu et re-borné ici — 1,169047 s observées contre 1,082785 s déclarées, compteurs recalculés 00 126 · 01 22 · 11 108 (somme 256, donc 10 à 0), parité 0,9140625 = 234/256, borne de médiane machine non reçue à −0,676σ, borne de support réel reçue à +0,150σ, asymétrie 22 contre 0 rejetant l'équiprobabilité à p = 4,77 × 10⁻⁷ sous Binom(22,½) exact en entiers ; le module ne fait tourner aucun qubit et ne teste aucune équation d'AL-MIZAN) et `GOULETS/` (10 équations, 10 contrôles : 23 vidéos comptées, durée maximale 30 s contre seuil déclaré 900 s soit 870 s de marge, barème 99 publications/jour contre plafond constaté 10/jour, cadence observée 1,3529/jour, 78 fichiers et 1 432,543 s en stock, 35 434 115 072 octets libres sur 252 841 029 632 soit 14,01 % ; quatre bornes datées et falsifiables, aucune levée de plafond revendiquée). Le registre passe à 219 équations, 219 contrôles et 14 modules CONFORME, les suites à 654 tests, le sceau à 276 entrées portant 0 date et `pages_depot/` à 21 fichiers.
- **Versions précédentes** : v3.3.1, https://doi.org/10.5281/zenodo.24114682 (10 novembre 2026) — `pages_depot/` : le site public al-mizan.world se régénère depuis le dépôt seul (mesuré sur une copie sans `.git`, sans variable d'environnement et sans clone voisin : 17 fichiers produits, 17 identiques octet pour octet aux pages servies), `docs/API_PASSERELLE_VPS.md` (table des routes réellement servies) et `oeuvre_universelle/espace_disque.py` (13 équations, 13 contrôles), ces trois nouveautés restant hors du registre d'audit ; 563 tests verts dans un clone — 556 dans l'archive ZIP seule, où 7 relectures d'histoire git s'ignorent d'elles-mêmes —, 199 équations et 199 contrôles, 12 modules CONFORME, manifeste de 245 entrées scellées sur le HEAD `50afbb8`, archive re-téléchargée identique octet pour octet ; v3.3.0, https://doi.org/10.5281/zenodo.24105422 (10 novembre 2026) — dossiers VERROUS (registre d'accès et exposition mesurées de la protection), DECLARATION (antériorité, fractales, ablation) et GUERRE (richesse et guerre, mesure et falsification), manifeste de 240 entrées scellées sur le HEAD `9d80f3f` ; v3.2.2, https://doi.org/10.5281/zenodo.24091259 (9 novembre 2026) — dossier HORLOGERIE (identité d'horloge `dx + dy + dz = dt` en arithmétique rationnelle exacte, vérificateur autonome qui n'importe pas le dépôt, confrontation aux éphémérides publiques) et son écran de laboratoire, 311 tests, 104 équations, 6 modules CONFORME, manifeste de 204 entrées ; v3.2.1, https://doi.org/10.5281/zenodo.24075082 (9 novembre 2026) ; v3.2.0, https://doi.org/10.5281/zenodo.24074846 (9 novembre 2026) ; v3.1.0, https://doi.org/10.5281/zenodo.24062292 (8 novembre 2026) ; v3.0.0, https://doi.org/10.5281/zenodo.24054060
- **Licence** : AGPL-3.0 / GPL-3.0 (double licence open source)

### À propos de l'auteur

M. Ahmed EL BAHLOUL est chercheur indépendant basé à Valence, France. Son travail porte sur la simulation quantique classique, la vérification computationnelle bornée, et l'architecture de certificats mathématiques avec contraintes d'honnêteté. AL-MIZAN est développé dans le cadre de l'initiative IMAM8MAHDI.

### Contact

M. Ahmed EL BAHLOUL
Email : elbahloulahmed505@gmail.com
GitHub : https://github.com/IMAM8MAHDI

---

**Note aux éditeurs :** Des captures d'écran, diagrammes d'architecture, et accès au code source sont disponibles sur demande. Le logiciel est entièrement open source et peut être cloné, testé, et audité librement.

**Mots-clés :** émulateur quantique, Python, correction d'erreur quantique, hypothèse de Riemann, conjecture BSD, certificats mathématiques, OpenQASM, code Steane, extrapolation à bruit nul, arithmétique d'intervalles, open source, AGPL-3.0

---

*Fin du communiqué*
