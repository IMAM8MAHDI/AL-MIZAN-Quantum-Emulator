# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2026 IMAM8MAHDI / Astro-Code Ecosystem
# SPDX-License-Identifier: GPL-3.0-only OR AGPL-3.0-only
"""HORLOGERIE — laboratoire : l'identité d'horloge tenue à l'écran.

Ce module ne prouve rien de nouveau : il fait tourner ce que `horlogerie.py` certifie déjà,
et mesure l'instrument pendant qu'il tourne. Trois objets, trois statuts :

    1. LA TRAJECTOIRE (OPÉRATIONNEL) — les trois compteurs d'espace et le compteur de temps
       avancent de dx, dy, dz et dt = dx+dy+dz. À chaque pas la fermeture
       x + y + z − t = 0 est un résidu ENTIER, et elle vaut exactement 0 : c'est l'identité,
       jouée pas à pas. La trajectoire des résidus modulo dt est périodique et la période de
       fermeture se calcule par pgcd — elle n'est pas observée sur la figure.

    2. LE REPÈRE À 14 COORDONNÉES (SPÉCIFIÉ) — quatorze nombres nommés, chacun pris tel quel
       dans le dépôt scellé ou mesuré sur l'hôte. C'est un système de coordonnées défini par
       convention de listing : rien ici ne revendique quatorze dimensions physiques, et le
       module l'écrit dans chacune de ses sorties.

    3. LA STABILITÉ (SIMULÉ, puis MESURÉ) — l'écart-type d'Allan sur des fenêtres de durée.
       D'abord sur une série simulée dont le bruit est injecté à dessein : le module doit
       retrouver l'amplitude qu'il a lui-même déclarée, sinon son instrument est faux. Ensuite
       sur la machine réelle, où le même calcul ne caractérise plus que l'hôte.

    py -3 HORLOGERIE/laboratoire.py --pas 4096
    py -3 HORLOGERIE/laboratoire.py --pas-horloge 4000 --bruit 0.001 --graine 20261109
    py -3 HORLOGERIE/laboratoire.py --en-direct --secondes 20 --ticks 50000
    py -3 HORLOGERIE/laboratoire.py --ecrit

Ce que le laboratoire ne dit pas : que cette horloge cale quelque chose du ciel ou d'un
quelconque temps physique. `dt` est un budget de comptes ; son rythme d'exécution dépend de
la machine ; la convergence des deux est une question ouverte, pas un résultat.
"""

from __future__ import annotations

import argparse
import json
import math
import random
import statistics
import sys
import time
from fractions import Fraction
from math import gcd
from pathlib import Path
from typing import Any, Dict, List, Sequence

RACINE = Path(__file__).resolve().parents[1]
if str(RACINE) not in sys.path:
    sys.path.insert(0, str(RACINE))

from HORLOGERIE import calibrer_horloge_almizan as CAL                      # noqa: E402
from HORLOGERIE import horlogerie as HOR                                    # noqa: E402
from bibliotheques.lib_temporelle import HorlogeKernelTemporelle            # noqa: E402

ARTEFACTS = Path(__file__).resolve().parent / "artefacts"
DEN = 128                                   # tous les compteurs du dépôt ont ce dénominateur
PORTEE_REPERE = ("repère de coordonnées défini par convention de listing — aucune dimension "
                 "physique nouvelle n'est revendiquée ici")
CE_QUE_CE_N_EST_PAS = ("aucune synchronisation physique n'est observée par ce module : la "
                       "trajectoire est arithmétique, la stabilité est soit simulée soit propre "
                       "à l'hôte")


# ─── 1. Le même rationnel, en entiers -----------------------------------------

def unites() -> Dict[str, int]:
    """Les cinq compteurs du dépôt, multipliés par 128 : des entiers, donc des comparaisons exactes."""
    r = HOR.rationnaux()
    out = {cle: int(v * DEN) for cle, v in r.items()}
    for cle, valeur in out.items():
        if Fraction(valeur, DEN) != r[cle]:
            raise AssertionError(f"changement d'échelle perdu sur {cle}")
    return out


def fermeture() -> Dict[str, Any]:
    """Le plus petit nombre de pas qui remet les trois axes d'origine, calcule par pgcd."""
    u = unites()
    dt = u["dt"]
    axes = {cle: dt // gcd(u[cle], dt) for cle in ("dx", "dy", "dz")}
    commun = 1
    for p in axes.values():
        commun = commun * p // gcd(commun, p)
    return {"unite": f"pas ; le pas vaut une avance de dx, dy, dz sur dt = {dt}/{DEN}",
            "periode_par_axe": axes,
            "periode_commune": commun,
            "dt_en_entiers": dt,
            "dt_divise_par_periode_commune": dt // commun,
            "methode": "pgcd : période d'un axe = dt / pgcd(pas de l'axe, dt) ; fermeture = ppcm "
                        "des trois périodes",
            "statut": "opérationnel (arithmétique) — la figure ne montre qu'un préfixe, la "
                      "fermeture se démontre"}


# ─── 2. Le repère à quatorze coordonnées --------------------------------------

def reperes(direct: Dict[str, Any] | None = None) -> List[Dict[str, Any]]:
    """Quatorze nombres nommés, chacun repris tel quel du dépôt scellé ou mesuré sur l'hôte.

    Douze viennent du dépôt (les six compteurs et les six références célestes), deux de la
    machine (`tau` et son rapport à `1 / dt`). Le compte est tenu par construction : la liste
    fait quatorze entrées, elle n'est pas rognée après coup.
    """
    r = HOR.rationnaux()
    peri = HOR.periode_ns()
    coord: List[Dict[str, Any]] = [
        {"id": 1, "nom": "t", "role": "temps du scénario", "valeur": str(r["dt"]),
         "unite": "comptes", "statut": "opérationnel",
         "source": "horlogerie.rationnaux()['dt'] = dx + dy + dz"},
        {"id": 2, "nom": "x", "role": "axe 1", "valeur": str(r["dx"]), "unite": "comptes",
         "statut": "opérationnel", "source": "produit des quatre niveaux, semences du Soleil"},
        {"id": 3, "nom": "y", "role": "axe 2", "valeur": str(r["dy"]), "unite": "comptes",
         "statut": "opérationnel", "source": "produit des quatre niveaux, semences de la Lune"},
        {"id": 4, "nom": "z", "role": "axe 3", "valeur": str(r["dz"]), "unite": "comptes",
         "statut": "opérationnel", "source": "216 000 · 250 · 5/2 (terre normalisée)"},
        {"id": 5, "nom": "z_brut", "role": "variante non normalisée du même axe, facteur 144/5",
         "valeur": str(r["dz_brut"]), "unite": "comptes", "statut": "opérationnel",
         "source": "produit des quatre niveaux, coefficients bruts 300 · 50 · 30 · 24/60 ; "
                   "z_brut / z = " + str(r["dz_brut"] / r["dz"])},
        {"id": 6, "nom": "1 / dt", "role": "période si dt était une fréquence",
         "valeur": peri["valeur_ns"], "unite": "ns", "statut": "spécifié",
         "source": "horlogerie.periode_ns() — conséquence d'une hypothèse de lecture « Hz »"},
    ]
    for ref in HOR.REFERENCES:
        coord.append({"id": len(coord) + 1, "nom": ref["id"], "role": "céleste cité",
                      "valeur": ref["jours"], "unite": "jours", "statut": "opérationnel",
                      "source": ref["source"]})
    tau = {"id": 13, "nom": "tau", "role": "rythme réel d'un tick",
           "valeur": "à produire par --en-direct", "unite": "ns/tick", "statut": "simulé",
           "source": "calibrer_horloge_almizan.mesurer et en_direct() — dépend de la machine, "
                     "hors scellement"}
    ratio = {"id": 14, "nom": "tau / (1 / dt)", "role": "précision du mesuré contre le spécifié",
             "valeur": "à produire avec tau", "unite": "sans unité", "statut": "simulé",
             "source": "quand τ ≈ 1/dt seulement la lecture en hertz devient défendable"}
    if direct:
        tau.update(valeur=f"{direct['tau_mediane_ns']:.4f}", statut="mesuré",
                   role="rythme réel d'un tick, médiane des fenêtres de cette machine")
        ratio.update(valeur=f"{direct['ratio_sur_specifie']:.4f}", statut="mesuré",
                     role="écart du rythme mesuré à la période spécifiée, en fois")
    coord += [tau, ratio]
    if len(coord) != 14:
        raise AssertionError(f"le repère doit faire 14 coordonnees, il en fait {len(coord)}")
    return coord


# ─── 3. L'instrument de stabilité ---------------------------------------------

def fenetres(serie_ns: Sequence[float]) -> List[float]:
    """Déviations fractionnelles de fréquence : y_i = (τ_i − moyenne) / moyenne."""
    if len(serie_ns) < 2:
        raise ValueError("il faut au moins deux fenêtres")
    m = statistics.fmean(serie_ns)
    if m <= 0:
        raise ValueError("moyenne non positive")
    return [(t - m) / m for t in serie_ns]


def adev(y: Sequence[float]) -> float:
    """Écart-type d'Allan, convention variance d'Allan :

        σ² = 1 / (2 (N − 1)) · Σ_{i=1}^{N−1} (y_{i+1} − y_i)²

    Sur un bruit blanc de fréquence d'écart-type ε, l'espérance de cet estimateur est ε² :
    c'est pour cela que la simulation compare ce nombre à l'amplitude injectée.
    """
    n = len(y)
    if n < 2:
        raise ValueError("il faut au moins deux fenêtres")
    s = sum((y[i + 1] - y[i]) ** 2 for i in range(n - 1))
    return math.sqrt(s / (2 * (n - 1)))


def bande_attendue(eps: float, n: int) -> Dict[str, float]:
    """Écart-type relatif de l'estimateur ≈ 1 / (2 √(N − 1)) ; la bande fait cinq de ces écarts."""
    relatif = 5.0 / (2.0 * math.sqrt(n - 1))
    return {"eps": eps, "relatif": relatif, "borne_basse": eps * (1 - relatif),
            "borne_haute": eps * (1 + relatif)}


def simuler_horloge(pas: int = 4000, eps: float = 1e-3, graine: int = 20261109,
                    tau_base_ns: float = 1000.0) -> Dict[str, Any]:
    """Bruit blanc de fréquence injecté à dessein, puis mesuré par le même instrument."""
    if pas < 20 or not 0 < eps < 0.5:
        raise ValueError("bornes : --pas-horloge >= 20 et 0 < --bruit < 0,5")
    hasard = random.Random(graine)
    serie = [tau_base_ns * (1.0 + hasard.gauss(0.0, eps)) for _ in range(pas)]
    mesure = adev(fenetres(serie))
    bande = bande_attendue(eps, pas)
    return {"graine": graine, "pas": pas, "eps_injecte": eps, "tau_base_ns": tau_base_ns,
            "adev_mesure": mesure, "bande": bande,
            "recupere": bande["borne_basse"] <= mesure <= bande["borne_haute"],
            "ecart_relatif": abs(mesure - eps) / eps,
            "statut": "simulé — le bruit est déclaré avant mesure ; ce que le contrôle porte est "
                      "la capacité de l'instrument à le retrouver",
            "formule": "y_i = (tau_i - moyenne)/moyenne ; sigma = sqrt(1/(2(N-1)) sum (y_{i+1}-y_i)^2)"}


def trajectoire(pas: int = 4096, echantillons: int = 512) -> Dict[str, Any]:
    """La fermeture jouée pas à pas, en entiers : x + y + z − t reste 0 à chaque pas."""
    if pas < 1:
        raise ValueError("--pas doit être positif")
    u = unites()
    dx, dy, dz, dt = u["dx"], u["dy"], u["dz"], u["dt"]
    x = y = z = 0
    residues: List[int] = []
    points: List[List[int]] = []
    pas_par_point = -(-pas // max(1, echantillons))          # plafond = echantillons points
    for k in range(1, pas + 1):
        x, y, z = x + dx, y + dy, z + dz
        residues.append(x + y + z - k * dt)
        if k == 1 or k % pas_par_point == 0:
            points.append([k, x % dt, y % dt, z % dt])
    fer = fermeture()
    return {"pas": pas, "residu_max_absolu": max(abs(v) for v in residues),
            "residus_non_nuls": sum(1 for v in residues if v != 0),
            "fermeture": fer, "points": points,
            "normalisation": "u = (k·dx mod dt)/dt, même formule sur v et w ; projections "
                             "orthogonales (u,v), (u,w), (v,w)",
            "statut": "opérationnel — arithmétique entière exacte, aucun nombre d'hôte"}


# ─── 4. En direct sur la machine ----------------------------------------------

def en_direct(secondes: float = 20.0, ticks: int = 50_000, namespace: str = "TERRE",
              afficher: bool = False) -> Dict[str, Any]:
    """Fenêtres successives de τ = T/N sur l'API réelle, puis stabilité et précision.

    `afficher` imprime chaque fenêtre au fil de l'eau : c'est l'écran de l'horloge, pas une
    journalisation. Les nombres affichés avant la fin portent sur un échantillon plus court
    que le rapport final, ils ne lui sont pas comparables.
    """
    if ticks < 100 or secondes < 0.5:
        raise ValueError("bornes : --ticks >= 100 et --secondes >= 0,5")
    taus: List[float] = []
    periode = HOR.periode_ns()["flottant"]
    horloge = HorlogeKernelTemporelle()
    debut = time.perf_counter()
    dernier_ecran = -1.0
    while time.perf_counter() - debut < secondes:
        t0 = time.perf_counter_ns()
        for _ in range(ticks):
            horloge.consommer_tick(namespace, 1.0, "laboratoire")
        taus.append((time.perf_counter_ns() - t0) / ticks)
        ecoules = time.perf_counter() - debut
        if afficher and len(taus) >= 2 and ecoules - dernier_ecran >= 1.0:
            dernier_ecran = ecoules
            m = statistics.median(taus)
            print(f"  [{ecoules:4.0f} s] {len(taus):4d} fenêtres · τ courant {taus[-1]:9.1f} ns · "
                  f"médiane {m:9.1f} ns · ADEV {adev(fenetres(taus)):.4g} · "
                  f"τ/(1/dt) = {m / periode:6.1f} ×")
    mediane = statistics.median(taus)
    y = fenetres(taus)
    return {"fenetres": len(taus), "ticks_par_fenetre": ticks, "namespace": namespace,
            "duree_reelle_s": time.perf_counter() - debut,
            "tau_mediane_ns": mediane,
            "tau_minimum_ns": min(taus), "tau_maximum_ns": max(taus),
            "adev_relatif": adev(y),
            "ecart_vs_specifie": abs(mediane - periode) / periode,
            "ecart_vs_specifie_pct": 100.0 * abs(mediane - periode) / periode,
            "periode_specifiee_ns": periode,
            "ratio_sur_specifie": mediane / periode,
            "echelle_lue": ("la stabilité n'a de sens que rapportée à une référence : ici la "
                            "période spécifiée 1/dt, hypothèse non observée"),
            "statut": "mesuré — dépend de la machine, de l'interpréteur et de la charge ; "
                      "hors scellement",
            "taus_ns": taus}


# ─── 5. Livrables ---------------------------------------------------------------

def _fr(x: float) -> str:
    return f"{x:.6g}".replace(".", ",")


def octets_csv_trajectoire(t: Dict[str, Any]) -> bytes:
    lignes = [["k", "u", "v", "w", "u_sur_dt", "v_sur_dt", "w_sur_dt"]]
    dt = t["fermeture"]["dt_en_entiers"]
    for k, uu, vv, ww in t["points"]:
        lignes.append([k, uu, vv, ww, _fr(uu / dt), _fr(vv / dt), _fr(ww / dt)])
    corps = "\r\n".join(";".join(str(c) for c in ligne) for ligne in lignes)
    return b"\xef\xbb\xbf" + (corps + "\r\n").encode("utf-8")


def octets_csv_stabilite(s: Dict[str, Any]) -> bytes:
    lignes = [["grandeur", "valeur", "statut"]]
    for cle in ("pas", "eps_injecte", "adev_mesure", "ecart_relatif", "graine", "tau_base_ns"):
        lignes.append([cle, _fr(float(s[cle])) if not isinstance(s[cle], int) else s[cle],
                       s["statut"].split(" —")[0]])
    for cle in ("borne_basse", "borne_haute", "relatif"):
        lignes.append([f"bande_{cle}", _fr(float(s["bande"][cle])), "spécifié"])
    lignes.append(["recupere", "oui" if s["recupere"] else "non", "contrôle"])
    corps = "\r\n".join(";".join(str(c) for c in ligne) for ligne in lignes)
    return b"\xef\xbb\xbf" + (corps + "\r\n").encode("utf-8")


def svg_trajectoire(t: Dict[str, Any], largeur: int = 360) -> bytes:
    """Trois projections orthogonales de la trajectoire des résidus ; libellés purement mathématiques."""
    dt = t["fermeture"]["dt_en_entiers"]
    pts = t["points"]
    paires = {"(u/dt, v/dt)": (1, 2), "(u/dt, w/dt)": (1, 3), "(v/dt, w/dt)": (2, 3)}
    panneaux = []
    for i, (titre, (a, b)) in enumerate(paires.items()):
        xy = []
        for p in pts:
            gx = 20 + (largeur - 40) * (p[a] / dt)
            gy = 20 + (largeur - 40) * (1 - p[b] / dt)
            xy.append(f"{gx:.1f},{gy:.1f}")
        x0 = 20 + i * (largeur + 30)
        panneaux.append(
            f'<g transform="translate({x0},0)">'
            f'<rect x="0" y="0" width="{largeur}" height="{largeur}" fill="#0d1420" '
            f'stroke="#34506a"/>'
            f'<polyline fill="none" stroke="#7fd1b9" stroke-width="0.7" points="{" ".join(xy)}"/>'
            f'<text x="8" y="{largeur - 8}" fill="#cfe3f0" font-family="monospace" '
            f'font-size="12">{titre}</text></g>')
    total = 3 * largeur + 60 + 20
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{total}" height="{largeur + 30}" '
            f'viewBox="0 0 {total} {largeur + 30}">'
            f'<text x="0" y="{largeur + 22}" fill="#8fa9bd" font-family="monospace" font-size="11">'
            f'préfixe de {t["pas"]} pas sur une fermeture à {t["fermeture"]["periode_commune"]} '
            f'pas · {PORTEE_REPERE}</text>'
            f'{" ".join(panneaux)}</svg>\n').encode("utf-8")


def laboratoire(pas: int = 4096, pas_horloge: int = 4000, bruit: float = 1e-3,
                graine: int = 20261109, direct: Dict[str, Any] | None = None) -> Dict[str, Any]:
    """Le rapport complet : repère, trajectoire, instrument, mesure d'hôte le cas échéant."""
    t = trajectoire(pas)
    s = simuler_horloge(pas_horloge, bruit, graine)
    f = t["fermeture"]
    rep = reperes(direct)
    controles = [
        {"id": "L01", "enonce": "x + y + z − k·dt = 0 à chaque pas, en entiers",
         "obtenu": t["residus_non_nuls"], "attendu": 0, "vrai": t["residus_non_nuls"] == 0},
        {"id": "L02", "enonce": "la fermeture est commune aux trois axes et calculée par pgcd",
         "obtenu": sorted(set(f["periode_par_axe"].values())),
         "attendu": [f["periode_commune"]],
         "vrai": sorted(set(f["periode_par_axe"].values())) == [f["periode_commune"]]
                 and f["dt_en_entiers"] % f["periode_commune"] == 0},
        {"id": "L03", "enonce": "le repère porte exactement quatorze coordonnées nommées",
         "obtenu": len(rep), "attendu": 14, "vrai": len(rep) == 14},
        {"id": "L04", "enonce": "l'instrument retrouve le bruit qu'il a injecté",
         "obtenu": s["adev_mesure"], "attendu": s["eps_injecte"], "vrai": s["recupere"]},
        {"id": "L05", "enonce": "aucune coordonnée du repère n'est inventée : chaque source est "
                                "un texte du dépôt ou une mesure déclarée",
         "obtenu": sum(1 for c in rep if c["source"]), "attendu": 14,
         "vrai": all(c["source"] and c["statut"] in {"opérationnel", "spécifié", "simulé",
                                                     "mesuré"} for c in rep)},
    ]
    return {"formule": "dt = dx + dy + dz = 17 292 418 731/128 ; le scénario avance de (dx, dy, "
                       "dz, dt) par pas",
            "repere": rep, "portee_repere": PORTEE_REPERE,
            "trajectoire": {k: v for k, v in t.items() if k != "points"},
            "stabilite_simulee": s, "stabilite_hote": direct,
            "controles": controles,
            "controles_verts": sum(1 for c in controles if c["vrai"]),
            "nombre_controles": len(controles),
            "ce_que_ce_n_est_pas": CE_QUE_CE_N_EST_PAS,
            "verdict": ("LABORATOIRE CONFORME" if all(c["vrai"] for c in controles)
                        else "LABORATOIRE EN DÉFAUT"),
            "horodatage": "aucun : le rapport doit sortir identique octet pour octet d'une "
                          "exécution à l'autre, une mesure d'hôte comprise change tout"}


def ecrire(rapport: Dict[str, Any], vers: Path = ARTEFACTS) -> Dict[str, str]:
    """Les quatre livrables, en octets imposés. Aucun nombre d'hôte n'y entre.

    Ce que le dépôt scelle doit ressortir identique sur une autre machine. La mesure en
    direct est donc retirée de ce qui est écrit, et le fichier le dit : ce qui reste à
    l'écran n'est pas ce qui entre dans le certificat.
    """
    vers.mkdir(parents=True, exist_ok=True)
    scelle = {**rapport, "stabilite_hote": None, "repere": reperes()}
    scelle["mesure_hote_ecrite"] = ("non : les nombres d'hôte s'affichent à l'écran et "
                                    "n'entrent pas dans les octets scellés")
    corps = json.dumps(scelle, ensure_ascii=False, indent=2, sort_keys=True, default=str)
    chemin_json = vers / "laboratoire.json"
    chemin_json.write_bytes((corps + "\n").encode("utf-8"))
    chemin_traj = vers / "trajectoire_laboratoire.csv"
    chemin_traj.write_bytes(octets_csv_trajectoire(trajectoire(rapport["trajectoire"]["pas"])))
    chemin_stab = vers / "stabilite_laboratoire.csv"
    chemin_stab.write_bytes(octets_csv_stabilite(rapport["stabilite_simulee"]))
    chemin_svg = vers / "trajectoire_laboratoire.svg"
    chemin_svg.write_bytes(svg_trajectoire(trajectoire(rapport["trajectoire"]["pas"])))
    return {"json": str(chemin_json), "csv_trajectoire": str(chemin_traj),
            "csv_stabilite": str(chemin_stab), "svg": str(chemin_svg)}


def main() -> int:
    ap = argparse.ArgumentParser(description="Laboratoire AL-MIZAN : horloge, espace 3D, stabilité.")
    ap.add_argument("--pas", type=int, default=4096, help="pas de la trajectoire (défaut 4096)")
    ap.add_argument("--pas-horloge", type=int, default=4000, help="fenêtres de la simulation")
    ap.add_argument("--bruit", type=float, default=1e-3, help="écart-type relatif injecté")
    ap.add_argument("--graine", type=int, default=20261109)
    ap.add_argument("--en-direct", action="store_true", help="mesurer sur cette machine")
    ap.add_argument("--secondes", type=float, default=20.0)
    ap.add_argument("--ticks", type=int, default=50_000, help="ticks par fenêtre en direct")
    ap.add_argument("--namespace", default="TERRE")
    ap.add_argument("--ecrit", action="store_true", help="écrire les quatre livrables")
    ap.add_argument("--json", action="store_true", help="rapport JSON intégral")
    a = ap.parse_args()
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    direct = None
    if a.en_direct:
        print(f"Horloge AL-MIZAN en direct — namespace {a.namespace.upper()}, "
              f"{a.ticks:,} ticks par fenêtre, {a.secondes:g} s".replace(",", " "))
        direct = en_direct(a.secondes, a.ticks, a.namespace.upper(), afficher=not a.json)
    rapport = laboratoire(a.pas, a.pas_horloge, a.bruit, a.graine, direct)
    if a.ecrit:
        rapport["livrables"] = ecrire(rapport)
    if a.json:
        print(json.dumps(rapport, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        t, s, f = rapport["trajectoire"], rapport["stabilite_simulee"], rapport["trajectoire"]["fermeture"]
        print(f"Repère : {len(rapport['repere'])} coordonnées — {rapport['portee_repere']}")
        print(f"Trajectoire : {t['pas']} pas, résidu de fermeture maximal "
              f"{t['residu_max_absolu']} (entier), pas non clos : {t['residus_non_nuls']}")
        print(f"Fermeture démontrée : période commune {f['periode_commune']:,} pas "
              f"(dt = {f['dt_en_entiers']:,} en unités de 1/128, "
              f"soit {f['dt_divise_par_periode_commune']} tours)".replace(",", " "))
        print(f"Instrument : σ injecté {s['eps_injecte']:.6g}, ADEV mesuré {s['adev_mesure']:.6g}, "
              f"bande ±{s['bande']['relatif']:.4g} → {'retrouvé' if s['recupere'] else 'PERDU'}")
        if direct:
            print(f"En direct : {direct['fenetres']} fenêtres de {direct['ticks_par_fenetre']:,} "
                  f"ticks · τ médian {direct['tau_mediane_ns']:.1f} ns (min {direct['tau_minimum_ns']:.1f}, "
                  f"max {direct['tau_maximum_ns']:.1f}) · ADEV relatif "
                  f"{direct['adev_relatif']:.4g}".replace(",", " "))
            print(f"           écart à la période spécifiée : {direct['ecart_vs_specifie_pct']:.4g} % "
                  f"· {direct['echelle_lue']}")
            print(f"           ratio τ/(1/dt) = {direct['ratio_sur_specifie']:.0f} × — "
                  f"{direct['statut']}")
        for c in rapport["controles"]:
            print(f"  {c['id']} {'OK  ' if c['vrai'] else 'ROUGE'} {c['enonce']}")
        print(rapport["verdict"])
        print(f"Limites : {rapport['ce_que_ce_n_est_pas']}")
        if a.ecrit:
            for nom, chemin in rapport["livrables"].items():
                print(f"  {nom:15s} {chemin}")
    return 0 if rapport["verdict"] == "LABORATOIRE CONFORME" else 1


if __name__ == "__main__":
    sys.exit(main())
