# CONTINUITÉ — énoncé, cheminement, résultat

**Domaine déclaré** D = [61/500 ; 249/400]
**Rapport de contraction** ρ = (249/400)^(1/12) ∈ [96126/100000 ; 96127/100000]

## Cheminement

1. les semences sont importées de `lib_almizan_extension.py`, puis écrites en rationnels ;
2. ρ est encadré par recherche dichotome sur des douzièmes puissances entières ;
3. la chaîne x_k = MIZAN·ρ^k est strictement décroissante et minorée par 0 ;
4. le télescopage Σ(x_{k−1} − x_k) = x_0 − x_N prouve qu'aucune valeur n'apparaît ni disparaît le long de la chaîne ;
5. la chaîne sort de D au pas 42 (prouvé par entiers aux pas 41 et 42) ;
6. clampée sur D, elle converge vers l'unique point fixe 61/500 en au plus 42 pas depuis n'importe lequel des 27 nœuds déclarés.

## Résultat

La continuité de cette chaîne est **entière, sans perte, et bornée** : elle ne peut pas se poursuivre au-delà de son propre domaine. Le nombre de pas disponibles — 42 — est une conséquence calculée, pas une décision.

## Ce que cela ne dit pas

- le théorème porte sur une application déclarée sur un intervalle déclaré : il s'applique au catalogue du dépôt, pas à la propagation du savoir humain
- les semences (0.6225, 0.122, 0.021) sont des constantes de conception de lib_almizan_extension.py ; rien dans ce dossier montre qu'elles mesurent quelque chose
- les 42 pas sont un compte d'itérations : ni une durée, ni une portée, ni une prévision
- le catalogue est stocké arrondi (8 et 6 décimales) : les dérives mesurées sont des défauts d'écriture du catalogue, pas des réfutations
- aucune des croix du plan global n'est remplie par cette couche
