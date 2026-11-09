# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2026 IMAM8MAHDI / Astro-Code Ecosystem
# SPDX-License-Identifier: GPL-3.0-only OR AGPL-3.0-only
"""OUTIL — auditer un dossier contre les quatre piliers de la base.

    py -3 FONDATION/OUTILS/audit_piliers.py FONDATION/fondation_base.py
    py -3 FONDATION/OUTILS/audit_piliers.py ABONDANCE/electricite_abondance.py CHIFFRES/chiffres_pi.py
    py -3 FONDATION/OUTILS/audit_piliers.py --tous            # les six modules principaux
    py -3 FONDATION/OUTILS/audit_piliers.py --tous --rigide   # un pilier NON TENU fait échouer

L'outil n'invente rien : il appelle `resoudre()` du module visé et lit ce que le module
déclare déjà. Quatre verdicts par pilier, et rien d'autre :

    P1 UNITE          une équation = un identifiant = un contrôle, en chaîne continue
    P2 BORNE          toute équation porte une `limite` écrite (>= 40 caractères)
    P3 CONFRONTATION  tout résultat porte un chemin module → fonction → contrôle, un statut
                      parmi les trois, et tout contrôle un attendu et un obtenu non vides
    P4 TRANSMISSION   imports stdlib ou locaux uniquement, `verifier()` callable, garde
                      `__main__` dans le fichier

Code de sortie : 0 si aucun pilier n'est FAIL (et, avec `--rigide`, aucun NON TENU) ; 1 sinon ;
2 si le module est illisible ou ne expose pas `resoudre()`.

Coût : l'audit APPELLE resoudre() du module visé. FONDATION et ABONDANCE répondent en
quelques dixièmes de seconde ; CHIFFRES calcule son domaine court (20 000 chiffres de π, e,
√2 plus un calibrage Monte-Carlo) et demande une à deux minutes.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any, Dict, List

RACINE = Path(__file__).resolve().parents[2]
if str(RACINE) not in sys.path:
    sys.path.insert(0, str(RACINE))

from FONDATION import fondation_base as FB                                 # noqa: E402

MIN_LIMITE = 40


def charger(chemin: Path) -> Any:
    nom = f"audit_{chemin.stem}"
    spec = importlib.util.spec_from_file_location(nom, str(chemin))
    if spec is None or spec.loader is None:
        raise ImportError(f"spec introuvable pour {chemin}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[nom] = module
    spec.loader.exec_module(module)
    return module


def _suite(ids: List[str], modele: str) -> List[str]:
    """Les identifiants doivent être exactement modele01..modeleNN, sans trou ni doublon."""
    attendu = [modele.format(i) for i in range(1, len(ids) + 1)]
    return [f"{a} / {b}" for a, b in zip(attendu, ids) if a != b]


def auditer(chemin: Path) -> Dict[str, Any]:
    module = charger(chemin)
    if not hasattr(module, "resoudre"):
        raise AttributeError(f"{chemin.name} n'expose pas resoudre()")
    donnees: Dict[str, Any] = module.resoudre()
    eqs: List[Dict[str, Any]] = donnees.get("equations", [])
    cs: List[Dict[str, Any]] = donnees.get("controles", [])
    resultat: Dict[str, Any] = {"fichier": str(chemin.relative_to(RACINE)),
                                "equations": len(eqs), "controles": len(cs)}

    def pilier(nom: str, etat: str, detail: str) -> None:
        resultat.setdefault("piliers", {})[nom] = {"etat": etat, "detail": detail}

    # P1 — UNITE
    ids_eq = [e.get("id", "") for e in eqs]
    ids_c = [c.get("id", "") for c in cs]
    trous = _suite(ids_eq, "EQ-{:02d}") + _suite(ids_c, "C{:02d}")
    doublons = sorted({i for i in ids_eq + ids_c if (ids_eq + ids_c).count(i) > 1})
    if not eqs or not cs:
        pilier("P1 UNITE", "FAIL", "aucune équation ou aucun contrôle déclaré")
    else:
        pilier("P1 UNITE", "OK" if (not trous and not doublons and len(eqs) == len(cs)) else "FAIL",
               f"{len(eqs)} équations, {len(cs)} contrôles, trous {trous or 'aucun'}, "
               f"doublons {doublons or 'aucun'}")

    # P2 — BORNE
    portees = [e for e in eqs if isinstance(e.get("limite"), str) and len(e["limite"].strip())
               >= MIN_LIMITE]
    if not any("limite" in e for e in eqs):
        pilier("P2 BORNE", "NON TENU", "le module ne porte pas la clé `limite` : "
               f"0/{len(eqs)} équation bornée")
    else:
        minuscules = [e["id"] for e in eqs if e["id"] not in {p["id"] for p in portees}]
        pilier("P2 BORNE", "OK" if len(portees) == len(eqs) else "FAIL",
               f"{len(portees)}/{len(eqs)} limites d'au moins {MIN_LIMITE} caractères, "
               f"absentes ou courtes : {minuscules or 'aucune'}")

    # P3 — CONFRONTATION
    chemins_absents = [e["id"] for e in eqs
                       if not isinstance(e.get("chemin"), str) or "→" not in e["chemin"]]
    statuts_inconnus = [e["id"] for e in eqs if e.get("statut") not in FB.STATUTS]
    controles_vides = [c["id"] for c in cs
                       if not str(c.get("attendu", "")).strip() or not str(c.get("obtenu", "")).strip()]
    controles_rouges = [c["id"] for c in cs if not c.get("ok")]
    p3_ok = not (chemins_absents or statuts_inconnus or controles_vides or controles_rouges)
    pilier("P3 CONFRONTATION", "OK" if p3_ok else "FAIL",
           f"{len(eqs)} chemins, {len(cs)} contrôles · sans chemin {chemins_absents or 'aucun'} · "
           f"statut inconnu {statuts_inconnus or 'aucun'} · attendu ou obtenu vide "
           f"{controles_vides or 'aucun'} · rouges {controles_rouges or 'aucun'}")

    # P4 — TRANSMISSION
    imports = FB.imports_de(str(chemin))
    texte = chemin.read_text(encoding="utf-8", errors="replace")
    garde = "__name__ == \"__main__\"" in texte or "__name__ == '__main__'" in texte
    verificable = callable(getattr(module, "verifier", None))
    p4_ok = not imports["tiers"] and garde and verificable
    pilier("P4 TRANSMISSION", "OK" if p4_ok else "FAIL",
           f"tiers {imports['tiers'] or 'aucun'} · garde __main__ {garde} · "
           f"verifier() {verificable} · {len(imports['stdlib'])} imports stdlib")

    etats = [p["etat"] for p in resultat["piliers"].values()]
    resultat["verdict"] = ("FAIL" if "FAIL" in etats
                           else "NON CONFORME (rigide)" if "NON TENU" in etats
                           else "CONFORME")
    return resultat


def main() -> int:
    ap = argparse.ArgumentParser(description="Audite un module contre les quatre piliers.")
    ap.add_argument("chemins", nargs="*", help="chemin(s) vers le ou les module(s) visé(s)")
    ap.add_argument("--tous", action="store_true",
                    help="auditer les modules principaux déclarés par la base")
    ap.add_argument("--rigide", action="store_true",
                    help="un pilier NON TENU compte comme un échec")
    ap.add_argument("--json", action="store_true", help="sortie JSON intégrale")
    arguments = ap.parse_args()
    cibles = [Path(c) for c in arguments.chemins]
    if arguments.tous:
        cibles += [RACINE / "FONDATION" / "fondation_base.py",
                   RACINE / "CHIFFRES" / "chiffres_pi.py",
                   RACINE / "HORLOGERIE" / "horlogerie.py"]
        cibles += [RACINE / "ABONDANCE" / m for m in FB.MODULES_PRINCIPAUX
                   if m.endswith("_abondance.py")]
    if not cibles:
        ap.error("donnez au moins un chemin, ou --tous")
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    rendus, codes = [], []
    for chemin in cibles:
        chemin = chemin.resolve()
        if not chemin.exists():
            print(f"CHEMIN ABSENT : {chemin}", file=sys.stderr)
            codes.append(2)
            continue
        try:
            rendus.append(auditer(chemin))
        except (AttributeError, TypeError) as erreur:
            print(f"MODULE INSUFFISANT : {chemin.name} — {erreur}", file=sys.stderr)
            codes.append(2)
            continue
    if arguments.json:
        print(json.dumps(rendus, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        for rendu in rendus:
            print(f"\n{rendu['fichier']} — {rendu['equations']} équations, "
                  f"{rendu['controles']} contrôles — {rendu['verdict']}")
            for nom, pilote in sorted(rendu["piliers"].items()):
                print(f"  {nom:<18} {pilote['etat']:<10} {pilote['detail']}")
    if codes:
        return min(codes) if all(c == 2 for c in codes) else 1
    strict = any(r["verdict"] == "FAIL" for r in rendus)
    if strict:
        return 1
    if arguments.rigide and any(r["verdict"] != "CONFORME" for r in rendus):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
