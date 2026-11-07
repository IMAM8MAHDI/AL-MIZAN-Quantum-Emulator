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
1.0.0

## Date de publication
7 novembre 2026

## Fichiers à déposer
1. **ZENODO_DEPOT_ALMIZAN.zip** (archive complète du dépôt)
   - Code source Python (13 modules quantiques + 14 modules certificats)
   - 48 tests unitaires
   - Documentation complète (README, PRESENTATION, paper.md)
   - Métadonnées (.zenodo.json, CITATION.cff)
   - Licences (AGPL-3.0, GPL-3.0)
   - Résultats scellés SHA-256

2. **paper.md** (article JOSS, peut servir de documentation scientifique)

3. **paper.bib** (bibliographie complète)

## Déclaration IA (obligatoire HAL)
Ce logiciel a été développé avec l'assistance d'IA générative (Devin SWE-2, Cognition AI) pour la génération de code, les tests et la documentation. L'auteur humain (M. Ahmed EL BAHLOUL) a révisé, validé et dirigé tous les résultats, et a pris les décisions de conception fondamentales incluant la doctrine Al-Mizan, les règles du noyau scellé, l'architecture des certificats mathématiques et les contraintes d'honnêteté. Tout le code généré par IA a été inspecté manuellement et intégré sous supervision humaine.

## Relations avec d'autres publications
- **Version révisée de :** ASTRO-Q°ODE_SYSTEME (DOI: 10.5281/zenodo.23554838)
- **Voir aussi :** DOI: 10.5281/zenodo.23479740, DOI: 10.5281/zenodo.23288947

## Notes de dépôt
- Logiciel développé dans le cadre de l'initiative IMAM8MAHDI
- Architecture "sans dolosif" : honnêteté scientifique stricte sur les capacités et limitations
- Chaque certificat mathématique porte des bornes explicites
- Émulation classique uniquement (pas de QPU matériel)
- 48 tests unitaires tous verts
- Documentation bilingue français/anglais
