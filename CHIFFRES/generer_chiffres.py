# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2026 IMAM8MAHDI / Astro-Code Ecosystem
# SPDX-License-Identifier: GPL-3.0-only OR AGPL-3.0-only
"""Décimales certifiées de π, e et √2 — arithmétique entière pure, deux voies par constante.

Trois constantes, et pour chacune deux algorithmes indépendants. La voie principale ne
rend pas seulement une chaîne de chiffres : elle rend un **certificat entier**. Un
encadrement exact est calculé aux deux bornes, puis on vérifie que les deux bornes ont
la même partie entière à l'échelle demandée : les chiffres sont *forcés*, aucun arrondi
ne peut les changer.

    π   splitting binaire de Chudnovsky (14,18 chiffres par terme, série alternée)
        seconde voie : formule de Machin (arccot 5 et arccot 239, séries alternées)
    e   splitting binaire de Σ 1/k!, queue bornée par 1/((m)·m!)
        seconde voie : somme itérative terme à terme
    √2  isqrt entier, preuve directe par les carrés : w² ≤ 2·10^{2n} < (w+1)²
        seconde voie : Newton sur entiers fixes, sans isqrt

Le seul emprunt à la littérature est la forme fermée (Chudnovsky 1989, Machin 1706,
série d'Euler pour e) : ce sont des identités publiées, pas des résultats d'ici.
Convergence, encadrement, contraction, stabilite et chiffres sont recalculés ici.

Usage :
    py -3 CHIFFRES/generer_chiffres.py [n] [n_croisement]
"""

from __future__ import annotations

import math
import sys
from fractions import Fraction
from typing import Any, Dict, Tuple

try:  # Python >= 3.11 borne int -> str ; les certificats depassent 10^6 chiffres.
    sys.set_int_max_str_digits(8_000_000)
except AttributeError:
    pass

# ── Constantes declarees (litterature, aucun ajustement local) ─────────────
A_CHUD = 13591409
B_CHUD = 545140134
C_CHUD = 640320
C3 = C_CHUD ** 3                  # 262 537 412 640 768 000
C3_24 = C3 // 24                  # 10 939 058 860 032 000 — division exacte
M_CHUD = 426880
GARDE = 40                        # chiffres de garde au-dela de la demande
N_CROISEMENT = 5000               # portee de la seconde voie (cout en n^2, declare)
CONSTANTES: Tuple[str, ...] = ("pi", "e", "racine2")


# ============================================================================
# π — Chudnovsky
# ============================================================================

def _terme_chud(k: int) -> Tuple[int, int]:
    """(p(k), q(k)) du ratio R_k = 24(6k−5)(2k−1)(6k−1)/(k³·C³), facteur 24 absorbé dans q."""
    return (6 * k - 5) * (2 * k - 1) * (6 * k - 1), k ** 3 * C3_24


def _bs_chud(a: int, b: int) -> Tuple[int, int, int]:
    """Splitting binaire sur les indices [a, b) : rend (P, Q, T) avec Σ_{k=a}^{b−1} t_k = T/Q.

    t_k est le terme signe de rang k. La feuille k = 0 vaut (1, 1, A) ; le facteur 24
    n'est jamais pose sur p(k), il est dans q(k) = k³·C³/24 — c'est ce qui rend R_k
    exact et la feuille initiale triviale.
    """
    if b - a == 1:
        if a == 0:
            return (1, 1, A_CHUD)
        p, q = _terme_chud(a)
        t = p * (B_CHUD * a + A_CHUD)
        return (p, q, -t if a % 2 else t)
    m = (a + b) // 2
    p1, q1, t1 = _bs_chud(a, m)
    p2, q2, t2 = _bs_chud(m, b)
    return (p1 * p2, q1 * q2, q2 * t1 + p1 * t2)


def _ajouter_chud(P: int, Q: int, T: int, k: int) -> Tuple[int, int, int]:
    """Prolonge la somme partielle [0, k) du terme d'indice k."""
    p, q = _terme_chud(k)
    t = p * (B_CHUD * k + A_CHUD)
    return (P * p, Q * q, q * T + (P * (-t if k % 2 else t)))


def ratios_chudnovsky(kmax: int = 64) -> Dict[str, Any]:
    """Preuve rationnelle que |t_{k+1}| < |t_k| pour tout k ≥ 1 : le bracket vaut.

    |t_k|/|t_{k−1}| = R_k·(A+Bk)/(A+B(k−1)) avec R_k = 24(6k−5)(2k−1)(6k−1)/(k³C³).
    Comme (6k−5) < 6k, (2k−1) < 2k, (6k−1) < 6k : R_k < 1728/C³ pour tout k ≥ 1, et le
    facteur lineaire est maximal en k = 1. La borne fermee est donc 1728(A+B)/(A·C³).
    """
    pire = Fraction(0)
    for k in range(1, kmax + 1):
        r = Fraction(24 * (6 * k - 5) * (2 * k - 1) * (6 * k - 1), k ** 3 * C3)
        r *= Fraction(B_CHUD * k + A_CHUD, B_CHUD * (k - 1) + A_CHUD)
        pire = max(pire, r)
    borne = Fraction(1728 * (A_CHUD + B_CHUD), A_CHUD * C3)
    return {"kmax_teste": kmax, "ratio_max": float(pire),
            "borne_fermee": float(borne), "tout_inferieur_a_un": bool(pire < 1),
            "borne_inferieure_a_un": bool(borne < 1)}


def decimales_pi(n: int) -> Dict[str, Any]:
    """n décimales de π avec certificat d'encadrement entier.

    π = M·√10005/S, S = Σ t_k (identité de Chudnovsky, déclarée). Série alternée à
    termes strictement décroissants (ratios_chudnovsky) : S est encadré par deux sommes
    partielles consécutives ; la troisième vérifie la contraction.
    """
    termes = n // 14 + 6
    P, Q, T = _bs_chud(0, termes)
    P1, Q1, T1 = _ajouter_chud(P, Q, T, termes)
    P2, Q2, T2 = _ajouter_chud(P1, Q1, T1, termes + 1)
    contraction = abs(T2 * Q1 - T1 * Q2) * Q < abs(T1 * Q - T * Q1) * Q2
    if T * Q1 <= T1 * Q:
        lo_num, lo_den, hi_num, hi_den = T, Q, T1, Q1
    else:
        lo_num, lo_den, hi_num, hi_den = T1, Q1, T, Q
    alternance = lo_num * hi_den <= hi_num * lo_den
    g = n + GARDE
    dix_g = 10 ** g
    u = math.isqrt(10005 * dix_g * dix_g)
    bas_s = (M_CHUD * u * hi_den) // hi_num
    haut_s = (M_CHUD * (u + 1) * lo_den) // lo_num
    certifie = bool(bas_s // 10 ** GARDE == haut_s // 10 ** GARDE) and alternance and contraction
    entier = str(bas_s // 10 ** GARDE)
    return {
        "constante": "pi", "n": n, "termes": termes,
        "chiffres": entier[1:1 + n], "entier": entier[0],
        "certifie": certifie, "alternance_valide": bool(alternance),
        "contraction_valide": bool(contraction),
        "marge_chiffres": _marge_chiffres(haut_s - bas_s, GARDE),
    }


def pi_par_machin(n: int) -> Tuple[str, bool]:
    """Seconde voie indépendante : π = 16·arccot(5) − 4·arccot(239) (Machin, 1706).

    Chaque arccot est une série alternée à termes décroissants : le dernier terme non nul
    borne l'erreur, majorée en plus par le nombre d'itérations (divisions entières).
    Rend (chaine des n décimales, certifie) où certifie dit que les deux bornes de
    Machin elles-mêmes donnent le même plancher.
    """
    g = n + GARDE
    ech = 10 ** g

    def arccot(x: int) -> Tuple[int, int]:
        pas = x * x
        a = ech // x
        tot = a
        prev = a
        k = 1
        it = 0
        while True:
            a //= pas
            k += 2
            it += 1
            terme = a // k
            if not terme:
                break
            tot += terme if k % 4 == 1 else -terme
            prev = terme
        t = prev + it + 1
        return (tot - t, tot + t)

    b1, h1 = arccot(5)
    b2, h2 = arccot(239)
    bas, haut = 16 * b1 - 4 * h2, 16 * h1 - 4 * b2
    bn, hn = bas // 10 ** GARDE, haut // 10 ** GARDE
    return str(bn)[1:1 + n], bool(bn == hn)


# ============================================================================
# e — Σ 1/k!
# ============================================================================

def _termes_e(seuil: int) -> int:
    """Plus petit m ≥ 1 tel que m·m! > 10^seuil — la condition du bornage de queue.

    Newton sur lgamma pour l'estimation, puis vérification entière exacte : la valeur
    rendue n'est pas une approximation, c'est l'entier qui satisfait l'inégalité.
    """
    m = max(4.0, seuil / max(1.0, math.log10(seuil / 4.0)))
    ln10 = math.log(10.0)
    for _ in range(80):
        f = math.lgamma(m + 1.0) / ln10 + math.log10(m) - seuil
        d = math.log(m) / ln10 + 1.0 / (m * ln10)
        nouveau = m - f / d
        if abs(nouveau - m) < 1e-10:
            m = nouveau
            break
        m = nouveau
    mi = max(1, int(m))
    facteur = math.factorial(mi)
    while mi * facteur <= 10 ** seuil:
        mi += 1
        facteur *= mi
    return mi


def _bs_e(a: int, b: int) -> Tuple[int, int]:
    """Splitting binaire de Σ_{k=a}^{b−1} 1/k! : rend (T, Q) avec Σ = T/Q exactement.

    p(k) = 1, q(k) = k (q(0) posé à 1), b(k) = 1 ; la règle d'assemblage est celle du
    splitting binaire, T = T₁·Q₂ + P₁·T₂, d'où Q(0, m+1) = m! exactement.
    """
    if b - a == 1:
        return (1, max(a, 1))
    m = (a + b) // 2
    t1, q1 = _bs_e(a, m)
    t2, q2 = _bs_e(m, b)
    return (t1 * q2 + t2, q1 * q2)


def decimales_e(n: int) -> Dict[str, Any]:
    """n décimales de e avec certificat : 0 < e − Σ_{k≤m}1/k! < 1/(m·m!).

    Bornage de la queue : 1/(m+1+j) < 1/((m+1)^{j+1}) pour j ≥ 0, donc
    Σ_{k>m} 1/k! < 1/(m!·m) pour m ≥ 1. Les deux bornes sont des rationnels exacts.
    """
    m = _termes_e(n + GARDE)
    T, Q = _bs_e(0, m + 1)
    factorielle = math.factorial(m)
    ech = 10 ** (n + GARDE)
    bas_s = (T * ech) // Q
    haut_s = ((T * m + 1) * ech) // (m * Q)
    entier = str(bas_s // 10 ** GARDE)
    return {
        "constante": "e", "n": n, "termes": m + 1,
        "chiffres": entier[1:1 + n], "entier": entier[0],
        "certifie": bool(bas_s // 10 ** GARDE == haut_s // 10 ** GARDE),
        "marge_chiffres": _marge_chiffres(haut_s - bas_s, GARDE),
        "factorielle_egale": bool(Q == factorielle),
    }


def e_par_somme_iterative(n: int) -> Tuple[str, bool]:
    """Seconde voie indépendante : la somme terme à terme, même bornage de queue."""
    ech = 10 ** (n + GARDE)
    m = _termes_e(n + GARDE)
    tot, terme = 0, ech
    for k in range(m + 1):
        if k:
            terme //= k
        tot += terme
    reste = ech // (m * math.factorial(m)) + 1
    bas_s, haut_s = tot - reste - (m + 1), tot + reste + (m + 1)
    bn, hn = bas_s // 10 ** GARDE, haut_s // 10 ** GARDE
    return str(bn)[1:1 + n], bool(bn == hn)


# ============================================================================
# √2 — preuve par les carrés
# ============================================================================

def decimales_racine2(n: int) -> Dict[str, Any]:
    """n décimales de √2 certifiées par w² ≤ 2·10^{2n} < (w+1)².

    Le certificat le plus fort des trois : aucune série, aucun terme de littérature,
    seule l'inégalité entière qui définit floor(√2·10^n) est mise à l'épreuve.
    """
    deux = 2 * 10 ** (2 * n)
    w = math.isqrt(deux)
    preuve = w * w <= deux < (w + 1) * (w + 1)
    chaine = str(w)[1:1 + n]
    return {
        "constante": "racine2", "n": n, "termes": None,
        "chiffres": chaine, "entier": str(w)[0],
        "certifie": bool(preuve) and len(chaine) == n, "marge_chiffres": 0,
        "preuve": "w² ≤ 2·10^(2n) < (w+1)²",
    }


def racine2_par_newton(n: int) -> Tuple[str, bool]:
    """Seconde voie indépendante : Newton sur entiers fixes, sans isqrt."""
    N = 2 * 10 ** (2 * n)
    x = 10 ** (n + 1)
    while True:
        y = (x + N // x) // 2
        if y >= x:
            break
        x = y
    while (x + 1) * (x + 1) <= N:
        x += 1
    preuve = x * x <= N < (x + 1) * (x + 1)
    return str(x)[1:1 + n], bool(preuve)


def decimales(constante: str, n: int) -> Dict[str, Any]:
    """Point d'entrée unique : « pi », « e » ou « racine2 » → certificat avec `chiffres`."""
    if constante == "pi":
        return decimales_pi(n)
    if constante == "e":
        return decimales_e(n)
    if constante == "racine2":
        return decimales_racine2(n)
    raise ValueError(f"constante inconnue : {constante!r}")


def _marge_chiffres(ecart: int, garde: int) -> int:
    """Chiffres de garde restés libres après l'incertitude de l'encadrement."""
    if ecart <= 0:
        return garde
    return garde - len(str(ecart))


def croiser(n_croisement: int = N_CROISEMENT) -> Dict[str, Any]:
    """Les deux voies, chiffre à chiffre, sur le domaine court déclaré."""
    secondes = {"pi": pi_par_machin, "e": e_par_somme_iterative, "racine2": racine2_par_newton}
    noms2 = {"pi": "machin", "e": "somme iterative", "racine2": "newton"}
    sortie: Dict[str, Any] = {}
    for c in CONSTANTES:
        premier = decimales(c, n_croisement)
        principal = premier["chiffres"]
        chaine2, certifie2 = secondes[c](n_croisement)
        sortie[c] = {"voie2": noms2[c], "n": n_croisement,
                     "identique": chaine2 == principal,
                     "certifie_2": certifie2, "certifie_1": premier["certifie"],
                     "premier_desaccord": next((i + 1 for i in range(n_croisement)
                                                if chaine2[i] != principal[i]), None)}
    return sortie


if __name__ == "__main__":
    import json

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    nb = int(sys.argv[1]) if len(sys.argv) > 1 else 2000
    nc = int(sys.argv[2]) if len(sys.argv) > 2 else min(500, nb)
    etat: Dict[str, Any] = {}
    for c in CONSTANTES:
        d = decimales(c, nb)
        etat[c] = {k: v for k, v in d.items() if k != "chiffres"}
        etat[c]["debut"] = d["chiffres"][:30]
    etat["ratios"] = ratios_chudnovsky()
    etat["croisement"] = croiser(nc)
    print(json.dumps(etat, ensure_ascii=False, indent=2))
    ok = all(etat[c]["certifie"] for c in CONSTANTES)
    ok = ok and all(v["identique"] and v["certifie_1"] and v["certifie_2"]
                    for v in etat["croisement"].values())
    sys.exit(0 if ok else 1)
