# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2026 IMAM8MAHDI / Astro-Code Ecosystem
# SPDX-License-Identifier: GPL-3.0-only OR AGPL-3.0-only
"""
===============================================================================
   PONTS VERS ASTRO-Q°ODE_SYSTEME — ÉMULATEUR QUANTIQUE AL-MIZAN
===============================================================================
Réutilisation (IMPORT LECTURE SEULE) des briques souveraines existantes :

  • qubit_logique_mizan.py        → couche de correction d'erreur [[7,1,3]] Steane
  • transducteur_quantique_...py  → traduction déterministe (MIZAN 0.6225, A–S)
  • horloge_noyau/                → horodatage de phase (capsule SCELLÉE, jamais écrite)

Chaque pont se dégrade proprement : si la brique est absente, l'émulateur
continue de fonctionner et le rapport indique "disponible": false.
===============================================================================
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Dict, Optional

RACINE = Path(__file__).resolve().parent
RACINE_SYSTEME_AQ = RACINE.parent / "ASTRO-Q°ODE_SYSTEME"

if str(RACINE_SYSTEME_AQ) not in sys.path and RACINE_SYSTEME_AQ.is_dir():
    sys.path.insert(0, str(RACINE_SYSTEME_AQ))


# ---------------------------------------------------------------------------
# 1. Couche QEC — code de Steane [[7,1,3]] (qubit_logique_mizan.py)
# ---------------------------------------------------------------------------

def charger_module_qec():
    """Importe qubit_logique_mizan en lecture seule (None si indisponible)."""
    try:
        import qubit_logique_mizan  # type: ignore
        return qubit_logique_mizan
    except Exception:
        return None


def analyse_qec_steane(p_depolarisant: float = 1e-3,
                       echantillons_mc: int = 50_000,
                       graine: int = 20261027) -> Dict[str, Any]:
    """Analyse de la couche de correction d'erreur via le module souverain.

    Retourne les taux d'échec logique exacts (modèle capacité de code),
    le pseudo-seuil, le recoupement Monte Carlo et la preuve de distance.
    """
    qlm = charger_module_qec()
    if qlm is None:
        return {"disponible": False,
                "raison": "qubit_logique_mizan.py introuvable dans ASTRO-Q°ODE_SYSTEME"}

    preuve = qlm.preuve_distance()
    taux_exact = qlm.taux_echec_depolarisant(p_depolarisant)
    mc = qlm.monte_carlo_depolarisant(p_depolarisant,
                                    echantillons=echantillons_mc,
                                    graine=graine)
    return {
        "disponible": True,
        "code": "[[7,1,3]] Steane",
        "distance": preuve["distance"],
        "preuve_distance": preuve,
        "p_physique": p_depolarisant,
        "taux_echec_logique_exact": taux_exact,
        "monte_carlo": mc,
        "pseudo_seuil_depolarisant": qlm.seuil_pseudo_depolarisant(),
        "empreinte_source_sha256": qlm.empreinte_source(),
        "statut": "calcul exact (syndromes parfaits) — pas une mesure QPU",
    }


def demonstration_correction_poids_un() -> Dict[str, Any]:
    """Démo vivante : injecte chaque erreur X/Z de poids 1 sur |0>_L et corrige."""
    qlm = charger_module_qec()
    if qlm is None:
        return {"disponible": False}

    etat0, _ = qlm.construire_etats_code()
    corriges = 0
    total = 0
    for qubit in range(7):
        for type_erreur in ("X", "Z"):
            ex, ez = (1 << qubit, 0) if type_erreur == "X" else (0, 1 << qubit)
            etat_erreur = qlm.appliquer_pauli(etat0, ex, ez)
            # Le module expose correction_syndrome(syndrome(e)) comme correction ;
            # decoder_pauli retourne quant à lui l'erreur RÉSIDUELLE e ^ c.
            cx = qlm.correction_syndrome(qlm.syndrome(ex))
            cz = qlm.correction_syndrome(qlm.syndrome(ez))
            etat_corrige = qlm.appliquer_pauli(etat_erreur, cx, cz)
            # Fidélité avec |0>_L (à phase globale près)
            prod = abs(sum(a.conjugate() * b
                           for a, b in zip(etat0, etat_corrige))) ** 2
            total += 1
            if prod > 1.0 - 1e-9:
                corriges += 1
    return {
        "disponible": True,
        "erreurs_testees": total,
        "erreurs_corrigees": corriges,
        "tous_poids_un_corriges": corriges == total,
        "verification_module": qlm.verifier_correction_poids_un(),
    }


# ---------------------------------------------------------------------------
# 2. Transducteur quantique → déterministe
# ---------------------------------------------------------------------------

def traduire_deterministe(distribution: Dict[str, float],
                          algorithme: str,
                          fidelite: float,
                          entropie: float) -> Dict[str, Any]:
    """Passe la distribution de mesure dans le TransducteurQuantiqueDeterministe."""
    try:
        from transducteur_quantique_deterministe_mizan import (  # type: ignore
            TransducteurQuantiqueDeterministe,
        )
        from dataclasses import asdict
    except Exception:
        return {"disponible": False,
                "raison": "transducteur_quantique_deterministe_mizan.py introuvable"}

    transducteur = TransducteurQuantiqueDeterministe()
    res = transducteur.traduire_distribution(
        distribution, algorithme=algorithme,
        fidelite=fidelite, entropie=entropie,
    )
    return {"disponible": True, "traduction": asdict(res)}


# ---------------------------------------------------------------------------
# 3. Horloge noyau (capsule scellée A137 — LECTURE SEULE)
# ---------------------------------------------------------------------------

def battement_noyau() -> Dict[str, Any]:
    """Lit une pulsation de HORLOGE_LOGIQUE pour horodater le résultat.

    Lecture uniquement : la capsule `horloge_noyau/` n'est jamais modifiée.
    """
    try:
        from horloge_noyau import HORLOGE_LOGIQUE  # type: ignore
        etat, cycle = HORLOGE_LOGIQUE.battre()
        return {
            "disponible": True,
            "pulsation": HORLOGE_LOGIQUE.compteur_pulsations,
            "etat_matiere": getattr(etat, "etat", str(etat)),
            "cycle_trinite": getattr(cycle, "__dict__", str(cycle)),
        }
    except Exception as exc:
        return {"disponible": False, "raison": str(exc)}
