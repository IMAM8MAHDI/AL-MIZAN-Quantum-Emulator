# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2026 IMAM8MAHDI / Astro-Code Ecosystem
# SPDX-License-Identifier: GPL-3.0-only OR AGPL-3.0-only
"""
===============================================================================
   ARBRE DE SAVOIR — LES 7 PROBLÈMES DU MILLÉNAIRE
===============================================================================
Racine : la méthode du Point Carré (énoncé formel → certificat borné → sceau).
Branches : les 7 problèmes du millénaire (Clay Mathematics Institute).
Fruits : les sous-certificats décidables sur chaque domaine fini.

Règle d'honnêteté : aucun nœud ne prétend résoudre un problème infini.
Chaque fruit indique sa borne de validité et son statut.
===============================================================================
"""

from __future__ import annotations

import time
from typing import Any, Dict, List

from .socle import ecrire_arbre, sceau
from . import (
    n01_riemann,
    n02_pvsnp,
    n03_navier_stokes,
    n04_yang_mills,
    n05_hodge,
    n06_bsd,
    n07_poincare,
    rigueur_intervalle,
    preuve_strip_riemann,
    preuve_N_T,
)

RACINE_METHODE = {
    "nom": "MÉTHODE DU POINT CARRÉ",
    "principe": "tout énoncé prolifique doit être (1) formulé précisément, "
                "(2) décidé exhaustivement sur son domaine fini, "
                "(3) scellé par empreinte reproductible",
    "heritage": "Conjecture du Point Carré — PC-1..PC-4 vérifiés par exhaustion",
}


def construire_arbre() -> Dict[str, Any]:
    """Exécute les 7 certificats et assemble l'arbre scellé."""
    branches: List[Dict[str, Any]] = [
        ("N1", "Hypothèse de Riemann", n01_riemann.certificat),
        ("N1b", "Riemann niveau 2 — zéros certifiés", rigueur_intervalle.certificat),
        ("N1c", "Riemann strip ≤ 100 — 29 zéros certifiés",
         preuve_strip_riemann.certificat),
        ("N1d", "Riemann THÉORÈME strip ≤ 100 (Turing)", preuve_N_T.certificat),
        ("N2", "P vs NP", n02_pvsnp.certificat),
        ("N3", "Navier-Stokes", n03_navier_stokes.certificat),
        ("N4", "Yang-Mills & trou de masse", n04_yang_mills.certificat),
        ("N5", "Conjecture de Hodge", n05_hodge.certificat),
        ("N6", "Birch & Swinnerton-Dyer", n06_bsd.certificat),
        ("N7", "Conjecture de Poincaré", n07_poincare.certificat),
    ]

    noeuds: List[Dict[str, Any]] = []
    for identifiant, nom, fonction in branches:
        try:
            noeud = fonction()
        except Exception as exc:
            from .socle import noeud_certificat
            noeud = noeud_certificat(nom, "(énoncé non exécuté)",
                                   {"erreur": str(exc)[:200]},
                                   "NON_DECIDABLE", f"échec d'exécution : {exc}")
        noeud["id_branche"] = identifiant
        noeuds.append(noeud)

    arbre: Dict[str, Any] = {
        "arbre": "ARBRE DE SAVOIR — PROBLÈMES DU MILLÉNAIRE",
        "racine": RACINE_METHODE,
        "branches": noeuds,
        "nb_branches": len(noeuds),
        "statuts_resume": {
            n["id_branche"]: {"probleme": n["probleme"], "statut": n["statut"]}
            for n in noeuds
        },
        "avertissement_maitre": (
            "Aucun nœud ne résout un problème du millénaire : chacun livre "
            "un certificat BORNÉ sur un domaine fini. Les problèmes portent "
            "sur des domaines infinis — ils exigent des démonstrations, "
            "pas des calculs. Cet arbre est prolifique en certificats "
            "honnêtes, pas en décrets."),
        "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    arbre["sceau_global_sha256"] = sceau(arbre)
    return arbre


def afficher_arbre(arbre: Dict[str, Any]) -> str:
    """Rendu texte élégant de l'arbre."""
    lignes = [
        "",
        "╔" + "═" * 68 + "╗",
        "   ARBRE DE SAVOIR — MÉTHODE DU POINT CARRÉ",
        "   énoncé formel → certificat borné → sceau SHA-256",
        "╚" + "═" * 68 + "╝",
        "",
        "RACINE : " + arbre["racine"]["nom"],
    ]
    for n in arbre["branches"]:
        marque = {"VERIFIE_EXHAUSTION": "◆", "CERTIFICAT_BORNE": "●",
                  "MESURE_INDICATION": "○", "DEJA_DEMONTRE": "★",
                  "NON_DECIDABLE": "◇"}.get(n["statut"], "?")
        lignes.append(f"  ├── {n['id_branche']} {marque} {n['probleme']}")
        lignes.append(f"  │      énoncé : {n['enonce_formel'][:80]}")
        lignes.append(f"  │      statut : {n['statut']}")
    lignes.append("  └── sceau global : " + arbre["sceau_global_sha256"][:48] + "…")
    return "\n".join(lignes)


if __name__ == "__main__":
    a = construire_arbre()
    print(afficher_arbre(a))
    print("\nÉcrit :", ecrire_arbre(a))
