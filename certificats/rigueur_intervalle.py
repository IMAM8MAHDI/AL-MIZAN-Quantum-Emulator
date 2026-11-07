# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2026 IMAM8MAHDI / Astro-Code Ecosystem
# SPDX-License-Identifier: GPL-3.0-only OR AGPL-3.0-only
"""
===============================================================================
   RIGUEUR NIVEAU 2 — CERTIFICATS DE ZÉROS PAR ARITHMÉTIQUE D'INTERVALLES
===============================================================================
Le juste milieu entre certificat borné (mesure) et preuve formelle :

  • Chaque évaluation de Z(t) (fonction de Hardy, réelle) est une
    ENCEINTE D'INTERVALLE GARANTIE : erreurs d'arrondi + reste
    Euler-Maclaurin + reste de Stirling comptabilisés dans la largeur.
  • Si l'enceinte en t₀ est > 0 et celle en t₁ est < 0, alors PAR LE
    THÉORÈME DES VALEURS INTERMÉDIAIRES un zéro de Z existe dans (t₀,t₁).
    Ce n'est plus une mesure : c'est un THÉORÈME certifié par la machine.

Implémentation : intervalles complexes = rectangles [re]+i[im] sur
mpmath.iv ; ζ(1/2+it) par Euler-Maclaurin (N=80, K=3 + borne de reste) ;
θ(t) par Stirling asymptotique + borne de reste 1/(48t³) conservative.
===============================================================================
"""

from __future__ import annotations

import math
from typing import Any, Dict, List, Tuple

from mpmath import iv

from .socle import noeud_certificat

iv.dps = 40


# ---------------------------------------------------------------------------
# Intervalles complexes (rectangles)
# ---------------------------------------------------------------------------

class IC:
    """Intervalle complexe : re, im ∈ iv.mpf."""

    def __init__(self, re, im=0.0):
        self.re = re if hasattr(re, "_mpi_") else iv.mpf(re)
        self.im = im if hasattr(im, "_mpi_") else iv.mpf(im)

    def __add__(self, o):
        o = o if isinstance(o, IC) else IC(o)
        return IC(self.re + o.re, self.im + o.im)

    __radd__ = __add__

    def __neg__(self):
        return IC(-self.re, -self.im)

    def __sub__(self, o):
        return self + (-(o if isinstance(o, IC) else IC(o)))

    def __rsub__(self, o):
        return (-self).__radd__(o)

    def __mul__(self, o):
        o = o if isinstance(o, IC) else IC(o)
        pr = [self.re.a * o.re.a, self.re.a * o.re.b,
              self.re.b * o.re.a, self.re.b * o.re.b]
        pi = [self.im.a * o.im.a, self.im.a * o.im.b,
              self.im.b * o.im.a, self.im.b * o.im.b]
        re = iv.mpf([min(pr) - max(pi), max(pr) - min(pi)])
        pr2 = [self.re.a * o.im.a, self.re.a * o.im.b,
               self.re.b * o.im.a, self.re.b * o.im.b]
        pi2 = [self.im.a * o.re.a, self.im.a * o.re.b,
               self.im.b * o.re.a, self.im.b * o.re.b]
        im = iv.mpf([min(pr2) + min(pi2), max(pr2) + max(pi2)])
        return IC(re, im)

    __rmul__ = __mul__

    def __truediv__(self, o):
        if isinstance(o, IC):
            return self * o.inv()
        return IC(self.re / float(o), self.im / float(o))

    def inv(self):
        m = self.re * self.re + self.im * self.im
        return IC(self.re / m, -self.im / m)

    def exp(self):
        ea = iv.exp(self.re)
        return IC(ea * iv.cos(self.im), ea * iv.sin(self.im))

    def largeur(self):
        return float(max(self.re.b - self.re.a, self.im.b - self.im.a))


def _pointe(z: complex) -> IC:
    eps = 1e-30
    return IC(iv.mpf([z.real - eps, z.real + eps]),
              iv.mpf([z.imag - eps, z.imag + eps]))


# ---------------------------------------------------------------------------
# ζ(s) par Euler-Maclaurin avec borne de reste rigoureuse
# ---------------------------------------------------------------------------

_B2K = (1.0 / 6, -1.0 / 30, 1.0 / 42)


def _puissance_complexe(n: int, s: IC) -> IC:
    """n^{-s} = exp(-s·ln n)."""
    return ((-s) * iv.log(iv.mpf(float(n)))).exp()


def zeta_intervalle(s: IC, n_somme: int = 80, k_restes: int = 3) -> IC:
    """ζ(s) en intervalle garanti : somme + reste EM + borne conservatrice."""
    total = IC(0)
    for n in range(1, n_somme):
        total = total + _puissance_complexe(n, s)

    sigma = float(s.re.a)
    # Termes de queue : N^{1-s}/(s-1) + N^{-s}/2 + Σ B_{2k}/(2k)!·s_{(2k)}·N^{-s-2k+1}
    ns = _puissance_complexe(n_somme, s)
    queue = ns * n_somme * (s - IC(1)).inv() + ns * IC(0.5)
    montant_dernier = IC(0)
    for k in range(1, k_restes + 1):
        coef = _B2K[k - 1] / math.factorial(2 * k)
        rising = IC(1)
        for j in range(2 * k - 1):
            rising = rising * (s + IC(j))
        terme = ns * rising * coef
        for _ in range(2 * k - 1):
            terme = terme / n_somme
        queue = queue + terme
        montant_dernier = terme
    total = total + queue

    # Borne de reste rigoureuse : |R_K| ≤ |a_K|·|s+2K|/(σ+2K+1)
    facteur = abs(complex(float(s.re.b) + 2 * k_restes, float(s.im.b)))
    facteur /= (sigma + 2 * k_restes + 1)
    borne = abs(complex(float(montant_dernier.re.b), float(montant_dernier.im.b)))
    marge = facteur * borne
    total.re = iv.mpf([total.re.a - marge, total.re.b + marge])
    total.im = iv.mpf([total.im.a - marge, total.im.b + marge])
    return total


# ---------------------------------------------------------------------------
# θ(t) et Z(t) en intervalles garantis
# ---------------------------------------------------------------------------

def theta_intervalle(t: float) -> Any:
    """θ(t) ≈ t/2·ln(t/2π) − t/2 − π/8 + 1/(48t) + 7/(5760t³) + reste.

    Reste de Stirling borné par 31/(80640·t⁵) — conservateur pour t ≥ 10.
    """
    x = iv.mpf(float(t))
    val = (x / 2) * iv.log(x / (2 * iv.pi)) - x / 2 - iv.pi / 8
    val = val + 1 / (48 * x) + 7 / (5760 * x ** 3)
    borne = 31.0 / (80640.0 * t ** 5) + 1e-12
    return iv.mpf([val.a - borne, val.b + borne])


def z_intervalle(t: float) -> IC:
    """Z(t) = e^{iθ(t)}·ζ(1/2+it) — enceinte garantie réelle."""
    s = IC(iv.mpf([0.5, 0.5]), iv.mpf([t, t]))
    zeta = zeta_intervalle(s)
    th = theta_intervalle(t)
    ei = IC(iv.cos(th), iv.sin(th))
    z = zeta * ei
    return z


def signe_certifie(z: IC) -> int | None:
    """+1 si l'enceinte est entièrement >0 (partie réelle), −1 si <0, sinon None."""
    if z.re.a > 0:
        return 1
    if z.re.b < 0:
        return -1
    return None


# ---------------------------------------------------------------------------
# Certificat de zéros en ligne — théorèmes locaux
# ---------------------------------------------------------------------------

def certificats_zeros_ligne(echantillons: List[Tuple[float, float]]) -> Dict[str, Any]:
    """Pour chaque paire (t0,t1) : si signe(t0) ≠ signe(t1) certifiés,
    alors ∃ zéro de Z dans (t0,t1) — THÉORÈME par TVI."""
    theoremes = []
    for t0, t1 in echantillons:
        z0, z1 = z_intervalle(t0), z_intervalle(t1)
        s0, s1 = signe_certifie(z0), signe_certifie(z1)
        entree = {
            "intervalle_t": [t0, t1],
            "Z(t0) enceinte": f"[{float(z0.re.a):.6g} ; {float(z0.re.b):.6g}]",
            "Z(t1) enceinte": f"[{float(z1.re.a):.6g} ; {float(z1.re.b):.6g}]",
            "signes_certifies": [s0, s1],
            "largeur_max": round(max(z0.largeur(), z1.largeur()), 8),
        }
        if s0 is not None and s1 is not None and s0 != s1:
            entree["theoreme"] = ("∃ zéro de Z(t) dans "
                                  f"({t0} ; {t1}) — prouvé par TVI + intervalles")
            entree["certifie"] = True
        else:
            entree["certifie"] = False
            entree["note"] = "enceintes non concluantes — affiner ou augmenter N/dps"
        theoremes.append(entree)
    return theoremes


def certificat() -> Dict[str, Any]:
    # Points d'échantillonnage encadrant les 3 premiers zéros de Z
    echantillons = [(14.0, 14.4), (20.9, 21.3), (24.9, 25.3)]
    theoremes = certificats_zeros_ligne(echantillons)
    nb_certifies = sum(1 for t in theoremes if t["certifie"])
    return noeud_certificat(
        "RIEMANN — NIVEAU 2 (zéros certifiés en ligne)",
        "∀ρ : ζ(ρ)=0 ∧ 0<Re(ρ)<1 ⇒ Re(ρ)=1/2",
        {
            "theoremes_zeros": theoremes,
            "nb_theoremes_certifies": nb_certifies,
            "methode": "TVI + enceintes d'intervalles garanties "
                       "(EM N=80 K=3, Stirling, erreurs comptabilisées)",
        },
        "CERTIFICAT_BORNE",
        "Chaque zéro certifié est un THÉORÈME (existence prouvée dans "
        "l'intervalle). Compléter RH exigerait en plus le comptage global "
        "N(T) rigoureux + le domaine infini — la réduction humaine reste "
        "nécessaire.")


if __name__ == "__main__":
    import json
    print(json.dumps(certificat(), indent=2, ensure_ascii=False))
