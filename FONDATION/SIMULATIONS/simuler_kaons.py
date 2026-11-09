# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2026 IMAM8MAHDI / Astro-Code Ecosystem
# SPDX-License-Identifier: GPL-3.0-only OR AGPL-3.0-only
"""SIMULATION — le seuil à cinq sigma, joué désintégration après désintégration.

Ce fichier ne prédit rien de neuf : il CONFRONTE les cinq affirmations numériques du dossier
FONDATION en tirant les comptes au hasard (loi de Poisson, bibliothèque standard seule) et en
opposant le tirage à la fermeture exacte.

    py -3 FONDATION/SIMULATIONS/simuler_kaons.py
    py -3 FONDATION/SIMULATIONS/simuler_kaons.py --tirages 200000 --graine 20261109

Validations attendues, toutes sur accord statistique ou encadrement — jamais sur un seuil
ajusté après coup :

    V1  la loi tirée a la moyenne et la variance annoncées ;
    V2  à l'excès requis, franchir 5 σ vaut bien environ une fois sur deux, et l'entier seuil
        encadre la solution continue de `evenements_requis` ;
    V3  sous le seul modèle standard, à l'exposition 2016-2018, le franchissement reste
        POSSIBLE mais rare : exacte et tirage doivent dire la même probabilité ;
    V4  la p-value publiée par NA62 en 2021 est plus CONSERVATRICE que la queue Poisson pure,
        ce que la `limite` de EQ-11 annonce ;
    V5  le gain √N que la loi donne est bien supérieur au gain publié : le différentiel est
        donc un surplus systématique, pas un artefact de formule.

Ce que la simulation ne fait pas : elle ne simule pas le détecteur, l'acceptance, les
systématiques du fond ni la vraisemblance complète de l'analyse. Elle teste la chaîne
arithmétique du dossier, pas l'expérience.
"""

from __future__ import annotations

import argparse
import json
import math
import random
import sys
from pathlib import Path
from typing import Any, Dict, List

RACINE = Path(__file__).resolve().parents[2]
if str(RACINE) not in sys.path:
    sys.path.insert(0, str(RACINE))

from FONDATION import fondation_base as FB                              # noqa: E402


def poisson(lam: float, rng: random.Random) -> int:
    """Tirage Poisson par l'algorithme de Knuth — stdlib seule, loi exacte."""
    if lam <= 0.0:
        return 0
    L, k, p = math.exp(-lam), 0, 1.0
    while True:
        k += 1
        p *= rng.random()
        if p <= L:
            return k - 1


def queue_superieure(lam: float, n_seuil: int, terme_max: int = 500) -> float:
    """P(N ≥ n_seuil) par sommation exacte, récurrence p(k+1) = p(k)·λ/(k+1) : pas de factorielle."""
    k, p = 0, math.exp(-lam)
    while k < n_seuil:
        k += 1
        p *= lam / k
    total = 0.0
    for _ in range(terme_max):
        total += p
        if p < total * 1e-14:
            break
        k += 1
        p *= lam / k
    return total


def n_seuil_pour_z(fond: float, z: float) -> int:
    """Plus petit entier n dont la signification Li–Ma (fond connu) atteint z."""
    n = max(1, int(fond))
    while FB.signification_lima(float(n), fond) < z:
        n += 1
        if n > 10 ** 7:
            raise ValueError("seuil hors portée")
    return n


def stats_tirage(n_tirages: int, lam: float, graine: int) -> Dict[str, float]:
    rng = random.Random(graine)
    comptes = [poisson(lam, rng) for _ in range(n_tirages)]
    moyenne = sum(comptes) / n_tirages
    variance = sum((c - moyenne) ** 2 for c in comptes) / (n_tirages - 1)
    se_moyenne = math.sqrt(lam / n_tirages)
    se_variance = math.sqrt((2.0 * lam ** 2 + 4.0 * lam ** 3 / n_tirages) / n_tirages)
    return {"moyenne": moyenne, "variance": variance, "se_moyenne": se_moyenne,
            "se_variance": se_variance}


def simuler(n_tirages: int, graine: int) -> Dict[str, Any]:
    gel = FB.prediction_gel(FB.DECLARE)["valeurs"]
    prevu = gel["n_signal_2016_2018"]
    c21, c24 = FB.COMPARE["NA62_2021"], FB.COMPARE["NA62_2024"]
    requis24 = FB.evenements_requis(c24["fond"], 5.0)
    justesses: List[Dict[str, Any]] = []

    def valider(nom: str, attendu: str, obtenu: str, ok: bool) -> None:
        justesses.append({"nom": nom, "attendu": attendu, "obtenu": obtenu, "ok": bool(ok)})

    # ── V1 — la loi tirée est bien celle qu'on annonce ────────────────────────
    lam24 = c24["fond"] + requis24
    t1 = stats_tirage(n_tirages, lam24, graine)
    valider("V1 loi tirée", f"moyenne et variance ≈ {lam24:.4f}",
            f"moyenne {t1['moyenne']:.4f} ± {t1['se_moyenne']:.4f} · variance "
            f"{t1['variance']:.4f} ± {t1['se_variance']:.4f}",
            abs(t1["moyenne"] - lam24) < 5.0 * t1["se_moyenne"]
            and abs(t1["variance"] - lam24) < 6.0 * t1["se_variance"])

    # ── V2 — le seuil de cinq sigma, joué au hasard ───────────────────────────
    n24 = n_seuil_pour_z(c24["fond"], 5.0)
    z_n24 = FB.signification_lima(float(n24), c24["fond"])
    z_n24_moins = FB.signification_lima(float(n24 - 1), c24["fond"])
    exacte24 = queue_superieure(lam24, n24)
    rng = random.Random(graine + 1)
    frac24 = sum(1 for _ in range(n_tirages)
                 if FB.signification_lima(float(poisson(lam24, rng)), c24["fond"]) >= 5.0
                 ) / n_tirages
    se24 = math.sqrt(exacte24 * (1.0 - exacte24) / n_tirages)
    valider("V2 seuil à cinq sigma", "n* encadre z=5 · P ≈ une fois sur deux · MC = exacte",
            f"n*={n24} (z={z_n24:.4f}, z(n*−1)={z_n24_moins:.4f}) · exacte {exacte24:.4f} · "
            f"Monte-Carlo {frac24:.4f} ± {5 * se24:.4f} · requis {requis24:.4f}",
            4.0 <= z_n24_moins < 5.0 <= z_n24
            and n24 - 1.0 <= lam24 <= n24 + 1.0
            and abs(frac24 - exacte24) < 5.0 * se24
            and 0.35 <= exacte24 <= 0.65)

    # ── V3 — exposition 2016-2018 sous le seul modèle standard ────────────────
    lam_sm = prevu + c21["fond"]
    n_sm = n_seuil_pour_z(c21["fond"], 5.0)
    exacte_sm = queue_superieure(lam_sm, n_sm)
    rng = random.Random(graine + 2)
    frac_sm = sum(1 for _ in range(n_tirages)
                  if FB.signification_lima(float(poisson(lam_sm, rng)), c21["fond"]) >= 5.0
                  ) / n_tirages
    se_sm = math.sqrt(max(exacte_sm, 1e-9) * (1.0 - exacte_sm) / n_tirages)
    valider("V3 le SM seul ne tranche pas",
            "un 5 σ reste possible sous le SM mais rare, et MC = exacte",
            f"P(5 σ | SM, 2016-18) exacte {exacte_sm:.4f} · Monte-Carlo {frac_sm:.4f} ± "
            f"{5 * se_sm:.4f} · n*={n_sm} sur λ={lam_sm:.4f} · prevu {prevu:.4f}",
            0.005 <= exacte_sm <= 0.20 and abs(frac_sm - exacte_sm) < 5.0 * se_sm
            and exacte_sm < 0.20)

    # ── V4 — la p publiée est-elle plus prudente que la queue Poisson ? ───────
    exacte_null = queue_superieure(c21["fond"], c21["candidates"])
    n4 = max(n_tirages, 200_000)          # une queue à 5·10⁻⁵ demande plus de tirages
    rng = random.Random(graine + 3)
    hits_null = sum(1 for _ in range(n4) if poisson(c21["fond"], rng) >= c21["candidates"])
    frac_null = hits_null / n4
    attendu_hits = exacte_null * n4
    valider("V4 la p publiée est conservatrice",
            "queue Poisson pure ≤ p publiée, de un à deux ordres ; comptage = attente ± 5σ",
            f"queue Poisson {exacte_null:.3e} · {hits_null} tirages sur {n4} "
            f"({frac_null:.3e}) · attendus {attendu_hits:.2f} · publiée "
            f"{c21['p_value']:.1e} · ratio {c21['p_value'] / max(exacte_null, 1e-300):.1f}",
            0.0 < exacte_null <= c21["p_value"]
            and 2.0 <= c21["p_value"] / max(exacte_null, 1e-300) <= 100.0
            and abs(hits_null - attendu_hits) < 5.0 * math.sqrt(attendu_hits) + 3.0)

    # ── V5 — la loi en √N, mesurée contre publiée ────────────────────────────
    s21, s24 = c21["candidates"] - c21["fond"], c24["candidates"] - c24["fond"]
    gain_loi = math.sqrt(s24 / s21)
    r21, r24 = c21["d_BR"][0] / c21["BR"], c24["d_BR"][0] / c24["BR"]
    valider("V5 la loi √N est celle du tirage",
            "gain publié < gain de loi, de moins de 10 %",
            f"loi {gain_loi:.4f} · publié {r21 / r24:.4f} · rapport {(r21 / r24) / gain_loi:.4f}",
            (r21 / r24) < gain_loi and 0.90 <= (r21 / r24) / gain_loi <= 1.0)

    return {"parametres": {"tirages": n_tirages, "graine": graine,
                           "module_confronte": "FONDATION/fondation_base.py",
                           "algorithme": "Poisson (Knuth), fond connu, seuil Li–Ma"},
            "entrees": {"prevu_gele_2016_2018": prevu, "fond_2021": c21["fond"],
                        "fond_2024": c24["fond"], "candidates_2021": c21["candidates"],
                        "candidates_2024": c24["candidates"], "excess_requis_2024": requis24},
            "justesses": justesses,
            "bilan": {"validations_ok": sum(1 for j in justesses if j["ok"]),
                      "validations_total": len(justesses),
                      "verdict": "SIMULATION EN ACCORD AVEC LE DOSSIER"
                                 if all(j["ok"] for j in justesses) else "DÉSACCORD"},
            "limite": "cinq confrontations sur des lois de comptage à fond connu : elles "
                      "testent l'arithmétique du dossier, pas le détecteur ; un désaccord "
                      "à 5 écarts-types du tirage invaliderait la validation, pas la nature"}


def main() -> int:
    ap = argparse.ArgumentParser(description="Joue le seuil de 5 σ désintégration après "
                                             "désintégration et le confronte au dossier.")
    ap.add_argument("--tirages", type=int, default=20_000)
    ap.add_argument("--graine", type=int, default=20_261_109)
    arguments = ap.parse_args()
    if not 1_000 <= arguments.tirages <= 2_000_000:
        print("tirages hors de [1 000 ; 2 000 000]", file=sys.stderr)
        return 2
    sortie = simuler(arguments.tirages, arguments.graine)
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    print(json.dumps(sortie, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if sortie["bilan"]["verdict"].startswith("SIMULATION EN ACCORD") else 1


if __name__ == "__main__":
    sys.exit(main())
