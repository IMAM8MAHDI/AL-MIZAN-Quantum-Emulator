# RÉSUMÉ EXÉCUTIF ACADÉMIQUE

**Titre** : Classification arithmétique exacte, signatures quadratiques et structures normiques du système AL-MIZAN
**Auteur** : M. Ahmed EL BAHLOUL (IMAM8MAHDI) × Devin (SWE-2), Cognition AI
**DOI** : 10.5281/zenodo.24028242 · **Licence** : AGPL-3.0 / GPL-3.0 (double licence, LICENSE.md)

## Abstract

Cette contribution formalise l'infrastructure arithmétique rigide du système déterministe Al-Mizan au moyen d'un émulateur en arithmétique exacte (fractions et entiers purs, sans approximation flottante). La recherche exhaustive d'invariants a mis au jour une structure de type « partie puissante » (powerful part) régissant les constantes du système, ainsi qu'un théorème de classification discriminant les cycles temporels par des équations de formes normiques au sein d'extensions quadratiques globales.

## 1. Fondements et décomposition en noyau sans facteur carré

Le système extrait quatre cycles fondamentaux (d_x, d_y, d_z, d_t) d'une matrice fixe appelée LA TABLE Point Zéro. L'analyse de factorisation montre que ces cycles obéissent strictement à la décomposition n = k²·μ, où μ désigne le noyau sans facteur carré. Alors que les constantes de substance (pôle 313, base 19) sont premières ou libres de carrés, les constantes cinétiques déduites accumulent des conducteurs métriques carrés massifs.

## 2. Théorème des Semences et classification calendaire

L'opérateur de degré global Q = 1536 = 16²·6 a pour classe de carrés 6 dans
ℚ×/(ℚ×)². Les cycles, **rendus en heures**, sont des rationnels :

    d'_x = dx/128 = 6 403 563/128        d'_y = dy/2 = 93 987/2

Dans ℚ×/(ℚ×)² exactement : [Q] = [d'_x] = [d'_y] = 6, alors que
[d_z] = 15 et [d'_t] = 47 441 478. Comme `Q·c` est un carré si et seulement
si `[c] = [Q]`, la loi s'écrit sans approximation :

- Soleil : Q·d'_x = 8766² — année solaire en heures (= 18·487)
- Lune : Q·d'_y = 8496² — année lunaire en heures (= 144·59)

et, sous forme entière équivalente (celle qu'un tiers peut vérifier sans
connaître l'échelonnage) : **8766² = 12·dx**, **8496² = 768·dy**.

Portée exacte de la sélectivité : sur l'ensemble **fini des quatre cycles**
du système, seuls le solaire et le lunaire partagent la classe de Q — donc
« exclusivement » vaut sur ces quatre éléments, et sur rien de plus. Sur les
numérateurs entiers non échelonnés, `Q·dx`, `Q·dy`, `Q·dz`, `Q·dt` ne sont
jamais des carrés (classes 3, 3, 15, 47 441 478 ≠ 6).

Les numérateurs partagent la grammaire 27·p² sur les gènes premiers p = 487 (Soleil) et p = 59 (Lune). Le quotient fondamental : d'_x/d'_y = (487/472)².

## 3. Classes spatiales et de synchronisation

- **Terrestre** (d_z) : la clé Q_espace = 15 résout 15·d_z = 45000² — 45000 secondes = 12,5 heures exactes (demi-jour).
- **Synchronisation** (d_t) : d_t,num = 3⁷·7·7906913. L'invariant 7906913 = 7·1129559 et se construit sur le gène solaire : 7906913 = 16236·487 − 19.

## 4. Clôture du dernier gardien

Le résidu premier 1129559 est la norme d'un entier algébrique de ℚ(√−7) :

$$1\,129\,559 = 884^2 + 7\cdot 223^2 = N(884 + 223\sqrt{-7})$$

## Conclusion

Le système Al-Mizan réalise une fermeture arithmétique quasi-totale : un modèle d'horlogerie diophantienne où espace, alphabet harmonique et cycles temporels sont les projections coordonnées d'une unique algèbre de contraintes. Tous les résultats sont certifiés par calcul exact et scellés SHA-256 ; l'émulateur, les certificats et la suite de tests (48 tests) sont publiés sur GitHub sous double licence AGPL-3.0 / GPL-3.0.
