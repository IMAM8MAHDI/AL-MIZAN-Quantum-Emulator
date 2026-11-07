# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2026 IMAM8MAHDI / Astro-Code Ecosystem
# SPDX-License-Identifier: GPL-3.0-only OR AGPL-3.0-only
"""
===============================================================================
   GÉNÉRATEUR GDSII — LAYOUT SYMBOLIQUE DU QUBIT LOGIQUE STEANE [[7,1,3]]
===============================================================================
Écrit un fichier .gds BINAIRE VALIDE (format GDSII stream v6) en pur Python :
enregistrements TLV (longueur u16, type u8, dtype u8, données).

STATUT HONNÊTE — LIMITES STRICTES :
  • Le fichier est géométriquement valide et s'ouvre dans KLayout/gdstk.
  • Ce N'EST PAS un masque fabricable : aucun PDK fonderie n'est utilisé.
  • Le "DRC" interne applique des règles GÉNÉRIQUES écrites ici
    (largeur min, espacement min, enclos du die) — pas les règles d'une
    fonderie réelle. Une tape-out exige un design physique complet sous
    CAO + PDK propriétaire + sign-off DRC/LVS de la fonderie.

Layout : tuile Steane = 7 qubits de données (heptagone) + 6 ancillas de
syndrome + coupleurs + ligne de lecture + cadre de die 5×5 mm.
Unités : 1 unité utilisateur = 1 µm ; DBU = 1 nm (cohérent GDSII classique).
===============================================================================
"""

from __future__ import annotations

import hashlib
import json
import math
import struct
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Sequence, Tuple

RACINE = Path(__file__).resolve().parent
DOSSIER_RESULTATS = RACINE / "resultats"

# Couches GDS (numérotation interne, non fonderie)
L_DIE = 0        # cadre du die
L_QUBIT = 1      # plots de qubits de données
L_ANCILLA = 2    # ancillas de mesure de syndrome
L_COUPLER = 3    # coupleurs qubit↔ancilla
L_READOUT = 4    # ligne de lecture / résonateurs
L_TEXTE = 7      # étiquettes

# Règles GÉNÉRIQUES internes (µm) — PAS un PDK
REGLE_LARGEUR_MIN_UM = 0.5
REGLE_ESPACEMENT_MIN_UM = 0.5
REGLE_MARGE_DIE_UM = 20.0


# ---------------------------------------------------------------------------
# Sérialisation binaire GDSII
# ---------------------------------------------------------------------------

def _rec(rectype: int, dtype: int, payload: bytes = b"") -> bytes:
    longueur = 4 + len(payload)
    return struct.pack(">HBB", longueur, rectype, dtype) + payload


def _rec_i2(rectype: int, *valeurs: int) -> bytes:
    return _rec(rectype, 0x02, struct.pack(">" + "h" * len(valeurs), *valeurs))


def _rec_i4(rectype: int, *valeurs: int) -> bytes:
    return _rec(rectype, 0x03, struct.pack(">" + "i" * len(valeurs), *valeurs))


def _rec_str(rectype: int, texte: str) -> bytes:
    brut = texte.encode("ascii")
    if len(brut) % 2:
        brut += b"\x00"
    return _rec(rectype, 0x06, brut)


def _reel8(x: float) -> bytes:
    """Réel 8 octets GDSII : excès-64, mantisse 56 bits, valeur = f·16^e."""
    if x == 0.0:
        return b"\x00" * 8
    signe = 0x80 if x < 0 else 0
    x = abs(x)
    e = int(math.floor(math.log(x, 16))) + 1
    f = x / (16.0 ** e)
    while f >= 1.0:
        e += 1
        f /= 16.0
    while f < 1.0 / 16.0:
        e -= 1
        f *= 16.0
    mant = int(round(f * (1 << 56)))
    return struct.pack(">B", signe | ((e + 64) & 0x7F)) + mant.to_bytes(7, "big")


def _horodatage_gds() -> bytes:
    t = time.localtime()
    return struct.pack(">12h", t.tm_year, t.tm_mon, t.tm_mday,
                       t.tm_hour, t.tm_min, t.tm_sec,
                       t.tm_year, t.tm_mon, t.tm_mday,
                       t.tm_hour, t.tm_min, t.tm_sec)


# ---------------------------------------------------------------------------
# Géométrie : rectangles (µm) par couche + textes
# ---------------------------------------------------------------------------

@dataclass
class Rect:
    couche: int
    x0: float
    y0: float
    x1: float
    y1: float

    @property
    def polygone(self) -> List[Tuple[float, float]]:
        return [(self.x0, self.y0), (self.x1, self.y0),
                (self.x1, self.y1), (self.x0, self.y1), (self.x0, self.y0)]


@dataclass
class Texte:
    couche: int
    x: float
    y: float
    contenu: str


def construire_tuile_steane(taille_die_um: float = 5000.0) -> Tuple[List[Rect], List[Texte]]:
    """Tuile d'un qubit logique Steane : 7 données heptagonales + 6 ancillas.

    Dimensions symboliques (µm) — géométrie d'illustration, pas un PDK.
    """
    rects: List[Rect] = []
    textes: List[Texte] = []

    c = taille_die_um / 2.0
    rects.append(Rect(L_DIE, 0, 0, taille_die_um, taille_die_um))
    textes.append(Texte(L_TEXTE, c - 400, 150, "STEANE [[7,1,3]] AL-MIZAN (symbolique)"))

    r_donnees = 1400.0       # rayon du cercle des 7 qubits de données
    r_ancillas = 950.0       # rayon des ancillas de syndrome
    pad = 80.0               # demi-côté des plots (80 µm → plot 160 µm)
    largeur_coupleur = 8.0   # largeur des coupleurs (8 µm)

    centres_d: List[Tuple[float, float]] = []
    for k in range(7):
        ang = 2 * math.pi * k / 7 + math.pi / 2
        cx, cy = c + r_donnees * math.cos(ang), c + r_donnees * math.sin(ang)
        centres_d.append((cx, cy))
        rects.append(Rect(L_QUBIT, cx - pad, cy - pad, cx + pad, cy + pad))
        textes.append(Texte(L_TEXTE, cx - 30, cy - 8, f"D{k}"))

    centres_a: List[Tuple[float, float]] = []
    for k in range(6):
        ang = 2 * math.pi * (k + 0.5) / 6 + math.pi / 2
        cx, cy = c + r_ancillas * math.cos(ang), c + r_ancillas * math.sin(ang)
        centres_a.append((cx, cy))
        rects.append(Rect(L_ANCILLA, cx - pad * 0.6, cy - pad * 0.6,
                          cx + pad * 0.6, cy + pad * 0.6))
        textes.append(Texte(L_TEXTE, cx - 30, cy - 8, f"A{k}"))

    # Coupleurs : chaque ancilla reliée aux 2 qubits de données les plus proches
    for (ax, ay) in centres_a:
        distances = sorted(centres_d, key=lambda d: (d[0] - ax) ** 2 + (d[1] - ay) ** 2)
        for (dx, dy) in distances[:2]:
            # Coupleur orthogonal en L : segment horizontal puis vertical
            milieu_x = (ax + dx) / 2
            rects.append(Rect(L_COUPLER,
                              min(ax, milieu_x) - largeur_coupleur / 2, ay - largeur_coupleur / 2,
                              max(ax, milieu_x) + largeur_coupleur / 2, ay + largeur_coupleur / 2))
            rects.append(Rect(L_COUPLER,
                              milieu_x - largeur_coupleur / 2, min(ay, dy) - largeur_coupleur / 2,
                              milieu_x + largeur_coupleur / 2, max(ay, dy) + largeur_coupleur / 2))
            rects.append(Rect(L_COUPLER,
                              min(milieu_x, dx) - largeur_coupleur / 2, dy - largeur_coupleur / 2,
                              max(milieu_x, dx) + largeur_coupleur / 2, dy + largeur_coupleur / 2))

    # Ligne de lecture : bus horizontal + brins vers chaque qubit de données
    y_bus = c - 2200.0
    rects.append(Rect(L_READOUT, c - 1800, y_bus - 6, c + 1800, y_bus + 6))
    for (dx, dy) in centres_d:
        rects.append(Rect(L_READOUT, dx - 4, min(y_bus, dy) - 4,
                          dx + 4, max(y_bus, dy) + 4))
    textes.append(Texte(L_TEXTE, c - 1800, y_bus - 120, "BUS LECTURE"))

    return rects, textes


# ---------------------------------------------------------------------------
# Écriture du fichier .gds
# ---------------------------------------------------------------------------

def ecrire_gds(chemin: Path, rects: Sequence[Rect], textes: Sequence[Texte],
               nom_structure: str = "STEANE_TILE", nom_lib: str = "ALMIZAN") -> None:
    """Sérialise le layout en flux binaire GDSII v6 (DBU = 1 nm)."""
    blocs: List[bytes] = []
    blocs.append(_rec_i2(0x00, 600))                 # HEADER v6
    blocs.append(_rec(0x01, 0x03, _horodatage_gds()))  # BGNLIB
    blocs.append(_rec_str(0x02, nom_lib))            # LIBNAME
    blocs.append(_rec(0x03, 0x05, _reel8(1e-3) + _reel8(1e-9)))  # UNITS
    blocs.append(_rec(0x05, 0x03, _horodatage_gds()))  # BGNSTR
    blocs.append(_rec_str(0x06, nom_structure))      # STRNAME

    for r in rects:
        blocs.append(_rec(0x08, 0x00))               # BOUNDARY
        blocs.append(_rec_i2(0x0D, r.couche))        # LAYER
        blocs.append(_rec_i2(0x0E, 0))               # DATATYPE
        coords: List[int] = []
        for (x, y) in r.polygone:
            coords += [int(round(x * 1000)), int(round(y * 1000))]
        blocs.append(_rec_i4(0x10, *coords))         # XY
        blocs.append(_rec(0x11, 0x00))               # ENDEL

    for t in textes:
        blocs.append(_rec(0x0C, 0x00))               # TEXT
        blocs.append(_rec_i2(0x0D, t.couche))        # LAYER
        blocs.append(_rec_i2(0x16, 0))               # TEXTTYPE
        blocs.append(_rec_i2(0x17, 0x0005))          # PRESENTATION (flags)
        blocs.append(_rec_i4(0x10, int(round(t.x * 1000)),
                             int(round(t.y * 1000))))  # XY
        blocs.append(_rec_str(0x19, t.contenu))      # STRING
        blocs.append(_rec(0x11, 0x00))               # ENDEL

    blocs.append(_rec(0x07, 0x00))                   # ENDSTR
    blocs.append(_rec(0x04, 0x00))                   # ENDLIB
    chemin.write_bytes(b"".join(blocs))


# ---------------------------------------------------------------------------
# DRC générique interne (PAS un PDK fonderie)
# ---------------------------------------------------------------------------

def verifier_drc(rects: Sequence[Rect]) -> Dict[str, object]:
    """Règles internes génériques : largeur min, espacement min (même couche),
    enclos dans le die. Retourne la liste des violations."""
    violations: List[str] = []

    for i, r in enumerate(rects):
        w = abs(r.x1 - r.x0)
        h = abs(r.y1 - r.y0)
        if min(w, h) < REGLE_LARGEUR_MIN_UM - 1e-9 and r.couche != L_DIE:
            violations.append(
                f"R{i} couche {r.couche} : largeur {min(w, h):.3f} µm "
                f"< min {REGLE_LARGEUR_MIN_UM} µm")

    par_couche: Dict[int, List[Rect]] = {}
    for r in rects:
        if r.couche == L_DIE:
            continue
        par_couche.setdefault(r.couche, []).append(r)

    for couche, liste in par_couche.items():
        for i in range(len(liste)):
            for j in range(i + 1, len(liste)):
                a, b = liste[i], liste[j]
                # Distance entre rectangles (0 si chevauchement)
                dx = max(0.0, max(a.x0 - b.x1, b.x0 - a.x1))
                dy = max(0.0, max(a.y0 - b.y1, b.y0 - a.y1))
                gap = math.hypot(dx, dy)
                if 0 < gap < REGLE_ESPACEMENT_MIN_UM - 1e-9:
                    violations.append(
                        f"couche {couche} : espacement {gap:.3f} µm "
                        f"< min {REGLE_ESPACEMENT_MIN_UM} µm")

    die = next((r for r in rects if r.couche == L_DIE), None)
    if die:
        for i, r in enumerate(rects):
            if r.couche == L_DIE:
                continue
            if (r.x0 < die.x0 + REGLE_MARGE_DIE_UM or r.y0 < die.y0 + REGLE_MARGE_DIE_UM
                    or r.x1 > die.x1 - REGLE_MARGE_DIE_UM
                    or r.y1 > die.y1 - REGLE_MARGE_DIE_UM):
                violations.append(
                    f"R{i} couche {r.couche} : hors marge die {REGLE_MARGE_DIE_UM} µm")

    return {
        "regles": {
            "largeur_min_um": REGLE_LARGEUR_MIN_UM,
            "espacement_min_um": REGLE_ESPACEMENT_MIN_UM,
            "marge_die_um": REGLE_MARGE_DIE_UM,
        },
        "nb_violations": len(violations),
        "violations": violations,
        "avertissement": "Règles génériques internes — PAS le DRC d'une fonderie",
    }


def generer_puce_steane(dossier: Path = DOSSIER_RESULTATS) -> Dict[str, object]:
    """Pipeline complet : layout → .gds binaire → DRC générique → manifeste scellé."""
    dossier.mkdir(parents=True, exist_ok=True)
    rects, textes = construire_tuile_steane()
    chemin_gds = dossier / "steane_tile_almizan.gds"
    ecrire_gds(chemin_gds, rects, textes)

    drc = verifier_drc(rects)
    empreinte = hashlib.sha256(chemin_gds.read_bytes()).hexdigest()

    manifeste = {
        "fichier_gds": str(chemin_gds),
        "taille_octets": chemin_gds.stat().st_size,
        "nb_rectangles": len(rects),
        "nb_textes": len(textes),
        "couches": {"die": L_DIE, "qubits": L_QUBIT, "ancillas": L_ANCILLA,
                    "coupleurs": L_COUPLER, "lecture": L_READOUT, "texte": L_TEXTE},
        "drc_generique": drc,
        "sha256_gds": empreinte,
        "statut": "GDSII géométriquement valide — NON fabricable, "
                  "aucun PDK fonderie, DRC interne générique uniquement",
    }
    chemin_man = dossier / "steane_tile_manifeste.json"
    chemin_man.write_text(json.dumps(manifeste, indent=2, ensure_ascii=False),
                          encoding="utf-8")
    manifeste["fichier_manifeste"] = str(chemin_man)
    return manifeste
