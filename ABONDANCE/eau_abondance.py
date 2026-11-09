# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2026 IMAM8MAHDI / Astro-Code Ecosystem
# SPDX-License-Identifier: GPL-3.0-only OR AGPL-3.0-only
"""Eau — équations posées, résolues, contrôlées. Abondance, dessalement, cycle.

Suite du parcours « Électricité : tout s'éclaire ! » (ARTE, Déclics,
cFx7Cm-c2nA) : la maîtrise de l'électricité est racontée de Thalès à Tesla ;
celle de l'eau suit la même exigence, et Thalès y apparaît déjà — son élève
Anaximandre en fait le principe de toute chose. Ce module ne cite pas la
vidéo : il n'en reprend ni chapitres (aucun) ni transcript (absent, timedtext
0 octet), seulement la façon de poser une idée par une grandeur.

Point d'honnêteté : le « travail minimum de dessalement » calculé ici est une
borne thermodynamique d'un modèle de solution idéale, pas le coût d'une usine.
Les coûts réels mesurés dans la littérature sont saisis comme valeurs
déclarées et comparés à la borne. Aucun chiffre de ressource n'est revendiqué
comme une preuve d'abondance : l'abondance, ici, est un rapport entre deux
ordres de grandeur chiffrés.

Convention de densité : les identités ρ·g·H partagées avec le dossier
électricité sont calculées à ρ = 1000 kg/m³ (RHO_CONVENTION, l'eau à ~4 °C)
pour que le contrôle croisé soit exactement nul. Les densités déclarées 997
(douce, 25 °C), 1025 (mer) et 917 (glace) restent employées là où elles
comportent physiquement.

Usage :
    py -3 ABONDANCE/eau_abondance.py
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path
from typing import Any, Dict, List

RACINE = Path(__file__).resolve().parent          # ABONDANCE/
if str(RACINE) not in sys.path:
    sys.path.insert(0, str(RACINE))

import electricite_abondance as ELEC  # noqa: E402  (contrôle croisé inter-dossiers)

# ── Constantes ──────────────────────────────────────────────────────────────
C = ELEC.C
G0 = ELEC.G0
K_B = ELEC.K_B
N_A = ELEC.N_A
R_GAZ = ELEC.R_GAZ
KWH_J = ELEC.KWH_J

M_EAU = 18.015e-3                 # kg/mol — déclaré (composition standard)
RHO_CONVENTION = 1000.0           # kg/m³ — convention partagée avec le dossier électricité
RHO_EAU_DOUCE = 997.0             # kg/m³ à 25 °C — déclaré
RHO_EAU_MER = 1025.0              # kg/m³ — déclaré
RHO_GLACE = 917.0                 # kg/m³ — déclaré
SALINITE_G_KG = 35.0              # g de sel dissous par kg d'eau — déclaré
M_NACL = 58.44e-3                 # kg/mol
T_AMBIANTE = 298.15               # K
R_VAPEUR = R_GAZ / M_EAU          # 461,52… J/(kg·K), dérivé
L_CHALEUR_LATENTE = 2.442e6       # J/kg à 25 °C — déclaré
P_ATM = 101_325.0                 # Pa — définition
E0_HPA = 6.1094                   # pression de vapeur à 0 °C — déclaré (Magnus)
A_MAGNUS, B_MAGNUS = 17.625, 243.04
SURFACE_TERRE_KM2 = 1.49e8        # km² émergés — déclaré
SURFACE_RACINE_KM2 = 5.1007e8     # km² planète — déclaré

# Valeurs déclarées de littérature (ordres de grandeur industriels).
SEC_RO_DECLARE_kWH_m3 = 3.0       # osmose inverse moderne, eau de mer
RECUPERATION_RO = 0.45            # taux de récupération typique — déclaré
RESEAU_FUITES_pct = 0.30          # pertes physiques moyennes mondiales — déclaré
I_EFFECTIF_NACL = 1.78            # coefficient réel, en deçà de i = 2 (ion pairing) — déclaré
PRESSION_RO_UTILISEE_BAR = 60.0   # pression aval typique d'une usine — déclarée

SOURCE = {
    "herite_de": "electricite_abondance.py (même patron EQ → fonction → contrôle)",
    "video_origine": ELEC.SOURCE["titre"],
    "video_url": ELEC.SOURCE["url"],
    "transcript": ELEC.SOURCE["transcript"],
    "fil_conducteur": "Thalès déjà tenait l'eau pour principe des choses ; "
                      "Archimède, Pascal, Bernoulli, van 't Hoff sont les prédécesseurs nommés ici",
}

STATUTS = ELEC.STATUTS


def _f(x: float, n: int = 6) -> str:
    return ELEC._f(x, n)


def _exp(x: float, n: int = 4) -> str:
    return ELEC._exp(x, n)


def _fa(x: float) -> str:
    return f"{x:.2f}"


# ============================================================================
# ÉQUATIONS
# ============================================================================

def repartition_terre() -> Dict[str, Any]:
    """EQ-01 — où est l'eau : volumes déclarés (ordre de grandeur USGS) et renouvellement."""
    total_km3 = 1_386_000_000.0
    douce_pct = 2.59
    repartition_douce = {"glaces et neige permanente": 68.7,
                         "nappes souterraines": 30.8,
                         "surface et autre": 0.5}
    douce_km3 = total_km3 * douce_pct / 100.0
    volumes = {nom: douce_km3 * pct / 100.0 for nom, pct in repartition_douce.items()}
    debit_renouvelable_km3_an = 12_000.0            # renouvellement continental — déclaré
    return {
        "total_km3": total_km3,
        "sale_pct": 100.0 - douce_pct,
        "douce_km3": douce_km3,
        "douce_pct": douce_pct,
        "repartition_douce_pct": repartition_douce,
        "volumes_km3": volumes,
        "somme_repartition": sum(repartition_douce.values()),
        "fermeture_des_volumes": abs(sum(volumes.values()) - douce_km3),
        "debit_renouvelable_km3_an": debit_renouvelable_km3_an,
        "annees_pour_renouveler_la_douce": douce_km3 / debit_renouvelable_km3_an,
        "fractions": {"douce_sur_totale": douce_pct / 100.0,
                      "renouvelable_sur_douce": debit_renouvelable_km3_an / douce_km3},
    }


def hydrostatique() -> Dict[str, Any]:
    """EQ-02 — P = ρgH : la barrique de Pascal en une ligne."""
    profondeurs = [1.0, 10.0, 100.0, 10_994.0]      # fosse des Mariannes, déclaré
    table = [{"h_m": h, "P_Pa": RHO_EAU_MER * G0 * h, "atmospheres": RHO_EAU_MER * G0 * h / P_ATM}
             for h in profondeurs]
    j_par_m3_std = RHO_CONVENTION * G0 * 100.0
    return {
        "table": table,
        "P_a_10m_Pa": RHO_EAU_DOUCE * G0 * 10.0,
        "atm_a_10m": (RHO_EAU_DOUCE * G0 * 10.0 + P_ATM) / P_ATM,
        "force_par_m2_a_1m_N": RHO_EAU_DOUCE * G0 * 1.0 * 1.0,
        "J_par_m3_convention_std": j_par_m3_std,
        "J_par_m3_eau_douce_25C": RHO_EAU_DOUCE * G0 * 100.0,
        "J_par_m3_eau_de_mer": RHO_EAU_MER * G0 * 100.0,
        "coherence_avec_elec": abs(j_par_m3_std - ELEC.hydro()["J_par_m3"])
                                / ELEC.hydro()["J_par_m3"],
        "relation": "P = ρ·g·h ; la forme du récipient ne compte pas (Pascal)",
    }


def architecte_flottant() -> Dict[str, Any]:
    """EQ-03 — poussée d'Archimède et part immergée d'un iceberg."""
    part = RHO_GLACE / RHO_EAU_MER
    navire_t = 50_000.0                              # tonnes de port en lourd, déclaré
    deplacement_m3 = navire_t * 1000.0 / RHO_EAU_MER
    return {
        "part_immergee_glace": part,
        "part_emergee_glace": 1.0 - part,
        "poussee_N_par_m3_immerge": RHO_EAU_MER * G0 * 1.0,
        "volume_deplace_m3_pour_50000t": deplacement_m3,
        "masse_d_eau_deplacee_kg": RHO_EAU_MER * deplacement_m3,
        "masse_navire_kg": navire_t * 1000.0,
        "equilibre": abs(RHO_EAU_MER * deplacement_m3 - navire_t * 1000.0),
        "ratio_flottaison_eau_douce": RHO_GLACE / RHO_EAU_DOUCE,
    }


def continuite() -> Dict[str, Any]:
    """EQ-04 — A·v constant : ce que la rivière accélère quand elle se resserre."""
    debit = 10.0
    sections = [10.0, 2.0, 0.5]
    vitesses = [debit / s for s in sections]
    produits = [s * v for s, v in zip(sections, vitesses)]
    return {
        "debit_m3_s": debit,
        "sections_m2": sections,
        "vitesses_m_s": vitesses,
        "produits": produits,
        "max_ecart": max(abs(p - debit) for p in produits),
        "rapport_v_max_sur_v_min": max(vitesses) / min(vitesses),
        "rapport_sections": max(sections) / min(sections),
    }


def bernoulli() -> Dict[str, Any]:
    """EQ-05 — Bernoulli et Torricelli : la hauteur devient vitesse."""
    hauteurs = [1.0, 10.0, 100.0]
    vitesses = [math.sqrt(2.0 * G0 * h) for h in hauteurs]
    h0, pas = 10.0, 1e-6
    dpe_dh = (G0 * (h0 + pas) - G0 * (h0 - pas)) / (2.0 * pas)
    return {
        "hauteurs_m": hauteurs,
        "vitesses_m_s": vitesses,
        "charge_cinematique_Pa": [0.5 * RHO_EAU_DOUCE * v * v for v in vitesses],
        "dPE_dh": dpe_dh,
        "attendu_g": G0,
        "v10m_m_s": vitesses[1],
        "kg_par_m3_par_v2_sur_2": (0.5 * RHO_EAU_DOUCE * vitesses[1] ** 2
                                   / (RHO_EAU_DOUCE * G0 * 10.0)),
    }


def pompage() -> Dict[str, Any]:
    """EQ-06 — pomper : énergie par m³, selon la hauteur et le rendement."""
    hauteurs = [10.0, 50.0, 100.0, 300.0]
    rendement = 0.65
    table = [{"H_m": h,
              "J_par_m3": RHO_EAU_DOUCE * G0 * h,
              "kWh_par_m3": RHO_EAU_DOUCE * G0 * h / KWH_J,
              "kWh_par_m3_rendement": RHO_EAU_DOUCE * G0 * h / KWH_J / rendement}
             for h in hauteurs]
    borne = travail_minimum_dessalement()["kWh_par_m3"]
    return {
        "table": table,
        "rendement_declare": rendement,
        "cout_euro_par_m3_a_0_12_kWh": [t["kWh_par_m3_rendement"] * 0.12 for t in table],
        "pour_1000_m3_jour_kW": table[1]["kWh_par_m3_rendement"] * 1000.0 / 24.0,
        "ratio_pompage_sur_borne_dessalement": table[1]["kWh_par_m3_rendement"] / borne,
    }


def osmose() -> Dict[str, Any]:
    """EQ-07 — pression osmotique de l'eau de mer (van 't Hoff, solution idéale)."""
    mol_eau_par_kg = 1.0 / M_EAU
    mol_sel_par_kg = SALINITE_G_KG / 1000.0 / M_NACL
    osmoles_par_kg = mol_sel_par_kg * 2.0                     # NaCl → Na⁺ + Cl⁻
    x_sel = osmoles_par_kg / (mol_eau_par_kg + osmoles_par_kg)
    volume_par_kg_de_solution_m3 = (mol_eau_par_kg * M_EAU) / RHO_EAU_MER
    c_osm = osmoles_par_kg / volume_par_kg_de_solution_m3      # osmoles par m³
    pi = c_osm * R_GAZ * T_AMBIANTE
    pi_dilue = 2.0 * mol_sel_par_kg * 1000.0 * R_GAZ * T_AMBIANTE
    pi_reelle = pi * (I_EFFECTIF_NACL / 2.0)
    return {
        "mol_eau_par_kg": mol_eau_par_kg,
        "mol_sel_par_kg": mol_sel_par_kg,
        "osmoles_par_kg": osmoles_par_kg,
        "c_osm_osm_par_m3": c_osm,
        "fraction_molaire_sel": x_sel,
        "x_eau": 1.0 - x_sel,
        "pi_ideale_Pa": pi,
        "pi_ideale_bar": pi / 1e5,
        "pi_ideale_bar_seconde_voie": pi_dilue / 1e5,
        "ecart_relatif_deux_voies": abs(pi - pi_dilue) / pi,
        "i_effectif_declare": I_EFFECTIF_NACL,
        "pi_reelle_bar": pi_reelle / 1e5,
        "valeur_litterature_bar_declaree": 27.0,
        "hauteur_equivalente_m": pi / (RHO_EAU_MER * G0),
        "pression_usine_declaree_bar": PRESSION_RO_UTILISEE_BAR,
        "marge_sur_pi": PRESSION_RO_UTILISEE_BAR / (pi / 1e5),
    }


def travail_minimum_dessalement() -> Dict[str, Any]:
    """EQ-08 — la borne : séparer réversiblement l'eau douce de l'eau de mer."""
    mol_eau_par_kg = 1.0 / M_EAU
    osmoles_par_kg = 2.0 * SALINITE_G_KG / 1000.0 / M_NACL
    x_eau = mol_eau_par_kg / (mol_eau_par_kg + osmoles_par_kg)
    rt = R_GAZ * T_AMBIANTE
    j_par_mol_exact = rt * math.log(1.0 / x_eau)
    j_par_mol_dilue = rt * (1.0 - x_eau)
    mol_eau_par_m3 = mol_eau_par_kg * RHO_EAU_DOUCE
    kwh_par_m3 = j_par_mol_exact * mol_eau_par_m3 / KWH_J
    monde_m3_par_jour_declare = 1.2e7 * 1000.0        # 12 millions m³/j produits — déclaré
    return {
        "x_eau": x_eau,
        "J_par_mol_eau": j_par_mol_exact,
        "J_par_mol_eau_approx_diluee": j_par_mol_dilue,
        "ecart_approx_diluee": abs(j_par_mol_exact - j_par_mol_dilue) / j_par_mol_exact,
        "J_par_m3": j_par_mol_exact * mol_eau_par_m3,
        "kWh_par_m3": kwh_par_m3,
        "monde_m3_par_jour_declare": monde_m3_par_jour_declare,
        "monde_kWh_par_jour_a_la_borne": kwh_par_m3 * monde_m3_par_jour_declare,
        "monde_TW_moyen_a_la_borne": kwh_par_m3 * monde_m3_par_jour_declare / 86400.0 / 1e12,
        "sec_ro_declare_kWh_m3": SEC_RO_DECLARE_kWH_m3,
        "ratio_ro_sur_borne": SEC_RO_DECLARE_kWH_m3 / kwh_par_m3,
        "a_remarquer": "borne réversible isotherme ; une usine paie aussi les pertes de "
                       "charge, le pompage et la saumure",
    }


def recuperation_concentration() -> Dict[str, Any]:
    """EQ-09 — bilan de matière : ce que devient le sel quand on prend l'eau."""
    c_feed = SALINITE_G_KG
    taux = [0.20, 0.45, 0.60, 0.75]
    table, residus = [], []
    for y in taux:
        c_conc = c_feed / (1.0 - y)
        sel_entree = c_feed * RHO_EAU_MER / 1000.0               # kg de sel par m³ d'aliment
        sel_sortie = (1.0 - y) * c_conc * RHO_EAU_MER / 1000.0   # ce qui repart en saumure
        residus.append(abs(sel_entree - sel_sortie) / sel_entree)
        table.append({"Y": y,
                      "saumure_g_kg": c_conc,
                      "sur_concentration": c_conc / c_feed,
                      "eau_rejetee_m3_par_m3_produit": 1.0 / y - 1.0})
    return {
        "table": table,
        "c_feed_g_kg": c_feed,
        "residus_bilan_max": max(residus),
        "sec_pratique_declare_kWh_m3": SEC_RO_DECLARE_kWH_m3,
        "hypothese": "volumes additifs et masse volumique commune : le bilan est écrit en "
                     "concentrations, pas en volumes exacts",
        "limite": "au-delà de Y ≈ 0,6 la saumure précipite (gypse, calcaire) : le modèle "
                  "linéaire s'arrête là",
    }


def vapeur_eau_air() -> Dict[str, Any]:
    """EQ-10 — deux formules, une physique : Magnus contre Clausius–Clapeyron."""
    def magnus(t_c: float) -> float:
        return E0_HPA * math.exp(A_MAGNUS * t_c / (t_c + B_MAGNUS))

    def clausius(t_c: float, n: int = 20_000) -> float:
        t0, t_fin = 273.15, t_c + 273.15
        pas = (t_fin - t0) / n
        e = E0_HPA
        for k in range(1, n + 1):
            t = t0 + k * pas
            e *= math.exp(L_CHALEUR_LATENTE / (R_VAPEUR * t * t) * pas)
        return e

    serie = [{"t_C": t, "e_hPa": magnus(t)} for t in (0.0, 10.0, 20.0, 25.0, 30.0, 40.0)]
    e25 = magnus(25.0)
    c25 = clausius(25.0)
    evaporer_m3_J = L_CHALEUR_LATENTE * RHO_EAU_DOUCE
    return {
        "serie_magnus": serie,
        "magnus_25C_hPa": e25,
        "clausius_clapeyron_25C_hPa": c25,
        "ecart_relatif_25C": abs(c25 - e25) / e25,
        "melange_g_kg_air_sature_25C": 0.622 * e25 / (1013.25 - e25) * 1000.0,
        "r_vapeur_J_kg_K": R_VAPEUR,
        "chaleur_latente_J_kg": L_CHALEUR_LATENTE,
        "evaporer_1_m3_exige_J": evaporer_m3_J,
        "equivalent_kWh_par_m3": evaporer_m3_J / KWH_J,
        "pluie_de_1mm_en_L_par_m2": 1.0,
    }


def cycle_global() -> Dict[str, Any]:
    """EQ-11 — bilan du cycle : ce qui tombe, ce qui s'évapore, ce qui court."""
    evap_ocean, precip_ocean = 453_000.0, 406_000.0   # km³/an — calés pour fermer le bilan
    precip_terre, evap_terre, ruissellement = 119_000.0, 72_000.0, 47_000.0
    precip_table_citee = 419_000.0
    return {
        "km3_par_an": {"precip_terre": precip_terre, "evap_terre": evap_terre,
                       "ruissellement": ruissellement, "precip_ocean": precip_ocean,
                       "evap_ocean": evap_ocean},
        "solde_terre": precip_terre - evap_terre - ruissellement,
        "solde_ocean": precip_ocean - evap_ocean + ruissellement,
        "cloture_planetaire": (precip_terre + precip_ocean) - (evap_terre + evap_ocean),
        "mm_par_an_sur_terre_emergee": precip_terre * 1e9 / (SURFACE_TERRE_KM2 * 1e6) * 1000.0,
        "mm_par_an_planete": ((precip_terre + precip_ocean) * 1e9
                              / (SURFACE_RACINE_KM2 * 1e6) * 1000.0),
        "habitant_equivalent_m3_par_an": ruissellement * 1e9 / 8.0e9,
        "ratio_ruissellement_sur_boisson": ruissellement * 1e9 / 8.0e9 / 3.0,
        "besoin_boisson_m3_par_an": 3.0,
        "avertissement": f"la table souvent citée (précipitations océan {precip_table_citee:.0f}, "
                         f"évaporation {evap_ocean:.0f}) laisse un trou de "
                         f"{evap_ocean - precip_table_citee - ruissellement:.0f} km³/an ; ici "
                         "406 000 ferme le bilan, et l'écart est revendiqué",
    }


def eau_par_aliment() -> Dict[str, Any]:
    """EQ-12 — empreinte eau : litres par kilogramme, masses consommées déclarées."""
    litres_par_kg = {"blé": 1_500.0, "riz": 2_800.0, "pomme de terre": 300.0,
                     "tomate": 250.0, "œuf": 4_200.0, "lait (litre)": 350.0,
                     "poulet": 4_300.0, "bœuf": 15_000.0}
    kilos_par_personne_an = {"blé": 150.0, "riz": 80.0, "pomme de terre": 90.0,
                             "tomate": 30.0, "œuf": 15.0, "lait (litre)": 60.0,
                             "poulet": 20.0, "bœuf": 10.0}
    litres_par_an = sum(litres_par_kg[k] * kilos_par_personne_an[k] for k in litres_par_kg)
    return {
        "litres_par_kg": litres_par_kg,
        "kilos_par_personne_an_declares": kilos_par_personne_an,
        "litres_par_personne_par_an": litres_par_an,
        "litres_par_personne_par_jour": litres_par_an / 365.0,
        "domestique_declare_litres_par_jour": 150.0,
        "ratio_agricole_sur_domestique": litres_par_an / 365.0 / 150.0,
        "seuil_potabilite_g_kg": 1.0,
        "litres_par_m3": 1000.0,
        "ratio_boeuf_sur_tomate": litres_par_kg["bœuf"] / litres_par_kg["tomate"],
        "masse_alimentaire_totale_kg_an": sum(kilos_par_personne_an.values()),
    }


def salinite_conductivite() -> Dict[str, Any]:
    """EQ-13 — mesurer sans prélever : conductivité ↔ salinité."""
    facteur = 0.64                                            # g/kg ≈ 0,64 × EC(dS/m) — déclaré
    ec_eau_mer = SALINITE_G_KG / facteur
    return {
        "facteur_declare": facteur,
        "EC_eau_de_mer_dS_m": ec_eau_mer,
        "EC_eau_saumatre_dS_m": 3.0 / facteur,
        "EC_seuil_potable_dS_m": 1.0 / facteur,
        "conductivite_eau_de_mer_S_m": ec_eau_mer * 0.1,
        "seuil_saumatre_g_kg": 3.0,
        "seuil_potable_g_kg": 1.0,
        "reciproque": SALINITE_G_KG / ec_eau_mer,
    }


def stockage_gravitaire_eau() -> Dict[str, Any]:
    """EQ-14 — l'eau comme batterie : le même ρgH que le dossier électricité."""
    volume_m3, hauteur = 1.0e9, 100.0                          # 1 km³ sous 100 m
    energie_j = RHO_CONVENTION * G0 * hauteur * volume_m3
    return {
        "volume_m3": volume_m3,
        "hauteur_m": hauteur,
        "rho_convention_kg_m3": RHO_CONVENTION,
        "energie_J": energie_j,
        "energie_kWh": energie_j / KWH_J,
        "energie_GWh": energie_j / KWH_J / 1e6,
        "energie_TWh": energie_j / KWH_J / 1e9,
        "J_par_m3": RHO_CONVENTION * G0 * hauteur,
        "identique_a_electricite_hydro": abs(RHO_CONVENTION * G0 * hauteur
                                             - ELEC.hydro()["J_par_m3"]) / ELEC.hydro()["J_par_m3"],
        "puissance_decharge_8h_W": energie_j / (8.0 * 3600.0),
        "Wh_par_kg_d_eau": G0 * hauteur / 3600.0,
        "rendement_round_trip_declare": 0.80,
        "energie_utile_GWh": energie_j / KWH_J / 1e6 * 0.80,
        "comparaison_lithium_Wh_kg_declaree": 250.0,
    }


def ponts_dossier() -> List[Dict[str, str]]:
    """EQ-15 — grille de lecture du dossier appliquée à l'eau (analogies déclarées)."""
    return [
        {"pilier": "P1 — Scellement",
         "dossier": "valeur = empreinte SHA-256 du fichier qui la porte",
         "eau": "bornes thermodynamiques : le travail minimum ne se négocie pas",
         "limite": "la borne n'est pas un devis d'usine"},
        {"pilier": "P2 — Horloge",
         "dossier": "tick 7,402 ns, 50 Hz réseau",
         "eau": "cycle de l'eau : évaporation le jour, rosée la nuit, mousson à saison fixe",
         "limite": "analogie de périodicité, aucun lien causal avec l'horloge du noyau"},
        {"pilier": "P3 — Tolérance à la panne",
         "dossier": "redondance, code correcteur",
         "eau": "double alimentation, stockage enterré, nappe de secours",
         "limite": "l'ingénierie réseau n'est pas de la théorie des codes"},
        {"pilier": "P4 — Registre et dette",
         "dossier": "qui doit quoi à qui",
         "eau": "nappes surexploitées = dette hydrologique ; eau virtuelle = commerce implicite",
         "limite": "comptabilité déclarative : les volumes exacts manquent, le cadre est posé"},
    ]


# ============================================================================
# ASSEMBLAGE
# ============================================================================

def _eq(id_: str, chemin: str, formule: str, resultat: str, statut: str,
        detail: Any, limite: str = "") -> Dict[str, Any]:
    return {"id": id_, "chemin": chemin, "formule": formule,
            "resultat": resultat, "statut": statut, "limite": limite, "detail": detail}


def resoudre() -> Dict[str, Any]:
    rp, hs, ar, co, be, po = (repartition_terre(), hydrostatique(), architecte_flottant(),
                              continuite(), bernoulli(), pompage())
    osm, wm, rc = osmose(), travail_minimum_dessalement(), recuperation_concentration()
    va, cy = vapeur_eau_air(), cycle_global()
    ea, sc, sg, pd = eau_par_aliment(), salinite_conductivite(), stockage_gravitaire_eau(), ponts_dossier()

    eqs = [
        _eq("EQ-01", "eau_abondance.py → repartition_terre() → C01",
            "V_douce = V_totale × 2,59 % ;  V_douce = Σ V_compartiments",
            f"douce = {rp['douce_km3'] / 1e6:.2f} × 10⁶ km³ sur {rp['total_km3'] / 1e6:.2f} × 10⁶ km³ · "
            f"renouvelable {100 * rp['fractions']['renouvelable_sur_douce']:.2f} % du stock · "
            f"{rp['annees_pour_renouveler_la_douce']:.0f} ans pour rajeunir toute l'eau douce",
            "SIMULÉ", rp,
            limite="les volumes et les 12 000 km³/an de renouvellement sont des ordres de "
                   "grandeur déclarés, non des relevés : C01 ne fait que refermer des "
                   "pourcentages entre eux, il ne peut découvrir une erreur commune à la table"),
        _eq("EQ-02", "eau_abondance.py → hydrostatique() → C02",
            "P = ρ·g·h ;  F = P·S",
            f"10 m (douce 25 °C) : {hs['P_a_10m_Pa'] / 1000.0:.3f} kPa = "
            f"{hs['atm_a_10m']:.3f} atm absolue · 100 m en mer : "
            f"{hs['table'][2]['P_Pa'] / 1000.0:.1f} kPa · ρgH(100 m) = "
            f"{_f(hs['J_par_m3_convention_std'], 4)} J/m³",
            "OPÉRATIONNEL", hs,
            limite="P = ρgH suppose l'eau au repos : ni houle, ni courant, ni capteur ; le "
                   "zéro de l'écart avec le dossier électricité est la convention ρ = 1000 "
                   "partagée entre les deux modules, pas une pression relevée quelque part"),
        _eq("EQ-03", "eau_abondance.py → architecte_flottant() → C03",
            "F_poussée = ρ_fluide·V·g ;  part immergée = ρ_objet/ρ_fluide",
            f"iceberg immergé {100 * ar['part_immergee_glace']:.2f} % · émerge "
            f"{100 * ar['part_emergee_glace']:.2f} % · 50 000 t ⇒ "
            f"{_exp(ar['volume_deplace_m3_pour_50000t'], 3)} m³ déplacés",
            "OPÉRATIONNEL", ar,
            limite="Archimède s'énonce pour un solide dans un fluide de densité déclarée : "
                   "la glace réelle porte bulles d'air et poches de saumure, et les 50 000 t "
                   "sont un port en lourd annoncé, pas un franc-bord observé sur une coque"),
        _eq("EQ-04", "eau_abondance.py → continuite() → C04",
            "Q = A·v constant ;  v = Q/A",
            f"10 m³/s : 10 m² → {co['vitesses_m_s'][0]:.1f} m/s, 0,5 m² → "
            f"{co['vitesses_m_s'][2]:.1f} m/s · écart max {co['max_ecart']:.2e}",
            "OPÉRATIONNEL", co,
            limite="Q = A·v est une identité pour un fluide incompressible remplissant "
                   "uniformément la section : profil de vitesse, rugosité du lit et régime "
                   "non permanent restent hors modèle, et le 10 m³/s est choisi, pas jaugé"),
        _eq("EQ-05", "eau_abondance.py → bernoulli() → C05",
            "P + ½ρv² + ρgh = const ;  v = √(2gh)",
            f"10 m → {be['v10m_m_s']:.3f} m/s · 100 m → {be['vitesses_m_s'][2]:.2f} m/s · "
            f"dPE/dh = {be['dPE_dh']:.6f} m/s²",
            "OPÉRATIONNEL", be,
            limite="v = √(2gh) ignore la viscosité et la contraction à l'orifice : la vitesse "
                   "d'un écoulement réel est plus basse ; dPE/dh = g ne mesure pas la pesanteur, "
                   "il éprouve la dérivation numérique de la constante déclarée"),
        _eq("EQ-06", "eau_abondance.py → pompage() → C06",
            "e = ρ·g·H/η (par m³) ;  P = e·Q",
            f"50 m à η 0,65 → {po['table'][1]['kWh_par_m3_rendement']:.4f} kWh/m³ · "
            f"1000 m³/j → {po['pour_1000_m3_jour_kW']:.1f} kW en moyenne · "
            f"{po['ratio_pompage_sur_borne_dessalement']:.2f}× la borne de EQ-08",
            "OPÉRATIONNEL", po,
            limite="η = 0,65 est un rendement global d'ordre de grandeur, pas un relevé sur "
                   "une station : pertes de ligne, NPSH et calendrier réel de pompage restent "
                   "dehors, et le 0,12 €/kWh est un prix d'entrée supposé, non un tarif constaté"),
        _eq("EQ-07", "eau_abondance.py → osmose() → C07",
            "π = i·c·R·T ;  c en osmoles par m³",
            f"35 g/kg → π idéale {osm['pi_ideale_bar']:.2f} bar "
            f"({osm['pi_ideale_bar_seconde_voie']:.2f} bar par la voie molaire), π réelle ≈ "
            f"{osm['pi_reelle_bar']:.1f} bar · colonne d'eau de "
            f"{osm['hauteur_equivalente_m']:.1f} m",
            "OPÉRATIONNEL", osm,
            limite="π = i·c·RT est une solution idéale à 298,15 K et 35 g/kg, sans membrane, "
                   "sans polarisation de concentration ni entartrage ; la valeur « réelle » "
                   "n'est que l'idéal multiplié par un i = 1,78 déclaré, et les 60 bar une "
                   "pression aval d'usine annoncée"),
        _eq("EQ-08", "eau_abondance.py → travail_minimum_dessalement() → C08",
            "w_min = R·T·ln(1/x_eau) par mole d'eau douce extraite",
            f"x_eau = {wm['x_eau']:.6f} → {wm['kWh_par_m3']:.4f} kWh/m³ (borne) · RO déclarée "
            f"{wm['sec_ro_declare_kWh_m3']:.1f} kWh/m³ = {wm['ratio_ro_sur_borne']:.2f}× la borne",
            "OPÉRATIONNEL", wm,
            limite="borne réversible isotherme d'un modèle de solution idéale : elle interdit "
                   "un devis plus bas, elle ne prédit le coût d'aucune usine — pertes de "
                   "charge, pompage et saumure sont dehors ; 3,0 kWh/m³ et 12 millions de "
                   "m³/jour y sont des valeurs déclarées"),
        _eq("EQ-09", "eau_abondance.py → recuperation_concentration() → C09",
            "C_saumure = C_alim/(1−Y) ;  bilan salin fermé",
            f"Y = 0,45 → {rc['table'][1]['saumure_g_kg']:.1f} g/kg "
            f"({rc['table'][1]['sur_concentration']:.2f}×) · "
            f"{rc['table'][1]['eau_rejetee_m3_par_m3_produit']:.2f} m³ rejetés par m³ produit · "
            f"résidu {rc['residus_bilan_max']:.2e}",
            "OPÉRATIONNEL", rc,
            limite="résidu nul : le bilan salin se referme sur sa propre écriture en "
                   "concentrations, volumes additifs et densité marine commune ; rien ici ne "
                   "dit qu'une membrane atteigne Y = 0,45 sur une eau de mer réelle"),
        _eq("EQ-10", "eau_abondance.py → vapeur_eau_air() → C10",
            "e_s(Magnus) = 6,1094·exp(17,625·t/(t+243,04)) ;  d ln e/dT = L/(R_v·T²)",
            f"25 °C : Magnus {va['magnus_25C_hPa']:.3f} hPa, Clausius "
            f"{va['clausius_clapeyron_25C_hPa']:.3f} hPa · écart "
            f"{100 * va['ecart_relatif_25C']:.2f} % · évaporer 1 m³ coûte "
            f"{va['equivalent_kWh_par_m3']:.1f} kWh",
            "OPÉRATIONNEL", va,
            limite="l'accord des deux formules compare deux paramétrisations déclarées — "
                   "Magnus ajustée, Clausius–Clapeyron intégrée avec une chaleur latente "
                   "tenue pour constante : il ne dit rien du vent, de la salinité ni de "
                   "l'humidité réelle d'une parcelle d'air"),
        _eq("EQ-11", "eau_abondance.py → cycle_global() → C11",
            "P_terre = ET_terre + R ;  P_océan + R = ET_océan",
            f"119 000 = 72 000 + 47 000 km³/an · {cy['mm_par_an_sur_terre_emergee']:.0f} mm/an "
            f"sur les terres émergées · {cy['mm_par_an_planete']:.0f} mm/an sur la planète",
            "SIMULÉ", cy,
            limite="le zéro de C11 est une clôture choisie : 406 000 km³/an est calé pour "
                   "fermer le bilan et l'écart avec la table souvent citée reste revendiqué, "
                   "non résolu ; ni année particulière, ni tendance, ni répartition régionale"),
        _eq("EQ-12", "eau_abondance.py → eau_par_aliment() → C12",
            "V_eau = Σᵢ (L/kg)ᵢ × mᵢ ;  mᵢ en kg par personne et par an",
            f"bœuf/tomate = {ea['ratio_boeuf_sur_tomate']:.0f}× · régime déclaré ≈ "
            f"{ea['litres_par_personne_par_jour']:.0f} L/j contre "
            f"{ea['domestique_declare_litres_par_jour']:.0f} L/j au robinet",
            "SIMULÉ", ea,
            limite="les L/kg et les kg/personne/an sont des chiffres déclarés d'ordre de "
                   "grandeur, très dépendants du pays et du climat : le ratio bœuf/tomate "
                   "oppose deux valeurs de table, et le total suppose le régime à huit "
                   "lignes exactement consommé"),
        _eq("EQ-13", "eau_abondance.py → salinite_conductivite() → C13",
            "S (g/kg) ≈ 0,64 × EC (dS/m)",
            f"35 g/kg → {sc['EC_eau_de_mer_dS_m']:.1f} dS/m = "
            f"{sc['conductivite_eau_de_mer_S_m']:.2f} S/m · seuil potable à "
            f"{sc['EC_seuil_potable_dS_m']:.2f} dS/m",
            "SIMULÉ", sc,
            limite="le facteur 0,64 est une calibration déclarée pour une composition ionique "
                   "marine moyenne à température de référence : la conductivité bouge avec la "
                   "température et avec la nature des ions ; C13 ne vérifie que la réciprocité "
                   "de la division"),
        _eq("EQ-14", "eau_abondance.py → stockage_gravitaire_eau() → C14",
            "E = ρ·g·H·V ;  même membre que le dossier électricité",
            f"1 km³ sous 100 m = {sg['energie_GWh']:.1f} GWh = {sg['energie_TWh']:.4f} TWh · "
            f"décharge en 8 h = {sg['puissance_decharge_8h_W'] / 1e9:.1f} GW · "
            f"{sg['Wh_par_kg_d_eau']:.3f} Wh/kg d'eau",
            "OPÉRATIONNEL", sg,
            limite="E = ρgHV est le potentiel d'un volume et d'une chute déclarés à la "
                   "convention ρ = 1000 : ni évaporation, ni fuites, ni plage réelle de plan "
                   "d'eau ; le round-trip 0,80 et les 250 Wh/kg de comparaison sont des "
                   "valeurs annoncées"),
        _eq("EQ-15", "eau_abondance.py → ponts_dossier() → C15",
            "P1 ↔ borne · P2 ↔ cycles · P3 ↔ redondance · P4 ↔ dette hydrologique",
            "4 ponts déclarés comme lectures, chacun borné par une limite",
            "SPÉCIFIÉ", pd,
            limite="quatre ponts posés comme grille de lecture, aucun calcul : chacun porte "
                   "déjà sa borne dans le détail, et rien dans cette liste n'établit un "
                   "lien causal entre l'eau et les piliers du noyau"),
    ]

    controles = [
        {"id": "C01", "nom": "la répartition de l'eau douce ferme à 100 % et en volumes",
         "attendu": "100.0", "obtenu": f"{rp['somme_repartition']:.1f}",
         "ok": abs(rp["somme_repartition"] - 100.0) < 1e-9
         and rp["fermeture_des_volumes"] < 1e-6
         and 2.0 < rp["douce_pct"] < 3.0
         and 0.02 < rp["douce_km3"] / rp["total_km3"] < 0.03},
        {"id": "C02", "nom": "ρgH(100 m) identique aux deux dossiers (convention ρ = 1000)",
         "attendu": "0.000000000000", "obtenu": f"{hs['coherence_avec_elec']:.12f}",
         "ok": hs["coherence_avec_elec"] < 1e-15
         and abs(hs["J_par_m3_convention_std"] - RHO_CONVENTION * G0 * 100.0) < 1e-9
         and abs(hs["P_a_10m_Pa"] - RHO_EAU_DOUCE * G0 * 10.0) < 1e-9
         and hs["J_par_m3_eau_de_mer"] > hs["J_par_m3_eau_douce_25C"]},
        {"id": "C03", "nom": "poids d'eau déplacée = poids du navire",
         "attendu": "0", "obtenu": f"{ar['equilibre']:.6f}",
         "ok": ar["equilibre"] < 1e-6 and 0.85 < ar["part_immergee_glace"] < 0.95
         and abs(ar["masse_d_eau_deplacee_kg"] - ar["masse_navire_kg"]) < 1e-6},
        {"id": "C04", "nom": "A·v constant sur trois sections",
         "attendu": "0.000000000000", "obtenu": f"{co['max_ecart']:.12e}",
         "ok": co["max_ecart"] < 1e-12 and abs(co["rapport_v_max_sur_v_min"] - 20.0) < 1e-9
         and abs(co["rapport_sections"] - co["rapport_v_max_sur_v_min"]) < 1e-12},
        {"id": "C05", "nom": "d(gh)/dh = g et ½ρv² = ρgh (Torricelli)",
         "attendu": _f(be["attendu_g"], 6), "obtenu": _f(be["dPE_dh"], 6),
         "ok": abs(be["dPE_dh"] - G0) < 1e-6 and abs(be["kg_par_m3_par_v2_sur_2"] - 1.0) < 1e-12
         and abs(be["v10m_m_s"] - math.sqrt(2.0 * G0 * 10.0)) < 1e-12},
        {"id": "C06", "nom": "kWh/m³ = ρgH/3,6 MJ/η et croît avec H",
         "attendu": _f(RHO_EAU_DOUCE * G0 * 50.0 / KWH_J / 0.65, 6),
         "obtenu": _f(po["table"][1]["kWh_par_m3_rendement"], 6),
         "ok": abs(po["table"][1]["kWh_par_m3_rendement"]
                   - RHO_EAU_DOUCE * G0 * 50.0 / KWH_J / 0.65) < 1e-12
         and po["table"][0]["kWh_par_m3"] < po["table"][3]["kWh_par_m3"]
         and 0.15 < po["table"][1]["kWh_par_m3_rendement"] < 0.25},
        {"id": "C07", "nom": "deux voies pour π, un ordre, et le réel sous l'idéal",
         "attendu": "≈ 27 bar déclarés", "obtenu": f"{osm['pi_reelle_bar']:.2f} bar",
         "ok": osm["ecart_relatif_deux_voies"] < 0.05
         and 25.0 < osm["pi_ideale_bar"] < 35.0
         and abs(osm["pi_reelle_bar"] - osm["valeur_litterature_bar_declaree"]) < 5.0
         and osm["marge_sur_pi"] > 1.5},
        {"id": "C08", "nom": "ln(1/x) contre son développement : la voie diluée suit l'exacte",
         "attendu": "< 0.02", "obtenu": f"{wm['ecart_approx_diluee']:.6f}",
         "ok": wm["ecart_approx_diluee"] < 0.02 and 0.55 < wm["kWh_par_m3"] < 1.05
         and 3.0 < wm["ratio_ro_sur_borne"] < 4.5},
        {"id": "C09", "nom": "bilan salin fermé pour quatre taux de récupération",
         "attendu": "0.000000000000", "obtenu": f"{rc['residus_bilan_max']:.12e}",
         "ok": rc["residus_bilan_max"] < 1e-12
         and abs(rc["table"][1]["saumure_g_kg"] - SALINITE_G_KG / 0.55) < 1e-9
         and all(rc["table"][i]["saumure_g_kg"] < rc["table"][i + 1]["saumure_g_kg"]
                 for i in range(3))},
        {"id": "C10", "nom": "Magnus ≈ Clausius–Clapeyron à 25 °C",
         "attendu": f"{va['magnus_25C_hPa']:.3f}",
         "obtenu": f"{va['clausius_clapeyron_25C_hPa']:.3f}",
         "ok": va["ecart_relatif_25C"] < 0.05 and 30.0 < va["magnus_25C_hPa"] < 33.0
         and abs(va["r_vapeur_J_kg_K"] - 461.5) < 1.0
         and 15.0 < va["melange_g_kg_air_sature_25C"] < 25.0},
        {"id": "C11", "nom": "le cycle ferme : terre, océan et planète",
         "attendu": "0.0", "obtenu": f"{cy['cloture_planetaire']:.6f}",
         "ok": abs(cy["solde_terre"]) < 1e-9 and abs(cy["solde_ocean"]) < 1e-9
         and abs(cy["cloture_planetaire"]) < 1e-9
         and 750.0 < cy["mm_par_an_sur_terre_emergee"] < 850.0
         and 950.0 < cy["mm_par_an_planete"] < 1100.0},
        {"id": "C12", "nom": "L/j issu des masses réellement consommées",
         "attendu": "60", "obtenu": f"{ea['ratio_boeuf_sur_tomate']:.0f}",
         "ok": abs(ea["ratio_boeuf_sur_tomate"] - 60.0) < 1e-9
         and ea["litres_par_kg"]["bœuf"] > ea["litres_par_kg"]["poulet"]
         and 500.0 < ea["litres_par_personne_par_jour"] < 5000.0
         and ea["ratio_agricole_sur_domestique"] > 5.0},
        {"id": "C13", "nom": "S/EC = 0,64 dans les deux sens et conversion en S/m",
         "attendu": "0.640000", "obtenu": f"{sc['reciproque']:.6f}",
         "ok": abs(sc["reciproque"] - 0.64) < 1e-9
         and abs(sc["EC_eau_de_mer_dS_m"] - SALINITE_G_KG / 0.64) < 1e-9
         and abs(sc["conductivite_eau_de_mer_S_m"] - 5.46875) < 1e-6},
        {"id": "C14", "nom": "1 km³ sous 100 m = 272,4 GWh et même ρgH qu'EQ-14 électricité",
         "attendu": _f(RHO_CONVENTION * G0 * 1e9 * 100.0 / KWH_J / 1e6, 3),
         "obtenu": _f(sg["energie_GWh"], 3),
         "ok": sg["identique_a_electricite_hydro"] < 1e-15
         and 270.0 < sg["energie_GWh"] < 275.0
         and abs(sg["Wh_par_kg_d_eau"] - G0 * 100.0 / 3600.0) < 1e-12},
        {"id": "C15", "nom": "quatre ponts déclarés, chacun borné",
         "attendu": "4", "obtenu": str(len(pd)),
         "ok": len(pd) == 4 and all(p["limite"] and p["eau"] for p in pd)},
    ]

    return {
        "version": "1.0",
        "theme": "EAU — ABONDANCE, DESSALEMENT ET CYCLE",
        "source": SOURCE,
        "invariants": {
            "rho_convention_kg_m3": RHO_CONVENTION,
            "rho_eau_douce_kg_m3": RHO_EAU_DOUCE, "rho_eau_mer_kg_m3": RHO_EAU_MER,
            "rho_glace_kg_m3": RHO_GLACE, "g_m_s2": G0, "M_eau_kg_mol": M_EAU,
            "R_vapeur_J_kg_K": R_VAPEUR, "kwh_J": KWH_J,
            "salinite_g_kg": SALINITE_G_KG, "T_K": T_AMBIANTE,
        },
        "valeurs_declarees": {
            "SEC_osmose_inverse_kWh_m3": SEC_RO_DECLARE_kWH_m3,
            "recuperation_RO": RECUPERATION_RO,
            "fuites_reseau_pct": RESEAU_FUITES_pct,
            "chaleur_latente_J_kg": L_CHALEUR_LATENTE,
            "i_effectif_NaCl": I_EFFECTIF_NACL,
            "pression_usine_RO_bar": PRESSION_RO_UTILISEE_BAR,
            "statut": "ordres de grandeur de littérature, non mesurés dans ce dépôt",
        },
        "equations": eqs,
        "controles": controles,
        "resume": {
            "equations": len(eqs),
            "controles_ok": sum(1 for c in controles if c["ok"]),
            "controles_total": len(controles),
            "statuts": {s: sum(1 for e in eqs if e["statut"] == s) for s in STATUTS},
            "travail_minimum_kWh_m3": wm["kWh_par_m3"],
            "pression_osmotique_ideale_bar": osm["pi_ideale_bar"],
            "pompage_50m_kWh_m3": po["table"][1]["kWh_par_m3_rendement"],
            "energie_1km3_sous_100m_GWh": sg["energie_GWh"],
            "part_immergee_glace": ar["part_immergee_glace"],
            "pression_vapeur_25C_hPa": va["magnus_25C_hPa"],
            "precipitations_terre_mm_par_an": cy["mm_par_an_sur_terre_emergee"],
            "eau_virtuelle_L_par_personne_par_jour": ea["litres_par_personne_par_jour"],
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
