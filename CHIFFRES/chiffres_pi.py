# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2026 IMAM8MAHDI / Astro-Code Ecosystem
# SPDX-License-Identifier: GPL-3.0-only OR AGPL-3.0-only
"""CHIFFRES — prédictions gelées sur les décimales de π, e et √2.

Le module est coupé en deux moitiés qui ne se parlent pas :

    predire(n, …)    ne reçoit AUCUN chiffre. Entrée : des entiers — taille du domaine,
                     classes, longueurs, sondes déclarées. Sortie : la table complète des
                     espérances, écarts-types, intervalles exactes et règles de rejet.
                     Elle est calculable, et identique, avant comme après la génération
                     des décimales, et elle est définie à n = 0 : contrôle C06.
    mesurer(chaine)  ne reçoit qu'une chaîne de chiffres. Aucune constante du modèle
                     n'est réajustée là.

Règle de verdict, déclarée une fois pour toutes :
    compte   → p = 2·min(P(Y ≤ x), P(Y ≥ x)) sous Poisson(λ_k) exacte, normale au-delà
               de λ = LIMITE_POISSON_EXACT (même règle, branche de calcul)
    fréquence→ p = 2·(1 − Φ(|z|)), z = (O − n/10)/√(0,09n)
    position → transformée intégrale : u = F(observed), p = 2·min(u, 1 − u)
    cell     → CONTENUE si p ≥ ALPHA = 0,001, EXCLUE sinon
Ce que rend le dossier est le COMPTE des cellules exclues sur les 108 annoncées — pas un
verdict par cellule choisi après coup.

Une seule hypothèse, jamais démontrée ici :

    H0 — les n décimales sont indépendantes et uniformes sur {0,…,9}.

C'est la définition de la normalité simple en base 10. Ni π, ni e, ni √2 n'est prouvé
normal : chapitre « A pattern nobody has proven » (12:46), et `limite` de ce dossier.
Ce qui est démontré est ailleurs : les décimales confrontées sont certifiées par
encadrements entiers (`generer_chiffres.py`), et l'identité
9·10^(k−1)·10^(−k) = 0,9 est une égalité de fractions, pas une mesure.

Source de la question — aucune donnée chiffrée n'en vient :
    Euclidea, « What Is Actually Hiding in the Digits of Pi? », 854 s,
    https://www.youtube.com/watch?v=M90ZAVojI30 , métadonnées mesurées 2026-11-08T23:43:25Z.
    Transcript ABSENT (timedtext : 0 octet en json3, srv3 et xml). Les dix titres de
    chapitres et leur horodatage sont repris verbatim dans VIDEO ; sans transcript il n'y
    a rien d'autre à citer, et rien n'est réinventé.

Usage :
    py -3 CHIFFRES/chiffres_pi.py                    # domaine court (20 000)
    py -3 CHIFFRES/chiffres_pi.py 1000000            # domaine de référence
    py -3 CHIFFRES/chiffres_pi.py 1000000 --ecrit    # + régénère artefacts/
"""

from __future__ import annotations

import math
import random
import sys
from fractions import Fraction
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

RACINE = Path(__file__).resolve().parent
if str(RACINE) not in sys.path:
    sys.path.insert(0, str(RACINE))

import generer_chiffres as GEN                                          # noqa: E402

# ── Déclarations de domaine (figées avant toute mesure) ───────────────────
N_REFERENCE = 1_000_000                 # décimales confrontées par constante
N_COURT = 20_000                        # domaine des tests
KMAX = 6                                # classes de positions 10^(k−1) … 10^k − 1
RMAX = 7                                # longueurs de runs de chiffres identiques
K_OCCULENCE: Tuple[int, ...] = (1, 2, 3, 4, 5, 6)
SONDES: Tuple[str, ...] = ("12345", "54321", "00000", "999999", "0123456789")
N_SIM = 100_000                         # domaine du calibrage Monte-Carlo
N_SIM2 = 50_000                         # second domaine : vérifie la loi en √n
REPILIQUES = 200
REPILIQUES2 = 100
GRAINE = 20261109                       # MT19937, graine déclarée
K_CALIBREES: Tuple[int, ...] = (4, 5)   # occulence calibrée par simulation
ALPHA = 0.001                           # seuil bilatère de rejet, déclaré
PAS_CUMUL = 10                          # points de la courbe cumulative, déclarés
LIMITE_POISSON_EXACT = 500              # au-delà, normale : exp(−λ) sous-flue vers λ ≈ 709
MIN_LAMBDA_RAPPORT = 1.0                # λ minimal pour estimer un rapport d'écarts-types
BANDE_RAPPORT = (0.5, 2.0)              # bande grossière autour de la loi en √n
KAPPA_BANDE = (0.0, 1.35)               # bande déclarée sur Var(Monte-Carlo)/Var(annonce)
CONSTANTES: Tuple[str, ...] = ("pi", "e", "racine2")
LIBELLES = {"pi": "π", "e": "e", "racine2": "√2"}
CHIFFRES_DE_REFERENCE = {
    "pi": "14159265358979323846264338327950288419716939937510",
    "e": "71828182845904523536028747135266249775724709369995",
    "racine2": "41421356237309504880168872420969807856967187537694",
}
LONGUEUR_ANCRE = 50                     # longueur citée ci-dessus, déclarée

VIDEO: Dict[str, Any] = {
    "url": "https://www.youtube.com/watch?v=M90ZAVojI30",
    "id": "M90ZAVojI30",
    "titre": "What Is Actually Hiding in the Digits of Pi?",
    "auteur": "Euclidea",
    "duree_s": 854,
    "horodatage_utc": "2026-11-08T23:43:25Z",
    "transcript": "absent — timedtext 0 octet en json3, srv3 et xml",
    "outils": "scripts/extraire_chapitres_youtube.py (Skill extraire-chapitres-youtube-sans-transcript)",
    "chapitres": [
        ["0:00", "Five digits at position 16470"],
        ["1:33", "Where position one is"],
        ["2:57", "Ninety thousand candidates"],
        ["4:17", "Zero point nine every time"],
        ["5:37", "Matches by length"],
        ["7:03", "The running total"],
        ["8:22", "Three ways to count"],
        ["9:39", "The same search in e and root two"],
        ["11:02", "Every short string shows up"],
        ["12:46", "A pattern nobody has proven"],
    ],
}

# ============================================================================
# LOIS — calculées sans aucune donnée
# ============================================================================

def p_bilatere_normale(z: float) -> float:
    """p = 2·(1 − Φ(|z|)) = erfc(|z|/√2) — aucune table, aucune interpolation."""
    return math.erfc(abs(z) / math.sqrt(2.0))


def z_de_p_bilatere(p: float) -> float:
    """Inverse exact de z ↦ erfc(z/√2) par bissection sur la seule fonction monotone dont
    on ait besoin — ni table, ni Newton : la dérivée d'erfc s'annule trop vite en z et
    la division qui en découle plantait pour p = 0,05."""
    if not 0.0 < p < 1.0:
        raise ValueError("p doit être dans ]0, 1[")
    bas, haut = 0.0, 10.0
    while p_bilatere_normale(haut) > p:
        haut *= 2.0
    for _ in range(100):
        milieu = 0.5 * (bas + haut)
        if p_bilatere_normale(milieu) > p:
            bas = milieu
        else:
            haut = milieu
    return 0.5 * (bas + haut)


Z_SEUIL = z_de_p_bilatere(ALPHA)


def pmf_poisson(lam: float, upto: int) -> List[float]:
    if lam <= 0:
        return [1.0] + [0.0] * upto
    probs: List[float] = []
    terme = math.exp(-lam)
    for k in range(upto + 1):
        if k:
            terme *= lam / k
        probs.append(terme)
    return probs


def p_bilatere_poisson(lam: float, x: int) -> float:
    """p = min(1, 2·min(P(Y ≤ x), P(Y ≥ x))) — règle déclarée, jamais retouchée."""
    if lam <= 0:
        return 1.0 if x == 0 else 0.0
    probs = pmf_poisson(lam, max(x + 60, int(14 * lam) + 30))
    basse = sum(probs[:x + 1])
    haute = max(0.0, 1.0 - sum(probs[:x]))
    return min(1.0, 2.0 * min(basse, haute))


def p_bilatere_bernoulli(q: float, presente: bool) -> float:
    """Issue binaire observée : p = min(1, 2·min(P(Y ≤ y), P(Y ≥ y))) = min(1, 2·P(Y = y)).
    C'est la même définition bilatère que pour la Poisson : l'issue attendue (absente
    quand q est minuscule) donne p = 1, et l'issue surprenante (présente) donne p = 2q."""
    return min(1.0, 2.0 * (q if presente else 1.0 - q))


def p_bilatere_compte(lam: float, x: int) -> float:
    """Règle déclarée pour un compte : Poisson exacte jusqu'à LIMITE_POISSON_EXACT,
    puis normale — Poisson(λ) converge en N(λ, λ), et la récurrence pmf_poisson n'est
    plus utilisable au-delà : exp(−λ) y sous-flue. Le seuil est un choix de calcul,
    pas de verdict ; les deux branches se recouvrent largement."""
    if lam <= LIMITE_POISSON_EXACT:
        return p_bilatere_poisson(lam, x)
    return p_bilatere_normale((x - lam) / math.sqrt(lam))


def intervalle_poisson(lam: float, alpha: float = ALPHA) -> Tuple[int, int]:
    """Intervalle central exact : plus petit [a, b] avec P(a ≤ Y ≤ b) ≥ 1 − alpha."""
    if lam <= 0:
        return (0, 0)
    probs = pmf_poisson(lam, int(14 * lam) + 80)
    seuil = alpha / 2.0
    bas, cum = len(probs) - 1, 0.0
    for k, pr in enumerate(probs):
        if cum + pr > seuil:
            bas = k
            break
        cum += pr
    queue, haut = 0.0, 0
    for k in range(len(probs) - 1, -1, -1):
        if queue + probs[k] > seuil:
            haut = k
            break
        queue += probs[k]
    return (bas, haut)


def chi2_intervalle(df: int, alpha: float = ALPHA) -> Tuple[float, float]:
    """Wilson–Hilferty : df·(1 − 2/(9df) ± z·√(2/(9df)))³, z bilatère de ALPHA."""
    z = z_de_p_bilatere(alpha)
    b = 2.0 / (9.0 * df)
    return (df * (1.0 - b - z * math.sqrt(b)) ** 3, df * (1.0 - b + z * math.sqrt(b)) ** 3)


def candidats_classe(n: int, k: int) -> int:
    """Positions à exactement k chiffres exploitables dans n décimales."""
    debut = 1 if k == 1 else 10 ** (k - 1)
    fin = min(10 ** k - 1, n - k + 1)
    return max(0, fin - debut + 1)


def esperance_auto_local(n: int, k: int) -> Fraction:
    """λ_k = candidats·10^(−k) — 9/10 exactement dès que la classe tient dans le domaine."""
    return Fraction(candidats_classe(n, k), 10 ** k)


def esperance_runs(n: int, r: int) -> Fraction:
    """E[run maximal de longueur r] = (n−r−1)·0,81·10^(−(r−1)) + 1,8·10^(−(r−1))."""
    if n <= 0:
        return Fraction(0)
    q = Fraction(1, 10) ** (r - 1)
    return max(0, n - r - 1) * Fraction(81, 100) * q + 2 * Fraction(9, 10) * q


def esperance_occulence(n: int, k: int) -> Fraction:
    """E[strings de longueur k présentes] = 10^k·(1 − (1 − 10^(−k))^m), m = fenêtres."""
    m = max(0, n - k + 1)
    if m <= 0:
        return Fraction(0)
    return Fraction(10 ** k) * (1 - (1 - Fraction(1, 10 ** k)) ** m)


def variance_occulence_independante(n: int, k: int) -> float:
    """Variance sous l'indépendance des cases (Poissonisation) — bornée en C14."""
    total = 10 ** k
    e = float(esperance_occulence(n, k)) / total
    return total * e * (1.0 - e)


def loi_attente_geometrique(L: int, n: int) -> Dict[str, Any]:
    p = 10.0 ** (-L)
    m = max(0, n - L + 1)
    q_bilatere = ALPHA / 2.0
    return {"longueur": L, "probabilite_par_position": p, "fenetres": m,
            "moyenne_inconditionnelle": 1.0 / p,
            "mediane": math.log(2.0) / p,
            "probabilite_de_presence": 1.0 - (1.0 - p) ** m,
            "quantile_de_rejet": math.log(q_bilatere) / math.log1p(-p)}


def percentile_attendu(position: Optional[int], L: int) -> Optional[float]:
    """u = P(T ≤ position) sous la géométrique déclarée — doit suivre une uniforme."""
    if position is None:
        return None
    return 1.0 - (1.0 - 10.0 ** (-L)) ** position


# ============================================================================
# MESURE — une chaîne de chiffres entre, des comptes sortent
# ============================================================================

def mesurer_frequence(d: str) -> List[int]:
    compte = [0] * 10
    for ch in d:
        compte[ord(ch) - 48] += 1
    return compte


def chi2_frequence(compte: Sequence[int]) -> float:
    n = sum(compte)
    if not n:
        return 0.0
    e = n / 10.0
    return sum((c - e) ** 2 / e for c in compte)


def positions_auto_local(d: str, kmax: int = KMAX) -> List[int]:
    """p tel que la lecture qui commence en p redonne p : d[p−1:p−1+k] == str(p)."""
    n = len(d)
    trouves: List[int] = []
    for k in range(1, kmax + 1):
        for b in range(1, 10):
            t0 = str(b)
            debut = 1 if k == 1 else b * 10 ** (k - 1)
            fin = min(9 if k == 1 else (b + 1) * 10 ** (k - 1) - 1, n - k + 1)
            for p in range(max(1, debut), fin + 1):
                if d[p - 1] == t0 and d[p - 1:p - 1 + k] == str(p):
                    trouves.append(p)
    return sorted(trouves)


def classes_auto_local(positions: Sequence[int], kmax: int = KMAX) -> Dict[int, int]:
    par_classe = {k: 0 for k in range(1, kmax + 1)}
    for p in positions:
        k = len(str(p))
        if k <= kmax:
            par_classe[k] += 1
    return par_classe


def verifier_auto_local(d: str, positions: Sequence[int]) -> bool:
    """Re-preuve indépendante de la mesure : relire le numéro à sa place, un par un."""
    return all(int(d[p - 1:p - 1 + len(str(p))]) == p for p in positions)


def mesurer_runs(d: str, rmax: int = RMAX) -> Dict[int, int]:
    par_r: Dict[int, int] = {r: 0 for r in range(1, rmax + 1)}
    n, i = len(d), 0
    while i < n:
        j = i
        while j + 1 < n and d[j + 1] == d[i]:
            j += 1
        r = j - i + 1
        if r <= rmax:
            par_r[r] += 1
        i = j + 1
    return par_r


def mesurer_occulence(d: str, longueurs: Sequence[int] = K_OCCULENCE) -> Dict[int, int]:
    sortie: Dict[int, int] = {}
    for k in longueurs:
        total, mod = 10 ** k, 10 ** (k - 1)
        vus = bytearray(total)
        code = nb = 0
        for i, ch in enumerate(d):
            code = (code % mod) * 10 + (ord(ch) - 48)
            if i >= k - 1 and not vus[code]:
                vus[code] = 1
                nb += 1
        sortie[k] = nb
    return sortie


def mesurer_attentes(d: str, sondes: Sequence[str] = SONDES) -> Dict[str, Optional[int]]:
    sortie: Dict[str, Optional[int]] = {}
    for s in sondes:
        i = d.find(s)
        sortie[s] = None if i < 0 else i + 1
    return sortie


def mesurer_cumul(d: str, positions: Sequence[int], pas: int = PAS_CUMUL) -> List[Tuple[int, int]]:
    """N(x) = #positions auto-localisées ≤ x, rendues sur la grille déclarée."""
    idx, courbe = 0, []
    for x in grille_cumul(len(d), pas):
        while idx < len(positions) and positions[idx] <= x:
            idx += 1
        courbe.append((x, idx))
    return courbe


def mesurer(chaine: str, kmax: int = KMAX, rmax: int = RMAX,
            longueurs: Sequence[int] = K_OCCULENCE,
            sondes: Sequence[str] = SONDES) -> Dict[str, Any]:
    freq = mesurer_frequence(chaine)
    positions = positions_auto_local(chaine, kmax)
    return {
        "n": len(chaine),
        "frequence": freq,
        "chi2": chi2_frequence(freq),
        "auto_local_positions": positions,
        "auto_local_classes": classes_auto_local(positions, kmax),
        "auto_local_total": len(positions),
        "runs": mesurer_runs(chaine, rmax),
        "occulence": mesurer_occulence(chaine, longueurs),
        "attentes": mesurer_attentes(chaine, sondes),
        "cumul": mesurer_cumul(chaine, positions),
    }


# ============================================================================
# PRÉDICTION — n'entre que des entiers
# ============================================================================

def predire_frequence(n: int) -> Dict[str, Any]:
    sigma = math.sqrt(0.09 * n) if n > 0 else 0.0
    return {"attendu_par_chiffre": n / 10.0, "sigma": sigma, "df": 9,
            "bande": [n / 10.0 - Z_SEUIL * sigma, n / 10.0 + Z_SEUIL * sigma],
            "chi2_attendu": 9.0, "chi2_ecart_type": math.sqrt(18.0),
            "chi2_intervalle": chi2_intervalle(9)}


def predire_auto_local(n: int, kmax: int = KMAX) -> Dict[str, Any]:
    par_classe: Dict[int, Any] = {}
    total = 0.0
    for k in range(1, kmax + 1):
        c = candidats_classe(n, k)
        lam = esperance_auto_local(n, k)
        par_classe[k] = {
            "candidats": c, "esperance_exacte": f"{lam.numerator}/{lam.denominator}",
            "esperance": float(lam), "complete": c == (9 if k == 1 else 9 * 10 ** (k - 1)),
            "intervalle": intervalle_poisson(float(lam)), "p_zero": math.exp(-float(lam)),
        }
        total += float(lam)
    return {"par_classe": par_classe, "total_attendu": total,
            "intervalle_total": intervalle_poisson(total),
            "algebre": "classe complète : 9·10^(k−1) candidats × 10^(−k) = 9/10 = 0,9"}


def cumuls_auto_local_attendus(n: int, xs: Sequence[int], kmax: int = KMAX) -> List[float]:
    """E[#auto-localisés ≤ x] : classes entières avant celle de x, puis part proportionnelle."""
    sortie: List[float] = []
    for x in xs:
        att = 0.0
        for k in range(1, kmax + 1):
            if k < len(str(x)):
                att += float(esperance_auto_local(n, k))
            elif k == len(str(x)):
                debut = 1 if k == 1 else 10 ** (k - 1)
                att += max(0, x - debut + 1) * 10.0 ** (-k)
        sortie.append(att)
    return sortie


def grille_cumul(n: int, pas: int = PAS_CUMUL) -> List[int]:
    """Grille des x où l'on lit le cumul : uniquement des entiers, gelée avant mesure."""
    if n <= 0:
        return [0]
    etape = max(1, n // pas)
    return sorted({min(etape * (j + 1), n) for j in range(pas)})


def predire_cumul(n: int, kmax: int = KMAX, pas: int = PAS_CUMUL) -> Dict[str, Any]:
    """Courbe cumulative annoncée, avec le seuil de Bonferroni sur les points déclarés."""
    grille = grille_cumul(n, pas)
    tests = len(grille) * len(CONSTANTES)
    alpha_point = ALPHA / tests
    return {"grille": grille, "attendu": cumuls_auto_local_attendus(n, grille, kmax),
            "points": len(grille), "tests": tests, "alpha_par_point": alpha_point,
            "z_seuil_bonferroni": z_de_p_bilatere(alpha_point)}


def predire_runs(n: int, rmax: int = RMAX) -> Dict[str, Any]:
    attendu = {r: float(esperance_runs(n, r)) for r in range(1, rmax + 1)}
    total_exact = 1.0 + 0.9 * max(0, n - 1)
    return {"attendu": attendu, "somme_comptee": sum(attendu.values()),
            "total_runs_exact": total_exact,
            "queue_non_comptee": total_exact - sum(attendu.values())}


def predire_occulence(n: int, longueurs: Sequence[int] = K_OCCULENCE) -> Dict[str, Any]:
    sortie: Dict[int, Any] = {}
    for k in longueurs:
        e = float(esperance_occulence(n, k))
        sortie[k] = {"fenetres": max(0, n - k + 1), "presentes_attendues": e,
                     "absentes_attendues": 10 ** k - e,
                     "sigma_independant": math.sqrt(variance_occulence_independante(n, k))}
    return sortie


def predire_attentes(n: int, sondes: Sequence[str] = SONDES) -> Dict[str, Any]:
    return {s: loi_attente_geometrique(len(s), n) for s in sondes}


def predire(n: int, kmax: int = KMAX, rmax: int = RMAX,
            longueurs: Sequence[int] = K_OCCULENCE,
            sondes: Sequence[str] = SONDES) -> Dict[str, Any]:
    """Table gelée : uniquement des entiers entrent, aucun chiffre ne est lu."""
    par_constante = (10 + 1 + kmax + 1 + rmax + len(longueurs) + len(sondes))
    return {
        "domaine": {"n": n, "kmax": kmax, "rmax": rmax, "longueurs": list(longueurs),
                    "sondes": list(sondes), "constantes": list(CONSTANTES)},
        "regles": {"alpha": ALPHA, "z_seuil": Z_SEUIL,
                   "limite_poisson_exact": LIMITE_POISSON_EXACT,
                   "pas_cumul": PAS_CUMUL, "bande_rapport": list(BANDE_RAPPORT),
                   "bande_kappa": list(KAPPA_BANDE),
                   "methodes": {"compte": "Poisson bilatère exact, normale au-delà de λ",
                                "frequence": "normale (binomiale) bilatère",
                                "position": "transformée intégrale, uniforme",
                                "binaire": "Bernoulli bilatère exact"},
                   "cellules_par_constante": par_constante,
                   "cellules_total": 3 * par_constante},
        "frequence": predire_frequence(n),
        "auto_local": predire_auto_local(n, kmax),
        "cumul": predire_cumul(n, kmax),
        "runs": predire_runs(n, rmax),
        "occulence": predire_occulence(n, longueurs),
        "attentes": predire_attentes(n, sondes),
    }


# ============================================================================
# SIMULATION — troisième voie de comptage, mêmes primitives que la mesure
# ============================================================================

def chiffres_au_hasard(n: int, rng: random.Random) -> str:
    morceaux: List[str] = []
    reste = n
    while reste > 0:
        q = min(9, reste)
        morceaux.append(str(rng.randrange(10 ** q)).zfill(q))
        reste -= q
    return "".join(morceaux)


def moments(v: Sequence[float]) -> Tuple[float, float]:
    if not v:
        return (0.0, 0.0)
    m = sum(v) / len(v)
    if len(v) < 2:
        return (m, 0.0)
    return (m, math.sqrt(sum((x - m) ** 2 for x in v) / (len(v) - 1)))


def simuler(n: int, repiliques: int, graine: int, longueurs: Sequence[int] = K_CALIBREES,
            kmax: int = KMAX, rmax: int = RMAX) -> Dict[str, Any]:
    rng = random.Random(graine)
    totaux: List[int] = []
    chi: List[float] = []
    occ = {k: [] for k in longueurs}
    runs = {r: [] for r in range(1, rmax + 1)}
    for _ in range(repiliques):
        s = chiffres_au_hasard(n, rng)
        chi.append(chi2_frequence(mesurer_frequence(s)))
        totaux.append(len(positions_auto_local(s, kmax)))
        rr = mesurer_runs(s, rmax)
        for r in range(1, rmax + 1):
            runs[r].append(rr[r])
        oo = mesurer_occulence(s, longueurs)
        for k in longueurs:
            occ[k].append(oo[k])
    return {"n": n, "repiliques": repiliques, "graine": graine,
            "auto_local_total": moments(totaux), "chi2": moments(chi),
            "runs": {r: moments(v) for r, v in runs.items()},
            "occulence": {k: moments(v) for k, v in occ.items()}}


def calibrage(n_sim: int, n_sim2: int, repiliques: int, repiliques2: int,
              graine: int, kmax: int = KMAX) -> Dict[str, Any]:
    """κ = variance simulée / variance d'indépendance, et preuve de la loi en √n."""
    a = simuler(n_sim, repiliques, graine, kmax=kmax)
    b = simuler(n_sim2, repiliques2, graine + 1, kmax=kmax)
    kappa: Dict[int, Any] = {}
    for k in K_CALIBREES:
        emp = a["occulence"][k][1] ** 2
        the = variance_occulence_independante(n_sim, k)
        emp2 = b["occulence"][k][1] ** 2
        kappa[k] = {"sigma_simule": math.sqrt(emp), "sigma_independant": math.sqrt(the),
                    "kappa": emp / the if the else 0.0,
                    "rapport_sqrt_n": math.sqrt(emp / emp2 / (n_sim / n_sim2)) if emp2 else None}
    rapport: Dict[str, Any] = {"auto_local_total": None, "runs": {}}
    if b["auto_local_total"][1]:
        rapport["auto_local_total"] = (a["auto_local_total"][1] / b["auto_local_total"][1]
                                       / math.sqrt(n_sim / n_sim2))
    kappa_runs: Dict[int, float] = {}
    for r in range(1, RMAX + 1):
        # un écart-type sur une longueur rare n'est pas estimable : λ déclaré sert de filtre
        lam_r = float(esperance_runs(n_sim, r))
        if lam_r < MIN_LAMBDA_RAPPORT:
            continue
        kappa_runs[r] = a["runs"][r][1] ** 2 / lam_r
        s1, s2 = a["runs"][r][1], b["runs"][r][1]
        if s2 and float(esperance_runs(n_sim2, r)) >= MIN_LAMBDA_RAPPORT:
            rapport["runs"][r] = s1 / s2 / math.sqrt(n_sim / n_sim2)
    rapport["testes"] = len(rapport["runs"]) + (1 if rapport["auto_local_total"] else 0)
    return {"principal": a, "second": b, "kappa_occulence": kappa, "kappa_runs": kappa_runs,
            "rapport_loi_sqrt_n": rapport,
            "auto_local_attendu_a_n_sim": predire_auto_local(n_sim, kmax)["total_attendu"],
            "note": "κ ≤ 1 : l'indépendance surestime la variance ; la bande reste prudente"}


def valeurs_rapport(cal: Dict[str, Any]) -> List[float]:
    v = [cal["rapport_loi_sqrt_n"]["auto_local_total"]]
    v += [x for x in cal["rapport_loi_sqrt_n"]["runs"].values() if x]
    return [x for x in v if x]


# ============================================================================
# CONFRONTATION
# ============================================================================

def _cellule(nom: str, attendu: float, obtenu: Any, p: float, meth: str) -> Dict[str, Any]:
    return {"nom": nom, "attendu": attendu, "obtenu": obtenu,
            "p_bilatere": p, "methode": meth,
            "verdict": "CONTENU" if p >= ALPHA else "EXCLUE"}


def confronter(pred: Dict[str, Any], mesures: Dict[str, Dict[str, Any]],
               cal: Dict[str, Any]) -> Dict[str, Any]:
    n = pred["domaine"]["n"]
    pf, pa = pred["frequence"], pred["auto_local"]
    prun, po, patt = pred["runs"], pred["occulence"], pred["attentes"]
    cellules: List[Dict[str, Any]] = []
    for c in CONSTANTES:
        m = mesures[c]
        for d in range(10):
            o = m["frequence"][d]
            z = (o - pf["attendu_par_chiffre"]) / pf["sigma"] if pf["sigma"] else 0.0
            cellules.append(_cellule(f"{c}.frequence.{d}", pf["attendu_par_chiffre"], o,
                                     p_bilatere_normale(z), "frequence"))
        lo, hi = pf["chi2_intervalle"]
        contenu = lo <= m["chi2"] <= hi
        cellules.append(_cellule(f"{c}.chi2", pf["chi2_attendu"], m["chi2"],
                                 1.0 if contenu else 0.0, "intervalle Wilson–Hilferty"))
        for k, att in pa["par_classe"].items():
            x = m["auto_local_classes"][k]
            cellules.append(_cellule(f"{c}.auto_local.k{k}", att["esperance"], x,
                                     p_bilatere_poisson(att["esperance"], x), "compte"))
        cellules.append(_cellule(f"{c}.auto_local.total", pa["total_attendu"],
                                 m["auto_local_total"],
                                 p_bilatere_poisson(pa["total_attendu"], m["auto_local_total"]),
                                 "compte"))
        for r, e in prun["attendu"].items():
            x = m["runs"][r]
            cellules.append(_cellule(f"{c}.run{r}", e, x, p_bilatere_compte(e, x), "compte"))
        for k, att in po.items():
            kap = cal["kappa_occulence"].get(min(k, max(cal["kappa_occulence"])),
                                             {"kappa": 1.0})["kappa"]
            sigma = att["sigma_independant"] * math.sqrt(max(kap, 0.0))
            x = m["occulence"][k]
            z = (x - att["presentes_attendues"]) / sigma if sigma else 0.0
            cellules.append(_cellule(f"{c}.occulence.k{k}", att["presentes_attendues"], x,
                                     p_bilatere_normale(z), "compte, variance calibrée κ"))
        for s, att in patt.items():
            pos = m["attentes"][s]
            q_present = att["probabilite_de_presence"]
            if pos is None:
                cellules.append(_cellule(f"{c}.attente.{s}", q_present, "absente",
                                         p_bilatere_bernoulli(q_present, False), "binaire"))
            else:
                u = percentile_attendu(pos, len(s))
                cellules.append(_cellule(f"{c}.attente.{s}", 0.5, u,
                                         min(1.0, 2.0 * min(u, 1.0 - u)), "position"))
    exclues = [x for x in cellules if x["verdict"] == "EXCLUE"]
    ncell = len(cellules)
    lam = ncell * ALPHA
    return {"cellules": cellules, "nombre_cellules": ncell,
            "exclues": [x["nom"] for x in exclues], "nombre_exclues": len(exclues),
            "exclues_attendues": lam,
            "p_globale": p_bilatere_poisson(lam, len(exclues)),
            "verdict_global": ("CONTENU" if p_bilatere_poisson(lam, len(exclues)) >= ALPHA
                               else "EXCLUE"),
            "deviance_auto_local": deviance_auto_local(pa, mesures)}


def deviance_auto_local(pa: Dict[str, Any], mesures: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    """G² de déviance de Poisson sur 3 constantes × KMAX classes, χ²(3·KMAX) déclaré."""
    g2 = lam_t = 0.0
    x_t = 0
    for c in CONSTANTES:
        for k, att in pa["par_classe"].items():
            lam, x = att["esperance"], mesures[c]["auto_local_classes"][k]
            lam_t += lam
            x_t += x
            g2 += 2.0 * (x * math.log(x / lam) + lam - x) if x else 2.0 * lam
    df = 3 * len(pa["par_classe"])
    lo, hi = chi2_intervalle(df)
    return {"g2": g2, "df": df, "x_total": x_t, "lambda_total": lam_t,
            "intervalle": [lo, hi], "verdict": "CONTENU" if lo <= g2 <= hi else "EXCLUE"}


# ============================================================================
# ASSEMBLAGE
# ============================================================================

def _eq(id_: str, chemin: str, formule: str, resultat: str, statut: str, detail: Any,
        chapitre: Optional[Sequence[Any]] = None, limite: str = "") -> Dict[str, Any]:
    return {"id": id_, "chemin": chemin, "formule": formule, "resultat": resultat,
            "statut": statut, "limite": limite, "detail": detail,
            "chapitre": ({"debut": chapitre[0], "titre": chapitre[1]} if chapitre else None)}


def _chap(i: int) -> List[str]:
    return VIDEO["chapitres"][i]


def algebre_0_9(kmax: int = 20) -> Dict[str, Any]:
    verifie = {k: str(esperance_auto_local(10 ** k + k, k)) for k in range(1, kmax + 1)}
    return {"par_classe": verifie,
            "toutes_egales_9_dixiemes": all(
                esperance_auto_local(10 ** k + k, k) == Fraction(9, 10)
                for k in range(1, kmax + 1)),
            "k_testes": kmax}


def convention_indexage(chaine_pi: str) -> Dict[str, Any]:
    """La position 1 est la première décimale ; l'autre convention décale de exactement 1."""
    n = len(chaine_pi)
    a = positions_auto_local(chaine_pi)
    decale = [p - 1 for p in a if p >= 2]
    return {"convention_retenue": "position 1 = première décimale",
            "chiffre_en_position_1": chaine_pi[0] if n else None,
            "positions_convention_retenue": a[:8],
            "positions_convention_alternative": decale[:8],
            "decalage_exact": 1 if n else 0,
            "16470_auto_localise": bool(n > 16474 and int(chaine_pi[16469:16474]) == 16470)}


def ancre_publiee(chaine: str, reference: str) -> Dict[str, Any]:
    """Confronte la chaîne produite par l'inégalité entière aux décimales citées ailleurs.

    Les deux voies sont indépendantes : la constante ci-dessus n'est produite par aucun
    code de ce dossier ; rien ici n'affirme que 50 chiffres prouvent quoi que ce soit.
    """
    comparable = min(LONGUEUR_ANCRE, len(chaine), len(reference))
    premier = next((i for i in range(comparable) if chaine[i] != reference[i]), None)
    return {"chiffres_comparables": comparable,
            "ancre_complete": comparable == LONGUEUR_ANCRE,
            "identique": premier is None,
            "premier_desaccord": premier}


def resoudre(n: int = N_COURT, n_sim: int = 5_000, n_sim2: int = 2_500,
             repiliques: int = 200, repiliques2: int = 100,
             kmax: int = KMAX, rmax: int = RMAX) -> Dict[str, Any]:
    certificats = {c: GEN.decimales(c, n) for c in CONSTANTES}
    chaines = {c: certificats[c]["chiffres"] for c in CONSTANTES}
    mesures = {c: mesurer(chaines[c], kmax, rmax) for c in CONSTANTES}
    pred = predire(n, kmax, rmax)
    cal = calibrage(n_sim, n_sim2, repiliques, repiliques2, GRAINE, kmax)
    conf = confronter(pred, mesures, cal)
    croisement = GEN.croiser(min(500, n))
    ancre = {c: ancre_publiee(chaines[c], CHIFFRES_DE_REFERENCE[c]) for c in CONSTANTES}
    conv = convention_indexage(chaines["pi"])
    alg = algebre_0_9()
    x_cumul = pred["cumul"]["grille"]
    att_cumul = pred["cumul"]["attendu"]
    y_cumul = {c: [p[1] for p in mesures[c]["cumul"]] for c in CONSTANTES}
    z_cumul = max((abs(y - a) / math.sqrt(a) if a > 0 else abs(y - a))
                  for c in CONSTANTES for y, a in zip(y_cumul[c], att_cumul))
    grille_conforme = all([p[0] for p in mesures[c]["cumul"]] == x_cumul for c in CONSTANTES)

    eqs: List[Dict[str, Any]] = [
        _eq("EQ-01", "chiffres_pi.py → generer_chiffres.decimales_pi() → C01",
            "π = 426880·√10005 / Σ(−1)ᵏ(6k)!(A+Bk)/((3k)!(k!)³C³), splitting binaire",
            f"{n} décimales certifiées · {certificats['pi']['termes']} termes · marge "
            f"{certificats['pi']['marge_chiffres']} chiffres de garde",
            "OPÉRATIONNEL",
            dict({k: v for k, v in certificats["pi"].items() if k != "chiffres"},
                 ancre_publiee=ancre["pi"]),
            limite="l'identité de Chudnovsky est déclarée (littérature) ; alternance, "
                   "contraction et plancher sont vérifiés ici en entiers"),
        _eq("EQ-02", "chiffres_pi.py → generer_chiffres.pi_par_machin() → C02",
            "π = 16·arccot 5 − 4·arccot 239 (Machin 1706), bornes alternées",
            f"accord sur {croisement['pi']['n']} chiffres · premier désaccord "
            f"{croisement['pi']['premier_desaccord']}", "OPÉRATIONNEL", croisement["pi"],
            limite="Machin 1706 est une identité déclarée, pas une démonstration : l'accord "
                   "entre deux voies entières certifie que le générateur ne dérive pas d'une "
                   "décimale à l'autre, rien de plus sur la suite elle-même"),
        _eq("EQ-03", "chiffres_pi.py → generer_chiffres.decimales_e() → C03",
            "e = Σ 1/k!, queue < 1/(m·m!) avec m·m! > 10^(n+40)",
            f"{n} décimales certifiées · m = {certificats['e']['termes'] - 1} · "
            f"Q = m! vérifié {certificats['e']['factorielle_egale']}",
            "OPÉRATIONNEL",
            dict({k: v for k, v in certificats["e"].items() if k != "chiffres"},
                 ancre_publiee=ancre["e"]),
            limite="la série de e est classique et la queue bornée par une inégalité entière : "
                   "le certificat atteste les n décimales produites, il ne dit pas que la suite "
                   "infinie est normale ni qu'elle est dépourvue de motif"),
        _eq("EQ-04", "chiffres_pi.py → generer_chiffres.decimales_racine2() → C04",
            "w = ⌊√2·10ⁿ⌋ éprouvé par w² ≤ 2·10²ⁿ < (w+1)²",
            f"{n} décimales, preuve {certificats['racine2']['certifie']} · voie Newton "
            f"{croisement['racine2']['identique']}", "OPÉRATIONNEL",
            dict({k: v for k, v in certificats["racine2"].items() if k != "chiffres"},
                 ancre_publiee=ancre["racine2"]),
            limite="aucune série, aucun emprunt : la seule inégalité entière qui définit "
                   "les décimales est mise à l'épreuve"),
        _eq("EQ-05", "chiffres_pi.py → convention_indexage() → C05",
            "position 1 = première décimale ; l'autre convention décale de 1",
            f"première décimale de π = {conv['chiffre_en_position_1']} et elle est en "
            f"position 1 ; 16470 auto-localisé : {conv['16470_auto_localise']}",
            "OPÉRATIONNEL", conv, _chap(1),
            limite="un choix d'écriture, pas un fait : les deux conventions diffèrent d'un "
                   "décalage et aucune statistique de ce dossier n'en dépend ; la valeur "
                   "affichée n'a de sens que dans la convention déclarée ici"),
        _eq("EQ-06", "chiffres_pi.py → predire() → C06",
            "H0 : décimales i.i.d. uniformes sur {0,…,9}",
            f"{pred['regles']['cellules_total']} cellules déclarées · ALPHA = {ALPHA} · "
            f"z seuil {Z_SEUIL:.6f} · {ALPHA * pred['regles']['cellules_total']:.3f} "
            f"exclusion(s) attendue(s)",
            "SPÉCIFIÉ", pred["regles"],
            limite="H0 n'est démontrée pour aucune des trois constantes — normalité simple, "
                   "ouverte depuis Borel (1909)"),
        _eq("EQ-07", "chiffres_pi.py → mesurer_frequence() → C07",
            "E[compte] = n/10, σ = √(0,09n), χ²(9) : 9 ± √18, intervalle Wilson–Hilferty",
            f"π χ² {mesures['pi']['chi2']:.4f} · e {mesures['e']['chi2']:.4f} · "
            f"√2 {mesures['racine2']['chi2']:.4f} dans "
            f"[{pred['frequence']['chi2_intervalle'][0]:.3f}, "
            f"{pred['frequence']['chi2_intervalle'][1]:.3f}]",
            "OPÉRATIONNEL", {c: {"compte": mesures[c]["frequence"],
                                 "chi2": mesures[c]["chi2"]} for c in CONSTANTES},
            limite="un χ² dans l'intervalle est une absence de rejet, jamais une preuve "
                   "d'uniformité ; la référence χ²(9) est une approximation asymptotique "
                   "appliquée à n = 20 000 chiffres, et les comptes d'une constante ne "
                   "transportent rien sur les autres"),
        _eq("EQ-08", "chiffres_pi.py → esperance_auto_local() → C08",
            "λ_k = 9·10^(k−1) · 10^(−k) = 9/10",
            f"exact en fractions pour k = 1..{alg['k_testes']} : {alg['par_classe'][1]}",
            "OPÉRATIONNEL", alg, _chap(3),
            limite="identité du modèle, pas une mesure : elle dit ce que H0 promet"),
        _eq("EQ-09", "chiffres_pi.py → positions_auto_local() → C09",
            "p tel que la lecture en p redonne p",
            f"π : {mesures['pi']['auto_local_positions'][:6]} … "
            f"{mesures['pi']['auto_local_total']} au total",
            "OPÉRATIONNEL", {c: {"positions": mesures[c]["auto_local_positions"],
                                 "total": mesures[c]["auto_local_total"]} for c in CONSTANTES},
            _chap(0),
            limite="propriété arithmétique de la chaîne finie réellement produite : une "
                   "position auto-localisée près de la borne du domaine peut disparaître si "
                   "n change, et rien ici n'étend ces positions au-delà des n décimales"),
        _eq("EQ-10", "chiffres_pi.py → classes_auto_local() → C10",
            "compte par classe de longueur, Poisson(λ_k) indépendante du nombre de chiffres",
            "π " + ", ".join(f"k{k}:{mesures['pi']['auto_local_classes'][k]}/"
                             f"{v['esperance']:.4f}∈{v['intervalle']}"
                             for k, v in pred["auto_local"]["par_classe"].items()),
            "OPÉRATIONNEL",
            {c: {"attendu": {k: v["esperance"] for k, v in pred["auto_local"]["par_classe"].items()},
                 "obtenu": mesures[c]["auto_local_classes"]} for c in CONSTANTES}, _chap(2),
            limite="le Poisson attendu est une loi du modèle H0 appliquée à un domaine fini : "
                   "le compte observé borne le rejet de H0 sur cette classe, il ne départage "
                   "pas π d'une suite uniforme fabriquée"),
        _eq("EQ-11", "chiffres_pi.py → mesurer_cumul() → C11",
            "E[N(x)] = Σ_{k'<k}λ_k' + (x − 10^(k−1) + 1)·10^(−k)",
            f"cumul sur {len(x_cumul)} points déclarés · |z| maximal {z_cumul:.3f} contre "
            f"le seuil de Bonferroni {pred['cumul']['z_seuil_bonferroni']:.3f}",
            "OPÉRATIONNEL", {"grille": x_cumul, "obtenu": y_cumul, "attendu": att_cumul,
                             "z_max": z_cumul,
                             "seuil": pred["cumul"]["z_seuil_bonferroni"]}, _chap(5),
            limite="la correction de Bonferroni ne porte que sur la grille de points déclarée "
                   "avant mesure : une autre grille donnerait un autre seuil, et un |z| maximal "
                   "sous ce seuil n'est pas une preuve d'indépendance des décimales"),
        _eq("EQ-12", "chiffres_pi.py → calibrage() → C12",
            "analytique / Monte-Carlo (MT19937, graine déclarée) / balayage direct",
            f"à n_sim = {n_sim} : simulé {cal['principal']['auto_local_total'][0]:.3f} ± "
            f"{cal['principal']['auto_local_total'][1]:.3f} vs analytique "
            f"{cal['auto_local_attendu_a_n_sim']:.3f}",
            "OPÉRATIONNEL", {k: v for k, v in cal.items() if k not in ("principal", "second")},
            _chap(6),
            limite="le tirage éprouve l'analytique sur un générateur pseudo-aléatoire dont la "
                   "période et la graine sont déclarées : il valide la chaîne de calcul des "
                   "attendus, il n'introduit aucun coup de dé dans les décimales de π"),
        _eq("EQ-13", "chiffres_pi.py → mesurer_runs() → C13",
            "E[run de longueur r] = (n−r−1)·0,81·10^(−(r−1)) + 1,8·10^(−(r−1))",
            "π " + ", ".join(f"r{r}:{mesures['pi']['runs'][r]}/{e:.1f}"
                             for r, e in pred["runs"]["attendu"].items()),
            "OPÉRATIONNEL", {c: mesures[c]["runs"] for c in CONSTANTES}, _chap(4),
            limite="la loi attendue des runs est celle du modèle i.i.d. ; la formule néglige "
                   "les bords de la chaîne et le nombre de runs longs croît avec n : la "
                   "coïncidence des comptes mesure le domaine, pas la suite"),
        _eq("EQ-14", "chiffres_pi.py → mesurer_occulence() → C14",
            "E[k-présentes] = 10^k·(1 − (1 − 10^(−k))^m)",
            "π " + ", ".join(f"k{k}:{mesures['pi']['occulence'][k]}/{a['presentes_attendues']:.0f}"
                             for k, a in pred["occulence"].items()),
            "OPÉRATIONNEL", {c: mesures[c]["occulence"] for c in CONSTANTES}, _chap(8),
            limite="compter les k-uplets présents dans un domaine fini ne dit rien de leur "
                   "présence au-delà : l'occulence est ici une mesure du domaine exploré, pas "
                   "d'une propriété de normalité de la suite"),
        _eq("EQ-15", "chiffres_pi.py → mesurer_attentes() → C15",
            "T ~ géométrique(10^(−L)) ; u = P(T ≤ t) doit suivre une uniforme",
            "π " + ", ".join(f"{s}:{mesures['pi']['attentes'][s]}" for s in SONDES),
            "OPÉRATIONNEL",
            {c: {"positions": mesures[c]["attentes"],
                 "u": {s: percentile_attendu(p, len(s))
                       for s, p in mesures[c]["attentes"].items()}} for c in CONSTANTES},
            _chap(8),
            limite="les cinq sondes sont déclarées avant toute mesure ; aucune n'est "
                   "choisie après avoir vu les chiffres"),
        _eq("EQ-16", "chiffres_pi.py → deviance_auto_local() → C16",
            "G² = 2Σ[x·ln(x/λ) + λ − x] ~ χ²(3·KMAX)",
            f"G² = {conf['deviance_auto_local']['g2']:.3f} sur "
            f"{conf['deviance_auto_local']['df']} ddl, "
            f"[{conf['deviance_auto_local']['intervalle'][0]:.2f}, "
            f"{conf['deviance_auto_local']['intervalle'][1]:.2f}] → "
            f"{conf['deviance_auto_local']['verdict']}",
            "OPÉRATIONNEL", {c: mesures[c]["auto_local_classes"] for c in CONSTANTES}, _chap(7),
            limite="l'intervalle de référence est une approximation asymptotique du χ² à "
                   "3·KMAX degrés de liberté, sommée sur les trois constantes : un G² qui y "
                   "tombe borne le rejet, il n'équivaut pas à une preuve de normalité"),
        _eq("EQ-17", "chiffres_pi.py → confronter() → C17",
            f"rejet si p < {ALPHA} ; global : Poisson(α·cellules) sur le nombre d'exclusions",
            f"{conf['nombre_exclues']} exclues sur {conf['nombre_cellules']} "
            f"(attendu {conf['exclues_attendues']:.2f}), p = {conf['p_globale']:.4f} → "
            f"{conf['verdict_global']}",
            "OPÉRATIONNEL", {"exclues": conf["exclues"], "p_globale": conf["p_globale"]},
            _chap(9),
            limite="aucune preuve de normalité : confrontation sur domaine fini déclaré. "
                   "Un échec ici ne prouverait rien ; une réussite ne prouve rien"),
    ]
    controles = _controles(certificats, croisement, chaines, mesures, pred, conf, cal,
                           conv, alg, z_cumul, grille_conforme, kmax, rmax, ancre)
    return {"domaine": {"n": n, "n_sim": n_sim, "n_sim2": n_sim2, "repiliques": repiliques,
                        "graine": GRAINE, "alpha": ALPHA, "z_seuil": Z_SEUIL,
                        "kmax": kmax, "rmax": rmax},
            "video": VIDEO, "equations": eqs, "controles": controles,
            "predictions": pred, "mesures": mesures, "confrontation": conf,
            "certificats": {c: dict({k: v for k, v in certificats[c].items() if k != "chiffres"},
                                    ancre_publiee=ancre[c]) for c in CONSTANTES},
            "calibrage": {k: v for k, v in cal.items() if k not in ("principal", "second")}}


def _controles(certificats: Dict[str, Any], croisement: Dict[str, Any],
               chaines: Dict[str, str], mesures: Dict[str, Any], pred: Dict[str, Any],
               conf: Dict[str, Any], cal: Dict[str, Any], conv: Dict[str, Any],
               alg: Dict[str, Any], z_cumul: float, grille_conforme: bool,
               kmax: int, rmax: int, ancre: Dict[str, Any]) -> List[Dict[str, Any]]:
    n = len(chaines["pi"])
    out: List[Dict[str, Any]] = []

    def ajouter(id_: str, nom: str, attendu: str, obtenu: str, ok: bool) -> None:
        out.append({"id": id_, "nom": nom, "attendu": attendu, "obtenu": obtenu,
                    "ok": bool(ok)})

    ok1 = (certificats["pi"]["certifie"] and certificats["pi"]["contraction_valide"]
           and certificats["pi"]["alternance_valide"]
           and all(a["identique"] and a["ancre_complete"] for a in ancre.values()))
    desaccords = {LIBELLES[c]: ancre[c]["premier_desaccord"] for c in CONSTANTES
                  if ancre[c]["premier_desaccord"] is not None}
    ajouter("C01", "certificat de π : alternance, contraction, plancher forcé ; et les "
                   f"{LONGUEUR_ANCRE} décimales publiées des trois sont rendues sans désaccord",
            f"True True True et {LONGUEUR_ANCRE}/{LONGUEUR_ANCRE} conformes",
            f"{certificats['pi']['certifie']} {certificats['pi']['alternance_valide']} "
            f"{certificats['pi']['contraction_valide']} ; ancre = "
            f"{sum(1 for c in CONSTANTES if ancre[c]['identique'])}/3 "
            f"et {LONGUEUR_ANCRE} chiffres comparés ; désaccords = {desaccords or 'aucun'}",
            ok1)
    ajouter("C02", "Machin rend les mêmes chiffres que Chudnovsky",
            "identique + certifié",
            f"{croisement['pi']['identique']}/{croisement['pi']['certifie_2']}",
            croisement["pi"]["identique"] and croisement["pi"]["certifie_2"])
    ajouter("C03", "certificat de e et Q = m! exact", "True True",
            f"{certificats['e']['certifie']}/{certificats['e']['factorielle_egale']}",
            certificats["e"]["certifie"] and certificats["e"]["factorielle_egale"])
    ajouter("C04", "√2 prouvé par les carrés et concordant avec Newton", "True True",
            f"{certificats['racine2']['certifie']}/{croisement['racine2']['identique']}",
            certificats["racine2"]["certifie"] and croisement["racine2"]["identique"])
    ajouter("C05", "convention d'indexage : décalage exactement 1, position 1 = 1",
            "1 ; décalage 1",
            f"{conv['chiffre_en_position_1']} ; {conv['decalage_exact']}",
            (not n or conv["chiffre_en_position_1"] == "1") and conv["decalage_exact"] == 1)
    rejeu = predire(n, kmax, rmax)
    ajouter("C06", "predire(n) ne lit aucun chiffre : table identique, définie à n = 0",
            "identique et n=0 défini",
            f"identique={rejeu == pred}, n0={bool(predire(0, kmax, rmax))}",
            rejeu == pred and bool(predire(0, kmax, rmax))
            and conf["nombre_cellules"] == pred["regles"]["cellules_total"])
    ok7 = (all(sum(mesures[c]["frequence"]) == n for c in CONSTANTES)
           and all(all("0" <= ch <= "9" for ch in chaines[c]) for c in CONSTANTES)
           and all(pred["frequence"]["chi2_intervalle"][0] <= mesures[c]["chi2"]
                   <= pred["frequence"]["chi2_intervalle"][1] for c in CONSTANTES))
    ajouter("C07", "Σ comptes = n, chaînes pures, χ²(9) dans l'intervalle des trois",
            "True", str(ok7), ok7)
    ajouter("C08", "algèbre du 0,9 exacte en fractions, k = 1..20", "True",
            str(alg["toutes_egales_9_dixiemes"]), alg["toutes_egales_9_dixiemes"])
    ok9 = all(verifier_auto_local(chaines[c], mesures[c]["auto_local_positions"])
              for c in CONSTANTES)
    ajouter("C09", "chaque position rendue relit bien son propre numéro", "True", str(ok9), ok9)
    c5 = pred["auto_local"]["par_classe"][5]["candidats"]
    ok10 = (c5 == 90_000) if n >= 100_005 else (c5 == max(0, n - 5 + 1 - 10_000 + 1))
    ok10 = ok10 and all(sum(mesures[c]["auto_local_classes"].values())
                        == mesures[c]["auto_local_total"] for c in CONSTANTES)
    ajouter("C10", "candidats de classe 5 = 90 000 dès que le domaine le permet, "
                   "et classes cohérentes avec la liste",
            "90000 (n ≥ 100005)", f"{c5}, n = {n}", ok10)
    seuil_cumul = pred["cumul"]["z_seuil_bonferroni"]
    monotone = all(y1 <= y2 for c in CONSTANTES
                   for (_, y1), (_, y2) in zip(mesures[c]["cumul"], mesures[c]["cumul"][1:]))
    ajouter("C11", "cumul auto-local : grille annoncée retrouvée, courbe croissante, "
                   "|z| sous le seuil de Bonferroni",
            f"grille et ≤ {seuil_cumul:.3f}",
            f"{z_cumul:.3f} monotone={monotone} grille={grille_conforme}",
            monotone and grille_conforme and z_cumul < seuil_cumul)
    ra = cal["principal"]["auto_local_total"][0]
    diff = abs(ra - cal["auto_local_attendu_a_n_sim"])
    sigma = cal["principal"]["auto_local_total"][1] / math.sqrt(cal["principal"]["repiliques"])
    lo_b, hi_b = BANDE_RAPPORT
    rapports = valeurs_rapport(cal)
    ok12 = (sigma > 0 and diff <= 3 * sigma and bool(rapports)
            and all(lo_b <= v <= hi_b for v in rapports))
    ajouter("C12", "trois voies de comptage : simulé ≈ analytique à ±3 σ de la moyenne, "
                   "rapports d'écarts-types dans la bande √n",
            f"Δ ≤ {3 * sigma:.4f} et {lo_b} ≤ rapport ≤ {hi_b}",
            f"Δ = {diff:.4f} ; rapports = {[round(v, 3) for v in rapports]}", ok12)
    total_runs = 1 + 0.9 * (n - 1)
    bilan = sum(mesures["pi"]["runs"].values()) + pred["runs"]["queue_non_comptee"]
    ecart = abs(bilan - total_runs)
    sigma_r = math.sqrt(0.9 * n * 0.1) if n else 1.0
    ajouter("C13", "bilan des runs : comptés + queue = 1 + 0,9(n−1)",
            f"≤ 3√(0,09n) = {3 * sigma_r:.1f}", f"{ecart:.1f}", ecart <= 3 * sigma_r)
    kap = ([v["kappa"] for v in cal["kappa_occulence"].values()]
           + list(cal["kappa_runs"].values()))
    lo_k, hi_k = KAPPA_BANDE
    m4 = cal["principal"]["occulence"][K_CALIBREES[-1]][0]
    a4 = float(esperance_occulence(cal["principal"]["n"], K_CALIBREES[-1]))
    tol14 = max(3.0, 0.01 * a4)
    ok14 = (bool(kap) and all(lo_k <= v <= hi_k for v in kap)
            and abs(m4 - a4) <= tol14)
    ajouter("C14", "variances simulées dans la bande κ déclarée (occulence et runs) ; "
                   "moyenne simulée ≈ analytique",
            f"{lo_k} ≤ κ ≤ {hi_k} ; |Δ| ≤ {tol14:.1f}",
            f"κ={[round(v, 3) for v in kap]} Δ={abs(m4 - a4):.2f}", ok14)
    q_sondes = sum(a["probabilite_de_presence"] for a in pred["attentes"].values())
    lam_sondes = q_sondes * len(CONSTANTES)
    n_presentes = sum(1 for c in CONSTANTES for s in SONDES
                      if mesures[c]["attentes"][s] is not None)
    lo15, hi15 = intervalle_poisson(lam_sondes)
    ajouter("C15", "les cinq sondes déclarées : le nombre de celles qu'on retrouve tombe "
                   "dans l'intervalle Poisson de leurs probabilités de présence",
            f"[{lo15}, {hi15}] (λ = {lam_sondes:.3f})",
            f"{n_presentes} sur {len(SONDES) * len(CONSTANTES)}",
            lo15 <= n_presentes <= hi15)
    dev = conf["deviance_auto_local"]
    ajouter("C16", "G² auto-local dans l'intervalle χ²(3·KMAX)",
            f"[{dev['intervalle'][0]:.2f}, {dev['intervalle'][1]:.2f}]", f"{dev['g2']:.3f}",
            dev["verdict"] == "CONTENU")
    ajouter("C17", "verdict global : exclusions ~ Poisson(α·cellules)",
            f"p ≥ {ALPHA}", f"{conf['p_globale']:.4f} ({conf['nombre_exclues']}/"
            f"{conf['nombre_cellules']})", conf["verdict_global"] == "CONTENU")
    return out


def verifier(donnees: Optional[Dict[str, Any]] = None) -> bool:
    donnees = donnees or resoudre()
    return all(c["ok"] for c in donnees["controles"])


def octets_confrontation_csv(cellules: Sequence[Dict[str, Any]]) -> bytes:
    """Le CSV livré, en octets : BOM UTF-8, séparateur « ; », décimale française,
    fins de ligne CRLF écrites à la main. Le format Excel français est une
    promesse du dossier ; le mode texte, lui, la laisse dépendre du système."""
    lignes: List[List[Any]] = [["constante", "statistique", "classe", "attendu", "obtenu",
                                "p_bilatere", "verdict"]]
    for cel in cellules:
        constante, reste = cel["nom"].split(".", 1)
        stats, _, classe = reste.partition(".")
        lignes.append([LIBELLES.get(constante, constante), stats, classe,
                       f"{cel['attendu']:.6g}", cel["obtenu"],
                       f"{cel['p_bilatere']:.6g}", cel["verdict"]])
    corps = "\r\n".join(";".join(str(x).replace(".", ",") for x in ligne) for ligne in lignes)
    return b"\xef\xbb\xbf" + (corps + "\r\n").encode("utf-8")


def ecrire_artefacts(donnees: Dict[str, Any], vers: Optional[Path] = None) -> Dict[str, str]:
    import json

    dossier = vers or (RACINE / "artefacts")
    dossier.mkdir(parents=True, exist_ok=True)
    rendu: Dict[str, str] = {}
    morceaux = {
        "predictions.json": {"domaine": donnees["domaine"], "video": donnees["video"],
                             "predictions": donnees["predictions"]},
        "mesures.json": {"domaine": donnees["domaine"], "certificats": donnees["certificats"],
                         "mesures": {c: {k: v for k, v in m.items() if k != "cumul"}
                                     for c, m in donnees["mesures"].items()}},
        "confrontation.json": {"domaine": donnees["domaine"], "calibrage": donnees["calibrage"],
                               "confrontation": donnees["confrontation"]},
        "etat.json": {"domaine": donnees["domaine"], "controles": donnees["controles"],
                      "equations": [{k: v for k, v in e.items() if k != "detail"}
                                    for e in donnees["equations"]]},
    }
    # Octets imposés, jamais `write_text` : en mode texte le système traduirait les
    # fins de ligne, et le même code rendrait du LF sur Linux, du CRLF sur Windows.
    for nom, contenu in morceaux.items():
        texte = json.dumps(contenu, ensure_ascii=False, indent=2, sort_keys=True, default=str)
        octets_json = (texte + "\n").encode("utf-8")
        (dossier / nom).write_bytes(octets_json)
        rendu[nom] = f"{len(octets_json)} octets"
    octets_csv = octets_confrontation_csv(donnees["confrontation"]["cellules"])
    (dossier / "confrontation.csv").write_bytes(octets_csv)
    rendu["confrontation.csv"] = f"{len(octets_csv)} octets"
    return rendu


if __name__ == "__main__":
    import json

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    arguments = [a for a in sys.argv[1:] if not a.startswith("--")]
    ecrit = "--ecrit" in sys.argv
    nb = int(arguments[0]) if arguments else N_COURT
    grand = nb >= 200_000
    donnees = resoudre(nb, N_SIM if grand else 5_000, N_SIM2 if grand else 2_500,
                       REPILIQUES, REPILIQUES2)
    summary = {"domaine": donnees["domaine"],
               "equations": [{k: v for k, v in e.items() if k != "detail"}
                             for e in donnees["equations"]],
               "controles": [{k: v for k, v in c.items() if k != "nom"}
                             for c in donnees["controles"]],
               "verdict_global": donnees["confrontation"]["verdict_global"],
               "exclues": donnees["confrontation"]["exclues"]}
    if ecrit:
        summary["artefacts"] = ecrire_artefacts(donnees)
    print(json.dumps(summary, ensure_ascii=False, indent=2, default=str))
    sys.exit(0 if verifier(donnees) else 1)
