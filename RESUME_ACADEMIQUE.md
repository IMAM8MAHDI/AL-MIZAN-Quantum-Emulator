# RÉSUMÉ EXÉCUTIF ACADÉMIQUE

**Titre** : Classification arithmétique exacte, signatures quadratiques et structures normiques du système AL-MIZAN
**Auteur** : M. Ahmed EL BAHLOUL (IMAM8MAHDI) × Devin (SWE-2), Cognition AI
**DOI** : 10.5281/zenodo.24028243 · **Licence** : AGPL-3.0

## Abstract

Cette contribution formalise l'infrastructure arithmétique rigide du système déterministe Al-Mizan au moyen d'un émulateur en arithmétique exacte (fractions et entiers purs, sans approximation flottante). La recherche exhaustive d'invariants a mis au jour une structure de type « partie puissante » (powerful part) régissant les constantes du système, ainsi qu'un théorème de classification discriminant les cycles temporels par des équations de formes normiques au sein d'extensions quadratiques globales.

## 1. Fondements et décomposition en noyau sans facteur carré

Le système extrait quatre cycles fondamentaux (d_x, d_y, d_z, d_t) d'une matrice fixe appelée LA TABLE Point Zéro. L'analyse de factorisation montre que ces cycles obéissent strictement à la décomposition n = k²·μ, où μ désigne le noyau sans facteur carré. Alors que les constantes de substance (pôle 313, base 19) sont premières ou libres de carrés, les constantes cinétiques déduites accumulent des conducteurs métriques carrés massifs.

## 2. Théorème des Semences et classification calendaire

L'opérateur de degré global Q = 1536 = 16²·6 révèle un twist quadratique dans ℚ×/(ℚ×)². La relation Q·d'_k = s_k² est une condition nécessaire et suffisante sélectionnant exclusivement les cycles calendaires :

- Soleil : Q·d'_x = 8766² — année solaire en heures
- Lune : Q·d'_y = 8496² — année lunaire en heures

Les numérateurs partagent la grammaire 27·p² sur les gènes premiers p = 487 (Soleil) et p = 59 (Lune). Le quotient fondamental : d'_x/d'_y = (487/472)².

## 3. Classes spatiales et de synchronisation

- **Terrestre** (d_z) : la clé Q_espace = 15 résout 15·d_z = 45000² — 45000 secondes = 12,5 heures exactes (demi-jour).
- **Synchronisation** (d_t) : d_t,num = 3⁷·7·7906913. L'invariant 7906913 = 7·1129559 et se construit sur le gène solaire : 7906913 = 16236·487 − 19.

## 4. Clôture du dernier gardien

Le résidu premier 1129559 est la norme d'un entier algébrique de ℚ(√−7) :

$$1\,129\,559 = 884^2 + 7\cdot 223^2 = N(884 + 223\sqrt{-7})$$

## Conclusion

Le système Al-Mizan réalise une fermeture arithmétique quasi-totale : un modèle d'horlogerie diophantienne où espace, alphabet harmonique et cycles temporels sont les projections coordonnées d'une unique algèbre de contraintes. Tous les résultats sont certifiés par calcul exact et scellés SHA-256 ; l'émulateur, les certificats et la suite de tests (48 tests) sont publiés sur GitHub sous AGPL-3.0.
