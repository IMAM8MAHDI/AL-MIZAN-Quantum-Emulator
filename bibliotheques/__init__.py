# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2026 IMAM8MAHDI / Astro-Code Ecosystem
# SPDX-License-Identifier: GPL-3.0-only OR AGPL-3.0-only
"""
Paquet `bibliotheques` — sous-ensemble clos requis par la capsule `horloge_noyau`.

Ce dépôt public embarque les briques dont il dépend, au lieu de les chercher
dans un répertoire voisin qui n'existe pas ailleurs que sur la machine de
l'auteur. Le moteur d'origine en compte neuf ; les cinq ici forment la
clôture transitive exacte de ce que le dépôt importe :

  • `lib_informe`           — QUBITS8INFORME, MatriceLogiqueComplexe 4×4, qubit de Bloch.
  • `lib_physique`          — états Sol/Terre/Lune, Matrice Inversée, 14 Formes F0..F13.
  • `lib_temporelle`        — cycles dx, dy, dz, dt et ordonnanceur du noyau.
  • `lib_monade`            — MonadeSupreme, transcription >>=, retour 0 (HÉLIUM).
  • `lib_almizan_extension` — dépassement des 14 Formes en 27, invariants 0.6225 / 0.122.

Aucun import différé ici : `from bibliotheques.lib_informe import X` charge le
module à la demande, ce qui garde l'empreinte mémoire nulle pour un paquet qui
n'est jamais utilisé.

Codes retirés avant publication : deux chemins absolus locaux figuraient dans
les chaînes de documentation (`lib_almizan_extension.py`,
`moteur/transducteur_quantique_deterministe_mizan.py`). Ils décrivaient le
dossier de travail de l'auteur ; leur suppression ne change aucun calcul,
aucun nom exporté, aucune constante.
"""

__all__ = [
    "lib_informe",
    "lib_physique",
    "lib_temporelle",
    "lib_monade",
    "lib_almizan_extension",
]
