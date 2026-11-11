# MÉTADONNÉES POUR DÉPÔT HAL

## Type de document
**Logiciel / Software**

## Titre
**AL-MIZAN : Émulateur quantique pur Python avec certificats mathématiques scellés pour les problèmes du millénaire**

## Titre anglais
**AL-MIZAN: A Pure-Python Quantum Emulator with Sealed Mathematical Certificates for Millennium Problems**

## Auteurs
**EL BAHLOUL, M. Ahmed**
- Affiliation : IMAM8MAHDI Research Initiative, Valence, France
- Email : elbahloulahmed505@gmail.com
- ORCID : (non renseigné)
- Rôle : Auteur principal, concepteur, développeur

**Devin (SWE-2), Cognition AI**
- Rôle : Assistance IA pour génération de code, tests et documentation
- Note : Conformément à la politique HAL sur l'IA générative, l'utilisation de Devin est déclarée

## Résumé (Français)
AL-MIZAN est un émulateur quantique complet implémenté en Python pur sans dépendances externes, unifiant la simulation par vecteur d'état, l'évolution par matrice densité, la correction d'erreurs quantiques (code Steane [[7,1,3]]), l'extrapolation à bruit nul (ZNE) et la génération de layout GDSII pédagogique. Au-delà de la simulation quantique, le paquetage fournit des certificats mathématiques scellés SHA-256 pour des vérifications bornées de problèmes du millénaire : la Conjecture du Point Carré (PC-1..PC-6 vérifiées par exhaustion sur le domaine fini déclaré), le théorème de Turing sur la bande de Riemann ≤100 (29 zéros certifiés par arithmétique d'intervalles), et la vérification BSD sur des courbes elliptiques nommées. L'architecture maintient des contraintes d'honnêteté strictes — chaque artefact porte sa borne de calcul, et aucun problème ouvert du millénaire n'est revendiqué comme résolu.

**Mots-clés français :** émulateur quantique, Python, correction d'erreurs quantiques, hypothèse de Riemann, conjecture BSD, certificats mathématiques, simulation quantique, OpenQASM, code Steane, extrapolation à bruit nul

## Abstract (English)
AL-MIZAN is a complete quantum emulator implemented in pure Python with zero external dependencies, unifying state vector simulation, density matrix evolution, quantum error correction (Steane [[7,1,3]] code), zero-noise extrapolation (ZNE), and pedagogical GDSII layout generation. Beyond quantum simulation, the package provides sealed SHA-256 mathematical certificates for bounded verifications of millennium problems: the Point Square Conjecture (PC-1..PC-6 verified by exhaustive computation over the declared finite domain), Turing's theorem on the Riemann strip ≤100 (29 zeros certified via interval arithmetic), and BSD verification on named elliptic curves. The architecture maintains strict honesty constraints—every artifact carries its computational bound, and no open millennium problem is claimed as solved.

**Keywords English:** quantum emulator, Python, quantum error correction, Riemann hypothesis, BSD conjecture, mathematical certificates, quantum simulation, OpenQASM, Steane code, zero-noise extrapolation

## Domaine scientifique
- **Informatique** / Calcul formel
- **Mathématiques** / Physique mathématique
- **Physique** / Mécanique quantique

## Licence
**AGPL-3.0** (GNU Affero General Public License v3.0)
- Licence ouverte, copyleft fort
- Compatible avec diffusion publique
- Voir fichier LICENSE-AGPL dans le dépôt

## Dépôt GitHub
https://github.com/IMAM8MAHDI/AL-MIZAN-Quantum-Emulator

## DOI Zenodo associé
10.5281/zenodo.24028242
https://doi.org/10.5281/zenodo.24028242

## Version
3.3.2 — dernière version effectivement publiée sur Zenodo
(DOI 10.5281/zenodo.24122287, archive `AL-MIZAN_v332_c9b7fbd.zip`, contrôle du 2026-11-11 fait
dans l'archive re-téléchargée : 250 membres = les 249 entrées scellées + `MANIFESTE_SHA256.txt`,
233 re-hachages exacts, 16 CSV « Excel français » conformes après seule normalisation des fins de
ligne, 0 divergent).
Le contenu de l'arbre de travail est postérieur : il ajoute `QPU_DISTANT/` et `GOULETS/`, soit
219 équations, 219 contrôles, 14 modules CONFORME, 654 tests et un sceau de 276 entrées portant
0 date. Le prochain numéro n'est pas encore publié et ne doit pas figurer dans un dépôt
avant l'émission de l'enregistrement.

## Date de publication
11 novembre 2026 (version 3.3.2 publiée)

## Fichiers à déposer
1. **ZENODO_DEPOT_ALMIZAN.zip** (archive complète du dépôt)
   - Code source Python (l'émulateur et les équations réparties dans les douze dossiers
     d'équations — 219 équations, 219 contrôles, 14 modules audités — compte relevé par
     `FONDATION/fondation_base.py → inventaire_parc()` et
     `FONDATION/OUTILS/audit_piliers.py --tous --rigide`, pas saisi à la main)
   - 53 tests unitaires pour l'émulateur, 654 pour le dépôt complet
   - Documentation complète (README, PRESENTATION, paper.md)
   - Métadonnées (.zenodo.json, CITATION.cff)
   - Licences (AGPL-3.0, GPL-3.0)
   - Résultats scellés SHA-256

2. **paper.md** (article JOSS, peut servir de documentation scientifique)

3. **paper.bib** (bibliographie complète)

## Déclaration IA (obligatoire HAL)
Ce logiciel a été développé avec l'assistance d'IA générative (Devin SWE-2, Cognition AI) pour la génération de code, les tests et la documentation. L'auteur humain (M. Ahmed EL BAHLOUL) a révisé, validé et dirigé tous les résultats, et a pris les décisions de conception fondamentales incluant la doctrine Al-Mizan, les règles du noyau scellé, l'architecture des certificats mathématiques et les contraintes d'honnêteté. Tout le code généré par IA a été inspecté manuellement et intégré sous supervision humaine.

## Relations avec d'autres publications
- **Source de l'émulateur :** ASTRO-Q°ODE_SYSTEME — aucun identifiant Zenodo résolvable
  à ce jour : 10.5281/zenodo.23554838 ne répond pas (handle 404) et
  10.5281/zenodo.23479740 comme 10.5281/zenodo.23288947 renvoient une page
  Zenodo 410 « Gone » (contrôlés le 2026-11-10). La relation est donc titrée,
  sans identifiant.
- **Version publiée de AL-MIZAN :** DOI: 10.5281/zenodo.24028242 (DOI de concept,
  résout vers la dernière version) et DOI: 10.5281/zenodo.24122287 (v3.3.2)

## Notes de dépôt
- Logiciel développé dans le cadre de l'initiative IMAM8MAHDI
- Architecture "sans dolosif" : honnêteté scientifique stricte sur les capacités et limitations
- Chaque certificat mathématique porte des bornes explicites
- Émulation classique dans ce dépôt : aucun qubit n'y tourne et aucune exécution distante n'y est
  pilotée. `QPU_DISTANT/` relit et re-borne l'archive d'un job déjà exécuté chez le fournisseur
  (`ibm_marrakesh`, statut `Completed`, 256 tirs), sans qiskit ni numpy.
- 53 tests unitaires pour l'émulateur, 654 pour le dépôt complet — tous verts
- Documentation bilingue français/anglais
