# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2026 IMAM8MAHDI / Astro-Code Ecosystem
# SPDX-License-Identifier: GPL-3.0-only OR AGPL-3.0-only
"""HORLOGERIE — mesure du rythme réel d'un tick : τ = T/N.

L'identité d'horloge du dépôt, `dt = dx + dy + dz = 17 292 418 731 / 128`, est un rationnel
exact : elle se certifie sans machine (voir `verifier_certificats.py`). Certains textes du
projet l'ont ensuite lue « Hz », ce qui engage beaucoup plus : une fréquence de
135 097 021,3359375 s⁻¹ impose une période de 1/dt = 7,402 087 7… ns, donc un tick toutes les
7,4 nanosecondes, sur n'importe quelle machine.

Ce script mesure autre chose, et c'est ce qui tranche : le temps wall-clock moyen d'un appel à
`HorlogeKernelTemporelle.consommer_tick()`, la seule fonction du dépôt qui consomme un tick.

    py -3 HORLOGERIE/calibrer_horloge_almizan.py --ticks 10000 --series 7
    py -3 HORLOGERIE/calibrer_horloge_almizan.py --ticks 10000 --series 7 --json
    py -3 HORLOGERIE/calibrer_horloge_almizan.py --sortie calibrage_almizan.csv

Statistique : la médiane et l'écart absolu médian, pas la moyenne. Un seul réveil de
l'ordonnanceur déplace une moyenne de plusieurs centaines de nanosecondes ; la série
`--series 7` est là pour que le premier échantillon froid ne tienne pas lieu de mesure.

Ce que la mesure dit : ce que CETTE machine, sous CETTE interprétation Python, fait d'un tick.
Ce qu'elle ne dit pas : ce que `dt` « vaut » en physique. Elle ne cale aucune constante du
dépôt, ne modifie aucun fichier du dépôt et n'entre dans aucun scellement : son résultat
dépend de l'hôte, et un nombre dépendant de l'hôte n'a rien à faire dans un certificat.
"""

from __future__ import annotations

import argparse
import json
import platform
import statistics
import sys
import time
from pathlib import Path
from typing import Any, Dict, List

RACINE = Path(__file__).resolve().parents[1]
if str(RACINE) not in sys.path:
    sys.path.insert(0, str(RACINE))

from bibliotheques.lib_temporelle import CLOCK_DT_KERNEL, HorlogeKernelTemporelle  # noqa: E402


def mesurer(ticks: int = 10_000, series: int = 7, namespace: str = "TERRE",
            cout: float = 1.0) -> Dict[str, Any]:
    """τ = T/N, série par série, en nanosecondes par tick, sur l'API réelle du dépôt."""
    horloge = HorlogeKernelTemporelle()
    echantillons: List[Dict[str, Any]] = []
    for numero in range(1, series + 1):
        debut = time.perf_counter_ns()
        for _ in range(ticks):
            horloge.consommer_tick(namespace, cout, "calibrage")
        duree_ns = time.perf_counter_ns() - debut
        echantillons.append({"serie": numero, "ticks": ticks, "duree_ns": duree_ns,
                            "tau_ns": duree_ns / ticks})
    taus = [e["tau_ns"] for e in echantillons]
    mediane = statistics.median(taus)
    return {
        "formule": "tau = T / N (T = perf_counter_ns sur N appels à consommer_tick)",
        "namespace": namespace,
        "cout_par_tick": cout,
        "ticks_par_serie": ticks,
        "series": series,
        "echantillons": echantillons,
        "mediane_ns": mediane,
        "ecart_absolu_median_ns": statistics.median([abs(t - mediane) for t in taus]),
        "minimum_ns": min(taus),
        "maximum_ns": max(taus),
        "budget_kernel_dt": CLOCK_DT_KERNEL,
        "tour_complet_du_budget_s": CLOCK_DT_KERNEL * mediane * 1e-9,
        "hote": {"systeme": platform.platform(), "python": platform.python_version(),
                 "processeur": platform.processor() or "non communiqué"},
        "portee": "mesuré · dépend du matériel et de l'interpréteur · non scellé",
    }


def octets_csv(mesure: Dict[str, Any]) -> bytes:
    """Le même format Excel français que partout dans le dépôt : BOM, « ; », CRLF, virgule."""
    lignes = [["serie", "ticks", "duree_ns", "tau_ns"]]
    for e in mesure["echantillons"]:
        lignes.append([e["serie"], e["ticks"], e["duree_ns"], f"{e['tau_ns']:.6g}"])
    lignes.append(["médiane", mesure["ticks_par_serie"] * mesure["series"], "",
                   f"{mesure['mediane_ns']:.6g}"])
    corps = "\r\n".join(";".join(str(x).replace(".", ",") for x in ligne) for ligne in lignes)
    return b"\xef\xbb\xbf" + (corps + "\r\n").encode("utf-8")


def main() -> int:
    ap = argparse.ArgumentParser(description="Mesure tau = T/N sur consommer_tick().")
    ap.add_argument("--ticks", type=int, default=10_000, help="N par série (défaut 10 000)")
    ap.add_argument("--series", type=int, default=7, help="nombre de séries (défaut 7)")
    ap.add_argument("--namespace", default="TERRE",
                    help="canal consommé : TERRE, SOLEIL ou LUNE (défaut TERRE)")
    ap.add_argument("--sortie", help="écrire le CSV à ce chemin (optionnel)")
    ap.add_argument("--json", action="store_true", help="rapport JSON intégral")
    arguments = ap.parse_args()
    if arguments.ticks < 100 or arguments.series < 3:
        print("MESURE REFUSÉE : --ticks >= 100 et --series >= 3 pour qu'une médiane existe.",
              file=sys.stderr)
        return 2
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    mesure = mesurer(arguments.ticks, arguments.series, arguments.namespace.upper())
    if arguments.sortie:
        chemin = Path(arguments.sortie)
        chemin.write_bytes(octets_csv(mesure))
        mesure["csv"] = {"chemin": str(chemin), "octets": chemin.stat().st_size}
    if arguments.json:
        print(json.dumps(mesure, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print(f"τ = T/N sur {arguments.namespace.upper()} — {arguments.series} séries "
              f"de {arguments.ticks} ticks")
        for e in mesure["echantillons"]:
            print(f"  série {e['serie']} : {e['tau_ns']:10.1f} ns/tick")
        print(f"  médiane  : {mesure['mediane_ns']:.1f} ns/tick "
              f"(écart absolu médian {mesure['ecart_absolu_median_ns']:.1f} ns, "
              f"min {mesure['minimum_ns']:.1f}, max {mesure['maximum_ns']:.1f})")
        print(f"  un tour complet du budget dt = {CLOCK_DT_KERNEL:,.4f} ticks durerait "
              f"{mesure['tour_complet_du_budget_s'] / 3600:.2f} h sur cette machine".replace(",", " "))
        print(f"  portée   : {mesure['portee']}")
        if arguments.sortie:
            print(f"  csv      : {mesure['csv']['chemin']} ({mesure['csv']['octets']} octets)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
