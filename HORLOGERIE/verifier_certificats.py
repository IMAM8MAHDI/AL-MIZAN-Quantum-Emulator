# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2026 IMAM8MAHDI / Astro-Code Ecosystem
# SPDX-License-Identifier: GPL-3.0-only OR AGPL-3.0-only
"""HORLOGERIE — vérificateur autonome du certificat d'horloge. N'importe RIEN du dépôt.

Un certificat ne vaut que si on peut le lire sans faire confiance à celui qui l'a produit.
Ce fichier est écrit dans cet esprit : il ne connaît ni `bibliotheques/`, ni `horloge_noyau/`,
ni `FONDATION/`. Sa propre implémentation du produit des quatre niveaux est réécrite ici, à la
main, à partir de la formule stockée dans le fichier — donc si le module qui produit le
certificat et le fichier se contredisent, c'est le fichier qui tombe.

    py -3 HORLOGERIE/verifier_certificats.py                      # le certificat du dépôt
    py -3 HORLOGERIE/verifier_certificats.py CHEMIN.json --json    # un certificat donné
    py -3 HORLOGERIE/verifier_certificats.py --importes            # preuve de l'isolement

Contrôles, dans l'ordre : structure du fichier, empreintes des six sous-certificats, racine
de Merkle, derivation entière de dx/dy/dz/dz_brut, identité dt = dx + dy + dz, minimalité du
dénominateur, période en décimale exacte, écarts astronomiques et verdicts recalculés depuis
les SEULS seuils stockés dans le fichier, sensibilité déclarée, statut de l'unité retenue.

Code de sortie : 0 si tout passe ; 1 si une ligne échoue ou si le fichier est illisible ;
2 en cas d'usage invalide.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import math
import sys
from decimal import Decimal, getcontext
from fractions import Fraction
from pathlib import Path
from typing import Any, Dict, List

ICI = Path(__file__).resolve().parent
CERTIFICAT_PAR_DEFAUT = ICI / "artefacts" / "certificats.json"
CLES_SOUS_CERTIFICAT = ("derivation", "rationnels", "identites", "periode", "astronomie",
                        "unites")


def canonique(objet: Any) -> bytes:
    return json.dumps(objet, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":")).encode("utf-8")


def F(x: Any) -> Fraction:
    return x if isinstance(x, Fraction) else Fraction(str(x))


def D(x: str) -> Fraction:
    return Fraction(str(x).replace(",", "."))


def produit_quatre_niveaux(annee_h: Fraction, mois_h: Fraction, semaine_h: Fraction,
                           coefficients: List[str]) -> Fraction:
    """La formule, réécrite ici sans regarder le module qui produit le certificat."""
    c1, c2, c3, c4 = (F(c) for c in coefficients)
    return (c1 * annee_h / 12) * (c2 * mois_h / semaine_h) * (c3 * semaine_h / 24) * c4


def verdict(ecart_s: Fraction, conforme: Fraction, signale: Fraction) -> str:
    a = abs(ecart_s)
    if a <= conforme:
        return "CONFORME"
    if a <= signale:
        return "ÉCART SIGNALÉ"
    return "HORS TOLÉRANCE"


def racine_de(cert: Dict[str, Any]) -> str:
    empreintes = {c: hashlib.sha256(canonique(cert[c])).hexdigest() for c in CLES_SOUS_CERTIFICAT}
    return hashlib.sha256(canonique(empreintes)).hexdigest()


def verifier(cert: Dict[str, Any]) -> List[Dict[str, Any]]:
    rendu: List[Dict[str, Any]] = []

    def ajouter(id_: str, enonce: str, attendu: str, obtenu: str, ok: bool) -> None:
        rendu.append({"id": id_, "enonce": enonce, "attendu": attendu, "obtenu": obtenu,
                      "ok": bool(ok)})

    c = cert
    manquantes = [k for k in CLES_SOUS_CERTIFICAT + ("limites", "empreintes_souche",
                                                     "racine_merkle_sha256") if k not in c]
    ajouter("V01", "le fichier porte les six sous-certificats et leurs scellements",
            "aucune clé manquante", f"{manquantes or 'aucune'}", not manquantes)
    if manquantes:
        return rendu

    empreintes = {k: hashlib.sha256(canonique(c[k])).hexdigest()
                  for k in CLES_SOUS_CERTIFICAT}
    divergentes = sorted(k for k in CLES_SOUS_CERTIFICAT
                         if empreintes[k] != c["empreintes_souche"].get(k))
    ajouter("V02", "l'empreinte SHA-256 de chaque sous-certificat est la sienne",
            "six empreintes concordantes",
            f"{len(CLES_SOUS_CERTIFICAT) - len(divergentes)}/6 · divergentes "
            f"{divergentes or 'aucune'}", not divergentes)
    ajouter("V03", "la racine de Merkle des six empreintes est celle du fichier",
            c["racine_merkle_sha256"][:16] + "…", racine_de(cert)[:16] + "…",
            racine_de(cert) == c["racine_merkle_sha256"])

    d = c["derivation"]
    s = {astre: {nom: F(v) for nom, v in clefs.items()} for astre, clefs in d["semences"].items()}
    recalcul = {
        "dx": produit_quatre_niveaux(s["soleil"]["annee_h"], s["soleil"]["mois_h"],
                                     s["soleil"]["semaine_h"], d["niveaux"]["celeste"]),
        "dy": produit_quatre_niveaux(s["lune"]["annee_h"], s["lune"]["mois_h"],
                                     s["lune"]["semaine_h"], d["niveaux"]["celeste"]),
        "dz": F(d["niveaux"]["terre_normalise"][0]) * F(d["niveaux"]["terre_normalise"][1])
              * F(d["niveaux"]["terre_normalise"][2]),
        "dz_brut": produit_quatre_niveaux(s["terre"]["annee_h"], s["terre"]["mois_h"],
                                          s["terre"]["semaine_h"], d["niveaux"]["terre_brut"]),
    }
    recalcul["dt"] = recalcul["dx"] + recalcul["dy"] + recalcul["dz"]
    declare = {k: F(f"{v['numerateur']}/{v['denominateur']}") for k, v in c["rationnels"].items()}
    derives = sorted(k for k in recalcul
                     if k not in declare or recalcul[k] != declare[k])
    ajouter("V04", "les cinq nombres dérivent des seules semences, en entiers",
            "dx dy dz dz_brut dt concordants", f"dérivés {derives or 'aucun'}", not derives)
    floats = sorted(k for k, v in c["rationnels"].items()
                    if v["flottant"] != repr(float(declare[k])))
    reduites = sorted(k for k, v in c["rationnels"].items()
                      if math.gcd(v["numerateur"], v["denominateur"]) != 1
                      or v["reduit"] is not True)
    ajouter("V05", "chaque écriture flottante est exactement le rationnel, et chaque fraction "
                   "est réduite",
            "aucun écart", f"flottants {floats or 'aucun'} · non réduites {reduites or 'aucune'}",
            not floats and not reduites)

    ids = {i["id"]: i for i in c["identites"]}
    dt = declare["dt"]
    ajouter("V06", "dt = dx + dy + dz (identité d'horloge)",
            "vraie", f"{ids['somme']['second_membre']} · vraie {ids['somme']['vraie']}",
            dt == recalcul["dt"] and ids["somme"]["vraie"] is True
            and ids["somme"]["second_membre"] == f"{dt.numerator}/{dt.denominator}")
    brut, norm = declare["dz_brut"], declare["dz"]
    ajouter("V07", "dz_brut / dz = 144/5 (la normalisation annoncée)",
            "144/5", f"{(brut / norm).numerator}/{(brut / norm).denominator}",
            brut / norm == F("144/5"))
    den = ids["denominateur"]
    ajouter("V08", "den(dt) = 2^7 et num(dt) impair : le dénominateur est minimal",
            "128 · impair", f"{dt.denominator} · {dt.numerator % 2 == 1}",
            dt.denominator == 128 and dt.numerator % 2 == 1 and den["vraie"] is True)

    getcontext().prec = 40
    periode = str(Decimal(dt.denominator * 10 ** 9) / Decimal(dt.numerator))
    ajouter("V09", "la période 1/dt en nanosecondes, recalculée en décimale exacte sur 40 rangs",
            periode[:20] + "…", f"{c['periode']['valeur_ns'][:20]}…",
            periode == c["periode"]["valeur_ns"]
            and F(c["periode"]["fraction"]) * dt == 10 ** 9)

    astro = c["astronomie"]
    seuils = astro["seuils"]
    refs = {r["id"]: r for r in astro["references"]}
    cycles = {x["id"]: x for x in astro["cycles_declares"]}
    ecart_attendu = []
    for p in astro["resultats"]:
        e = (F(cycles[p["cycle"]]["jours"]) - F(refs[p["reference"]]["jours"])) * 86400
        ecart_attendu.append((p, e, verdict(e, F(seuils["conforme_s_par_an"]),
                                            F(seuils["signale_s_par_an"]))))
    faux_ecarts = [f"{p['cycle']}/{p['reference']}" for p, e, _ in ecart_attendu
                   if F(p["ecart_s_par_an"]) != e]
    faux_verdicts = [f"{p['cycle']}/{p['reference']}" for p, _, v in ecart_attendu
                     if v != p["verdict"]]
    ajouter("V10", "les neuf écarts astronomiques sortent des nombres du fichier, pas d'un copier-coller",
            "9 écart(s) exact(s)", f"faux {faux_ecarts or 'aucun'}", not faux_ecarts)
    ajouter("V11", "les verdicts se relisent dans les SEULS seuils gelés du fichier",
            "9 verdict(s) cohérents", f"divergents {faux_verdicts or 'aucun'}",
            not faux_verdicts and F(seuils["conforme_s_par_an"]) < F(seuils["signale_s_par_an"]))
    pire = {"CONFORME": 0, "ÉCART SIGNALÉ": 1, "HORS TOLÉRANCE": 2}
    par_cycle = {}
    for cycle in cycles:
        siennes = [v for p, _, v in ecart_attendu if p["cycle"] == cycle]
        par_cycle[cycle] = max(siennes, key=lambda v: pire[v])
    faux_cycles = sorted(k for k, v in par_cycle.items()
                         if astro["par_cycle"][k]["verdict"] != v)
    ajouter("V12", "le verdict par cycle est bien le pire de ses confrontations",
            "Soleil Lune Terre concordants", f"{faux_cycles or 'aucun'}", not faux_cycles)
    sens = astro["sensibilite"]
    e = (F("354") - 12 * F(sens["lunaison_alternee"])) * 86400
    ajouter("V13", "la sensibilité annoncée tient sous la variante du mois synodique",
            sens["verdict"],
            verdict(e, F(seuils["conforme_s_par_an"]), F(seuils["signale_s_par_an"])),
            F(sens["ecart_s_par_an"]) == e
            and sens["verdict"] == verdict(e, F(seuils["conforme_s_par_an"]),
                                           F(seuils["signale_s_par_an"])))

    unites = c["unites"]
    ajouter("V14", "l'unité retenue est énoncée, avec une condition de réfutation chiffrable",
            "lecture_retenue et condition non vides · ≥ 3 lectures rencontrées",
            f"{unites['lecture_retenue']} · {len(unites['lectures_rencontrees'])} lieux",
            bool(unites["lecture_retenue"].strip()) and bool(unites["condition_de_refutation"]
                                                             .strip())
            and len(unites["lectures_rencontrees"]) >= 3)
    ajouter("V15", "le fichier écrit ses propres limites",
            "au moins trois limites", f"{len(c['limites'])}", len(c["limites"]) >= 3)
    co = astro.get("coherence_des_sources", {})
    recalculees = {
        "lunaisons_12 = 12 × lunaison":
            F(refs["lunaisons_12"]["jours"]) == 12 * F(refs["lunaison"]["jours"]),
        "pour chaque référence, la fraction du fichier est la décimale citée":
            all(F(r["jours"]) == D(r["decite"]) for r in astro["references"]),
    }
    annoncees = {x["enonce"]: bool(x["vraie"]) for x in co.get("identites", [])}
    ajouter("V16", "les références citées se recoupent en entiers, et chaque fraction "
                   "rend la décimale de sa source",
            "deux identités vraies, et le fichier dit la même chose",
            f"recalculées {sorted(k for k, v in recalculees.items() if v)} · fichier "
            f"{sorted(k for k, v in annoncees.items() if v)}",
            all(recalculees.values()) and annoncees == recalculees)
    return rendu


def imports_de(chemin: Path) -> Dict[str, List[str]]:
    """Les racines importées par ce fichier, triées : la preuve de l'isolement se lit ici."""
    arbres = ast.parse(chemin.read_text(encoding="utf-8"))
    racines = set()
    for n in ast.walk(arbres):
        if isinstance(n, ast.Import):
            racines |= {a.name.split(".")[0] for a in n.names}
        elif isinstance(n, ast.ImportFrom) and n.module and n.level == 0:
            racines.add(n.module.split(".")[0])
    std = set(getattr(sys, "stdlib_module_names", ()))
    return {"stdlib": sorted(racines & std), "autres": sorted(racines - std)}


def main() -> int:
    ap = argparse.ArgumentParser(description="Vérifie un certificat d'horloge sans le dépôt.")
    ap.add_argument("chemin", nargs="?", default=str(CERTIFICAT_PAR_DEFAUT),
                    help=f"chemin du certificat (défaut {CERTIFICAT_PAR_DEFAUT.name})")
    ap.add_argument("--json", action="store_true", help="rapport JSON intégral")
    ap.add_argument("--importes", action="store_true",
                    help="afficher les imports de ce fichier et quitter")
    arguments = ap.parse_args()
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    if arguments.importes:
        print(json.dumps(imports_de(Path(__file__)), ensure_ascii=False, sort_keys=True))
        return 0

    chemin = Path(arguments.chemin)
    if not chemin.exists():
        print(f"CERTIFICAT ABSENT : {chemin}", file=sys.stderr)
        return 1
    octets = chemin.read_bytes()
    try:
        cert = json.loads(octets.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as erreur:
        print(f"CERTIFICAT ILLISIBLE : {erreur}", file=sys.stderr)
        return 1

    rendu = verifier(cert)
    verts = sum(1 for x in rendu if x["ok"])
    if arguments.json:
        print(json.dumps({"fichier": str(chemin), "sha256": hashlib.sha256(octets).hexdigest(),
                          "racine": cert.get("racine_merkle_sha256"),
                          "controles": rendu, "conforme": verts == len(rendu)},
                         ensure_ascii=False, indent=2, sort_keys=True))
        return 0 if verts == len(rendu) else 1

    print(f"{chemin.name} — {len(octets)} octets · SHA-256 {hashlib.sha256(octets).hexdigest()}")
    for x in rendu:
        print(f"  {x['id']} {'PASS' if x['ok'] else 'FAIL'}  {x['enonce']}")
        print(f"          attendu : {x['attendu']}")
        print(f"          obtenu  : {x['obtenu']}")
    c = cert
    if "racine_merkle_sha256" in c:
        print(f"racine de Merkle : {c['racine_merkle_sha256']}")
    print(f"CERTIFICAT {'CONFORME' if verts == len(rendu) else 'NON CONFORME'} — "
          f"{verts}/{len(rendu)} contrôles")
    return 0 if verts == len(rendu) else 1


if __name__ == "__main__":
    sys.exit(main())
