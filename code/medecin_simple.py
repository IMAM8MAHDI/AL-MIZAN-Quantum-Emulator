# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2026 IMAM8MAHDI / Astro-Code Ecosystem
# SPDX-License-Identifier: GPL-3.0-only OR AGPL-3.0-only
"""
===============================================================================
   MÉDECIN SIMPLE — l'interface clinique d'AL-MIZAN (expérimental)
===============================================================================
Deux moteurs, UNE réponse : score, couleur, action.

  ADN : séquence → invariants normiques quadratiques dans ℚ(√−d)
        (les 64 codons = alphabet fini base-4 ; la signature de la
        séquence est testée contre les formes x²+dy²).

  TSM (Tenseur de Stabilité Modulaire) : plusieurs signaux vitaux
        (coeur, cerveau, hormones) → UN score global 0-100.

INTERFACE CLINIQUE — 3 champs seulement :
    score : 0 à 100
    couleur : VERT / ORANGE / ROUGE
    action : une phrase simple pour le praticien

HONNÊTETÉ : recherche expérimentale — PAS un dispositif médical.
===============================================================================
"""

from __future__ import annotations

import math
from typing import Any, Dict, List

from certificats.socle import noeud_certificat
from mizan_clinical_shield import score_almizan


# ---------------------------------------------------------------------------
# ADN — invariants normiques quadratiques (64 codons = alphabet base-4)
# ---------------------------------------------------------------------------

_BASES = {"A": 0, "C": 1, "G": 2, "T": 3}


def codon_index(triplet: str) -> int:
    """Triplet nucléotidique → indice 0..63 (base-4)."""
    return 16 * _BASES[triplet[0]] + 4 * _BASES[triplet[1]] + _BASES[triplet[2]]


def _forme_normique(n: int, d: int, ymax: int = 400) -> tuple | None:
    """Teste n = x² + d·y² — retourne (x, y) ou None."""
    for y in range(0, min(ymax, int((n / d) ** 0.5) + 1)):
        r = n - d * y * y
        x = int(r ** 0.5 + 0.5)
        if x * x == r:
            return (x, y)
    return None


def analyse_adn(seq: str, corps: List[int] | None = None) -> Dict[str, Any]:
    """Signature de séquence ADN + recherche de formes normiques.

    corps : discriminants testés (défaut {1,2,3,7} — dont √−7, corps
    du gardien découvert dans le système).
    """
    corps = corps or [1, 2, 3, 7]
    seq = seq.upper()
    codons = [seq[i:i + 3] for i in range(0, len(seq) - 2, 3)
              if len(seq[i:i + 3]) == 3 and all(b in _BASES for b in seq[i:i + 3])]
    if not codons:
        return {"erreur": "aucun codon valide"}
    signature = sum(codon_index(c) for c in codons)
    trouvees = {}
    for d in corps:
        r = _forme_normique(signature, d)
        if r:
            trouvees[f"Q(sqrt(-{d}))"] = {"x": r[0], "y": r[1],
                                          "forme": f"{r[0]}² + {d}·{r[1]}²"}
    return {
        "nb_codons": len(codons),
        "signature": signature,
        "formes_normiques": trouvees,
        "normique": bool(trouvees),
    }


# ---------------------------------------------------------------------------
# TSM — Tenseur de Stabilité Modulaire (multi-signaux → 1 score)
# ---------------------------------------------------------------------------

def tenseur_stabilite(signaux: Dict[str, List[float]],
                      poids: Dict[str, float] | None = None) -> Dict[str, Any]:
    """Fusionne les SAM de plusieurs signaux vitaux en un score global."""
    poids = poids or {}
    scores = {}
    total_w = 0.0
    somme = 0.0
    for nom, sig in signaux.items():
        s = score_almizan(sig)
        w = poids.get(nom, 1.0)
        scores[nom] = s["SAM"]
        somme += s["SAM"] * w
        total_w += w
    global_score = round(somme / total_w, 1) if total_w else 0.0
    return {
        "scores_par_organe": scores,
        "score_global": global_score,
        "organe_faible": min(scores, key=scores.get),
    }


# ---------------------------------------------------------------------------
# INTERFACE CLINIQUE — score, couleur, action. C'est tout.
# ---------------------------------------------------------------------------

def clinique(score: float, contexte: str = "signal vital") -> Dict[str, Any]:
    """Traduit un score en langage médecin. Trois champs. Point."""
    if score >= 75:
        couleur, action = "VERT", "stable — surveillance de routine"
    elif score >= 50:
        couleur, action = "ORANGE", "vigilance — re-mesurer sous 24h"
    else:
        couleur, action = "ROUGE", "alerte — évaluation clinique immédiate"
    return {"score": score, "couleur": couleur, "action": action,
            "contexte": contexte}


# ---------------------------------------------------------------------------
# Certificat de démonstration
# ---------------------------------------------------------------------------

def certificat_demo() -> Dict[str, Any]:
    import random
    random.seed(3)
    # ADN : séquence de 21 codons
    seq = "ATGGCTGACTTGCCAAAGGTA"[:60]
    adn = analyse_adn(seq)
    # TSM : coeur stable + cerveau stable + hormones dégradées
    coeur = [math.sin(2 * math.pi * t / 24) + 0.05 * random.gauss(0, 1)
             for t in range(96)]
    cerveau = [math.sin(2 * math.pi * t / 12) + 0.08 * random.gauss(0, 1)
               for t in range(96)]
    hormones = [random.gauss(0, 1) for _ in range(96)]
    tsm = tenseur_stabilite({"coeur": coeur, "cerveau": cerveau,
                             "hormones": hormones})
    return noeud_certificat(
        "MÉDECIN SIMPLE — ADN normique + Tenseur de Stabilité",
        "invariants quadratiques de l'ADN + score vital unifié 0-100",
        {
            "adn": adn,
            "tenseur": tsm,
            "interface_clinique": clinique(tsm["score_global"],
                                           "tableau vital global"),
        },
        "CERTIFICAT_BORNE",
        "Recherche expérimentale — PAS un dispositif médical. "
        "La lecture clinique est sciemment simplifiée à 3 champs.")


if __name__ == "__main__":
    import json
    print(json.dumps(certificat_demo(), indent=2, ensure_ascii=False))
