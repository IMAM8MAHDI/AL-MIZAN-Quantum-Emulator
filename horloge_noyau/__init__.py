# -*- coding: utf-8 -*-
"""
Capsule HORLOGE-NOYAU (IMAM8MAHDI)

Politique de verrouillage (acte A137) :
  ✓ Lecture, import, exécution, tests
  ✗ Écriture, modification, troncature

À l'import : vérification d'intégrité SHA-256 des fichiers scellés.
"""

from __future__ import annotations

from .verrou import (
    NoyauVerrouilleError,
    refuser_ecriture,
    statut_verrou,
    verifier_integrite,
)

# Garde à l'import : le noyau doit être intact (lecture OK, altération = exception)
_INTEGRITE = verifier_integrite()

from .horloge_logique_mizan import (  # noqa: E402
    HORLOGE_LOGIQUE,
    HORLOGE_DEDUITE_DU_NOYAU,
    CYCLE_DX_SOLAIRE,
    CYCLE_DY_LUNAIRE,
    CYCLE_DZ_QUANTIQUE,
    CYCLE_DT_KERNEL,
)
from .architecture_informe_couche_matiere_table_mizan import (  # noqa: E402
    ARCHITECTURE_FIGEE,
    confirmer_harmonie_et_prouver_justesse,
    TRAJECTOIRE_ZERO_EXPANSION,
    SYNCHRONISATION_HARMONIQUE_TRINITE,
)

__all__ = [
    "HORLOGE_LOGIQUE",
    "HORLOGE_DEDUITE_DU_NOYAU",
    "CYCLE_DX_SOLAIRE",
    "CYCLE_DY_LUNAIRE",
    "CYCLE_DZ_QUANTIQUE",
    "CYCLE_DT_KERNEL",
    "ARCHITECTURE_FIGEE",
    "confirmer_harmonie_et_prouver_justesse",
    "TRAJECTOIRE_ZERO_EXPANSION",
    "SYNCHRONISATION_HARMONIQUE_TRINITE",
    "verifier_integrite",
    "statut_verrou",
    "refuser_ecriture",
    "NoyauVerrouilleError",
    "_INTEGRITE",
]
