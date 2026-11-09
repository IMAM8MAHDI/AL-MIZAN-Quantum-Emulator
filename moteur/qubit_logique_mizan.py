# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2026 IMAM8MAHDI / Astro-Code Ecosystem
# SPDX-License-Identifier: GPL-3.0-only OR AGPL-3.0-only
"""
Qubit logique Al-Mizan — construction, preuve et simulation
===========================================================
Ce module construit un qubit logique [[7,1,3]] (code de Steane), vérifie ses
propriétés par calcul exact, simule son taux d'erreur logique sous bruit
dépolarisant et modélise la contribution du matériel classique (DAC, horloge,
bruit 1/f, décodeur CMOS).

Statut honnête :
- le code, les stabilisateurs, la distance et le décodeur sont **opérationnels**
  au sens logiciel : ils s'exécutent et sont vérifiables ;
- les taux d'erreur sont **exacts** pour le modèle de bruit de capacité de code
  (syndrômes parfaits), et recoupés par Monte Carlo ;
- le budget processeur/transistors est un **modèle d'ingénierie** paramétré,
  pas une mesure de laboratoire ;
- aucun QPU, cryostat ou capteur physique n'est utilisé. Il n'y a donc pas de
  démonstration expérimentale de qubit logique physique.

La reconnaissance par les pairs ne se décrète pas : elle exige une publication,
une reproductibilité indépendante et une revue externe. Le module fournit les
preuves calculées, les commandes de reproduction et les empreintes SHA-256.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import random
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, Sequence

RACINE = Path(__file__).resolve().parent
DOSSIER_RESULTATS = RACINE / "resultats" / "qubit_logique"

N_QUBITS = 7
MASQUE_TOTAL = (1 << N_QUBITS) - 1
LIGNES_H = (0b1010101, 0b1100110, 0b1111000)

VERSION = "1.0"
GRAINE_MONTE_CARLO = 20261027


# ---------------------------------------------------------------------------
# 1. Outils GF(2) et géométrie du code
# ---------------------------------------------------------------------------

def poids(masque: int) -> int:
    """Poids de Hamming d'un masque binaire."""
    return int(masque).bit_count()


def syndrome(masque: int) -> int:
    """Syndrome de Hamming : trois bits (lignes de H) pour un masque de qubits."""
    valeur = 0
    for rang, ligne in enumerate(LIGNES_H):
        if poids(masque & ligne) & 1:
            valeur |= 1 << rang
    return valeur


def _engendrer(base: Sequence[int]) -> frozenset[int]:
    resultat = {0}
    for vecteur in base:
        resultat |= {x ^ vecteur for x in tuple(resultat)}
    return frozenset(resultat)


ESPACE_C = tuple(x for x in range(1 << N_QUBITS) if syndrome(x) == 0)
ESPACE_DUAL = _engendrer(LIGNES_H)
ENSEMBLE_LOGIQUE = frozenset(ESPACE_C) - ESPACE_DUAL
POIDS_MINIMAL_LOGIQUE = min(poids(x) for x in ENSEMBLE_LOGIQUE)
SYNDROMES_UNIQUES = {syndrome(1 << j): j for j in range(N_QUBITS)}


# ---------------------------------------------------------------------------
# 2. États logiques et action des Pauli
# ---------------------------------------------------------------------------

def appliquer_pauli(vecteur: Sequence[complex], x: int, z: int) -> list[complex]:
    """Applique X(x)Z(z) à un vecteur de dimension 2^7 (phase globale ignorée)."""
    sortie = [0j] * (1 << N_QUBITS)
    for indice, amplitude in enumerate(vecteur):
        if amplitude:
            phase = -1.0 if poids(indice & z) & 1 else 1.0
            sortie[indice ^ x] += phase * amplitude
    return sortie


def construire_etats_code() -> tuple[list[complex], list[complex]]:
    """|0>_L uniforme sur C, |1>_L = Z^{⊗7}|0>_L (convention explicitée)."""
    amplitude = 1.0 / math.sqrt(len(ESPACE_C))
    zero = [0j] * (1 << N_QUBITS)
    un = [0j] * (1 << N_QUBITS)
    for codage in ESPACE_C:
        zero[codage] = amplitude
        un[codage] = amplitude * (-1.0 if poids(codage) & 1 else 1.0)
    return zero, un


ETAT_ZERO, ETAT_UN = construire_etats_code()
X_LOGIQUE = (0, MASQUE_TOTAL)
Z_LOGIQUE = (MASQUE_TOTAL, 0)


def _produit_scalaire(gauche: Sequence[complex], droite: Sequence[complex]) -> complex:
    return sum(a.conjugate() * b for a, b in zip(gauche, droite))


def matrice_projection(x: int, z: int) -> tuple[complex, complex, complex, complex]:
    """Matrice 2x2 de P E P dans la base {|0>_L, |1>_L}."""
    image_zero = appliquer_pauli(ETAT_ZERO, x, z)
    image_un = appliquer_pauli(ETAT_UN, x, z)
    return (
        _produit_scalaire(ETAT_ZERO, image_zero),
        _produit_scalaire(ETAT_ZERO, image_un),
        _produit_scalaire(ETAT_UN, image_zero),
        _produit_scalaire(ETAT_UN, image_un),
    )


def est_proportionnelle_identite(matrice: tuple[complex, complex, complex, complex], tolerance: float = 1e-9) -> bool:
    m00, m01, m10, m11 = matrice
    return abs(m01) < tolerance and abs(m10) < tolerance and abs(m00 - m11) < tolerance


def verifier_stabilisateurs() -> bool:
    for ligne in LIGNES_H:
        for x, z in ((ligne, 0), (0, ligne)):
            if not est_proportionnelle_identite(matrice_projection(x, z)):
                return False
            image_zero = appliquer_pauli(ETAT_ZERO, x, z)
            image_un = appliquer_pauli(ETAT_UN, x, z)
            if abs(_produit_scalaire(ETAT_ZERO, image_zero) - 1.0) > 1e-9:
                return False
            if abs(_produit_scalaire(ETAT_UN, image_un) - 1.0) > 1e-9:
                return False
    return True


def verifier_operateurs_logiques() -> bool:
    """Vérifie que P X_L P = σ_x et P Z_L P = σ_z (à phase globale près)."""
    mx = matrice_projection(*X_LOGIQUE)
    mz = matrice_projection(*Z_LOGIQUE)
    return (
        abs(mx[0]) < 1e-9
        and abs(mx[3]) < 1e-9
        and abs(abs(mx[1]) - 1.0) < 1e-9
        and abs(abs(mx[2]) - 1.0) < 1e-9
        and abs(mz[0] - 1.0) < 1e-9
        and abs(mz[3] + 1.0) < 1e-9
        and abs(mz[1]) < 1e-9
        and abs(mz[2]) < 1e-9
    )


def paulis_poids_max(maximal: int) -> Iterable[tuple[int, int]]:
    for x in range(1 << N_QUBITS):
        for z in range(1 << N_QUBITS):
            if poids(x | z) <= maximal:
                yield x, z


def verifier_knill_laflamme(maximal: int = 2) -> tuple[bool, int]:
    """Vérifie P E P proportionnelle à P pour tous les Pauli de poids <= maximal."""
    compteur = 0
    for x, z in paulis_poids_max(maximal):
        compteur += 1
        if not est_proportionnelle_identite(matrice_projection(x, z)):
            return False, compteur
    return True, compteur


def preuve_distance() -> dict:
    kl_ok, nb_verifies = verifier_knill_laflamme(2)
    exemple = min((x for x in ENSEMBLE_LOGIQUE if poids(x) == POIDS_MINIMAL_LOGIQUE), default=0)
    matrice_logique = matrice_projection(exemple, 0)
    logique_non_triviale = not est_proportionnelle_identite(matrice_logique)
    return {
        "parametres": "[[7,1,3]]",
        "dimension_espace_code": len(ESPACE_C),
        "dimension_dual": len(ESPACE_DUAL),
        "operateurs_logiques_distincts": len(ENSEMBLE_LOGIQUE),
        "poids_minimal_operateur_logique": POIDS_MINIMAL_LOGIQUE,
        "exemple_operateur_poids_3": format(exemple, "07b"),
        "paulis_verifies_poids_max_2": nb_verifies,
        "knill_laflamme_poids_2": kl_ok,
        "operateur_poids_3_non_trivial": logique_non_triviale,
        "distance": POIDS_MINIMAL_LOGIQUE,
        "stabilisateurs_ok": verifier_stabilisateurs(),
        "operateurs_logiques_ok": verifier_operateurs_logiques(),
        "convention": "|0>_L uniforme sur C ; X_logique = Z^{⊗7} ; Z_logique = X^{⊗7}",
    }


# ---------------------------------------------------------------------------
# 3. Décodeur et taux d'erreur exacts
# ---------------------------------------------------------------------------

def correction_syndrome(s: int) -> int:
    if s == 0:
        return 0
    return 1 << (s - 1)


def decoder_pauli(ex: int, ez: int) -> tuple[int, int]:
    return ex ^ correction_syndrome(syndrome(ex)), ez ^ correction_syndrome(syndrome(ez))


def echec_logique(ex: int, ez: int) -> bool:
    rx, rz = decoder_pauli(ex, ez)
    return rx in ENSEMBLE_LOGIQUE or rz in ENSEMBLE_LOGIQUE


def verifier_correction_poids_un() -> tuple[bool, int]:
    compteur = 0
    for j in range(N_QUBITS):
        bit = 1 << j
        for ex, ez in ((bit, 0), (0, bit), (bit, bit)):
            compteur += 1
            if decoder_pauli(ex, ez) != (0, 0):
                return False, compteur
    return True, compteur


def _statistiques_depolarisant() -> dict[int, list[int]]:
    stats = {w: [0, 0] for w in range(N_QUBITS + 1)}
    for ex in range(1 << N_QUBITS):
        for ez in range(1 << N_QUBITS):
            w = poids(ex | ez)
            stats[w][0] += 1
            if echec_logique(ex, ez):
                stats[w][1] += 1
    return stats


def _statistiques_independant() -> dict[tuple[int, int], list[int]]:
    stats: dict[tuple[int, int], list[int]] = {}
    for ex in range(1 << N_QUBITS):
        for ez in range(1 << N_QUBITS):
            cle = (poids(ex), poids(ez))
            stats.setdefault(cle, [0, 0])
            stats[cle][0] += 1
            if echec_logique(ex, ez):
                stats[cle][1] += 1
    return stats


STATS_DEPOLARISANT = _statistiques_depolarisant()
STATS_INDEPENDANT = _statistiques_independant()


def taux_echec_depolarisant(p: float) -> float:
    if not 0.0 <= p <= 1.0:
        raise ValueError("p doit être dans [0, 1].")
    total = 0.0
    for w, (_, echecs) in STATS_DEPOLARISANT.items():
        total += echecs * (p / 3.0) ** w * (1.0 - p) ** (N_QUBITS - w)
    return total


def taux_echec_independant(q: float) -> float:
    if not 0.0 <= q <= 1.0:
        raise ValueError("q doit être dans [0, 1].")
    total = 0.0
    for (wx, wz), (_, echecs) in STATS_INDEPENDANT.items():
        total += echecs * q ** (wx + wz) * (1.0 - q) ** (2 * N_QUBITS - wx - wz)
    return total


COEFFICIENT_QUADRATIQUE = STATS_DEPOLARISANT[2][1] / 9.0


def seuil_pseudo_depolarisant() -> float | None:
    def ecart(p: float) -> float:
        return taux_echec_depolarisant(p) - p

    if ecart(0.5) <= 0.0:
        return None
    bas, haut = 1e-9, 0.5
    for _ in range(200):
        milieu = (bas + haut) / 2.0
        if ecart(milieu) > 0.0:
            haut = milieu
        else:
            bas = milieu
    return (bas + haut) / 2.0


def monte_carlo_depolarisant(p: float, echantillons: int = 200_000, graine: int = GRAINE_MONTE_CARLO) -> dict:
    generateur = random.Random(graine)
    echecs = 0
    for _ in range(echantillons):
        ex = 0
        ez = 0
        for j in range(N_QUBITS):
            if generateur.random() < p:
                choix = generateur.randrange(3)
                if choix == 0:
                    ex |= 1 << j
                elif choix == 1:
                    ez |= 1 << j
                else:
                    ex |= 1 << j
                    ez |= 1 << j
        if echec_logique(ex, ez):
            echecs += 1
    taux = echecs / echantillons
    z = 1.96
    denominateur = 1.0 + z * z / echantillons
    centre = (taux + z * z / (2.0 * echantillons)) / denominateur
    demi = z * math.sqrt(
        taux * (1.0 - taux) / echantillons + z * z / (4.0 * echantillons * echantillons)
    ) / denominateur
    return {
        "echantillons": echantillons,
        "echecs": echecs,
        "taux": taux,
        "ic95": [max(0.0, centre - demi), min(1.0, centre + demi)],
        "graine": graine,
    }


# ---------------------------------------------------------------------------
# 4. Modèle matériel : DAC, horloge, bruit, décodeur, transistors
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class ParametresMateriel:
    duree_porte_s: float = 20e-9
    t1_s: float = 100e-6
    t2_s: float = 80e-6
    bits_dac: int = 12
    tension_pleine_echelle_v: float = 1.0
    tension_pi_v: float = 0.1
    gigue_horloge_s: float = 10e-12
    bruit_1f_v2_hz: float = 1e-12
    frequence_min_hz: float = 1.0


def infidelite_dac(bits: int, tension_pleine_echelle_v: float = 1.0, tension_pi_v: float = 0.1) -> float:
    """Erreur de rotation due à la quantification du DAC (porte π)."""
    pas = tension_pleine_echelle_v / (2 ** bits)
    epsilon = pas / tension_pi_v
    return math.sin(math.pi * epsilon / 2.0) ** 2


def infidelite_gigue(duree_porte_s: float, gigue_s: float) -> float:
    """Erreur de rotation due à la gigue temporelle : δθ = Ω σ_t, Ω = π/t_g."""
    omega = math.pi / duree_porte_s
    return math.sin(omega * gigue_s / 2.0) ** 2


def infidelite_bruit_1f(
    bruit_v2_hz: float,
    tension_pi_v: float = 0.1,
    duree_porte_s: float = 20e-9,
    frequence_min_hz: float = 1.0,
) -> float:
    """Bruit de contrôle intégré entre f_min et 1/(2 t_g), modèle d'ingénierie."""
    frequence_max = 1.0 / (2.0 * duree_porte_s)
    sigma_v = math.sqrt(bruit_v2_hz * math.log(frequence_max / frequence_min_hz))
    epsilon = sigma_v / tension_pi_v
    return math.sin(math.pi * epsilon / 2.0) ** 2


def infidelite_decoherence(duree_porte_s: float, t1_s: float, t2_s: float) -> float:
    """Borne d'ingénierie : t_g/T2 + t_g/(3 T1)."""
    return duree_porte_s / t2_s + duree_porte_s / (3.0 * t1_s)


def bits_dac_requis(cible: float, tension_pleine_echelle_v: float = 1.0, tension_pi_v: float = 0.1) -> int:
    bits = 1
    while infidelite_dac(bits, tension_pleine_echelle_v, tension_pi_v) > cible:
        bits += 1
    return bits


def gigue_requise(cible: float, duree_porte_s: float = 20e-9) -> float:
    omega = math.pi / duree_porte_s
    return 2.0 * math.asin(math.sqrt(cible)) / omega


def budget_materiel(parametres: ParametresMateriel | None = None) -> list[dict]:
    p = parametres or ParametresMateriel()
    elements = [
        ("Décohérence T1/T2", f"t_g={p.duree_porte_s*1e9:.0f} ns, T1={p.t1_s*1e6:.0f} µs, T2={p.t2_s*1e6:.0f} µs",
         infidelite_decoherence(p.duree_porte_s, p.t1_s, p.t2_s)),
        ("Quantification DAC", f"{p.bits_dac} bits, V_FS={p.tension_pleine_echelle_v:.2f} V, V_pi={p.tension_pi_v:.3f} V",
         infidelite_dac(p.bits_dac, p.tension_pleine_echelle_v, p.tension_pi_v)),
        ("Gigue d'horloge", f"σ_t={p.gigue_horloge_s*1e12:.0f} ps", infidelite_gigue(p.duree_porte_s, p.gigue_horloge_s)),
        ("Bruit 1/f de contrôle", f"A_V={p.bruit_1f_v2_hz:.0e} V²/Hz", infidelite_bruit_1f(p.bruit_1f_v2_hz, p.tension_pi_v, p.duree_porte_s)),
    ]
    total = sum(valeur for _, _, valeur in elements)
    elements.append(("Total (premier ordre)", "somme des contributions", total))
    return [{"composant": nom, "parametre": parametre, "infidelite": valeur} for nom, parametre, valeur in elements]


def table_dac(max_bits: int = 16) -> list[dict]:
    return [
        {"bits": bits, "pas_v": 1.0 / (2 ** bits), "infidelite": infidelite_dac(bits)}
        for bits in range(8, max_bits + 1)
    ]


def table_gigue() -> list[dict]:
    return [
        {"gigue_ps": gigue * 1e12, "infidelite": infidelite_gigue(20e-9, gigue)}
        for gigue in (1e-12, 3e-12, 10e-12, 30e-12, 100e-12, 300e-12)
    ]


def table_decoherence() -> list[dict]:
    return [
        {
            "t2_us": t2 * 1e6,
            "t1_us": 100.0,
            "infidelite": infidelite_decoherence(20e-9, 100e-6, t2),
        }
        for t2 in (20e-6, 40e-6, 80e-6, 100e-6, 200e-6)
    ]


def budget_decodeur(
    distance: int,
    cycle_s: float = 1e-6,
    frequence_hz: float = 3e9,
    portes_logiques: int = 1_000_000,
    capacite_par_porte_f: float = 1e-15,
    tension_v: float = 0.8,
    activite: float = 0.1,
) -> dict:
    """Budget du décodeur classique pour un code de surface rotatif de distance d."""
    qubits = 2 * distance * distance - 1
    stabilisateurs = distance * distance - 1
    debit = stabilisateurs / cycle_s
    cycles_par_bit = frequence_hz * cycle_s / stabilisateurs
    puissance = activite * capacite_par_porte_f * tension_v ** 2 * frequence_hz * portes_logiques
    return {
        "distance": distance,
        "qubits_physiques": qubits,
        "stabilisateurs": stabilisateurs,
        "debit_syndrome_bits_s": debit,
        "cycles_par_bit": cycles_par_bit,
        "puissance_decodeur_w": puissance,
    }


def table_decodeur() -> list[dict]:
    return [budget_decodeur(d) for d in (9, 17, 25, 33, 41)]


def projection_surface(p: float, distance: int, seuil: float = 0.01, prefacteur: float = 0.1) -> float | None:
    """Modèle d'extrapolation P_L ≈ A (p/p_th)^((d+1)/2), valable sous le seuil."""
    if p >= seuil:
        return None
    return prefacteur * (p / seuil) ** ((distance + 1) / 2)


def distance_requise(p: float, cible: float = 1e-12, seuil: float = 0.01, prefacteur: float = 0.1) -> int | None:
    if p >= seuil or cible <= 0.0:
        return None
    exposant = math.log(cible / prefacteur) / math.log(p / seuil)
    distance = max(3, int(math.ceil(2.0 * exposant - 1.0)))
    if distance % 2 == 0:
        distance += 1
    return distance


def table_surface() -> list[dict]:
    lignes = []
    for p in (5e-4, 1e-3, 2e-3, 5e-3):
        distance = distance_requise(p)
        if distance is None:
            lignes.append({"p": p, "distance_requise": None, "qubits_physiques": None, "taux_projete": None})
        else:
            lignes.append({
                "p": p,
                "distance_requise": distance,
                "qubits_physiques": 2 * distance * distance - 1,
                "taux_projete": projection_surface(p, distance),
            })
    return lignes


# ---------------------------------------------------------------------------
# 5. Rapport et sorties
# ---------------------------------------------------------------------------

def _sci(valeur: float, chiffres: int = 3) -> str:
    if valeur == 0.0:
        return "0"
    return f"{valeur:.{chiffres}e}"


def _horodatage() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def empreinte_source() -> str:
    return hashlib.sha256(Path(__file__).read_bytes()).hexdigest()


def _ecrire_csv(chemin: Path, lignes: Sequence[dict]) -> None:
    chemin.parent.mkdir(parents=True, exist_ok=True)
    if not lignes:
        chemin.write_text("", encoding="utf-8")
        return
    with chemin.open("w", encoding="utf-8", newline="") as fichier:
        ecrivain = csv.DictWriter(fichier, fieldnames=list(lignes[0].keys()), delimiter=";")
        ecrivain.writeheader()
        for ligne in lignes:
            ecrivain.writerow(ligne)


def _echelle_log(valeur: float, minimum: float, maximum: float, taille: int) -> float:
    if maximum <= minimum:
        return taille / 2.0
    return (math.log10(valeur) - math.log10(minimum)) / (math.log10(maximum) - math.log10(minimum)) * taille


def ecrire_svg_steane(chemin: Path, points: Sequence[tuple[float, float]]) -> None:
    largeur, hauteur = 760, 460
    marge_g, marge_d, marge_h, marge_b = 82, 28, 42, 58
    zone_l = largeur - marge_g - marge_d
    zone_h = hauteur - marge_h - marge_b
    valides = [(p, taux) for p, taux in points if p > 0.0 and taux > 0.0]
    if not valides:
        chemin.write_text("<svg xmlns='http://www.w3.org/2000/svg'/>", encoding="utf-8")
        return
    x_min = min(p for p, _ in valides) / 2.0
    x_max = max(p for p, _ in valides) * 2.0
    y_min = min(t for _, t in valides) / 10.0
    y_max = max(t for _, t in valides) * 10.0
    y_min = min(y_min, x_min)
    y_max = max(y_max, x_max)

    def x_px(p: float) -> float:
        return marge_g + _echelle_log(p, x_min, x_max, zone_l)

    def y_px(t: float) -> float:
        return marge_h + zone_h - _echelle_log(t, y_min, y_max, zone_h)

    elements = [
        f"<svg xmlns='http://www.w3.org/2000/svg' width='{largeur}' height='{hauteur}' viewBox='0 0 {largeur} {hauteur}'>",
        "<rect width='100%' height='100%' fill='#0b1020'/>",
        f"<text x='{largeur/2}' y='26' fill='#e8eefc' font-family='sans-serif' font-size='18' text-anchor='middle'>Qubit logique [[7,1,3]] — taux d'erreur exact</text>",
    ]
    for decade_x in range(math.floor(math.log10(x_min)), math.ceil(math.log10(x_max)) + 1):
        valeur = 10.0 ** decade_x
        if x_min <= valeur <= x_max:
            px = x_px(valeur)
            elements.append(f"<line x1='{px:.1f}' y1='{marge_h}' x2='{px:.1f}' y2='{marge_h+zone_h}' stroke='#23304d' stroke-width='1'/>")
            elements.append(f"<text x='{px:.1f}' y='{marge_h+zone_h+22}' fill='#9fb0d0' font-family='sans-serif' font-size='12' text-anchor='middle'>1e{decade_x}</text>")
    for decade_y in range(math.floor(math.log10(y_min)), math.ceil(math.log10(y_max)) + 1):
        valeur = 10.0 ** decade_y
        if y_min <= valeur <= y_max:
            py = y_px(valeur)
            elements.append(f"<line x1='{marge_g}' y1='{py:.1f}' x2='{marge_g+zone_l}' y2='{py:.1f}' stroke='#23304d' stroke-width='1'/>")
            elements.append(f"<text x='{marge_g-10}' y='{py+4:.1f}' fill='#9fb0d0' font-family='sans-serif' font-size='12' text-anchor='end'>1e{decade_y}</text>")
    elements.append(f"<line x1='{marge_g}' y1='{marge_h+zone_h}' x2='{marge_g+zone_l}' y2='{marge_h}' stroke='#6c7fa5' stroke-width='1'/>")
    elements.append(f"<text x='{largeur/2}' y='{hauteur-14}' fill='#c7d4ee' font-family='sans-serif' font-size='13' text-anchor='middle'>probabilité d'erreur physique p (échelle log)</text>")
    elements.append(f"<text x='18' y='{hauteur/2}' fill='#c7d4ee' font-family='sans-serif' font-size='13' text-anchor='middle' transform='rotate(-90 18 {hauteur/2})'>taux d'erreur logique P_L</text>")
    polyligne = " ".join(f"{x_px(p):.1f},{y_px(t):.1f}" for p, t in sorted(valides))
    elements.append(f"<polyline points='{polyligne}' fill='none' stroke='#49e0a8' stroke-width='3'/>")
    elements.append(f"<line x1='{x_px(x_min):.1f}' y1='{y_px(x_min):.1f}' x2='{x_px(min(x_max, 1.0)):.1f}' y2='{y_px(min(x_max, 1.0)):.1f}' stroke='#ffb454' stroke-width='2' stroke-dasharray='7 5'/>")
    elements.append("<text x='640' y='70' fill='#49e0a8' font-family='sans-serif' font-size='13'>code Steane</text>")
    elements.append("<text x='640' y='90' fill='#ffb454' font-family='sans-serif' font-size='13'>P_L = p</text>")
    elements.append("</svg>")
    chemin.write_text("\n".join(elements), encoding="utf-8")


def ecrire_svg_budget(chemin: Path, lignes: Sequence[dict]) -> None:
    largeur = 760
    hauteur = 90 + 34 * len(lignes) + 40
    marge_g, marge_d, marge_h, marge_b = 260, 40, 48, 40
    zone_l = largeur - marge_g - marge_d
    valeurs = [max(float(ligne["infidelite"]), 1e-15) for ligne in lignes]
    maximum = max(valeurs) * 10.0
    minimum = min(valeurs) / 10.0
    elements = [
        f"<svg xmlns='http://www.w3.org/2000/svg' width='{largeur}' height='{hauteur}' viewBox='0 0 {largeur} {hauteur}'>",
        "<rect width='100%' height='100%' fill='#0b1020'/>",
        f"<text x='{largeur/2}' y='28' fill='#e8eefc' font-family='sans-serif' font-size='18' text-anchor='middle'>Budget d'erreur du contrôle classique</text>",
    ]
    for indice, (ligne, valeur) in enumerate(zip(lignes, valeurs)):
        y = marge_h + indice * 34
        longueur = max(2.0, _echelle_log(valeur, minimum, maximum, zone_l))
        couleur = "#49e0a8" if "Total" not in ligne["composant"] else "#ffb454"
        elements.append(f"<text x='{marge_g-12}' y='{y+16}' fill='#c7d4ee' font-family='sans-serif' font-size='12' text-anchor='end'>{ligne['composant']}</text>")
        elements.append(f"<rect x='{marge_g}' y='{y+4}' width='{longueur:.1f}' height='18' rx='4' fill='{couleur}' opacity='0.85'/>")
        elements.append(f"<text x='{marge_g+longueur+8:.1f}' y='{y+18}' fill='#9fb0d0' font-family='sans-serif' font-size='11'>{_sci(ligne['infidelite'])}</text>")
    elements.append(f"<text x='{largeur/2}' y='{hauteur-12}' fill='#c7d4ee' font-family='sans-serif' font-size='12' text-anchor='middle'>infidélité par porte (échelle log)</text>")
    elements.append("</svg>")
    chemin.write_text("\n".join(elements), encoding="utf-8")


def generer_rapport(dossier: Path | str = DOSSIER_RESULTATS) -> dict:
    dossier = Path(dossier)
    dossier.mkdir(parents=True, exist_ok=True)

    preuve = preuve_distance()
    correction_ok, nb_corrections = verifier_correction_poids_un()
    p_reference = 1e-3
    taux_reference = taux_echec_depolarisant(p_reference)
    seuil = seuil_pseudo_depolarisant()
    monte_carlo = monte_carlo_depolarisant(1e-2, echantillons=200_000)
    exact_mc = taux_echec_depolarisant(1e-2)
    surface = table_surface()
    decodeur = table_decodeur()
    materiel = budget_materiel()
    dac = table_dac()
    gigue = table_gigue()
    decoherence = table_decoherence()

    points = []
    for exposant in range(-50, -1):
        p = 10.0 ** (exposant / 10.0)
        points.append((p, taux_echec_depolarisant(p)))

    _ecrire_csv(dossier / "donnees_steane.csv", [
        {"p": f"{p:.6e}", "taux_echec_depolarisant": f"{taux:.6e}", "taux_echec_independant_q_egal_p": f"{taux_echec_independant(p):.6e}"}
        for p, taux in points
    ])
    _ecrire_csv(dossier / "donnees_materiel.csv", materiel)
    _ecrire_csv(dossier / "donnees_dac.csv", dac)
    _ecrire_csv(dossier / "donnees_gigue.csv", gigue)
    _ecrire_csv(dossier / "donnees_decoherence.csv", decoherence)
    _ecrire_csv(dossier / "donnees_decodeur.csv", decodeur)
    _ecrire_csv(dossier / "donnees_surface.csv", [
        {k: ("" if v is None else f"{v:.6g}" if isinstance(v, float) else v) for k, v in ligne.items()}
        for ligne in surface
    ])

    ecrire_svg_steane(dossier / "courbe_steane.svg", points)
    ecrire_svg_budget(dossier / "budget_materiel.svg", materiel[:-1])

    resume = {
        "version": VERSION,
        "horodatage_iso": _horodatage(),
        "source": {"fichier": Path(__file__).name, "sha256": empreinte_source()},
        "statut": {
            "code_et_preuves": "opérationnel (logiciel, calcul exact)",
            "simulation": "exacte pour le modèle de capacité de code, recoupée par Monte Carlo",
            "materiel": "modèle d'ingénierie paramétré, non mesuré",
            "qubit_physique": "non réalisé : aucun QPU, cryostat ou capteur physique",
            "reconnaissance_par_les_pairs": "non acquise : elle exige une revue externe indépendante",
        },
        "code": {
            "parametres": preuve["parametres"],
            "distance": preuve["distance"],
            "poids_minimal_logique": preuve["poids_minimal_operateur_logique"],
            "stabilisateurs_ok": preuve["stabilisateurs_ok"],
            "operateurs_logiques_ok": preuve["operateurs_logiques_ok"],
            "knill_laflamme_poids_2": preuve["knill_laflamme_poids_2"],
            "paulis_verifies": preuve["paulis_verifies_poids_max_2"],
            "correction_poids_1_ok": correction_ok,
            "corrections_poids_1_testees": nb_corrections,
        },
        "resultats": {
            "p_reference": p_reference,
            "taux_exact_p_reference": taux_reference,
            "taux_exacts": [
                {"p": p, "taux": taux_echec_depolarisant(p)} for p in (1e-4, 1e-3, 1e-2, 5e-2)
            ],
            "coefficient_quadratique": COEFFICIENT_QUADRATIQUE,
            "seuil_pseudo": seuil,
            "seuil_concatenation": (1.0 / COEFFICIENT_QUADRATIQUE) if COEFFICIENT_QUADRATIQUE > 0 else None,
            "monte_carlo_p_0_01": monte_carlo,
            "taux_exact_p_0_01": exact_mc,
            "recoupement_mc_ok": monte_carlo["ic95"][0] <= exact_mc <= monte_carlo["ic95"][1],
            "statistiques_par_poids": {
                str(w): {"motifs": total, "echecs": echecs}
                for w, (total, echecs) in STATS_DEPOLARISANT.items()
            },
        },
        "materiel": {
            "budget": materiel,
            "bits_dac_requis_pour_1e-4": bits_dac_requis(1e-4),
            "gigue_requise_pour_1e-4_s": gigue_requise(1e-4),
            "decodeur": decodeur,
        },
        "surface": {
            "modele": "P_L ≈ A (p/p_th)^((d+1)/2), A=0.1, p_th=1% (extrapolation, non simulée)",
            "lignes": surface,
        },
        "limites": [
            "Syndrômes supposés parfaits : pas d'erreurs de mesure ni de circuit de mesure.",
            "Décodeur CSS indépendant X/Z par table de syndrome minimale, non optimal.",
            "Le modèle matériel est une budgétisation analytique, pas une mesure.",
            "La projection du code de surface est une extrapolation paramétrée, pas une simulation.",
            "Aucune reconnaissance par les pairs ne peut être auto-attribuée.",
        ],
    }
    (dossier / "resume.json").write_text(json.dumps(resume, ensure_ascii=False, indent=2), encoding="utf-8")
    _ecrire_rapport_markdown(dossier / "rapport_qubit_logique.md", preuve, resume, materiel, dac, gigue, decoherence, decodeur, surface, points)
    return resume


def _ecrire_rapport_markdown(
    chemin: Path,
    preuve: dict,
    resume: dict,
    materiel: Sequence[dict],
    dac: Sequence[dict],
    gigue: Sequence[dict],
    decoherence: Sequence[dict],
    decodeur: Sequence[dict],
    surface: Sequence[dict],
    points: Sequence[tuple[float, float]],
) -> None:
    r = resume["resultats"]
    seuil = r["seuil_pseudo"]
    seuil_txt = f"{seuil:.6f}" if seuil is not None else "non atteint sous 0,5"
    lignes = [
        "# Qubit logique Al-Mizan — construction, preuve et résultats",
        "",
        f"Version {VERSION} — {resume['horodatage_iso']}",
        f"Source : `qubit_logique_mizan.py`, SHA-256 `{resume['source']['sha256']}`.",
        "",
        "## 0. Statut honnête",
        "",
        "| Élément | Statut |",
        "| :--- | :--- |",
        "| Code [[7,1,3]], stabilisateurs, distance, décodeur | **Opérationnel** (logiciel, calcul exact) |",
        "| Taux d'erreur logique | **Simulé exactement** pour le modèle de capacité de code, recoupé par Monte Carlo |",
        "| Budget DAC / horloge / 1/f / décodeur CMOS | **Modèle d'ingénierie** paramétré, non mesuré |",
        "| Qubit logique physique | **Non réalisé** : aucun QPU, cryostat ou capteur physique |",
        "| Reconnaissance par les pairs | **Non acquise** : elle exige une revue externe indépendante |",
        "",
        "Ce document ne prétend ni conscience, ni suprématie quantique, ni certification. Il fournit un objet mathématique vérifiable et des résultats reproductibles.",
        "",
        "## 1. Problème du qubit en équations",
        "",
        "### 1.1 État et évolution",
        "",
        "```text",
        "|ψ> = α|0> + β|1>,  |α|² + |β|² = 1",
        "ρ = |ψ><ψ|,  ρ† = ρ,  Tr ρ = 1,  ρ ≥ 0",
        "iħ dρ/dt = [H, ρ] + Σ_k (L_k ρ L_k† - ½{L_k†L_k, ρ})",
        "```",
        "",
        "### 1.2 Canaux de bruit",
        "",
        "```text",
        "Dépolarisant : ρ -> (1-p)ρ + (p/3)(XρX + YρY + ZρZ)",
        "Amplitude :    ρ -> E0ρE0† + E1ρE1†,  E0=[[1,0],[0,√(1-γ)]], E1=[[0,√γ],[0,0]]",
        "Phase :        ρ -> (1-λ)ρ + λ ZρZ",
        "T1 : relaxation ; T2 : cohérence ; 1/T2 = 1/(2T1) + 1/Tφ",
        "```",
        "",
        "### 1.3 Correction d'erreur",
        "",
        "```text",
        "Stabilisateurs : S_i|ψ> = |ψ>,  [S_i,S_j]=0",
        "Opérateurs logiques : L P = P L,  L ∉ <S_i>",
        "Distance : d = min_{L ≠ I} poids(L)",
        "Correction : t = floor((d-1)/2)",
        "Knill-Laflamme : P E_a† E_b P = C_ab P  pour poids(E_a), poids(E_b) ≤ t",
        "Seuil (modèle) : P_L ≈ A (p/p_th)^((d+1)/2),  p < p_th",
        "Concaténation : P_{k+1} = C P_k²,  p_th = 1/C",
        "```",
        "",
        "## 2. Construction du qubit logique [[7,1,3]]",
        "",
        "Matrice de contrôle du code de Hamming [7,4,3] :",
        "",
        "```text",
        "H =",
        "1 0 1 0 1 0 1",
        "0 1 1 0 0 1 1",
        "0 0 0 1 1 1 1",
        "```",
        "",
        "Les six stabilisateurs sont X(h) et Z(h) pour chaque ligne h de H. Les états logiques sont :",
        "",
        "```text",
        "|0>_L = (1/√8) Σ_{c ∈ C} |c>,   C = ker H  (16 mots de code)",
        "|1>_L = Z^{⊗7}|0>_L",
        "X_logique = Z^{⊗7}   (change |0>_L en |1>_L)",
        "Z_logique = X^{⊗7}   (valeurs +1/-1 sur |0>_L/|1>_L)",
        "```",
        "",
        "Cette convention est explicite : les rôles X/Z sont échangés par rapport à la notation habituelle, car |0>_L est ici l'état propre +1 de X^{⊗7}.",
        "",
        "### 2.1 Preuves calculées",
        "",
        "| Propriété | Résultat |",
        "| :--- | :--- |",
        f"| Paramètres | {preuve['parametres']} |",
        f"| Taille de C / C^⊥ | {preuve['dimension_espace_code']} / {preuve['dimension_dual']} |",
        f"| Opérateurs logiques distincts | {preuve['operateurs_logiques_distincts']} |",
        f"| Poids minimal logique | {preuve['poids_minimal_operateur_logique']} |",
        f"| Exemple de poids 3 | {preuve['exemple_operateur_poids_3']} |",
        f"| Pauli de poids ≤ 2 vérifiés | {preuve['paulis_verifies_poids_max_2']} |",
        f"| Knill-Laflamme (poids ≤ 2) | {'PASS' if preuve['knill_laflamme_poids_2'] else 'FAIL'} |",
        f"| Opérateur de poids 3 non trivial | {'OUI' if preuve['operateur_poids_3_non_trivial'] else 'NON'} |",
        f"| Distance | {preuve['distance']} |",
        f"| Stabilisateurs +1 | {'PASS' if preuve['stabilisateurs_ok'] else 'FAIL'} |",
        f"| Opérateurs logiques | {'PASS' if preuve['operateurs_logiques_ok'] else 'FAIL'} |",
        f"| Correction de tous les Pauli de poids 1 | {'PASS' if resume['code']['correction_poids_1_ok'] else 'FAIL'} ({resume['code']['corrections_poids_1_testees']} cas) |",
        "",
        "**Preuve de distance.** Tous les Pauli de poids ≤ 2 laissent la projection invariante à un scalaire près : aucune erreur de poids ≤ 2 n'implémente une opération logique. Un opérateur de poids 3 (par exemple 0000111) est logique et non trivial. Donc d = 3, et le code corrige exactement t = 1 erreur.",
        "",
        "## 3. Résultats exacts sous bruit dépolarisant",
        "",
        "Le décodeur applique la correction minimale de syndrome séparément aux composantes X et Z. L'énumération porte sur les 4⁷ = 16 384 motifs de Pauli, donc le taux est **exact** pour ce modèle, sans échantillonnage.",
        "",
        "| p | P_L exact |",
        "| :--- | :--- |",
    ]
    for entree in r["taux_exacts"]:
        lignes.append(f"| {entree['p']:.0e} | {entree['taux']:.6e} |")
    lignes += [
        "",
        f"- Coefficient quadratique : **{r['coefficient_quadratique']:.6f}** (P_L ≈ C p² à bas p).",
        f"- Seuil de pseudo-concaténation : **{seuil_txt}**.",
        f"- Monte Carlo à p = 0,01 : {r['monte_carlo_p_0_01']['taux']:.6e} (IC 95 % {r['monte_carlo_p_0_01']['ic95'][0]:.6e} – {r['monte_carlo_p_0_01']['ic95'][1]:.6e}), exact {r['taux_exact_p_0_01']:.6e} ; recoupement : {'OUI' if r['recoupement_mc_ok'] else 'NON'}.",
        "",
        "Répartition des échecs par poids (modèle dépolarisant) :",
        "",
        "| Poids | Motifs | Échecs |",
        "| :--- | :--- | :--- |",
    ]
    for poids_str, valeurs in r["statistiques_par_poids"].items():
        lignes.append(f"| {poids_str} | {valeurs['motifs']} | {valeurs['echecs']} |")
    lignes += [
        "",
        "Interprétation : les erreurs de poids 1 sont toutes corrigées ; les échecs commencent au poids 2, ce qui est cohérent avec d = 3. Le taux logique décroît comme p² à bas bruit, signature d'un vrai premier niveau de protection.",
        "",
        "## 4. Rôle du processeur et des transistors",
        "",
        "### 4.1 Équations du contrôle classique",
        "",
        "```text",
        "Pas du DAC : ΔV = V_FS / 2^n",
        "Erreur d'amplitude : ε = ΔV / V_pi",
        "Erreur de rotation : δθ = π ε",
        "Infidélité : 1-F ≈ sin²(δθ/2) ≈ (π ε / 2)²",
        "Gigue : δθ = Ω σ_t,  Ω = π/t_g,  1-F ≈ sin²(Ω σ_t/2)",
        "Bruit 1/f : σ_V² = A_V ln(f_max/f_min),  f_max = 1/(2 t_g)",
        "Décohérence : 1-F ≲ t_g/T2 + t_g/(3 T1)",
        "Décodeur : débit = (d²-1)/t_cycle,  latence < t_cycle,  P = α C V² f N",
        "```",
        "",
        "### 4.2 Budget de référence",
        "",
        "| Composant | Paramètre | Infidélité |",
        "| :--- | :--- | :--- |",
    ]
    for ligne in materiel:
        lignes.append(f"| {ligne['composant']} | {ligne['parametre']} | {_sci(ligne['infidelite'])} |")
    lignes += [
        "",
        f"- Bits DAC requis pour 10⁻⁴ : **{resume['materiel']['bits_dac_requis_pour_1e-4']}**.",
        f"- Gigue requise pour 10⁻⁴ : **{resume['materiel']['gigue_requise_pour_1e-4_s']*1e12:.1f} ps**.",
        "- Conclusion de ce budget : avec 12 bits et 10 ps, la décohérence domine ; le DAC devient le facteur limitant en dessous d'environ 10 bits.",
        "",
        "### 4.3 Décodeur classique",
        "",
        "| Distance | Qubits | Stabilisateurs | Débit (Mbit/s) | Cycles/bit à 3 GHz | Puissance (W) |",
        "| :--- | :--- | :--- | :--- | :--- | :--- |",
    ]
    for ligne in decodeur:
        lignes.append(
            f"| {ligne['distance']} | {ligne['qubits_physiques']} | {ligne['stabilisateurs']} | "
            f"{ligne['debit_syndrome_bits_s']/1e6:.1f} | {ligne['cycles_par_bit']:.2f} | {ligne['puissance_decodeur_w']:.3f} |"
        )
    lignes += [
        "",
        "Le processeur ne « pense » pas à la place du qubit : il échantillonne les syndromes, décode et applique les corrections dans le temps du cycle. Un débit insuffisant crée un retard de correction et annule le bénéfice du code.",
        "",
        "## 5. Projection vers le code de surface",
        "",
        "Modèle d'extrapolation, **non simulé** : P_L ≈ 0,1 (p/0,01)^((d+1)/2), avec un seuil de 1 % et une cible de 10⁻¹².",
        "",
        "| p | Distance requise | Qubits physiques | P_L projeté |",
        "| :--- | :--- | :--- | :--- |",
    ]
    for ligne in surface:
        if ligne["distance_requise"] is None:
            lignes.append(f"| {ligne['p']:.0e} | — | — | — |")
        else:
            lignes.append(
                f"| {ligne['p']:.0e} | {ligne['distance_requise']} | {ligne['qubits_physiques']} | {ligne['taux_projete']:.2e} |"
            )
    lignes += [
        "",
        "Cette projection sert au dimensionnement, pas à la preuve. Un vrai seuil de surface exige un simulateur circuit-level avec erreurs de mesure et un décodeur MWPM ou union-find validé.",
        "",
        "## 6. Reproduction",
        "",
        "```bash",
        "cd ASTRO-Q°ODE_SYSTEME",
        "py -3 qubit_logique_mizan.py --verifier",
        "py -3 qubit_logique_mizan.py --rapport",
        "py -3 -m unittest tests.test_qubit_logique_mizan -v",
        "```",
        "",
        f"Graine Monte Carlo : `{GRAINE_MONTE_CARLO}`. Les preuves et l'énumération exacte sont déterministes.",
        "",
        "## 7. Limites et reconnaissance par les pairs",
        "",
        "1. **Pas de qubit physique** : le module ne remplace ni un processeur quantique, ni un cryostat, ni une mesure.",
        "2. **Syndrômes parfaits** : les erreurs de mesure, de préparation et de porte ne sont pas simulées ici.",
        "3. **Décodeur sous-optimal** : la table de syndrome minimale est exacte pour le code de Steane, mais pas un décodeur optimal global.",
        "4. **Projection de surface** : extrapolation paramétrée, pas une simulation.",
        "5. **Reconnaissance** : un résultat n'est reconnu qu'après publication, reproduction indépendante et revue externe. Ce document fournit les éléments nécessaires, pas le statut.",
        "",
        "## 8. Fichiers produits",
        "",
        "- `resume.json` — synthèse machine.",
        "- `donnees_steane.csv`, `donnees_materiel.csv`, `donnees_dac.csv`, `donnees_gigue.csv`, `donnees_decoherence.csv`, `donnees_decodeur.csv`, `donnees_surface.csv`.",
        "- `courbe_steane.svg`, `budget_materiel.svg`.",
        "",
    ]
    chemin.write_text("\n".join(lignes), encoding="utf-8")


# ---------------------------------------------------------------------------
# 6. CLI
# ---------------------------------------------------------------------------

def _afficher_synthese() -> None:
    preuve = preuve_distance()
    correction_ok, nb = verifier_correction_poids_un()
    seuil = seuil_pseudo_depolarisant()
    print("Qubit logique Al-Mizan — code [[7,1,3]]")
    print(f"Stabilisateurs : {'PASS' if preuve['stabilisateurs_ok'] else 'FAIL'}")
    print(f"Opérateurs logiques : {'PASS' if preuve['operateurs_logiques_ok'] else 'FAIL'}")
    print(f"Knill-Laflamme poids <= 2 : {'PASS' if preuve['knill_laflamme_poids_2'] else 'FAIL'} ({preuve['paulis_verifies_poids_max_2']} Pauli)")
    print(f"Distance : {preuve['distance']} (min logique {preuve['poids_minimal_operateur_logique']})")
    print(f"Correction poids 1 : {'PASS' if correction_ok else 'FAIL'} ({nb} cas)")
    print(f"P_L(1e-3) = {taux_echec_depolarisant(1e-3):.6e}")
    print(f"Coefficient quadratique = {COEFFICIENT_QUADRATIQUE:.6f}")
    print(f"Seuil pseudo-concaténation = {seuil if seuil is None else f'{seuil:.6f}'}")
    print(f"Bits DAC requis (1e-4) = {bits_dac_requis(1e-4)}")
    print(f"Gigue requise (1e-4) = {gigue_requise(1e-4)*1e12:.1f} ps")


def main(argv: Sequence[str] | None = None) -> int:
    analyseur = argparse.ArgumentParser(description="Qubit logique [[7,1,3]] : preuves, simulation exacte et budget matériel.")
    analyseur.add_argument("--verifier", action="store_true", help="Exécute les preuves et retourne 0 si tout passe.")
    analyseur.add_argument("--rapport", action="store_true", help="Génère le rapport et les fichiers de résultats.")
    analyseur.add_argument("--sortie", default=str(DOSSIER_RESULTATS), help="Répertoire de sortie du rapport.")
    analyseur.add_argument("--p", type=float, default=1e-3, help="Probabilité physique pour l'affichage.")
    arguments = analyseur.parse_args(list(argv) if argv is not None else None)

    if arguments.rapport:
        resume = generer_rapport(arguments.sortie)
        print(f"Rapport généré dans {Path(arguments.sortie).resolve()}")
        print(json.dumps({
            "distance": resume["code"]["distance"],
            "knill_laflamme": resume["code"]["knill_laflamme_poids_2"],
            "taux_p_reference": resume["resultats"]["taux_exact_p_reference"],
            "seuil_pseudo": resume["resultats"]["seuil_pseudo"],
            "monte_carlo_ok": resume["resultats"]["recoupement_mc_ok"],
        }, ensure_ascii=False, indent=2))
        return 0

    if arguments.verifier:
        preuve = preuve_distance()
        correction_ok, nb = verifier_correction_poids_un()
        seuil = seuil_pseudo_depolarisant()
        controle = (
            preuve["stabilisateurs_ok"]
            and preuve["operateurs_logiques_ok"]
            and preuve["knill_laflamme_poids_2"]
            and preuve["distance"] == 3
            and correction_ok
            and seuil is not None
        )
        print("PASS" if controle else "FAIL")
        print(f"distance={preuve['distance']} poids_min={preuve['poids_minimal_operateur_logique']} "
              f"paulis={preuve['paulis_verifies_poids_max_2']} corrections={nb} "
              f"seuil={seuil if seuil is None else round(seuil, 6)}")
        return 0 if controle else 1

    if arguments.p:
        if not 0.0 <= arguments.p <= 1.0:
            print("p doit être dans [0, 1].", file=sys.stderr)
            return 2
    _afficher_synthese()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
