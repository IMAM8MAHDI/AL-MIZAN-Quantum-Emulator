# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2026 IMAM8MAHDI / Astro-Code Ecosystem
# SPDX-License-Identifier: GPL-3.0-only OR AGPL-3.0-only
"""Électricité et abondance énergétique — équations posées, résolues, contrôlées.

Source du parcours : « Électricité : tout s'éclaire ! | Déclics | ARTE »,
ARTE, 26 min 05 s, vidéo écrite par Pierre Lergenmüller (France, 2020),
identifiant YouTube cFx7Cm-c2nA. La page YouTube ne rend que du JavaScript
d'amorçage, la description ne porte aucun chapitre horodaté et timedtext
répond 200 avec 0 octet : le transcript est tenu pour absent. La vidéo
fournit le thème (de Thalès à Tesla) et une exigence pédagogique, pas des
citations. Aucune formule ci-dessous n'est présentée comme extraite de la
vidéo.

Ce que fait ce module : il pose les formules standard, de l'électrostatique à
l'électrotechnique, les calcule à partir des constantes SI, puis fait croiser
deux dérivations indépendantes par résultat (contrôles C01..C21).

Ce qu'il ne fait pas : il ne revendique aucun matériau « optimal », aucune
preuve d'abondance, aucune mesure instrumentale. Les chiffres de matériaux, de
rendement et de consommation mondiale sont des VALEURS DÉCLARÉES de littérature,
étiquetées SIMULÉ ou SPÉCIFIÉ avec leurs bornes. Deux bornes sont démontrées,
dans le cadre de leurs hypothèses : le plafond de Betz (16/27, disque actuator
idéal) et le rendement de Carnot (machine réversible).

Usage :
    py -3 ABONDANCE/electricite_abondance.py
"""

from __future__ import annotations

import cmath
import json
import math
import sys
from fractions import Fraction
from pathlib import Path
from typing import Any, Dict, List

RACINE = Path(__file__).resolve().parents[1]
if str(RACINE) not in sys.path:
    sys.path.insert(0, str(RACINE))

# ── Constantes SI exactes par définition, ou CODATA 2018 (incertaines) ──────
C = 299_792_458.0                    # vitesse de la lumière — exacte
E_CHARGE = 1.602_176_634e-19         # charge élémentaire — exacte
H_PLANCK = 6.626_070_15e-34          # constante de Planck — exacte
K_B = 1.380_649e-23                  # constante de Boltzmann — exacte
N_A = 6.022_140_76e23                # nombre d'Avogadro — exact
R_GAZ = N_A * K_B                    # 8,314462618… J/(mol·K), dérivé exact
MU0 = 1.256_637_062_12e-6            # perméabilité du vide — CODATA 2018
EPS0 = 8.854_187_8128e-12            # permittivité du vide — CODATA 2018
G0 = 9.806_65                        # acceleration normale — exacte (définition)
EV_J = E_CHARGE                      # 1 eV en joule — exact
L_SOLAIRE = 3.828e26                 # luminosité solaire — déclarée (IAU 2015)
AU = 1.495_978_707e11                # unité astronomique — exacte
RAYON_TERRE = 6.371e6                # rayon moyen — déclaré (IUGG)

# ── Valeurs de matériaux DÉCLARÉES (littérature/normes), non mesurées ici ────
RESISTIVITE_CU_PUR = 1.68e-8         # Ω·m à 20 °C, cuivre recuit très pur
RESISTIVITE_CU_IEC = 1.7241e-8       # Ω·m, norme du conducteur IEC
RESISTIVITE_AL = 2.65e-8             # Ω·m, aluminium 1350-H19 (conducteur)
DENSITE_ELECTRON_CU = 8.5e28         # électrons libres/m³, cuivre — déclaré
BANDE_GAP_SI = 1.12                  # eV, silicium indirect à 300 K
BANDE_GAP_GAAS = 1.42                # eV
BANDE_GAP_PEROVSKITE = 1.55          # eV, MAPbI3
BANDE_GAP_CDTE = 1.45                # eV
CAPACITE_LFP = 170.0                 # mAh/g théorique, LiFePO4
TENSION_LFP = 3.45                   # V vs Li, plateau moyen déclaré
CAPACITE_GRAPHITE = 372.0            # mAh/g théorique, C6
LHV_H2 = 120.0e6                     # J/kg, pouvoir calorifique inférieur
HHV_H2 = 141.8e6                     # J/kg, pouvoir calorifique supérieur
PCI_ESSENCE = 46.0e6                 # J/kg
TC_YBCO = 92.0                       # K — déclaré
TC_NBTI = 9.2                        # K — déclaré
RAPPORT_BCS = 3.53                   # 2Δ(0)/(k_B·Tc) — rapport déclaré

KWH_J = 3.6e6                        # 1 kW·h = 3,6 MJ exact
EV_NM = H_PLANCK * C / EV_J * 1e9    # 1239,841984… eV·nm, dérivé des exactes
CONSO_MONDIALE_W = 1.9e13            # ≈ 600 EJ/an primaire — déclarée

SOURCE = {
    "titre": "Électricité : tout s'éclaire ! | Déclics | ARTE",
    "chaine": "ARTE",
    "video_id": "cFx7Cm-c2nA",
    "url": "https://www.youtube.com/watch?v=cFx7Cm-c2nA",
    "duree_s": 1565,
    "auteur_scenario": "Pierre Lergenmüller (Points de repères)",
    "programme": "France, 2020, 26 mn",
    "chapitres_publics": 0,
    "transcript": "absent (timedtext : 0 octet en json3, srv3 et xml)",
    "mesure_le": "2026-11-08T16:56:27Z",
}

STATUTS = {
    "OPÉRATIONNEL": "formule standard, calcul exact reproductible",
    "SIMULÉ": "valeur ou scénario déclaré, explicité comme tel",
    "SPÉCIFIÉ": "posé ou analogie structurante, non évalué ici",
}


def _f(x: float, n: int = 6) -> str:
    return f"{x:,.{n}f}".replace(",", " ")


def _exp(x: float, n: int = 4) -> str:
    m, e = f"{x:.{n}e}".split("e")
    return f"{m} × 10^{int(e)}"


def _fa(x: float) -> str:
    return f"{x:.2f}"


# ============================================================================
# ÉQUATIONS
# ============================================================================

def coulomb() -> Dict[str, Any]:
    """EQ-01 — charge élémentaire et loi de Coulomb (de l'ambre frotté au newton)."""
    ke = 1.0 / (4.0 * math.pi * EPS0)
    ke_alt = MU0 * C * C / (4.0 * math.pi)
    return {
        "ke_m2_c2": ke,
        "ke_par_mu0_c2": ke_alt,
        "ecart_relatif": abs(ke - ke_alt) / ke,
        "electrons_par_coulomb": 1.0 / E_CHARGE,
        "force_entre_2x1C_a_1m_N": ke,
        "force_entre_electrons_a_1nm_N": ke * E_CHARGE**2 / 1e-18,
        "epsilon0": EPS0,
    }


def condensateur() -> Dict[str, Any]:
    """EQ-02 — champ, tension, capacité planaire et énergie du champ électrique."""
    surface, ecart, tension = 1.0, 1.0e-3, 1000.0
    cap = EPS0 * surface / ecart
    charge = cap * tension
    energie = 0.5 * cap * tension**2
    champ = tension / ecart
    volume = surface * ecart
    densite = 0.5 * EPS0 * champ**2
    return {
        "capacite_F": cap,
        "charge_C": charge,
        "tension_V": tension,
        "champ_V_m": champ,
        "energie_J": energie,
        "energie_par_QV_J": 0.5 * charge * tension,
        "densite_energetique_J_m3": densite,
        "energie_par_volume_J": densite * volume,
        "coherence": abs(energie - densite * volume) / energie,
    }


def ohm() -> Dict[str, Any]:
    """EQ-03 — courant, résistance géométrique et lenteur réelle des électrons."""
    longueur, section, courant = 1000.0, 10.0e-6, 50.0
    r_cu = RESISTIVITE_CU_PUR * longueur / section
    r_al = RESISTIVITE_AL * longueur / section
    derive = courant / (DENSITE_ELECTRON_CU * E_CHARGE * section)
    return {
        "longueur_m": longueur,
        "section_m2": section,
        "R_cu_ohm": r_cu,
        "R_cu_iec_ohm": RESISTIVITE_CU_IEC * longueur / section,
        "R_al_ohm": r_al,
        "ratio_al_sur_cu": r_al / r_cu,
        "conductivite_cu_S_m": 1.0 / RESISTIVITE_CU_PUR,
        "courant_A": courant,
        "derive_m_s": derive,
        "derive_mm_s": derive * 1e3,
        "distance_par_heure_m": derive * 3600.0,
        "vitesse_du_signal_m_s": C,
        "ratio_signal_sur_derive": C / derive,
    }


def puissance() -> Dict[str, Any]:
    """EQ-04 — puissance électrique, effet Joule et l'unité de facture."""
    u, i, r = 230.0, 10.0, 23.0
    p_ui, p_i2r, p_u2r = u * i, i * i * r, u * u / r
    ligne = 2500.0**2 * 0.05
    return {
        "U_V": u, "I_A": i, "R_ohm": r,
        "P_UI_W": p_ui, "P_I2R_W": p_i2r, "P_U2R_W": p_u2r,
        "ecart_max_W": max(abs(p_ui - p_i2r), abs(p_ui - p_u2r)),
        "kwh_en_j": KWH_J,
        "energie_1h_kWh": p_ui / 1000.0,
        "pertes_ligne_W": ligne,
        "pertes_ligne_kWh_par_heure": ligne / 1000.0,
    }


def kirchhoff() -> Dict[str, Any]:
    """EQ-05 — lois de Kirchhoff résolues en rationnels : zéro arrondi possible."""
    tension, r1, r2, r3 = Fraction(12), Fraction(1000), Fraction(2000), Fraction(3000)
    r_par = (r2 * r3) / (r2 + r3)
    r_tot = r1 + r_par
    i_tot = tension / r_tot
    u_par = i_tot * r_par
    i2, i3 = u_par / r2, u_par / r3
    somme_noeud = i_tot - i2 - i3
    chutes = {"R1": i_tot * i_tot * r1, "R2": i2 * i2 * r2, "R3": i3 * i3 * r3}
    bilan = tension * i_tot - sum(chutes.values())
    return {
        "I_total_A": float(i_tot),
        "I2_A": float(i2),
        "I3_A": float(i3),
        "U_parallelement_V": float(u_par),
        "R_total_ohm": float(r_tot),
        "R_parallelle_ohm": float(r_par),
        "somme_noeud_exacte": str(somme_noeud),
        "bilan_puissance_exact": str(bilan),
        "puissances_W": {k: float(v) for k, v in chutes.items()},
        "repartition_i2_sur_itotale": float(i2 / i_tot),
    }


def champ_fil() -> Dict[str, Any]:
    """EQ-06 — champ d'un fil infini : ce que l'ancienne définition de l'ampère disait."""
    courant, distance = 1.0, 1.0
    b = MU0 * courant / (2.0 * math.pi * distance)
    b_avant_2019 = 2.0e-7
    return {
        "B_T": b,
        "B_attendu_avant_2019_T": b_avant_2019,
        "ecart_relatif": abs(b - b_avant_2019) / b_avant_2019,
        "ecart_absolu_T": b - b_avant_2019,
        "force_par_metre_deux_fils_N_m": MU0 * courant * courant / (2.0 * math.pi * distance),
        "mu0": MU0,
        "mu0_historique_4pi_e_7": 4.0 * math.pi * 1e-7,
    }


def faraday() -> Dict[str, Any]:
    """EQ-07 — induction de Faraday–Lenz, du disque qui tourne à la tension."""
    spires, surface, champ, frequence = 100, 0.01, 1.0, 50.0
    omega = 2.0 * math.pi * frequence
    pic = spires * surface * champ * omega
    rms = pic / math.sqrt(2.0)
    pas, t0 = 1e-7, 0.123
    flux = lambda t: spires * champ * surface * math.cos(omega * t)
    num = (flux(t0 + pas) - flux(t0 - pas)) / (2.0 * pas)
    ana = -pic * math.sin(omega * t0)
    return {
        "omega_rad_s": omega,
        "f_em_pic_V": pic,
        "f_em_rms_V": rms,
        "ratio_rms_sur_pic": rms / pic,
        "derivation_numerique": num,
        "derivation_analytique": ana,
        "ecart_relatif_derivation": abs(num - ana) / max(abs(ana), 1e-12),
        "fil_mouvant_BLv_V": champ * 1.0 * 1.0,
        "sens_lenz": "le courant créé s'oppose à la variation (signe moins)",
    }


def inductance() -> Dict[str, Any]:
    """EQ-08 — énergie stockée dans un champ magnétique, densité des deux champs."""
    longueur, surface, spires, courant = 0.10, 1.0e-4, 500, 2.0
    L = MU0 * spires * spires * surface / longueur
    energie = 0.5 * L * courant**2
    b = MU0 * spires * courant / longueur
    volume = longueur * surface
    densite_b = b * b / (2.0 * MU0)
    champ_e = 1.0e6
    densite_e = 0.5 * EPS0 * champ_e**2
    return {
        "L_H": L,
        "energie_J": energie,
        "B_T": b,
        "densite_mag_J_m3": densite_b,
        "densite_elec_J_m3": densite_e,
        "coherence_volume": abs(densite_b * volume - energie) / energie,
        "ratio_mag_sur_elec": densite_b / densite_e,
    }


def ondes() -> Dict[str, Any]:
    """EQ-09 — Maxwell : l'éclair et la lumière ont la même vitesse."""
    v = 1.0 / math.sqrt(MU0 * EPS0)
    z0 = math.sqrt(MU0 / EPS0)
    z0_alt = MU0 * v
    return {
        "v_calculee_m_s": v,
        "v_exacte_c": C,
        "ecart_relatif": abs(v - C) / C,
        "z0_ohm": z0,
        "z0_par_mu0_v": z0_alt,
        "ecart_z0": abs(z0 - z0_alt) / z0,
        "E_sur_B_V_m_par_T": z0,
        "pression_radiation_pa_pour_1000W_m2": 1000.0 / C,
    }


def courant_alternatif() -> Dict[str, Any]:
    """EQ-10 — valeur efficace, facteur de puissance, triangle des puissances."""
    n = 200_001
    a, b, h = 0.0, 2.0 * math.pi, 2.0 * math.pi / (n - 1)
    s = sum((1.0 if k in (0, n - 1) else (4.0 if k % 2 else 2.0)) * math.sin(a + k * h) ** 2
            for k in range(n))
    aire = s * h / 3.0
    crete, phi, i_rms = 325.0, math.pi / 3.0, 10.0
    u_rms = crete / math.sqrt(2.0)
    p, q = u_rms * i_rms * math.cos(phi), u_rms * i_rms * math.sin(phi)
    sa = u_rms * i_rms
    return {
        "aire_sin2_sur_periode": aire,
        "aire_attendue_pi": math.pi,
        "ecart_relatif_aire": abs(aire - math.pi) / math.pi,
        "valeur_efficace_V": u_rms,
        "ratio_rms_sur_crete": u_rms / crete,
        "cos_phi": math.cos(phi),
        "P_W": p, "Q_var": q, "S_VA": sa,
        "ecart_triangle": abs(sa * sa - (p * p + q * q)) / (sa * sa),
        "courant_pour_meme_P_a_cos_phi_0_5_A": p / (u_rms * 0.5),
    }


def triphase() -> Dict[str, Any]:
    """EQ-11 — le choix de Tesla : trois phases, un champ qui tourne, √3 partout."""
    phase = lambda k: cmath.exp(-1j * 2.0 * math.pi * k / 3.0)
    u_phase, i_ligne = 230.0, 10.0
    somme = sum(phase(k) for k in range(3))
    compose = u_phase * (phase(0) - phase(1))
    u_ligne = abs(compose)
    p_trois = 3.0 * u_phase * i_ligne * math.cos(math.pi / 6.0)
    p_formule = math.sqrt(3.0) * u_ligne * i_ligne * math.cos(math.pi / 6.0)
    return {
        "somme_phasores": abs(somme),
        "U_composee_V": u_ligne,
        "ratio_ligne_sur_phase": u_ligne / u_phase,
        "racine_3": math.sqrt(3.0),
        "ecart_racine_3": abs(u_ligne / u_phase - math.sqrt(3.0)),
        "P_trois_fois_phase_W": p_trois,
        "P_formule_sqrt3_W": p_formule,
        "ecart_puissance": abs(p_trois - p_formule) / p_trois,
    }


def transformateur() -> Dict[str, Any]:
    """EQ-12 — monter la tension, baisser le courant : le rapport de spires."""
    u_p, u_s, apparent = 20_000.0, 400.0, 400e3
    spires_p = 2000
    spires_s = spires_p * u_s / u_p
    i_s, i_p = apparent / u_s, apparent / u_p
    r_enroulement, pertes_fer = 0.01, 800.0
    pertes_cuivre = i_s * i_s * r_enroulement
    return {
        "rapport_spires": spires_p / spires_s,
        "rapport_tensions": u_p / u_s,
        "spires_secondaire": spires_s,
        "I_secondaire_A": i_s,
        "I_primaire_A": i_p,
        "conservation_S": abs(u_p * i_p - u_s * i_s) / (u_p * i_p),
        "pertes_cuivre_W": pertes_cuivre,
        "pertes_fer_W_declarees": pertes_fer,
        "rendement": apparent / (apparent + pertes_cuivre + pertes_fer),
        "chute_relative": (pertes_cuivre + pertes_fer) / apparent,
    }


def transport_haute_tension() -> Dict[str, Any]:
    """EQ-13 — pourquoi on transporte à 400 kV plutôt qu'à 400 V."""
    p, r = 1.0e9, 0.05
    tensions = [400.0, 20_000.0, 400_000.0, 800_000.0]
    table = [{"U_V": u, "I_A": p / u, "pertes_W": (p / u) ** 2 * r,
              "pertes_pct": 100.0 * (p / u) ** 2 * r / p} for u in tensions]
    ratios = [t["pertes_W"] / table[0]["pertes_W"] for t in table]
    attendus = [(tensions[0] / t["U_V"]) ** 2 for t in table]
    return {
        "puissance_W": p,
        "resistance_ohm": r,
        "table": table,
        "ratios_pertes": ratios,
        "attendu_en_inverse_carre": attendus,
        "ecart_max": max(abs(a - b) / a for a, b in zip(ratios, attendus)),
        "gain_400V_vers_400kV": table[0]["pertes_W"] / table[2]["pertes_W"],
    }


def hydro() -> Dict[str, Any]:
    """EQ-14 — la chute d'eau devient puissance : le pont vers le dossier EAU."""
    rho, hauteur, debit, rendement = 1000.0, 100.0, 10.0, 0.90
    p = rho * G0 * debit * hauteur * rendement
    par_m3 = rho * G0 * hauteur
    return {
        "P_W": p,
        "P_MW": p / 1e6,
        "J_par_m3": par_m3,
        "kWh_par_m3": par_m3 / KWH_J,
        "masse_par_seconde_kg": rho * debit,
        "rendement_declare": rendement,
        "coherence_par_m3": abs(p - par_m3 * debit * rendement) / p,
    }


def betz() -> Dict[str, Any]:
    """EQ-15 — plafond de Betz : 16/27, consequence d'une conservation."""
    cp = lambda a: 4.0 * a * (1.0 - a) ** 2
    a_scan, cp_scan = 0.0, 0.0
    for k in range(1, 10_001):
        a = k / 20_000.0
        if cp(a) > cp_scan:
            a_scan, cp_scan = a, cp(a)
    lo, hi = 0.01, 0.9
    for _ in range(200):
        m = 0.5 * (lo + hi)
        if cp(m + 1e-9) - cp(m - 1e-9) > 0.0:
            lo = m
        else:
            hi = m
    a_star = 0.5 * (lo + hi)
    rho, surface, vent = 1.225, 50.0, 10.0
    dispo = 0.5 * rho * surface * vent**3
    return {
        "cp_max": cp(a_star),
        "a_max_bissection": a_star,
        "a_max_balayage": a_scan,
        "seize_sur_vingt_sept": 16.0 / 27.0,
        "ecart": abs(cp(a_star) - 16.0 / 27.0),
        "puissance_disponible_W": dispo,
        "puissance_max_capturable_W": dispo * cp(a_star),
        "derivee_nulle_en_a_star": abs(4.0 * (1.0 - a_star) * (1.0 - 3.0 * a_star)),
    }


def carnot() -> Dict[str, Any]:
    """EQ-16 — la chaleur a un plafond, et il ne dépend que des deux températures."""
    source, froid = 800.0, 300.0
    ideal = 1.0 - froid / source
    declares = {"vapeur supercritique": 0.45, "cycle combine gaz": 0.61,
                "diesel automobile": 0.35, "solaire thermodynamique": 0.30}
    return {
        "T_source_K": source, "T_froid_K": froid,
        "eta_carnot": ideal,
        "fraction_rejetee_au_froid": froid / source,
        "somme_eta_plus_rejet": ideal + froid / source,
        "rendements_declares": declares,
        "meilleur_declare": max(declares.values()),
        "ratio_meilleur_sur_carnot": max(declares.values()) / ideal,
    }


def photovoltaique() -> Dict[str, Any]:
    """EQ-17 — seuil spectral d'un semi-conducteur et part perdue en chaleur."""
    seuil = lambda ev: EV_NM / ev
    e_deux_eg = 2.0 * BANDE_GAP_SI
    photons_par_m2_s = 1000.0 / (1.5 * EV_J)
    return {
        "constante_eV_nm": EV_NM,
        "lambda_seuil_si_nm": seuil(BANDE_GAP_SI),
        "lambda_seuil_gaas_nm": seuil(BANDE_GAP_GAAS),
        "lambda_seuil_perovskite_nm": seuil(BANDE_GAP_PEROVSKITE),
        "lambda_seuil_cdte_nm": seuil(BANDE_GAP_CDTE),
        "retour_calcul": abs(seuil(seuil(BANDE_GAP_SI)) - BANDE_GAP_SI),
        "perte_thermalisation_photon_2Eg": (e_deux_eg - BANDE_GAP_SI) / e_deux_eg,
        "photons_par_m2_s_pour_1000W_m2_a_1e5_eV": photons_par_m2_s,
        "rendement_shockley_queisser_declare": 0.337,
        "conditions_declarees": "AM1.5G, 1000 W/m², 25 °C — valeur de littérature",
    }


def stockage_materiau() -> Dict[str, Any]:
    """EQ-18 — mettre toutes les densités d'énergie sur la même échelle."""
    wh = lambda j_par_kg: j_par_kg / 3600.0
    cathode = TENSION_LFP * CAPACITE_LFP          # V × mAh/g = mWh/g = Wh/kg
    bareme_wh_kg = {
        "LiFePO4 materiau actif (theorique)": cathode,
        "graphite materiau actif (theorique)": 0.1 * CAPACITE_GRAPHITE,
        "cellule Li-ion (declaree)": 250.0,
        "accumulateur plomb (declare)": 35.0,
        "supercondensateur (declare)": 10.0,
        "essence PCI": wh(PCI_ESSENCE),
        "dihydrogene LHV": wh(LHV_H2),
        "stockage gravitaire 100 m": wh(G0 * 100.0),
    }
    return {
        "Wh_par_kg": bareme_wh_kg,
        "kWh_par_kg": {k: v / 1000.0 for k, v in bareme_wh_kg.items()},
        "cathode_LFP_Wh_kg": cathode,
        "hydrogene_sur_essence": LHV_H2 / PCI_ESSENCE,
        "equivalence_J_par_kg": {k: v * 3600.0 for k, v in bareme_wh_kg.items()},
        "LHV_H2_sur_HHV": LHV_H2 / HHV_H2,
        "gravitaire_J_par_kg": G0 * 100.0,
    }


def supraconductivite() -> Dict[str, Any]:
    """EQ-19 — résistance nulle : ce que ça supprime, ce que ça n'enlève pas."""
    k_ev = K_B / EV_J
    gap = lambda tc: 0.5 * RAPPORT_BCS * k_ev * tc * 1e3
    ligne = RESISTIVITE_CU_PUR * 1000.0 / 10.0e-6
    return {
        "k_B_eV_K": k_ev,
        "gap_nbti_meV": gap(TC_NBTI),
        "gap_ybco_meV": gap(TC_YBCO),
        "rapport_verifie": 2.0 * gap(TC_NBTI) / (k_ev * TC_NBTI * 1e3),
        "rapport_declare": RAPPORT_BCS,
        "pertes_cuivre_W_pour_50A_sur_1km": 50.0**2 * ligne,
        "pertes_ohmiques_supra_W": 0.0,
        "refrigerants_declares_K": {"NbTi (LHe)": 4.2, "YBCO (LN2)": 77.0},
        "champ_critique_T_declare": {"NbTi": 14.5, "YBCO": 100.0},
    }


def budget_solaire_terre() -> Dict[str, Any]:
    """EQ-20 — l'ordre de grandeur qui rend le mot « abondance » chiffrable."""
    flux = L_SOLAIRE / (4.0 * math.pi * AU**2)
    section = math.pi * RAYON_TERRE**2
    interceptee = flux * section
    ratio = interceptee / CONSO_MONDIALE_W
    surface_20tw = 20e12 / (0.22 * flux)
    return {
        "irradiance_hors_atmosphere_W_m2": flux,
        "constante_solaire_declaree_W_m2": 1361.0,
        "ecart_relatif": abs(flux - 1361.0) / 1361.0,
        "section_terre_m2": section,
        "puissance_interceptee_W": interceptee,
        "consommation_mondiale_declaree_W": CONSO_MONDIALE_W,
        "ratio_interceptee_sur_consommee": ratio,
        "surface_utile_m2_pour_20TW_a_22pct": surface_20tw,
        "surface_utile_km2": surface_20tw / 1e6,
        "surface_emergee_km2_declaree": 1.49e8,
        "fraction_des_terres_emergees": surface_20tw / 1e6 / 1.49e8,
        "kWh_par_m2_an_pour_200W_m2_moyen": 200.0 * 8.76,
    }


# ============================================================================
# ASSEMBLAGE
# ============================================================================

def ponts_dossier() -> List[Dict[str, str]]:
    """EQ-21 — grille de lecture du dossier AL-MIZAN appliquée à la chaîne électrique.

    Ces quatre lignes sont des analogies structurelles déclarées. Elles
    organisent la lecture ; elles n'établissent aucune identité entre la
    physique de l'énergie et le socle de sécurité du dossier.
    """
    return [
        {"pilier": "P1 — Scellement (preuve attachée à la valeur)",
         "dossier": "chaque équation porte son contrôle C01..C21",
         "electricite": "une grandeur non contrôlée n'entre pas dans le tableau",
         "limite": "un contrôle numérique ne vaut pas mesure instrumentale"},
        {"pilier": "P2 — Horloge (rythme borné, tick macroscopique)",
         "dossier": "50 Hz, période 20 ms exactement",
         "electricite": "fréquence réseau = horloge des machines synchrones",
         "limite": "analogie de rythme : aucune horloge quantique n'intervient"},
        {"pilier": "P3 — Code correcteur (redondance qui tolère la panne)",
         "dossier": "Steane [[7,1,3]], 21 corrections",
         "electricite": "redondance N-1 des réseaux et protections sélectives",
         "limite": "même mot, deux objets différents : information vs kilowatts"},
        {"pilier": "P4 — Registre (ce qui est dû, à qui, quand)",
         "dossier": "registre des équations et traçabilité des DOI",
         "electricite": "compteurs, facturation, attribution des prédécesseurs",
         "limite": "le registre décrit une convention, pas une loi physique"},
    ]


def _eq(id_: str, chemin: str, formule: str, resultat: str, statut: str,
        detail: Any, limite: str = "") -> Dict[str, Any]:
    return {"id": id_, "chemin": chemin, "formule": formule,
            "resultat": resultat, "statut": statut, "limite": limite, "detail": detail}


def resoudre() -> Dict[str, Any]:
    cq, cd, oh, pu, ki = coulomb(), condensateur(), ohm(), puissance(), kirchhoff()
    ch, fa, in_, on, ca = champ_fil(), faraday(), inductance(), ondes(), courant_alternatif()
    tr, tf, ht, hy, bz = triphase(), transformateur(), transport_haute_tension(), hydro(), betz()
    car, pv, st, su, bs = carnot(), photovoltaique(), stockage_materiau(), \
        supraconductivite(), budget_solaire_terre()
    po = ponts_dossier()

    eqs = [
        _eq("EQ-01", "electricite_abondance.py → coulomb() → C01",
            "F = q₁q₂/(4π ε₀ r²) ;  k = 1/(4πε₀) = μ₀c²/4π ;  1 C = 1/e",
            f"k = {_exp(cq['ke_m2_c2'])} N·m²/C² · 1 C = {_exp(cq['electrons_par_coulomb'])} e · "
            f"2 × 1 C à 1 m : {_exp(cq['force_entre_2x1C_a_1m_N'])} N",
            "OPÉRATIONNEL", cq,
            limite="l'accord des deux écritures de k éprouve la cohérence des constantes "
                   "déclarées, non un équilibre de forces mesuré ; deux charges de 1 C tenues "
                   "à 1 m sont une expérience de pensée : aucun électromètre n'a pesé ce newton"),
        _eq("EQ-02", "electricite_abondance.py → condensateur() → C02",
            "E = U/d ;  C = ε₀S/d ;  W = ½CU² = ½QU = ½ε₀E²·(Sd)",
            f"C(1 m², 1 mm) = {_f(cd['capacite_F'], 12)} F · W à 1 kV = {_f(cd['energie_J'], 4)} J",
            "OPÉRATIONNEL", cd,
            limite="C = ε₀S/d s'écrit pour des armatures infinies : aucun condensateur réel "
                   "n'échappe aux effets de bord, et le diélectrique est absent d'ici ; 1 m², "
                   "1 mm, 1 kV sont des entrées choisies pour faire parler la formule"),
        _eq("EQ-03", "electricite_abondance.py → ohm() → C03",
            "R = ρ·ℓ/S ;  σ = 1/ρ ;  v_dérive = I/(n·e·S)",
            f"1 km sous 10 mm² : Cu {_f(oh['R_cu_ohm'], 3)} Ω, Al {_f(oh['R_al_ohm'], 3)} Ω · "
            f"dérive {_f(oh['derive_mm_s'], 4)} mm/s",
            "OPÉRATIONNEL", oh,
            limite="résistivités et densité d'électrons libres se lisent dans une table "
                   "déclarée à 20 °C : un conducteur réel varie en température et en état "
                   "métallurgique ; la vitesse de dérive est une moyenne de modèle, personne "
                   "n'a suivi les électrons sur un mètre"),
        _eq("EQ-04", "electricite_abondance.py → puissance() → C04",
            "P = UI = I²R = U²/R ;  1 kW·h = 3,6 MJ",
            f"230 V × 10 A = {_f(pu['P_UI_W'], 1)} W · trois écritures à "
            f"{pu['ecart_max_W']:.2e} W près",
            "OPÉRATIONNEL", pu,
            limite="les trois écritures coïncident parce que U, I et R ont été choisis pour "
                   "satisfaire R = U/I : identité algébrique pour charge purement résistive, "
                   "muette sur tout appareil branché ; les 2 500 A et 0,05 Ω des pertes ligne "
                   "sont des scénarios écrits dans la fonction"),
        _eq("EQ-05", "electricite_abondance.py → kirchhoff() → C05",
            "ΣI(nœud) = 0 ;  ΣU(maille) = 0 ;  résolution en rationnels",
            f"I = {ki['I_total_A']:.6f} A · nœud {ki['somme_noeud_exacte']} · "
            f"bilan {ki['bilan_puissance_exact']} (exact, sans arrondi)",
            "OPÉRATIONNEL", ki,
            limite="les deux zéros sont une clôture du modèle résolu en fractions exactes : "
                   "la source de 12 V est déclarée sans résistance interne, les capacités "
                   "parasites n'existent pas ici ; l'arithmétique garantit la résolution, pas "
                   "l'existence d'un montage"),
        _eq("EQ-06", "electricite_abondance.py → champ_fil() → C06",
            "B = μ₀I/(2πr) ;  F/ℓ = μ₀I₁I₂/(2πd)",
            f"B(1 A, 1 m) = {_exp(ch['B_T'], 11)} T · écart relatif à 2·10⁻⁷ = "
            f"{_exp(ch['ecart_relatif'], 2)}",
            "OPÉRATIONNEL", ch,
            limite="le fil infini est une fiction de calcul : une ligne réelle a un retour et "
                   "une fin ; l'écart à 2·10⁻⁷ T mesure la dérive de μ₀ après la réforme de "
                   "2019, non le champ produit par un ampère quelconque"),
        _eq("EQ-07", "electricite_abondance.py → faraday() → C07",
            "ℰ = −N·dΦ/dt ;  Φ = B·S·cos(ωt) ;  ℰ_rms = N·B·S·ω/√2",
            f"100 spires à 50 Hz : crête {_fa(fa['f_em_pic_V'])} V, rms {_fa(fa['f_em_rms_V'])} V",
            "OPÉRATIONNEL", fa,
            limite="flux sinusoïdal déclaré, 1 T sans saturation, 100 spires et 0,01 m² "
                   "choisies : l'accord numérique/analytique teste une chaîne de dérivation, "
                   "pas une machine ; le rapport au pic ne vaut que pour la sinusoïde pure "
                   "qu'aucun alternateur réel ne fournit"),
        _eq("EQ-08", "electricite_abondance.py → inductance() → C08",
            "L = μ₀N²S/ℓ ;  W = ½LI² ;  u_B = B²/(2μ₀) ;  u_E = ½ε₀E²",
            f"L = {_f(in_['L_H'], 9)} H · W = {_f(in_['energie_J'], 6)} J · "
            f"u_B/u_E = {_exp(in_['ratio_mag_sur_elec'], 2)}",
            "OPÉRATIONNEL", in_,
            limite="le solénoïde long ignore fuites et circuit magnétique dans une géométrie "
                   "déclarée ; u_B/u_E compare deux intensités posées sans lien, 2 A et "
                   "10⁶ V/m : confrontation de formules, non de deux états d'un même "
                   "composant"),
        _eq("EQ-09", "electricite_abondance.py → ondes() → C09",
            "c = 1/√(μ₀ε₀) ;  Z₀ = √(μ₀/ε₀) = μ₀c ;  E/B = c",
            f"c calculée = {_exp(on['v_calculee_m_s'], 9)} m/s · Z₀ = {_f(on['z0_ohm'], 4)} Ω",
            "OPÉRATIONNEL", on,
            limite="depuis 2019 ε₀ se déduit de μ₀ et de c : 1/√(μ₀ε₀) = c est une identité "
                   "du SI vérifiée par les déclarations, non par la lumière ; l'onde plane "
                   "dans le vide ne dit rien d'une onde guidée par une ligne réelle"),
        _eq("EQ-10", "electricite_abondance.py → courant_alternatif() → C10",
            "U_rms = Û/√2 ;  P = UI·cos φ ;  S² = P² + Q²",
            f"325 V crête → {_fa(ca['valeur_efficace_V'])} V · cos 60° = {ca['cos_phi']:.6f} · "
            f"P = {_fa(ca['P_W'])} W sur {(_fa(ca['S_VA']))} VA",
            "OPÉRATIONNEL", ca,
            limite="π ici contrôle une intégration numérique de sin², pas une période relevée "
                   "en poste ; le triangle des puissances se ferme pour tout φ sur une "
                   "sinusoïde pure déclarée, et 60° est choisi — aucune charge industrielle "
                   "ne fournit ce déphasage"),
        _eq("EQ-11", "electricite_abondance.py → triphase() → C11",
            "U_ligne = √3·U_phase ;  Σ phasores = 0 ;  P = √3·U_L·I_L·cos φ",
            f"√3 = {tr['racine_3']:.12f} · somme = {tr['somme_phasores']:.1e} · "
            f"230 V → {_fa(tr['U_composee_V'])} V",
            "OPÉRATIONNEL", tr,
            limite="la somme des phasores ne s'annule que pour trois phases rigoureusement "
                   "égales et décalées de 120° exactement : le déséquilibre d'un réseau réel "
                   "reste hors modèle ; √3 est une identité trigonométrique et 230 V une "
                   "tension de lecture, pas relevée ici"),
        _eq("EQ-12", "electricite_abondance.py → transformateur() → C12",
            "U₂/U₁ = N₂/N₁ ;  I₂/I₁ = N₁/N₂ ;  S = UI conservée",
            f"20 kV → 400 V : I₂ = {_fa(tf['I_secondaire_A'])} A · rendement "
            f"{100 * tf['rendement']:.2f} % avec pertes déclarées",
            "SIMULÉ", tf,
            limite="rapport de spires et conservation de S sont des propriétés du "
                   "transformateur idéal : pas de courant aimantant, pas de fuites ; le "
                   "rendement divise par des pertes déclarées (0,01 Ω d'enroulement, 800 W "
                   "de fer) — un scénario de table, pas un essai de banc"),
        _eq("EQ-13", "electricite_abondance.py → transport_haute_tension() → C13",
            "P_pertes = (P/U)²·R  ⇒  pertes ∝ 1/U²",
            f"1 GW : 400 V → {_exp(ht['table'][0]['pertes_W'], 2)} W · 400 kV → "
            f"{_exp(ht['table'][2]['pertes_W'], 2)} W · facteur {_exp(ht['gain_400V_vers_400kV'], 1)}",
            "OPÉRATIONNEL", ht,
            limite="la loi en 1/U² est une identité du modèle pour une résistance unique "
                   "déclarée de 0,05 Ω quel que soit le trajet : ni effet couronne, ni "
                   "réactif, ni température ; le facteur 10⁶ confronte deux scénarios "
                   "arithmétiques, non deux réseaux existants"),
        _eq("EQ-14", "electricite_abondance.py → hydro() → C14",
            "P = ρ·g·Q·H·η ;  e = ρ·g·H (par m³)",
            f"100 m, 10 m³/s, η = 0,90 → {_f(hy['P_MW'], 2)} MW · "
            f"{hy['kWh_par_m3']:.4f} kWh/m³",
            "OPÉRATIONNEL", hy,
            limite="P = ρgQHη vaut pour une chute d'eau posée une fois pour toutes : 100 m, "
                   "10 m³/s et surtout η = 0,90 sont des entrées déclarées ; ni turbine, ni "
                   "conduite forcée, ni étiage n'entrent ici, et le module ne promet aucune "
                   "centrale"),
        _eq("EQ-15", "electricite_abondance.py → betz() → C15",
            "C_P(a) = 4a(1−a)² ;  a* = 1/3 ;  C_P,max = 16/27",
            f"C_P,max = {bz['cp_max']:.9f} · 16/27 = {bz['seize_sur_vingt_sept']:.9f} · "
            f"a* = {bz['a_max_bissection']:.9f}",
            "OPÉRATIONNEL", bz,
            limite="le disque actuator est un modèle déclaré : fluide incompressible, poussée "
                   "uniforme, sillage sans rotation ; 16/27 borne ce modèle seulement — une "
                   "machine réelle est sous 16/27, et cette équation ne dit rien de la "
                   "distance"),
        _eq("EQ-16", "electricite_abondance.py → carnot() → C16",
            "η ≤ 1 − T_froid/T_source ;  rejet = T_froid/T_source",
            f"800 K / 300 K → {100 * car['eta_carnot']:.2f} % · meilleur rendement déclaré à "
            f"{100 * car['ratio_meilleur_sur_carnot']:.1f} % du plafond",
            "OPÉRATIONNEL", car,
            limite="Carnot borne les machines réversibles entre deux températures choisies "
                   "comme entrées, 800 K et 300 K : le rapport aux quatre rendements de la "
                   "table compare des déclarations à un théorème et ne mesure aucune "
                   "chaufferie"),
        _eq("EQ-17", "electricite_abondance.py → photovoltaique() → C17",
            "λ_seuil = hc/E_g ;  perte = (E_photon − E_g)/E_photon",
            f"Si 1,12 eV → {pv['lambda_seuil_si_nm']:.1f} nm · un photon à 2E_g perd "
            f"{100 * pv['perte_thermalisation_photon_2Eg']:.0f} %",
            "OPÉRATIONNEL", pv,
            limite="les longueurs d'onde seuil convertissent des gaps déclarés pour des "
                   "cristaux parfaits à 300 K : ni impuretés, ni désordre de bande ; la "
                   "thermalisation est comptée photon par photon sans spectre ni "
                   "recombinaison, et les 33,7 % de littérature sont rappelés, non démontrés"),
        _eq("EQ-18", "electricite_abondance.py → stockage_materiau() → C18",
            "e = U·capacité (Wh/kg) ;  Wh = J/3600 ;  gravitaire = g·h",
            f"LiFePO₄ actif {st['cathode_LFP_Wh_kg']:.0f} Wh/kg · H₂ LHV "
            f"{_f(st['kWh_par_kg']['dihydrogene LHV'], 2)} kWh/kg · 100 m d'eau "
            f"{st['Wh_par_kg']['stockage gravitaire 100 m']:.3f} Wh/kg",
            "SIMULÉ", st,
            limite="l'échelle classe des matériaux actifs à leur capacité théorique : "
                   "collecteurs, électrolyte, boîtier, température et vieillissement ne "
                   "pèsent pas ici ; les 250 Wh/kg de cellule comme les 35 du plomb sont des "
                   "ordres de grandeur déclarés, sans promesse sur un pack commercial"),
        _eq("EQ-19", "electricite_abondance.py → supraconductivite() → C19",
            "2Δ(0)/(k_B·T_c) ≈ 3,53 (déclaré) ;  R = 0 ⇒ pertes ohmiques nulles",
            f"NbTi Δ = {su['gap_nbti_meV']:.3f} meV · rapport recalculé "
            f"{su['rapport_verifie']:.3f} · 1 km de Cu à 50 A : "
            f"{_fa(su['pertes_cuivre_W_pour_50A_sur_1km'])} W",
            "SIMULÉ", su,
            limite="le rapport 3,53 est une valeur de modèle BCS déclarée puis reproduite par "
                   "calcul : C19 vérifie que l'arithmétique rend ce qu'on lui a prêté ; le "
                   "zéro des pertes ohmiques est la définition de l'état supraconducteur, non "
                   "une performance relevée, et aucun cryostat ne vient consommer le gain"),
        _eq("EQ-20", "electricite_abondance.py → budget_solaire_terre() → C20",
            "Φ = L☉/(4π·AU²) ;  P interceptée = Φ·πR⊕² ;  S = P/(η·Φ)",
            f"Φ = {_fa(bs['irradiance_hors_atmosphere_W_m2'])} W/m² · interceptée = "
            f"{_exp(bs['puissance_interceptee_W'], 3)} W = {bs['ratio_interceptee_sur_consommee']:.0f}× "
            f"la consommation déclarée",
            "SIMULÉ", bs,
            limite="L☉, rayon terrestre, 1,9·10¹³ W de consommation et 22 % de rendement sont "
                   "quatre déclarations : le rapport est une confrontation de tables, pas un "
                   "gisement ; ni la nuit, ni les nuages, ni le foncier, ni les calendriers "
                   "n'entrent dans une surface calculée en soleil de midi"),
        _eq("EQ-21", "electricite_abondance.py → ponts_dossier() → C21",
            "P1 ↔ contrôle · P2 ↔ 50 Hz · P3 ↔ redondance N-1 · P4 ↔ comptage",
            "4 ponts déclarés comme analogies de lecture, chacun avec sa limite",
            "SPÉCIFIÉ", po,
            limite="ces quatre lignes rangent la lecture, n'affermissent aucune identité : le "
                   "50 Hz n'est pas une horloge quantique et la redondance réseau n'est pas "
                   "un code correcteur sur les kilowatts ; chaque pont porte déjà sa limite "
                   "interne, celle-ci rappelle qu'aucun pont n'est un résultat"),
    ]

    controles = [
        {"id": "C01", "nom": "k = 1/(4πε₀) coïncide avec μ₀c²/4π",
         "attendu": _exp(cq["ke_par_mu0_c2"]), "obtenu": _exp(cq["ke_m2_c2"]),
         "ok": cq["ecart_relatif"] < 1e-9},
        {"id": "C02", "nom": "½CU² = ½ε₀E²·volume = ½QU",
         "attendu": "0.000000000000", "obtenu": f"{cd['coherence']:.12f}",
         "ok": cd["coherence"] < 1e-12 and abs(cd["energie_J"] - cd["energie_par_QV_J"]) < 1e-12},
        {"id": "C03", "nom": "ρσ = 1 et R(Al)/R(Cu) ≈ 1,58",
         "attendu": "1.000000000000", "obtenu":
         f"{oh['conductivite_cu_S_m'] * RESISTIVITE_CU_PUR:.12f}",
         "ok": abs(oh["conductivite_cu_S_m"] * RESISTIVITE_CU_PUR - 1.0) < 1e-12
         and 1.5 < oh["ratio_al_sur_cu"] < 1.7},
        {"id": "C04", "nom": "P = UI = I²R = U²/R et 1 kW·h = 3,6 MJ",
         "attendu": "2300.000000", "obtenu": _f(pu["P_I2R_W"], 6),
         "ok": pu["ecart_max_W"] < 1e-9 and pu["kwh_en_j"] == 3.6e6},
        {"id": "C05", "nom": "nœud et bilan de puissance exacts (rationnels)",
         "attendu": "0 / 0", "obtenu": f"{ki['somme_noeud_exacte']} / {ki['bilan_puissance_exact']}",
         "ok": ki["somme_noeud_exacte"] == "0" and ki["bilan_puissance_exact"] == "0"},
        {"id": "C06", "nom": "B(1 A, 1 m) à 10⁻⁸ près de 2·10⁻⁷ T",
         "attendu": "< 1e-8", "obtenu": _exp(ch["ecart_relatif"], 3),
         "ok": ch["ecart_relatif"] < 1e-8 and ch["force_par_metre_deux_fils_N_m"] < 2.000001e-7},
        {"id": "C07", "nom": "dΦ/dt numérique contre analytique",
         "attendu": "< 1e-6", "obtenu": _exp(fa["ecart_relatif_derivation"], 2),
         "ok": fa["ecart_relatif_derivation"] < 1e-6
         and abs(fa["ratio_rms_sur_pic"] - 1.0 / math.sqrt(2.0)) < 1e-12},
        {"id": "C08", "nom": "½LI² = u_B·volume",
         "attendu": "0.000000000000", "obtenu": f"{in_['coherence_volume']:.12f}",
         "ok": in_["coherence_volume"] < 1e-12},
        {"id": "C09", "nom": "1/√(μ₀ε₀) = c et Z₀ = μ₀c",
         "attendu": _f(C, 3), "obtenu": _f(on["v_calculee_m_s"], 3),
         "ok": on["ecart_relatif"] < 1e-9 and on["ecart_z0"] < 1e-9},
        {"id": "C10", "nom": "∮sin² = π et S² = P² + Q²",
         "attendu": f"{math.pi:.9f}", "obtenu": f"{ca['aire_sin2_sur_periode']:.9f}",
         "ok": ca["ecart_relatif_aire"] < 1e-10 and ca["ecart_triangle"] < 1e-12},
        {"id": "C11", "nom": "déphasage de 120° ⇒ √3 et somme nulle",
         "attendu": "0.000000000000", "obtenu": f"{tr['ecart_racine_3']:.12e}",
         "ok": tr["ecart_racine_3"] < 1e-12 and tr["somme_phasores"] < 1e-14
         and tr["ecart_puissance"] < 1e-12},
        {"id": "C12", "nom": "S primaire = S secondaire (transformateur idéal)",
         "attendu": "0.000000000000", "obtenu": f"{tf['conservation_S']:.12f}",
         "ok": tf["conservation_S"] < 1e-12
         and abs(tf["rapport_tensions"] - tf["rapport_spires"]) < 1e-9},
        {"id": "C13", "nom": "pertes en 1/U² sur quatre tensions",
         "attendu": "0.000000000000", "obtenu": f"{ht['ecart_max']:.12e}",
         "ok": ht["ecart_max"] < 1e-12 and ht["gain_400V_vers_400kV"] > 2e5},
        {"id": "C14", "nom": "P = ρgQHη cohérent avec (ρgH)·Q·η",
         "attendu": "0.000000000000", "obtenu": f"{hy['coherence_par_m3']:.12f}",
         "ok": hy["coherence_par_m3"] < 1e-12 and 0.25 < hy["kWh_par_m3"] < 0.30},
        {"id": "C15", "nom": "max 4a(1−a)² = 16/27 à a = 1/3",
         "attendu": f"{16 / 27:.9f}", "obtenu": f"{bz['cp_max']:.9f}",
         "ok": bz["ecart"] < 1e-9 and abs(bz["a_max_bissection"] - 1 / 3) < 1e-6
         and bz["derivee_nulle_en_a_star"] < 1e-6},
        {"id": "C16", "nom": "η + rejet = 1 exactement",
         "attendu": "1.000000000000", "obtenu": f"{car['somme_eta_plus_rejet']:.12f}",
         "ok": abs(car["somme_eta_plus_rejet"] - 1.0) < 1e-12 and car["eta_carnot"] == 0.625},
        {"id": "C17", "nom": "hc/e = 1239,841984 eV·nm et seuil Si ≈ 1107 nm",
         "attendu": "1239.841984", "obtenu": f"{pv['constante_eV_nm']:.6f}",
         "ok": abs(pv["constante_eV_nm"] - 1239.841984) < 1e-6
         and 1100.0 < pv["lambda_seuil_si_nm"] < 1115.0
         and abs(pv["perte_thermalisation_photon_2Eg"] - 0.5) < 1e-12},
        {"id": "C18", "nom": "Wh/kg × 3600 = J/kg et H₂ > essence > Li-ion",
         "attendu": _f(LHV_H2, 1),
         "obtenu": _f(st["equivalence_J_par_kg"]["dihydrogene LHV"], 1),
         "ok": abs(st["equivalence_J_par_kg"]["dihydrogene LHV"] - LHV_H2) < 1.0
         and 2.5 < st["hydrogene_sur_essence"] < 2.75
         and 550 < st["cathode_LFP_Wh_kg"] < 620
         and st["Wh_par_kg"]["dihydrogene LHV"] > st["Wh_par_kg"]["essence PCI"]},
        {"id": "C19", "nom": "2Δ/kTc reproduit le rapport déclaré 3,53",
         "attendu": "3.530000", "obtenu": f"{su['rapport_verifie']:.6f}",
         "ok": abs(su["rapport_verifie"] - RAPPORT_BCS) < 1e-9
         and su["pertes_ohmiques_supra_W"] == 0.0},
        {"id": "C20", "nom": "L☉/(4π AU²) ≈ 1361 W/m² et ordre de grandeur du budget",
         "attendu": "1361.000000", "obtenu": _f(bs["irradiance_hors_atmosphere_W_m2"], 6),
         "ok": bs["ecart_relatif"] < 0.01 and 5e3 < bs["ratio_interceptee_sur_consommee"] < 1.5e4},
        {"id": "C21", "nom": "quatre ponts déclarés, chacun borné par une limite",
         "attendu": "4", "obtenu": str(len(po)),
         "ok": len(po) == 4 and all(p["limite"] for p in po)
         and all(p["dossier"] and p["electricite"] for p in po)},
    ]

    return {
        "version": "1.0",
        "theme": "ÉLECTRICITÉ & ABONDANCE ÉNERGÉTIQUE",
        "source": SOURCE,
        "invariants": {
            "c_m_s": C, "mu0_T_m_A": MU0, "epsilon0_F_m": EPS0, "e_C": E_CHARGE,
            "k_B_J_K": K_B, "R_J_mol_K": R_GAZ, "g_m_s2": G0,
            "kwh_J": KWH_J, "eV_nm": EV_NM,
        },
        "materiaux_declares": {
            "resistivites_ohm_m": {"cuivre pur": RESISTIVITE_CU_PUR,
                                   "cuivre IEC": RESISTIVITE_CU_IEC,
                                   "aluminium": RESISTIVITE_AL},
            "bandes_gap_eV": {"Si": BANDE_GAP_SI, "GaAs": BANDE_GAP_GAAS,
                              "MAPbI3": BANDE_GAP_PEROVSKITE, "CdTe": BANDE_GAP_CDTE},
            "stockage": {"LiFePO4 mAh/g": CAPACITE_LFP, "LiFePO4 V": TENSION_LFP,
                         "graphite mAh/g": CAPACITE_GRAPHITE, "H2 LHV J/kg": LHV_H2,
                         "H2 HHV J/kg": HHV_H2, "essence J/kg": PCI_ESSENCE},
            "supraconducteurs": {"YBCO Tc K": TC_YBCO, "NbTi Tc K": TC_NBTI},
            "statut": "valeurs déclarées de littérature, non mesurées dans ce dépôt",
        },
        "equations": eqs,
        "controles": controles,
        "resume": {
            "equations": len(eqs),
            "controles_ok": sum(1 for c in controles if c["ok"]),
            "controles_total": len(controles),
            "statuts": {s: sum(1 for e in eqs if e["statut"] == s) for s in STATUTS},
            "betz_max": bz["cp_max"],
            "carnot_800_300_K": car["eta_carnot"],
            "seuil_Si_nm": pv["lambda_seuil_si_nm"],
            "pertes_1GW_a_400kV_W": ht["table"][2]["pertes_W"],
            "puissance_solaire_interceptee_W": bs["puissance_interceptee_W"],
            "surface_utile_km2_pour_20TW": bs["surface_utile_km2"],
        },
    }


def verifier(donnees: Dict[str, Any] | None = None) -> bool:
    donnees = donnees or resoudre()
    return all(c["ok"] for c in donnees["controles"])


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    resultat = resoudre()
    print(json.dumps(resultat, ensure_ascii=False, indent=2, default=str))
    sys.exit(0 if verifier(resultat) else 1)
