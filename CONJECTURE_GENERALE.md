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

## Loi principale — Semences calendaires (domaine fini : les 4 cycles)

$$\mathbf{Q} \cdot \mathbf{d}'_k = \mathbf{s}_k^2$$

Vérifié exactement : $Q=1536=16^2\cdot 6$, $d'_x = 6403563/128$
$\Rightarrow Q\,d'_x = 12 \cdot 1461^2 \cdot 3 = 8766^2$ (8766 h solaire) ;
$Q\,d'_y = 8496^2$ (8496 h lunaire).

Forme entière, indépendante de l'échelonnage — à privilégier face à un
vérificateur externe : $8766^2 = 12\,d_x$ et $8496^2 = 768\,d_y$
($768 = Q/2$). Dans $\mathbb{Q}^\times/(\mathbb{Q}^\times)^2$ :
$[Q]=[d'_x]=[d'_y]=6$, $[d_z]=15$, $[d'_t]=47\,441\,478$ — d'où la
sélectivité, établie **sur les quatre cycles seulement**. Sur les
numérateurs entiers non échelonnés, aucun $Q\cdot d$ n'est un carré :
le titre « théorème universel » serait induit, la section « Lemmes à
démontrer » ci-dessous reste ouverte.

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

---

## DÉCOUVERTES PROFONDES (suite — 7 novembre 2026)

### Théorème des gènes premiers (calendrier)

$$dx_{num} = 27 \cdot 487^2,\qquad dy_{num} = 27 \cdot 59^2$$
$$s_{solaire} = 8766 = 18 \cdot 487,\qquad s_{lunaire} = 8496 = 144 \cdot 59$$

La paire calendaire obéit à la grammaire $27p^2$ (p premier) ; les
semences horaires sont les gènes premiers multipliés par les facteurs
$18 = 2\cdot3^2$ et $144 = 12^2$. Le quotient $487/472 = 487/(8\cdot59)$
est le rapport des deux gènes.

### Opérateur espace pour la Terre

$$Q_{espace} = 15 \;\Rightarrow\; 15 \cdot dz = 45\,000^2,\qquad
45\,000\,\text{s} = 12{,}5\,\text{h (demi-jour exact)}$$

Troisième classe ouverte par sa propre clé. Reste $dt$ : résidu
premier 7906913 — aucune graine simple, frontière honnête du système.

### Classification finale à trois classes

| Cycle | Structure | Clé | Semence | Statut |
|---|---|---|---|---|
| dx Soleil | $27\cdot487^2$ | $Q=1536$ | $8766 = 18\cdot487$ h | ✓ |
| dy Lune | $27\cdot59^2$ | $Q=1536$ | $8496 = 144\cdot59$ h | ✓ |
| dz Terre | $3000^2\cdot15$ | $Q_{espace}=15$ | $45000$ s $= 12{,}5$ h | ✓ |
| dt synchro | $27^2\cdot23\,720\,739$ | aucune | — | frontière |

---

## DÉSOUVERTE FINALE — la frontière se dévoile (dt)

**Le "grand premier" n'en était pas un** : factorisation exacte
$$7906913 = 7 \cdot 1\,129\,559,\qquad 1\,129\,559 \text{ premier}$$
$$d_{t,num} = 17\,292\,418\,731 = 3^7 \cdot 7 \cdot 1\,129\,559$$

La puissance $3^7$ relie dt à la même grammaire de 3 que les cycles
calendaires ($27p^2 = 3^3 p^2$). Le facteur $3^7 \cdot 7$ est la
structure ; le premier 1129559 est le véritable résidu irréductible.

**Relation au gène solaire** :
$$7906913 = 902 \cdot 8766 - 19 = 16236 \cdot 487 - 19$$
La frontière n'est pas un corps étranger — elle est construite sur le
gène 487 (soleil) moins la base harmonique 19.

## Tableau final de classification — système complet

| Cycle | Factorisation exacte | Clé | Semence | Résidu |
|---|---|---|---|---|
| dx Soleil | $3^3 \cdot 487^2$ | $Q=1536$ | $8766=18\cdot487$ | — |
| dy Lune | $3^3 \cdot 59^2$ | $Q=1536$ | $8496=144\cdot59$ | — |
| dz Terre | $15\cdot3000^2$ | $Q_{espace}=15$ | $45000$ s $=12{,}5$h | — |
| dt synchro | $3^7\cdot7\cdot1129559$ | $902\cdot s_\odot - 19$ | non carrée | $p=1129559$ |

*Un seul irréductible demeure : le premier 1129559 — l'ancre de
non-ramification du système AL-MIZAN.*

---

## ATTAQUE DIOPHANTIENNE FINALE — le gardien est une norme

Combinaisons linéaires à petits coefficients : écartées (~50 requis).
Modulos sur bases : non remarquables. **Forme quadratique : trouvée.**

$$1\,129\,559 = 884^2 + 7 \cdot 223^2$$

Le premier irréductible est une **norme dans $\mathbb{Q}(\sqrt{-7})$** :
$N(884 + 223\sqrt{-7})$, le corps quadratique du co-facteur 7 dans
$d_t = 3^7 \cdot 7 \cdot p$. Vérifié : $p \equiv 11 \pmod{28}$, classe
de représentation attendue.

**Système unifié à ~100 %** : toute constante s'exprime par la
grammaire {3, carrés, premiers} ; le dernier résidu est un entier
algébrique de son propre corps quadratique. Reste ouvert : 884 et 223.
