# -*- coding: utf-8 -*-
"""
Garde technique du dossier horloge_noyau.

Politique :
  - LECTURE / IMPORT / EXÉCUTION / TESTS : autorisés
  - ÉCRITURE / MODIFICATION / TRONCATURE : INTERDITES

Mécanismes :
  1) Empreintes SHA-256 dans sceau/EMPREINTES.json — vérifiées à l'import
  2) Refuse toute API d'écriture exposée par ce module
  3) Les permissions FS (RX, Deny Write) sont appliquées au scellage (A137)
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Dict, List

CAPSULE = Path(__file__).resolve().parent
FICHIER_EMPREINTES = CAPSULE / "sceau" / "EMPREINTES.json"
FICHIER_VERROU = CAPSULE / "VERROU.json"

# Fichiers couverts par le sceau (relatifs à la capsule)
FICHIERS_SCELES: tuple[str, ...] = (
    "horloge_logique_mizan.py",
    "architecture_informe_couche_matiere_table_mizan.py",
    "verrou.py",
    "__init__.py",
    "actes/almizan_acte_a134_zero_expansion_matrice_complexe.json",
    "actes/almizan_acte_a136_horloge_deduite_du_noyau.json",
    "actes/almizan_acte_a137_verrouillage_horloge_noyau.json",
    "tests/test_horloge_noyau_complet.py",
)


class NoyauVerrouilleError(PermissionError):
    """Levée si le noyau est altéré ou si une écriture est tentée."""


def _sha256_fichier(chemin: Path) -> str:
    h = hashlib.sha256()
    with chemin.open("rb") as f:
        for bloc in iter(lambda: f.read(65536), b""):
            h.update(bloc)
    return h.hexdigest()


def calculer_empreintes() -> Dict[str, str]:
    out: Dict[str, str] = {}
    for rel in FICHIERS_SCELES:
        p = CAPSULE / rel
        if not p.is_file():
            raise NoyauVerrouilleError(f"Fichier noyau manquant : {rel}")
        out[rel.replace("\\", "/")] = _sha256_fichier(p)
    return out


def verifier_integrite() -> Dict[str, object]:
    """
    Vérifie que les fichiers scellés n'ont pas été modifiés.
    Lecture seule — n'écrit rien.
    """
    if not FICHIER_EMPREINTES.is_file():
        raise NoyauVerrouilleError(
            "Sceau absent (EMPREINTES.json). Le noyau n'est pas scellé."
        )
    attendu = json.loads(FICHIER_EMPREINTES.read_text(encoding="utf-8"))
    hashes = attendu.get("empreintes_sha256", {})
    actuel = calculer_empreintes()
    alters: List[str] = []
    for rel, digest in hashes.items():
        if actuel.get(rel) != digest:
            alters.append(rel)
    for rel in actuel:
        if rel not in hashes:
            alters.append(f"+{rel}")
    if alters:
        raise NoyauVerrouilleError(
            "ALTERATION DÉTECTÉE du noyau horloge_noyau : " + ", ".join(alters)
        )
    return {
        "integrite": True,
        "lecture_execution": True,
        "ecriture": False,
        "nb_fichiers": len(hashes),
        "acte_verrou": attendu.get("acte", "A137"),
    }


def refuser_ecriture(*_a, **_k) -> None:
    """Toute tentative d'écriture programmatique via cette API est refusée."""
    raise NoyauVerrouilleError(
        "HORLOGE-NOYAU VERROUILLÉE : lecture/exécution autorisées ; "
        "écriture, modification et troncature INTERDITES (acte A137)."
    )


def statut_verrou() -> Dict[str, object]:
    info = {
        "capsule": str(CAPSULE),
        "politique": "RX_ALLOWED_WRITE_DENIED",
        "lecture": True,
        "execution": True,
        "ecriture": False,
        "modification": False,
        "troncature": False,
    }
    if FICHIER_VERROU.is_file():
        info["verrou_json"] = json.loads(FICHIER_VERROU.read_text(encoding="utf-8"))
    try:
        info["integrite"] = verifier_integrite()
    except NoyauVerrouilleError as exc:
        info["integrite"] = {"integrite": False, "erreur": str(exc)}
    return info
