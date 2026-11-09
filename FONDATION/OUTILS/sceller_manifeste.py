# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2026 IMAM8MAHDI / Astro-Code Ecosystem
# SPDX-License-Identifier: GPL-3.0-only OR AGPL-3.0-only
"""OUTIL — sceller ou revérifier MANIFESTE_SHA256.txt du dépôt.

    py -3 FONDATION/OUTILS/sceller_manifeste.py            # régénère le manifeste
    py -3 FONDATION/OUTILS/sceller_manifeste.py --verifier  # lecture seule, ne écrit rien
    py -3 FONDATION/OUTILS/sceller_manifeste.py --json      # rapport de vérification en JSON

La règle est celle que `README_DEPOT.md` documente : une empreinte SHA-256 par
fichier **suivi par git**, deux espaces, puis le chemin relatif en POSIX, trié
par chemin ; le manifeste lui-même est exclu (pas d'auto-référence).

Les hashes portent sur les octets du **blob git** (`HEAD:CHEMIN`), donc
normalisés LF. Un `sha256sum` direct sur un worktree Windows (`core.autocrlf`
turne CRLF) ne correspondra pas — c'est voulu, et c'est la raison d'être de cet
outil : il lit `git ls-tree` puis `git cat-file --batch`, jamais le disque.

Code de sortie : 0 (écriture réussie, ou vérification conforme) ; 1 (manifeste
divergent) ; 2 (git indisponible, HEAD illisible, objet manquant).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Tuple

RACINE = Path(__file__).resolve().parents[2]
SORTIE = RACINE / "MANIFESTE_SHA256.txt"
EXCLU = "MANIFESTE_SHA256.txt"


def git(*arguments: str, entree: bytes = b"") -> bytes:
    processeur = subprocess.run(["git", "-C", str(RACINE), *arguments],
                                input=entree, capture_output=True)
    if processeur.returncode != 0:
        raise RuntimeError(processeur.stderr.decode("utf-8", "replace").strip())
    return processeur.stdout


def entrees() -> List[Tuple[str, bytes]]:
    """Les fichiers suivis par HEAD : (chemin, octets du blob), triés par chemin.

    `-z` évite tout echappement de chemin : les enregistrements sont separes par
    NUL et le chemin suit une tabulation, en octets bruts.
    """
    bruts = [r for r in git("ls-tree", "-r", "-z", "HEAD").split(b"\0") if r]
    table = {}
    for enregistrement in bruts:
        objet, chemin = enregistrement.split(b"\t", 1)
        table[chemin] = objet.split()[2]
    chimins = sorted(c for c in table if c != EXCLU.encode())
    return [(c.decode("utf-8"), b) for c, b in zip(chimins, corps_blocs([table[c] for c in chimins]))]


def corps_blocs(shas: List[bytes]) -> List[bytes]:
    """Les octets de chaque blob, en une seule passe `cat-file --batch`.

    L'entree est une liste de SHA, la sortie une suite d'enregistrements
    `<sha> blob <taille>\\n<octets>\\n`. Passer par les SHA plutot que par les
    chemins evite toute question d'encodage ou de separateur de chemin.
    """
    sortie = git("cat-file", "--batch", entree=b"\n".join(shas) + b"\n")
    corps, pos = [], 0
    for _ in shas:
        fin = sortie.index(b"\n", pos)
        entete = sortie[pos:fin].split()
        if entete[-1] == b"missing":
            raise RuntimeError(f"objet absent de HEAD : {entete[0].decode()}")
        taille = int(entete[2])
        corps.append(sortie[fin + 1:fin + 1 + taille])
        pos = fin + 1 + taille + 1
    return corps


def manifester(paires: List[Tuple[str, bytes]]) -> bytes:
    lignes = [f"{hashlib.sha256(corps).hexdigest()}  {chemin}" for chemin, corps in paires]
    return ("\n".join(lignes) + "\n").encode("utf-8")


def lire_manifeste(chemin: Path) -> Dict[str, str]:
    """Le manifeste lu : {chemin: empreinte}, vide si le fichier n'existe pas."""
    if not chemin.exists():
        return {}
    table = {}
    for ligne in chemin.read_bytes().decode("utf-8").split("\n"):
        parts = ligne.split("  ", 1)
        if len(parts) == 2 and len(parts[0]) == 64:
            table[parts[1]] = parts[0]
    return table


def comparer(attendu: Dict[str, str], observe: Dict[str, str]) -> Dict[str, List[str]]:
    return {"ajoutes": sorted(set(attendu) - set(observe)),
            "retires": sorted(set(observe) - set(attendu)),
            "modifies": sorted(c for c in set(attendu) & set(observe) if attendu[c] != observe[c])}


def main() -> int:
    ap = argparse.ArgumentParser(description="Scelle ou revérifie le manifeste SHA-256 du dépôt.")
    ap.add_argument("--verifier", action="store_true", help="compare sans écrire (code 1 si divergent)")
    ap.add_argument("--json", action="store_true", help="rapport de vérification en JSON")
    arguments = ap.parse_args()
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    try:
        paires = entrees()
        octets = manifester(paires)
    except (RuntimeError, ValueError, IndexError) as erreur:
        print(f"SCALEMENT IMPOSSIBLE : {erreur}", file=sys.stderr)
        return 2

    attendu = {chemin: hashlib.sha256(corps).hexdigest() for chemin, corps in paires}
    if arguments.verifier:
        ecart = comparer(attendu, lire_manifeste(SORTIE))
        conforme = not any(ecart.values())
        if arguments.json:
            print(json.dumps({"conforme": conforme, "entrees": len(attendu), **ecart},
                             ensure_ascii=False, indent=2, sort_keys=True))
        else:
            print(f"MANIFESTE {'CONFORME' if conforme else 'DIVERGENT'} — {len(attendu)} entrées "
                  f"attendues contre {len(lire_manifeste(SORTIE))} lues")
            for nom, liste in ecart.items():
                if liste:
                    print(f"  {nom} : {len(liste)} — {', '.join(liste[:6])}"
                          f"{' …' if len(liste) > 6 else ''}")
        return 0 if conforme else 1

    SORTIE.write_bytes(octets)
    print(f"{len(attendu)} entrées scellées sur HEAD {git('rev-parse', '--short', 'HEAD').decode().strip()}"
          f" -> {SORTIE.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
