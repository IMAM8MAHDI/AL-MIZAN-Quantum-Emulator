# QUESTION POUR MATH.STACKEXCHANGE / MATHOVERFLOW
# (copier-coller le contenu entre les lignes ═══ sur le site)

Titre conseillé :
**Exact square-signature invariants in a finite parametric system: is this structure known?**

═══ DÉBUT ═══

While studying a closed parametric system (a deterministic engine whose
parameters are all derived from a single "zero-point" table), I found an
exact algebraic structure that I cannot locate in the literature. All
computations are exact (rational arithmetic), so the identities below are
verified equalities rather than approximations — but they are checked on a
**finite** domain, and no general theorem is claimed here.

## Setup

The system derives four real "cycle" constants from the table, whose
exact numerators are:

$$d_x = 6\,403\,563 = 1461^2 \cdot 3,\qquad
  d_y = 93\,987 = 177^2 \cdot 3,$$
$$d_z = 135\,000\,000 = 3000^2 \cdot 15,\qquad
  d_t = 17\,292\,418\,731 = 27^2 \cdot 23\,720\,739.$$

Every derived constant carries a large square factor — while the
"substance" constants ($313$ prime, $24\,434 = 2 \cdot 12\,217$, base $19$)
are square-free.

## The surprising relations

Let $Q = 1536 = 16^2 \cdot 6$ be a declared degree constant. The engine
emits the cycles in **hours**, and there they are rationals, not integers:

$$d_x^{h} = \frac{d_x}{128} = \frac{6\,403\,563}{128},\qquad
  d_y^{h} = \frac{d_y}{2} = \frac{93\,987}{2}.$$

Over $\mathbb{Q}$ these hold exactly:

$$Q \cdot d_x^{h} = 76\,842\,756 = 8766^2,\qquad
  Q \cdot d_y^{h} = 72\,182\,016 = 8496^2 .$$

Clearing the denominators gives the integer form, which is the one a
third party can check without knowing my scaling convention:

$$8766^2 = 12 \cdot d_x,\qquad 8496^2 = 768 \cdot d_y \;\;(768 = Q/2),$$

so that $\text{seed}^2/\text{cycle} \in \{12, 768\}$ — exact integers, in
ratio $1:2^{6}$. Here $8766$ is the solar year in hours and $8496$ the
lunar year in hours: the very calendar seeds the cycles were built from
($8766 = 18 \cdot 487$, and $487$ is prime). In other words, *a small
exact integer times the cycle reproduces the square of the calendar
seed.*

Also exact: $313 \cdot 313 = 313^2$ (the "pole" constant squared),
$2304 \cdot 9 = 144^2$, $2304 \cdot 4 = 96^2$.

One further shape, which looks more standard than the rest: the large
prime factor of $d_t$ is $d_t = 3^7 \cdot 7 \cdot 1\,129\,559$, and that
prime is represented *uniquely* by $x^2 + 7y^2$, namely
$1\,129\,559 = 884^2 + 7 \cdot 223^2$. Note $1\,129\,559 \equiv 4 \pmod 7$.

## Question

1. Is this "largest-square-factor signature" structure a known object —
   e.g., in the theory of square kernels / powerful part
   ($n = k^2 \cdot m$ with $m$ square-free)?
2. Does the exact integer relation $\text{seed}^2 = m \cdot \text{cycle}$
   ($8766^2 = 12\,d_x$, $8496^2 = 768\,d_y$), where both $d$'s come from
   the same generator, correspond to a known construction — norm
   equations, quadratic twists, or something in the shape of a
   parametrised family whose member squares land back on its seeds?
3. For $1\,129\,559 = 884^2 + 7 \cdot 223^2$ I expect a classical answer
   (I checked the $x^2 + 7y^2$ criterion by exhaustion over the 301 odd
   primes below 2000, with $p \bmod 7 \in \{1,2,4\}$, no counterexample;
   $p = 2$ is the known exception). Which reference states it precisely —
   Cox, *Primes of the form $x^2 + ny^2$*, or genus theory?
4. Any reference would be welcome — is there a framework where such
   exact square relations between *generated* constants are studied?

All of it is verified by exact rational arithmetic and reproducible:
`python code/conjecture_point_carre.py` prints the six checks (PC-1…PC-6)
with their seal. A sealed, reproducible certificate set is on Zenodo
(DOI 10.5281/zenodo.24028242), with homage to Turing, Riemann, Hasse,
Wiles, and all predecessors whose bricks made this work possible.

═══ FIN ═══

NOTE d'usage : MathOverflow = niveau recherche ; Mathematics SE = plus
accueillant pour une découverte de ce type. Commencer par Mathematics SE ;
le lien "MathOverflow" dans ton profil existe déjà pour la suite.
L'hommage est inclus en fin de post — les prédécesseurs nommés :
Turing, Riemann, Hasse, Wiles, Gross-Zagier, Kolyvagin, Perelman.
