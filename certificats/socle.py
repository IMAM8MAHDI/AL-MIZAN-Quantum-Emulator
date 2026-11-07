# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2026 IMAM8MAHDI / Astro-Code Ecosystem
# SPDX-License-Identifier: GPL-3.0-only OR AGPL-3.0-only
"""
Socle de l'Arbre de Savoir — construction commune des certificats bornés.

MÉTHODE (héritée de la Conjecture du Point Carré) :
  énoncé formel précis → certificat de calcul borné → sceau SHA-256.

Statuts honnêtes :
  VERIFIE_EXHAUSTION  — propriété décidée sur un domaine fini
  CERTIFICAT_BORNE    — vérifié jusqu'à une borne explicite (pas au-delà)
  MESURE_INDICATION   — observation numérique, jamais une preuve
  DEJA_DEMONTRE       — théorème établi dans la littérature (rappel)
  NON_DECIDABLE       — énoncé infini : aucun calcul ne peut trancher
"""

from __future__ import annotations

import hashlib
import json
import math
import time
from pathlib import Path
from typing import Any, Dict

RACINE = Path(__file__).resolve().parent.parent
DOSSIER_RESULTATS = RACINE / "resultats"


def sceau(obj: Any) -> str:
    brut = json.dumps(obj, sort_keys=True, ensure_ascii=False, default=str)
    return hashlib.sha256(brut.encode("utf-8")).hexdigest()


def noeud_certificat(probleme: str, enonce: str, sous_resultats: Dict[str, Any],
                     statut: str, note_honnete: str) -> Dict[str, Any]:
    """Fabrique un nœud de l'arbre : énoncé + résultats + sceau."""
    noeud: Dict[str, Any] = {
        "probleme": probleme,
        "enonce_formel": enonce,
        "sous_certificats": sous_resultats,
        "statut": statut,
        "note_honnete": note_honnete,
        "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    noeud["sceau_sha256"] = sceau(noeud)
    return noeud


def ecrire_arbre(arbre: Dict[str, Any], nom: str = "arbre_savoir_millenaire") -> Path:
    DOSSIER_RESULTATS.mkdir(parents=True, exist_ok=True)
    chemin = DOSSIER_RESULTATS / f"{nom}.json"
    chemin.write_text(json.dumps(arbre, indent=2, ensure_ascii=False, default=str),
                      encoding="utf-8")
    return chemin


def plus_grand_facteur_carre(n: int) -> tuple[int, int]:
    """n = k² · reste, k maximal — signature carrée (méthode Point Carré)."""
    n = abs(n)
    if n == 0:
        return (0, 0)
    k = math.isqrt(n)
    while k > 1:
        if n % (k * k) == 0:
            return (k, n // (k * k))
        k -= 1
    return (1, n)
