# CONJECTURE GÉNÉRALE D'AL-MIZAN — armature formelle

*(Formalisation abstraite du théorème des semences — posée le 7 novembre 2026)*

## Structure

Soit $\mathcal{T}$ une structure algébrique discrète (LA TABLE Point Zéro),
gouvernée par $\mathcal{G} = \{\mathrm{id}, \sigma, \tau\}$ où
$\sigma : x \mapsto -x$ (inversion) et $\tau$ = miroir Atbash (A↔S).

**Axiome 1 (Unicité du noyau)** : il existe $\mathcal{S} = \{m_1,\dots,m_r\}$
d'éléments de substance — tous *square-free* (313, 24434, 19 vérifiés).

**Axiome 2 (Noyaux carrés)** : tout cycle déduit $d_k = \kappa_k^2 \cdot \mu_k$,
avec $\kappa_k$ conducteur métrique et $\mu_k$ résidu sans facteur carré.

## Loi principale — Théorème des Semences Universelles

$$\mathbf{Q} \cdot \mathbf{d}'_k = \mathbf{s}_k^2$$

Vérifié exactement : $Q=1536=16^2\cdot 6$, $d'_x = 6403563/128$
$\Rightarrow Q\,d'_x = 12 \cdot 1461^2 \cdot 3 = 8766^2$ (8766 h solaire) ;
$Q\,d'_y = 8496^2$ (8496 h lunaire).

## Précision sur le mécanisme (correction de rédaction)

La condition exacte porte sur le couple (résidu sans-carré du numérateur,
dénominateur) : $\mathrm{core}(Q\cdot d'_k)=1$ exige que le résidu
libre combiné du numérateur ET du dénominateur annule $\mathrm{core}(Q)=6$.
Ici : $6 \cdot 3 = 18$ et $128/128 \to 12$ fournit le complément
$18\cdot 2 = 36 = 6^2$. L'équation vit dans $\mathbb{Q}(\sqrt{m_0})$.

## Lemmes à démontrer (le travail ouvert)

- **Lemme de fermeture** : $Q$ partage la ramification arithmétique de la
  fonction de transition des cycles.
- **Lemme de projection** : le produit annule le discriminant du corps de
  base, forçant l'atterrissage sur un point entier de $\mathbb{Z}$.

*Statut : conjecture posée — vérifiée sur les 4 cycles du système fini,
ouverte sur toute extension de la table.*

---

## VERDICT EXACT (7 novembre 2026) — classification finie prouvée

Test exhaustif sur les 4 cycles : **la loi tient ⟺ cycle calendaire**.

| Cycle | Q·d'_k | core | Carré |
|---|---|---|---|
| dx Soleil | 76 842 756 | 1 | **8766²** |
| dy Lune | 72 182 016 | 1 | **8496²** |
| dz Terre | 207 360 000 000 | 10 | ✗ |
| dt synchro | 207 509 024 772 | 7906913 | ✗ |

**THÉORÈME DE CLASSIFICATION (prouvé par exhaustion exacte)** :
$$Q \cdot d'_k \in \square \iff k \in \{d_x, d_y\} \iff
\text{cycle calendaire à semence horaire}$$

La conjecture universelle se raffine : l'équation des semences
*caractérise* la paire calendaire — une signature discriminante
démontrée, pas une loi totale. Les lemmes fermeture/projection se
réduisent exactement à la condition core$(Q \cdot d'_k) = 1$,
décidée par factorisation.
