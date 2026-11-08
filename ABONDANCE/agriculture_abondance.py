# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2026 IMAM8MAHDI / Astro-Code Ecosystem
# SPDX-License-Identifier: GPL-3.0-only OR AGPL-3.0-only
"""Agriculture — équations posées, résolues, contrôlées. Du photon à l'assiette.

Même patron que `electricite_abondance.py` (21 EQ) et `eau_abondance.py`
(15 EQ) : une idée = une grandeur = une équation = un contrôle numérique.
L'agriculture est la suite logique du parcours, pas un résumé de la vidéo
d'origine (ARTE, Déclics, cFx7Cm-c2nA) : celle-ci ne fournit que la manière
de poser — ni chapitres (aucun), ni transcript (0 octet), ni contenu agricole.

Deux plafonds sont démontrés, jamais revendiqués comme preuves :
  — le plafond quantique de la photosynthèse (photons par CO2 fixée) ;
  — le rendement d'usage de l'eau et de l'azote, borné par la loi du minimum.
Tout le reste (rendements, teneurs, efficiances LED, gisements) est saisi en
valeurs DÉCLARÉES de littérature, explicites dans `valeurs_declarees`.

Usage :
    py -3 ABONDANCE/agriculture_abondance.py
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

import electricite_abondance as ELEC  # noqa: E402
import eau_abondance as EAU           # noqa: E402

# ── Constantes reprises ─────────────────────────────────────────────────────
C = ELEC.C
H = ELEC.H_PLANCK
K_B = ELEC.K_B
N_A = ELEC.N_A
R_GAZ = ELEC.R_GAZ
KWH_J = ELEC.KWH_J
G0 = ELEC.G0
SIGMA = (2.0 * math.pi ** 5 * K_B ** 4) / (15.0 * H ** 3 * C ** 2)   # exacte (dérivée des defined)

# ── Poids atomiques déclarés (IUPAC 2021, g/mol) ────────────────────────────
M_C, M_H, M_O = 12.011, 1.008, 15.999
M_N, M_P, M_K, M_CL = 14.007, 30.974, 39.098, 35.45
M_CO2 = M_C + 2.0 * M_O
M_H2O = 2.0 * M_H + M_O
M_O2 = 2.0 * M_O
M_CH2O = M_C + 2.0 * M_H + M_O            # 30,026 — unité de biomasse
M_Glucose = 6.0 * M_C + 6.0 * M_H2O       # 180,156
M_NH3 = M_N + 3.0 * M_H
M_P2O5 = 2.0 * M_P + 5.0 * M_O
M_K2O = 2.0 * M_K + M_O
M_KCL = M_K + M_CL

LUMIERE_ROUGE_NM = 680.0                  # λ de référence des réactions photochimiques
PHOTONS_CO2_MIN = 4.0                     # schéma en Z : 2 NADPH + 3 ATP par CO2
PHOTONS_CO2_DECLARES = 8.5                # mesure en feuille, ATP cyclique inclus — déclaré
DELTA_G_GLUCOSE_KJ_MOL = 2870.0           # énergie chimique stockée — déclarée

# Température du corps noir solaire et bandes
T_PHOTOSPHERE = 5772.0
PAR_BAS, PAR_HAUT = 400e-9, 700e-9

# Rendements, besoins et matériaux DÉCLARÉS (littérature agronomique)
RENDIMENT_BLE_T_HA = 3.5
RENDIMENT_MAIS_T_HA = 10.0
KCAL_PAR_T_BLE = 3.4e6
KCAL_PAR_T_MAIS = 3.65e6
KCAL_PERSONNE_JOUR = 2100.0
POPULATION = 8.0e9
JOUR_KCAL = 4184.0                        # 1 kcal thermique — définition
PROTEINE_BLE_pct = 12.0
FACTEUR_N_PROTEINE = 5.7                  # blé — déclaré
AZOTE_APPLIQUE_KG_HA = 120.0
N_HABER_GJ_T_NH3 = 31.0                   # 28–34 GJ/t — déclaré
ET_BLE_MM_AN = 500.0
RN_DISPONIBLE_W_M2 = 100.0                # énergie nette d'une culture de référence — déclaré
EFFICACITE_GOUTTELETTE = 0.90
EFFICACITE_SUPERFICIELLE = 0.60
EPS_C3_G_MJ = 1.5                         # g matière sèche / MJ de rayonnement global — déclaré
EPS_C4_G_MJ = 3.0                         # déclaré
FRACTION_PAR_SOL_declaree = 0.45          # part 400–700 nm au sol — déclaré
INSOLATION_TERRE_AGRAVE_W_M2 = 220.0      # moyenne annuelle sur terres cultivables — déclaré
SURFACE_CULTIVABLE_HA = 1.4e9
DELTA_13C_C3_POURMILLE = 19.5             # discrimination mesurée — déclarée
A_DIFFUSION, B_RUBISCO = 4.4, 27.0        #‰ — déclarés (C3)
CA_CO2_PPM = 420.0                        # CO2 atmosphérique actuel — déclaré
CA_PREINDUSTRIEL_PPM = 300.0
DLI_TOMATE_MOL_M2_JOUR = 15.0             # daily light integral serre haute technologie — déclaré
U_MOL_PAR_JOULE_LED = 2.8                 # µmol/J en système 660 nm — déclaré (top commercial)
RENDEMENT_SERRE_TOMATE_KG_M2_AN = 40.0    # déclaré
PHOTOPERIODE_H = 16.0

# Matériaux déclarés
PE_FILM_EPAISSEUR_M = 30e-6
PE_MASSE_VOL_KG_M3 = 920.0
SAP_RETENTION_DOUCE = 300.0               # × sa masse — déclaré
SAP_RETENTION_SOLUTION = 50.0             # en solution nutritive — déclaré
BIOCHAR_SURFACE_M2_G = 200.0              # BET — déclaré
BIOCARBONE_C_pct = 60.0
ROCHE_PHOSPHATE_P2O5_pct = 30.0
KCL_K2O_pct = 60.0
BIOCHAR_T_HA = 10.0
P_KG_HA, K_KG_HA = 25.0, 30.0
SOL_PROFONDEUR_M = 0.30
SOL_MASSE_VOL_T_M3 = 1.3                  # dense apparente — déclaré
SOL_PRODUCTION_T_HA_AN = 0.5              # formation in situ — déclaré
SOL_ÉROSION_T_HA_AN = 10.0                # travail mécanique intensif — déclaré

SOURCE = {
    "herite_de": "electricite_abondance.py (21 EQ) puis eau_abondance.py (15 EQ)",
    "video_origine": ELEC.SOURCE["titre"],
    "video_url": ELEC.SOURCE["url"],
    "transcript": ELEC.SOURCE["transcript"],
    "statut_contenu": "la vidéo ne fournit AUCUNE donnée agricole : ni les rendements, "
                      "ni la photosynthèse, ni les matériaux n'en sont extraits",
    "fil_conducteur": "Thalès → van 't Hoff → Boussingault (loi du minimum) → Liebig → "
                      "Haber/Bosch → Blackman → Calvin → Monteith (RUE) → Allan/Hoekstra "
                      "(eau virtuelle)",
}

STATUTS = ELEC.STATUTS


def _f(x: float, n: int = 6) -> str:
    return ELEC._f(x, n)


def _exp(x: float, n: int = 4) -> str:
    return ELEC._exp(x, n)


def _fa(x: float) -> str:
    return f"{x:.2f}"


def _simpson(y: List[float], pas: float) -> float:
    """Simpson composite sur un nombre impair de points."""
    s = y[0] + y[-1]
    s += 4.0 * sum(y[1:-1:2])
    s += 2.0 * sum(y[2:-1:2])
    return s * pas / 3.0


# ============================================================================
# ÉQUATIONS
# ============================================================================

def stoechiometrie_photosynthese() -> Dict[str, Any]:
    """EQ-01 — 6 CO2 + 6 H2O → C6H12O6 + 6 O2 : le bilan atomique avant de parler rendement."""
    reactifs = {"C": 6.0, "H": 12.0, "O": 18.0}
    produits = {"C": 6.0, "H": 12.0, "O": 18.0}
    masse_reactifs = 6.0 * M_CO2 + 6.0 * M_H2O
    masse_produits = M_Glucose + 6.0 * M_O2
    return {
        "equation": "6 CO2 + 6 H2O + lumière → C6H12O6 + 6 O2",
        "masses_molaires_g_mol": {"CO2": M_CO2, "H2O": M_H2O, "O2": M_O2,
                                  "C6H12O6": M_Glucose, "CH2O": M_CH2O},
        "atomes_reactifs": reactifs,
        "atomes_produits": produits,
        "desequilibre_atomique": max(abs(reactifs[k] - produits[k]) for k in reactifs),
        "masse_reactifs_g": masse_reactifs,
        "masse_produits_g": masse_produits,
        "desequilibre_massique": abs(masse_reactifs - masse_produits),
        "co2_par_g_biomasse": M_CO2 / M_CH2O,
        "o2_par_g_biomasse": M_O2 / M_CH2O,
        "carbone_fraction_biomasse": M_C / M_CH2O,
    }


def exigence_quantique() -> Dict[str, Any]:
    """EQ-02 — le prix en photons : 4 au minimum, ~8,5 mesurés, par CO2 fixé."""
    e_photon_J = H * C / (LUMIERE_ROUGE_NM * 1e-9)
    einstein_kJ = e_photon_J * N_A / 1000.0
    e_photon_eV = ELEC.EV_NM / LUMIERE_ROUGE_NM
    einstein_par_eV = e_photon_eV * N_A * E_CHARGE_KJ / 1000.0
    energie_min = PHOTONS_CO2_MIN * einstein_kJ          # kJ par mole de CO2
    energie_declaree = PHOTONS_CO2_DECLARES * einstein_kJ
    chimie_kj_par_mol_co2 = DELTA_G_GLUCOSE_KJ_MOL / 6.0
    return {
        "lambda_nm": LUMIERE_ROUGE_NM,
        "e_photon_J": e_photon_J,
        "e_photon_eV": e_photon_eV,
        "einstein_kJ_par_mol_photons": einstein_kJ,
        "einstein_par_eV_kJ": einstein_par_eV,
        "coherence_deux_voies": abs(einstein_kJ - einstein_par_eV) / einstein_kJ,
        "photons_par_co2_min": PHOTONS_CO2_MIN,
        "photons_par_co2_declares": PHOTONS_CO2_DECLARES,
        "energie_min_kj_par_mol_co2": energie_min,
        "energie_declaree_kj_par_mol_co2": energie_declaree,
        "energie_chimie_kj_par_mol_co2": chimie_kj_par_mol_co2,
        "rendement_plafond_min": chimie_kj_par_mol_co2 / energie_min,
        "rendement_plafond_mesure": chimie_kj_par_mol_co2 / energie_declaree,
        "surcout_photons": PHOTONS_CO2_DECLARES / PHOTONS_CO2_MIN,
    }


E_CHARGE_KJ = ELEC.E_CHARGE * 1.0     # C/mol → J par eV (96 485 J/mol par eV)


def spectre_PAR() -> Dict[str, Any]:
    """EQ-03 — combien de photons dans 400–700 nm : intégration du corps noir 5772 K."""
    hc = H * C
    n = 100_001
    lam_lo, lam_hi = 1e-8, 1e-4
    pas_l = (lam_hi - lam_lo) / (n - 1)

    def exitance(lam: float) -> float:
        x = hc / (lam * K_B * T_PHOTOSPHERE)
        if x > 700.0:
            return 0.0
        return (2.0 * math.pi * H * C * C) / lam ** 5 / (math.exp(x) - 1.0)

    grille = [lam_lo + i * pas_l for i in range(n)]
    m_tout = [exitance(l) for l in grille]
    n_tout = [m * l / hc for m, l in zip(m_tout, grille)]
    total_E = _simpson(m_tout, pas_l)
    total_N = _simpson(n_tout, pas_l)

    nb = 30_001
    pas_b = (PAR_HAUT - PAR_BAS) / (nb - 1)
    grille_b = [PAR_BAS + i * pas_b for i in range(nb)]
    m_b = [exitance(l) for l in grille_b]
    n_b = [m * l / hc for m, l in zip(m_b, grille_b)]
    par_E = _simpson(m_b, pas_b)
    par_N = _simpson(n_b, pas_b)

    stefan = SIGMA * T_PHOTOSPHERE ** 4
    umol_par_J_par = par_N / total_E * 1e6 / N_A
    umol_par_J_dans_bande = par_N / par_E * 1e6 / N_A
    return {
        "T_photosphere_K": T_PHOTOSPHERE,
        "exitance_integree_W_m2": total_E,
        "exitance_stefan_W_m2": stefan,
        "ecart_integration_stefan": abs(total_E - stefan) / stefan,
        "fraction_energie_PAR": par_E / total_E,
        "fraction_photons_PAR": par_N / total_N,
        "umol_par_joule_de_rayonnement_total": umol_par_J_par,
        "umol_par_joule_dans_la_bande": umol_par_J_dans_bande,
        "ppfd_1000_W_m2_hors_atmosphere": 1000.0 * umol_par_J_par,
        "ppfd_declare_au_sol_umol": 2000.0,
        "ppfd_1000_W_m2_au_sol_45pct": 1000.0 * FRACTION_PAR_SOL_declaree * umol_par_J_dans_bande,
        "lambda_effectif_bande_nm": hc / (par_E / par_N) * 1e9,
        "note": "le corps noir seul sous-estime le PAR au sol : l'atmosphère retire l'infrarouge, "
                "la bande 400–700 nm passe de 37 à ~45 %",
    }


def budget_solaire_agricole() -> Dict[str, Any]:
    """EQ-04 — le rayonnement que la photosynthèse reçoit, contre ce que l'assiette demande."""
    elec = ELEC.budget_solaire_terre()
    surface_m2 = SURFACE_CULTIVABLE_HA * 1e4
    par_W = INSOLATION_TERRE_AGRAVE_W_M2 * FRACTION_PAR_SOL_declaree * surface_m2
    par_J_an = par_W * 365.0 * 86400.0
    demande_kcal_an = POPULATION * KCAL_PERSONNE_JOUR * 365.0
    demande_J_an = demande_kcal_an * JOUR_KCAL
    rendements = {}
    for eta in (0.002, 0.005, 0.01, 0.02):
        rendements[f"{100 * eta:.1f} %"] = par_J_an * eta / demande_J_an
    return {
        "irradiance_hors_atmosphere_W_m2": elec["irradiance_hors_atmosphere_W_m2"],
        "insolation_moyenne_declaree_W_m2": INSOLATION_TERRE_AGRAVE_W_M2,
        "surface_cultivable_m2": surface_m2,
        "puissance_PAR_W": par_W,
        "energie_PAR_J_par_an": par_J_an,
        "energie_PAR_ZJ_par_an": par_J_an / 1e21,
        "demande_alimentaire_J_par_an": demande_J_an,
        "demande_alimentaire_ZJ_par_an": demande_J_an / 1e21,
        "facteurs_de_conversion": rendements,
        "ratio_par_sur_consommation_energie_mondiale": par_W / elec["consommation_mondiale_declaree_W"],
        "limite": "le goulot n'est pas le nombre de joules : il est dans l'eau, l'azote, le sol "
                  "et la saison — voir EQ-05 à EQ-15",
    }


def rayonnement_use_efficiency() -> Dict[str, Any]:
    """EQ-05 — Monteith : biomasse = ε · fAPAR · PAR absorbé, borné par EQ-02."""
    einstein_kJ = H * C / (LUMIERE_ROUGE_NM * 1e-9) * N_A / 1000.0
    einstein_par_MJ = 1e6 / (einstein_kJ * 1000.0)
    plafond_min = einstein_par_MJ / PHOTONS_CO2_MIN * M_CH2O          # g/MJ PAR
    plafond_mesure = einstein_par_MJ / PHOTONS_CO2_DECLARES * M_CH2O
    global_par = EPS_C3_G_MJ / FRACTION_PAR_SOL_declaree              # ε rapporté au PAR
    global_par_c4 = EPS_C4_G_MJ / FRACTION_PAR_SOL_declaree
    return {
        "einstein_kJ": einstein_kJ,
        "einstein_par_MJ": einstein_par_MJ,
        "plafond_theorique_g_par_MJ_PAR": plafond_min,
        "plafond_a_8_5_photons_g_par_MJ_PAR": plafond_mesure,
        "eps_C3_declare_g_par_MJ_global": EPS_C3_G_MJ,
        "eps_C4_declare_g_par_MJ_global": EPS_C4_G_MJ,
        "eps_C3_rapporte_au_PAR": global_par,
        "eps_C4_rapporte_au_PAR": global_par_c4,
        "part_du_plafond_C3": global_par / plafond_mesure,
        "part_du_plafond_C4": global_par_c4 / plafond_mesure,
        "fapar_declare": 0.85,
        "exemple_ble_par_jour_MJ_m2": 20.0 * FRACTION_PAR_SOL_declaree,
        "biomasse_par_jour_g_m2": 20.0 * EPS_C3_G_MJ * 0.85,
    }


def voies_photosynthetiques() -> Dict[str, Any]:
    """EQ-06 — C3, C4, CAM : trois solutions au même problème (l'oxygène de Rubisco)."""
    c3 = {"ε_g_MJ": EPS_C3_G_MJ, "compensation_CO2_ppm": 40.0, "optimum_T_C": 22.0,
          "wue_relative": 1.0}
    c4 = {"ε_g_MJ": EPS_C4_G_MJ, "compensation_CO2_ppm": 8.0, "optimum_T_C": 33.0,
          "wue_relative": 2.0}
    cam = {"ε_g_MJ": 0.8, "compensation_CO2_ppm": 20.0, "optimum_T_C": 28.0,
           "wue_relative": 3.5}
    speciacite_rubisco = 85.0                                      # CO2/O2 — déclaré
    cout_photorespiration = 1.0 - PHOTONS_CO2_MIN / PHOTONS_CO2_DECLARES
    return {
        "voies": {"C3": c3, "C4": c4, "CAM": cam},
        "gain_C4_sur_C3": c4["ε_g_MJ"] / c3["ε_g_MJ"],
        "specificite_rubisco_declaree": speciacite_rubisco,
        "surcout_quantique_feuille": PHOTONS_CO2_DECLARES / PHOTONS_CO2_MIN,
        "part_perdue_par_photorespiration": cout_photorespiration,
        "seuil_CO2_effondrement_C3_ppm": 50.0,
        "note": "le C4 n'a pas inventé une chimie meilleure : il a ajouté une pompe à CO2 "
                "devant Rubisco — la limite est énergétique (ATP), pas catalytique",
    }


def loi_du_minimum() -> Dict[str, Any]:
    """EQ-07 — Liebig : le baril ne se remplit pas au niveau de la planche la plus haute."""
    planches = {"lumière": 0.90, "azote": 0.80, "phosphore": 0.40, "potasse": 1.00, "eau": 0.70}
    rendement_max_t_ha = RENDIMENT_BLE_T_HA

    def rendement(facteurs: Dict[str, float]) -> float:
        """Une planche remplie au-delà de 1 ne déborde pas : le facteur est saturé à 1."""
        return rendement_max_t_ha * min(min(v, 1.0) for v in facteurs.values())

    base = dict(planches)
    y0 = rendement(base)
    double_p = dict(base, phosphore=0.80)
    y1 = rendement(double_p)
    triple_p = dict(double_p, phosphore=1.60)
    y2 = rendement(triple_p)
    double_eau = dict(triple_p, eau=1.40)
    y3 = rendement(double_eau)
    sature = dict(double_eau, **{"lumière": 1.00, "azote": 1.00})
    y4 = rendement(sature)
    return {
        "planches": planches,
        "rendement_max_t_ha": rendement_max_t_ha,
        "serie": [{"etat": "départ (P limitant)", "phosphore": base["phosphore"],
                   "rendement_t_ha": y0},
                  {"etat": "P ×2", "phosphore": double_p["phosphore"], "rendement_t_ha": y1},
                  {"etat": "P ×4", "phosphore": triple_p["phosphore"], "rendement_t_ha": y2},
                  {"etat": "P ×4 et eau ×2", "phosphore": double_eau["phosphore"],
                   "rendement_t_ha": y3},
                  {"etat": "toutes les planches ≥ 1", "phosphore": sature["phosphore"],
                   "rendement_t_ha": y4}],
        "y0": y0, "y1": y1, "y2": y2, "y3": y3, "y4": y4,
        "limitant_depart": min(planches, key=planches.get),
        "limitant_depart": min(base, key=lambda k: min(base[k], 1.0)),
        "limitant_apres_P_x4": min(triple_p, key=lambda k: min(triple_p[k], 1.0)),
        "saut_attendu_apres_P": rendement_max_t_ha * 0.70,
        "plate_apres_P_x4": abs(y2 - y1) < 1e-12,
        "loi": "doubler un facteur non limitant ne change rien : le test est exact, "
               "ce n'est pas une opinion",
    }


def azote_haber_bosch() -> Dict[str, Any]:
    """EQ-08 — l'azote acheté : de NH3 au blé, en énergie."""
    fraction_N = M_N / M_NH3
    mj_par_kg_N = N_HABER_GJ_T_NH3 / fraction_N      # 1 GJ/t ≡ 1 MJ/kg : même grandeur
    azote_grain_kg_ha = RENDIMENT_BLE_T_HA * 1000.0 * (PROTEINE_BLE_pct / 100.0) / FACTEUR_N_PROTEINE
    noue = azote_grain_kg_ha / AZOTE_APPLIQUE_KG_HA
    energie_n_gj_ha = AZOTE_APPLIQUE_KG_HA * mj_par_kg_N / 1000.0
    return {
        "M_NH3_g_mol": M_NH3,
        "fraction_N_dans_NH3": fraction_N,
        "habere_gj_par_t_nh3_declare": N_HABER_GJ_T_NH3,
        "MJ_par_kg_N": mj_par_kg_N,
        "proteine_pct": PROTEINE_BLE_pct,
        "facteur_N_proteine": FACTEUR_N_PROTEINE,
        "azote_du_grain_kg_ha": azote_grain_kg_ha,
        "azote_applique_kg_ha": AZOTE_APPLIQUE_KG_HA,
        "noue_recuperation_grain": noue,
        "energie_azote_GJ_ha": energie_n_gj_ha,
        "energie_azote_kwh_par_t_grain": energie_n_gj_ha * 1000.0 / RENDIMENT_BLE_T_HA / 3.6,
        "nh3_kg_ha": AZOTE_APPLIQUE_KG_HA / fraction_N,
        "limite": "la NUE dépend de la date, de la forme (urée, ammonitrate) et du sol : "
                  "le chiffre ici est celui d'un declared, pas une mesure du dépôt",
    }


def evapotranspiration() -> Dict[str, Any]:
    """EQ-09 — l'eau part en vapeur : le même L que le dossier EAU."""
    L = EAU.L_CHALEUR_LATENTE
    flux_kg_m2_s = RN_DISPONIBLE_W_M2 / L
    mm_par_jour = flux_kg_m2_s * 86400.0 * 1000.0 / EAU.RHO_EAU_DOUCE
    m3_par_ha_par_mm = 10_000.0 * 0.001
    besoin_ha = ET_BLE_MM_AN * m3_par_ha_par_mm
    return {
        "L_J_kg": L,
        "Rn_W_m2_declare": RN_DISPONIBLE_W_M2,
        "flux_kg_m2_s": flux_kg_m2_s,
        "mm_par_jour": mm_par_jour,
        "mm_par_an_si_constant": mm_par_jour * 365.0,
        "m3_par_ha_par_mm": m3_par_ha_par_mm,
        "et_ble_mm_an_declare": ET_BLE_MM_AN,
        "besoin_m3_ha_an": besoin_ha,
        "besoin_litre_par_kg_grain": besoin_ha * 1000.0 / (RENDIMENT_BLE_T_HA * 1000.0),
        "coherence_avec_eau_1mm": abs(m3_par_ha_par_mm * 1000.0 / 10_000.0
                                      - EAU.vapeur_eau_air()["pluie_de_1mm_en_L_par_m2"])
                                  / EAU.vapeur_eau_air()["pluie_de_1mm_en_L_par_m2"],
        "energie_evaporer_ha_J": besoin_ha * EAU.RHO_EAU_DOUCE * L,
    }


def energie_irrigation() -> Dict[str, Any]:
    """EQ-10 — pomper l'eau du blé : le kWh/m³ vient du dossier EAU, pas d'un devis."""
    kwh_m3 = EAU.pompage()["table"][1]["kWh_par_m3_rendement"]      # 50 m, η 0,65
    besoin = evapotranspiration()["besoin_m3_ha_an"]
    brut_superficiel = besoin / EFFICACITE_SUPERFICIELLE
    brut_gouttelette = besoin / EFFICACITE_GOUTTELETTE
    return {
        "kWh_par_m3_depuis_eau": kwh_m3,
        "besoin_net_m3_ha": besoin,
        "economie_kWh_par_ha": kwh_m3 * (brut_superficiel - brut_gouttelette),
        "energie_gouttelette_GJ_ha": kwh_m3 * brut_gouttelette * KWH_J / 1e9,
        "energie_superficielle_GJ_ha": kwh_m3 * brut_superficiel * KWH_J / 1e9,
        "eau_prelevee_gouttelette_m3_ha": brut_gouttelette,
        "eau_prelevee_superficielle_m3_ha": brut_superficiel,
        "kwh_par_tonne_gouttelette": kwh_m3 * brut_gouttelette / RENDIMENT_BLE_T_HA,
        "ratio_irrigation_sur_azote": (kwh_m3 * brut_gouttelette * KWH_J / 1e9)
                                      / azote_haber_bosch()["energie_azote_GJ_ha"],
        "coherence_identite_rho_g_h": abs(kwh_m3 - EAU.RHO_EAU_DOUCE * G0 * 50.0 / KWH_J / 0.65)
                                      / kwh_m3,
    }


def eau_virtuelle() -> Dict[str, Any]:
    """EQ-11 — deux chemins vers le même litre : EQ-09 ici, EQ-12 du dossier EAU."""
    declare = EAU.eau_par_aliment()["litres_par_kg"]["blé"]
    derive = evapotranspiration()["besoin_litre_par_kg_grain"]
    return {
        "litres_par_kg_declareEAU": declare,
        "litres_par_kg_derive_agriculture": derive,
        "ecart_relatif": abs(declare - derive) / declare,
        "grise_declare_pct": 20.0,
        "verte_pct": 70.0,
        "bleue_pct": 10.0,
        "somme_compartiments": 100.0,
        "m3_ha_par_an": evapotranspiration()["besoin_m3_ha_an"],
        "litres_par_personne_an": declare * 90.0,
        "m3_par_personne_an": declare * 90.0 / 1000.0,
        "note": "l'eau verte (pluie) ne s'achète pas ; la bleue (irrigation) se compte en kWh",
    }


def discrimination_carbone() -> Dict[str, Any]:
    """EQ-12 — lire la soif d'une plante dans ses isotopes : Δ13C ⇒ ci/ca ⇒ efficience."""
    ci_sur_ca = (DELTA_13C_C3_POURMILLE - A_DIFFUSION) / (B_RUBISCO - A_DIFFUSION)
    wue_actuelle = CA_CO2_PPM * (1.0 - ci_sur_ca)
    wue_preindustrielle = CA_PREINDUSTRIEL_PPM * (1.0 - ci_sur_ca)
    gain = wue_actuelle / wue_preindustrielle
    return {
        "a_diffusion_pourmille": A_DIFFUSION,
        "b_rubisco_pourmille": B_RUBISCO,
        "delta_mesure_pourmille": DELTA_13C_C3_POURMILLE,
        "ci_sur_ca": ci_sur_ca,
        "ca_actuel_ppm": CA_CO2_PPM,
        "ca_preindustriel_ppm": CA_PREINDUSTRIEL_PPM,
        "wue_indice_actuel": wue_actuelle,
        "wue_indice_preindustriel": wue_preindustrielle,
        "gain_d_efficience_hydrique": gain - 1.0,
        "proportionnalite_exacte": abs(gain - CA_CO2_PPM / CA_PREINDUSTRIEL_PPM),
        "limite": "à Δ inchangé seulement : si la plante referme ses stomates, ci/ca baisse et "
                  "le gain se mange en photorespiration",
    }


def calories_par_hectare() -> Dict[str, Any]:
    """EQ-13 — ce qu'une hectare nourrit de personnes, en kcal et en jours."""
    def ligne(tonnes: float, kcal_t: float) -> Dict[str, float]:
        kcal_ha = tonnes * kcal_t
        return {"tonnes_par_ha": tonnes, "kcal_par_tonne": kcal_t, "kcal_par_ha": kcal_ha,
                "personnes_par_ha": kcal_ha / (KCAL_PERSONNE_JOUR * 365.0),
                "jours_personne_par_ha": kcal_ha / KCAL_PERSONNE_JOUR}

    ble, mais = ligne(RENDIMENT_BLE_T_HA, KCAL_PAR_T_BLE), ligne(RENDIMENT_MAIS_T_HA, KCAL_PAR_T_MAIS)
    return {
        "ble": ble, "mais": mais,
        "rapport_mais_sur_ble": mais["personnes_par_ha"] / ble["personnes_par_ha"],
        "kcal_par_kg_ble": KCAL_PAR_T_BLE / 1000.0,
        "personnes_par_ha_monde_reel_ble_2t5": ligne(2.5, KCAL_PAR_T_BLE)["personnes_par_ha"],
        "note": "rendements déclarés : 3,5 t/ha de blé et 10 t/ha de maïs sont des moyennes "
                "de bonnes terres irriguées, pas une moyenne mondiale",
    }


def surface_nourrir_le_monde() -> Dict[str, Any]:
    """EQ-14 — surface théorique pour 8 milliards, en régime céréalier simple."""
    cal = calories_par_hectare()
    demande_kcal_an = POPULATION * KCAL_PERSONNE_JOUR * 365.0
    surface_ble = demande_kcal_an / cal["ble"]["kcal_par_ha"]
    surface_mais = demande_kcal_an / cal["mais"]["kcal_par_ha"]
    part_produits_animaux = 0.25            # déclaration d'apport calorique indirect
    indice_conversion = 6.0                 # kg d'aliment par kg de produit animal — déclaré
    surface_avec_elevage = (surface_ble * (1.0 - part_produits_animaux)
                            + surface_ble * part_produits_animaux * indice_conversion)
    return {
        "demande_kcal_par_an": demande_kcal_an,
        "surface_ble_ha": surface_ble,
        "surface_mais_ha": surface_mais,
        "surface_cultivable_disponible_ha": SURFACE_CULTIVABLE_HA,
        "marge_cerealiere": SURFACE_CULTIVABLE_HA / surface_ble,
        "part_calorique_animale_declaree": part_produits_animaux,
        "indice_conversion_declare": indice_conversion,
        "surface_avec_elevage_ha": surface_avec_elevage,
        "marge_avec_elevage": SURFACE_CULTIVABLE_HA / surface_avec_elevage,
        "limite": "ce calcul ignore l'eau, l'azote, la saison, le gaspillage (≈ 30 %) et les "
                  "sols : il ne prouve rien, il borne l'ordre de grandeur",
    }


def dette_de_sol() -> Dict[str, Any]:
    """EQ-15 — le sol est un stock, l'érosion un débit : la dette se calcule."""
    masse_sol_t_ha = SOL_PROFONDEUR_M * 10_000.0 * SOL_MASSE_VOL_T_M3
    ans_avant_perte = masse_sol_t_ha / SOL_ÉROSION_T_HA_AN
    ans_pour_reformer = masse_sol_t_ha / SOL_PRODUCTION_T_HA_AN
    return {
        "masse_horizon_t_ha": masse_sol_t_ha,
        "profondeur_m": SOL_PROFONDEUR_M,
        "densite_apparente_t_m3": SOL_MASSE_VOL_T_M3,
        "production_declaree_t_ha_an": SOL_PRODUCTION_T_HA_AN,
        "erosion_declaree_t_ha_an": SOL_ÉROSION_T_HA_AN,
        "ratio_erosion_sur_formation": SOL_ÉROSION_T_HA_AN / SOL_PRODUCTION_T_HA_AN,
        "annees_avant_horizon_perdu": ans_avant_perte,
        "annees_pour_reformer_l_horizon": ans_pour_reformer,
        "dette_nette_t_ha_an": SOL_ÉROSION_T_HA_AN - SOL_PRODUCTION_T_HA_AN,
        "mm_par_an_equivalent_erosion": SOL_ÉROSION_T_HA_AN / (10_000.0 * SOL_MASSE_VOL_T_M3) * 1000.0,
        "seuil_tolerable_declare_t_ha_an": 2.0,
        "note": "le sol se forme à ~0,1–1 mm/an : toute érosion au-delà est un emprunt, "
                "pas un coût d'exploitation",
    }


def serre_led_bilan() -> Dict[str, Any]:
    """EQ-16 — la lumière achetée : du DLI au kWh, du kWh au kilogramme de tomate."""
    einstein_J = H * C / (LUMIERE_ROUGE_NM * 1e-9) * N_A
    kwh_minimal = DLI_TOMATE_MOL_M2_JOUR * einstein_J / KWH_J
    j_systeme = DLI_TOMATE_MOL_M2_JOUR * 1e6 / U_MOL_PAR_JOULE_LED
    kwh_systeme = j_systeme / KWH_J
    wpe = einstein_J / (1e6 / U_MOL_PAR_JOULE_LED)
    ppfd = DLI_TOMATE_MOL_M2_JOUR * 1e6 / (PHOTOPERIODE_H * 3600.0)
    W_photon_m2 = ppfd * 1e-6 * einstein_J
    return {
        "dli_mol_m2_jour": DLI_TOMATE_MOL_M2_JOUR,
        "einstein_J_par_mol_photons": einstein_J,
        "kWh_m2_jour_minimum_photons": kwh_minimal,
        "kWh_m2_jour_systeme_led": kwh_systeme,
        "umol_par_joule_declare": U_MOL_PAR_JOULE_LED,
        "wall_plug_efficiency": wpe,
        "photoperiode_h": PHOTOPERIODE_H,
        "ppfd_umol_m2_s": ppfd,
        "W_photon_m2": W_photon_m2,
        "W_electrique_m2": W_photon_m2 / wpe,
        "kWh_par_m2_an": kwh_systeme * 365.0,
        "rendement_serre_kg_m2_an_declare": RENDEMENT_SERRE_TOMATE_KG_M2_AN,
        "kWh_par_kg_tomate_lumiere_seule": kwh_systeme * 365.0 / RENDEMENT_SERRE_TOMATE_KG_M2_AN,
        "rapport_systeme_sur_minimum": kwh_systeme / kwh_minimal,
    }


def materiaux_optimisants() -> Dict[str, Any]:
    """EQ-17 — les matériaux, dimensionnés par les équations précédentes (valeurs déclarées)."""
    azote = azote_haber_bosch()
    irr = energie_irrigation()
    led = serre_led_bilan()
    film_kg_ha = PE_FILM_EPAISSEUR_M * 10_000.0 * PE_MASSE_VOL_KG_M3
    tampon_mm = 20.0
    eau_a_retention_kg_ha = tampon_mm * 10.0 * 1000.0            # 1 mm = 10 m³/ha = 10 000 kg
    sap_douce_kg_ha = eau_a_retention_kg_ha / SAP_RETENTION_DOUCE
    sap_solution_kg_ha = eau_a_retention_kg_ha / SAP_RETENTION_SOLUTION
    biochar_g_ha = BIOCHAR_T_HA * 1e6
    surface_interne_m2 = biochar_g_ha * BIOCHAR_SURFACE_M2_G
    p2o5_kg_ha = P_KG_HA / (2.0 * M_P / M_P2O5)
    minerai_kg_ha = p2o5_kg_ha / (ROCHE_PHOSPHATE_P2O5_pct / 100.0)
    k2o_kg_ha = K_KG_HA / (2.0 * M_K / M_K2O)
    kcl_kg_ha = k2o_kg_ha / (KCL_K2O_pct / 100.0)
    return {
        "materiaux": [
            {"materiau": "azote ammoniacal ( Haber-Bosch, catalyseur fer )",
             "quantite_par_ha": azote["nh3_kg_ha"], "unite": "kg NH3/an",
             "energie_par_ha_GJ": azote["energie_azote_GJ_ha"], "equation": "EQ-08"},
            {"materiau": "film polyéthylène de paillage, 30 µm",
             "quantite_par_ha": film_kg_ha, "unite": "kg/ha",
             "energie_par_ha_GJ": None, "equation": "géométrie × densité déclarée"},
            {"materiau": "hydrogel (SAP) pour tamponner 20 mm",
             "quantite_par_ha": sap_douce_kg_ha, "unite": "kg/ha en eau douce",
             "quantite_en_solution_kg_ha": sap_solution_kg_ha,
             "energie_par_ha_GJ": None, "equation": "EQ-09 (1 mm = 10 m³/ha)"},
            {"materiau": "biochar, 10 t/ha, 60 % de carbone",
             "quantite_par_ha": BIOCHAR_T_HA * 1000.0, "unite": "kg/ha",
             "surface_interne_m2_ha": surface_interne_m2,
             "surface_interne_km2_ha": surface_interne_m2 / 1e6,
             "energie_par_ha_GJ": None, "equation": "stock P4 — surface BET déclarée"},
            {"materiau": "minerai phosphaté (30 % P2O5) pour 25 kg P/ha",
             "quantite_par_ha": minerai_kg_ha, "unite": "kg/ha",
             "energie_par_ha_GJ": None, "equation": "stoichiométrie P2O5"},
            {"materiau": "potasse KCl (60 % K2O) pour 30 kg K/ha",
             "quantite_par_ha": kcl_kg_ha, "unite": "kg/ha",
             "energie_par_ha_GJ": None, "equation": "stoichiométrie K2O"},
            {"materiau": "LED 660 nm (AlGaInP) pour DLI 15 mol",
             "quantite_par_ha": led["W_electrique_m2"] * 1e4 / 1000.0, "unite": "kW installés/ha",
             "energie_par_ha_GJ": led["kWh_par_m2_an"] * KWH_J / 1e9 * 1e4,
             "equation": "EQ-16 (annualisé, photopériode 16 h)"},
            {"materiau": "goutte-à-goutte (eau prélevée)",
             "quantite_par_ha": irr["eau_prelevee_gouttelette_m3_ha"], "unite": "m³/ha",
             "energie_par_ha_GJ": irr["energie_gouttelette_GJ_ha"], "equation": "EQ-10"},
        ],
        "fractions_stoechiometriques": {
            "N_dans_NH3": M_N / M_NH3,
            "P_dans_P2O5": 2.0 * M_P / M_P2O5,
            "K_dans_K2O": 2.0 * M_K / M_K2O,
            "K2O_dans_KCl": M_K2O / (2.0 * M_KCL),
            "C_dans_CH2O": M_C / M_CH2O,
        },
        "statut": "les quantités sont calculées ; les performances des matériaux sont déclarées ; "
                  "la colonne d'énergie est en GJ par hectare et par an",
    }


def ponts_dossier() -> List[Dict[str, str]]:
    """EQ-18 — grille de lecture du dossier appliquée à l'agriculture (analogies déclarées)."""
    return [
        {"pilier": "P1 — Scellement",
         "dossier": "valeur = empreinte SHA-256 du fichier qui la porte",
         "agriculture": "le plafond quantique (EQ-02) ne se négocie pas : toute promesse "
                        "au-dessus de 20 g/MJ PAR est une erreur de compte",
         "limite": "le plafond ne dit rien du rendement d'une parcelle donnée"},
        {"pilier": "P2 — Horloge",
         "dossier": "tick 7,402 ns, 50 Hz réseau",
         "agriculture": "photopériode, saison, délai de charge d'un sol : EQ-16 la compte en "
                        "heures, EQ-15 en siècles",
         "limite": "l'horloge agronomique est biologique, pas électronique"},
        {"pilier": "P3 — Tolérance à la panne",
         "dossier": "redondance, code correcteur",
         "agriculture": "diversité variétale et réserves d'eau : EQ-07 montre qu'une seule "
                        "planche borne tout le baril",
         "limite": "la redondance générique n'est pas un théorème de codage"},
        {"pilier": "P4 — Registre et dette",
         "dossier": "qui doit quoi à qui",
         "agriculture": "EQ-15 dette de sol, EQ-11 eau virtuelle, EQ-12 signature isotopique : "
                        "trois comptabilités mesurables",
         "limite": "les volumes exacts dépendent du parcellaire ; le cadre est posé, pas l'inventaire"},
    ]


# ============================================================================
# ASSEMBLAGE
# ============================================================================

def _eq(id_: str, chemin: str, formule: str, resultat: str, statut: str,
        detail: Any) -> Dict[str, Any]:
    return {"id": id_, "chemin": chemin, "formule": formule,
            "resultat": resultat, "statut": statut, "detail": detail}


def resoudre() -> Dict[str, Any]:
    st, eq2, sp = stoechiometrie_photosynthese(), exigence_quantique(), spectre_PAR()
    bs, rue, voy, lim = budget_solaire_agricole(), rayonnement_use_efficiency(), \
        voies_photosynthetiques(), loi_du_minimum()
    az, ev, ir, vv = azote_haber_bosch(), evapotranspiration(), energie_irrigation(), eau_virtuelle()
    dc, cal, sf, ds = discrimination_carbone(), calories_par_hectare(), \
        surface_nourrir_le_monde(), dette_de_sol()
    sl, ma, pd = serre_led_bilan(), materiaux_optimisants(), ponts_dossier()

    eqs = [
        _eq("EQ-01", "agriculture_abondance.py → stoechiometrie_photosynthese() → C01",
            "6 CO2 + 6 H2O → C6H12O6 + 6 O2 ;  équilibre atome par atome",
            f"{_f(st['masse_reactifs_g'], 3)} g de réactifs = {_f(st['masse_produits_g'], 3)} g de "
            f"produits · {_f(st['co2_par_g_biomasse'], 3)} g CO2 par g de biomasse · "
            f"{st['desequilibre_atomique']:.0f} atome d'écart",
            "OPÉRATIONNEL", st),
        _eq("EQ-02", "agriculture_abondance.py → exigence_quantique() → C02",
            "E = N_A·hc/λ par einstein ;  4 photons/CO2 au minimum, 8,5 mesurés",
            f"680 nm → {_f(eq2['e_photon_eV'], 4)} eV = {_f(eq2['einstein_kJ_par_mol_photons'], 2)} "
            f"kJ/mol de photons · plafond {100 * eq2['rendement_plafond_min']:.1f} % (4 photons), "
            f"{100 * eq2['rendement_plafond_mesure']:.1f} % (8,5)",
            "OPÉRATIONNEL", eq2),
        _eq("EQ-03", "agriculture_abondance.py → spectre_PAR() → C03",
            "M_λ(T) intégrée sur 400–700 nm ;  φ = ∫M_λλ/(hc)dλ",
            f"PAR = {100 * sp['fraction_energie_PAR']:.1f} % de l'énergie · "
            f"{_f(sp['umol_par_joule_de_rayonnement_total'], 3)} µmol/J · pleine lumière hors "
            f"atmosphère ≈ {sp['ppfd_1000_W_m2_hors_atmosphere']:.0f} µmol/m²/s · "
            f"STEFAN-BOLTZMANN re-vérifiée par l'intégrale à {sp['ecart_integration_stefan']:.1e}",
            "OPÉRATIONNEL", sp),
        _eq("EQ-04", "agriculture_abondance.py → budget_solaire_agricole() → C04",
            "E_PAR = I·f_PAR·S ;  demande = N·(kcal/j)·365·4184",
            f"PAR sur les cultivables = {bs['energie_PAR_ZJ_par_an']:.1f} ZJ/an contre "
            f"{bs['demande_alimentaire_ZJ_par_an']:.3f} ZJ/an demandés · à 0,5 % de conversion : "
            f"{bs['facteurs_de_conversion']['0.5 %']:.1f}× la demande",
            "SIMULÉ", bs),
        _eq("EQ-05", "agriculture_abondance.py → rayonnement_use_efficiency() → C05",
            "ΔB = ε·fAPAR·PAR  (Monteith) ;  ε ≤ plafond EQ-02",
            f"plafond {rue['plafond_a_8_5_photons_g_par_MJ_PAR']:.2f} g/MJ PAR · C4 déclaré à "
            f"{100 * rue['part_du_plafond_C4']:.1f} % du plafond, C3 à "
            f"{100 * rue['part_du_plafond_C3']:.1f} %",
            "OPÉRATIONNEL", rue),
        _eq("EQ-06", "agriculture_abondance.py → voies_photosynthetiques() → C06",
            "Rubisco : v_C/v_O = 85 · C4 = pompe à CO2 devant Rubisco",
            f"C4/C3 en ε = {voy['gain_C4_sur_C3']:.2f}× · coût de la photorespiration = "
            f"{100 * voy['part_perdue_par_photorespiration']:.1f} % des photons",
            "SIMULÉ", voy),
        _eq("EQ-07", "agriculture_abondance.py → loi_du_minimum() → C07",
            "Y = Y_max · minᵢ(fᵢ) ;  doubler un facteur non limitant ne change rien",
            f"P limitant : {_fa(lim['y0'])} t/ha · P ×2 : {_fa(lim['y1'])} · P ×4 : "
            f"{_fa(lim['y2'])} (plateau, limitant = {lim['limitant_apres_P_x4']}) · eau ×2 : "
            f"{_fa(lim['y3'])} · toutes les planches pleines : {_fa(lim['y4'])}",
            "OPÉRATIONNEL", lim),
        _eq("EQ-08", "agriculture_abondance.py → azote_haber_bosch() → C08",
            "NH3 = 82,25 % d'azote ;  31 GJ/t NH3 ⇒ 37,7 MJ par kg N",
            f"grain : {_fa(az['azote_du_grain_kg_ha'])} kg N/ha sur "
            f"{az['azote_applique_kg_ha']:.0f} kg appliqués → NUE {100 * az['noue_recuperation_grain']:.1f} % · "
            f"{_f(az['energie_azote_kwh_par_t_grain'], 0)} kWh par tonne de blé",
            "OPÉRATIONNEL", az),
        _eq("EQ-09", "agriculture_abondance.py → evapotranspiration() → C09",
            "ET = R_n/(ρL) ;  1 mm sur 1 ha = 10 m³",
            f"R_n 100 W/m² → {_f(ev['mm_par_jour'], 3)} mm/jour · blé {ET_BLE_MM_AN:.0f} mm = "
            f"{ev['besoin_m3_ha_an']:.0f} m³/ha = {_fa(ev['besoin_litre_par_kg_grain'])} L/kg",
            "OPÉRATIONNEL", ev),
        _eq("EQ-10", "agriculture_abondance.py → energie_irrigation() → C10",
            "e = kWh/m³ du dossier EAU (ρgH/η à 50 m) × volume prélevé",
            f"{ir['kWh_par_m3_depuis_eau']:.4f} kWh/m³ · goutte-à-goutte "
            f"{_f(ir['energie_gouttelette_GJ_ha'], 3)} GJ/ha vs superficielle "
            f"{_f(ir['energie_superficielle_GJ_ha'], 3)} GJ/ha · irrigation/azote = "
            f"{ir['ratio_irrigation_sur_azote']:.2f}",
            "OPÉRATIONNEL", ir),
        _eq("EQ-11", "agriculture_abondance.py → eau_virtuelle() → C11",
            "L/kg dérivé (EQ-09) contre L/kg déclaré (dossier EAU EQ-12)",
            f"dérivé {_fa(vv['litres_par_kg_derive_agriculture'])} vs déclaré "
            f"{vv['litres_par_kg_declareEAU']:.0f} L/kg · écart "
            f"{100 * vv['ecart_relatif']:.1f} % · compartiments vert/bleu/gris fermés",
            "SIMULÉ", vv),
        _eq("EQ-12", "agriculture_abondance.py → discrimination_carbone() → C12",
            "Δ¹³C = a + (b−a)·ci/ca ;  WUE ∝ ca·(1 − ci/ca)",
            f"Δ {DELTA_13C_C3_POURMILLE}‰ ⇒ ci/ca = {dc['ci_sur_ca']:.4f} · 300 → 420 ppm : "
            f"efficience hydrique +{100 * dc['gain_d_efficience_hydrique']:.1f} % à Δ constant",
            "OPÉRATIONNEL", dc),
        _eq("EQ-13", "agriculture_abondance.py → calories_par_hectare() → C13",
            "personnes/ha = (t/ha)·(kcal/t) / (2100 kcal/j × 365)",
            f"blé {_fa(cal['ble']['personnes_par_ha'])} pers/ha · maïs "
            f"{_fa(cal['mais']['personnes_par_ha'])} pers/ha · ratio "
            f"{cal['rapport_mais_sur_ble']:.2f}",
            "SIMULÉ", cal),
        _eq("EQ-14", "agriculture_abondance.py → surface_nourrir_le_monde() → C14",
            "S = N·(kcal/j)·365 / (kcal/ha) ;  élevage = surface × indice de conversion",
            f"8 Md en céréales seules : {sf['surface_ble_ha'] / 1e6:.0f} Mha sur "
            f"{SURFACE_CULTIVABLE_HA / 1e6:.0f} Mha disponibles ({sf['marge_cerealiere']:.1f}×) · "
            f"avec 25 % d'apport animal : {sf['surface_avec_elevage_ha'] / 1e6:.0f} Mha",
            "SIMULÉ", sf),
        _eq("EQ-15", "agriculture_abondance.py → dette_de_sol() → C15",
            "M = z·S·ρ ;  dette = débit d'érosion − taux de formation",
            f"horizon 30 cm = {ds['masse_horizon_t_ha']:.0f} t/ha · érosion {SOL_ÉROSION_T_HA_AN:.0f} "
            f"t/ha/an = {ds['ratio_erosion_sur_formation']:.0f}× la formation · "
            f"{ds['annees_avant_horizon_perdu']:.0f} ans avant disparition",
            "SIMULÉ", ds),
        _eq("EQ-16", "agriculture_abondance.py → serre_led_bilan() → C16",
            "kWh/m² = DLI·E_einstein ;  WPE = φ·E_photon/Pélec",
            f"15 mol/m²/j : minimum {_f(sl['kWh_m2_jour_minimum_photons'], 4)} kWh, système "
            f"{_f(sl['kWh_m2_jour_systeme_led'], 4)} kWh ({sl['W_electrique_m2']:.0f} W/m²) · "
            f"{_fa(sl['kWh_par_kg_tomate_lumiere_seule'])} kWh/kg de tomate (lumière seule)",
            "OPÉRATIONNEL", sl),
        _eq("EQ-17", "agriculture_abondance.py → materiaux_optimisants() → C17",
            "quantité/ha = f(EQ-08, EQ-09, EQ-10, EQ-16) avec facteurs stoechiométriques exacts",
            f"{len(ma['materiaux'])} matériaux dimensionnés · film {_fa(ma['materiaux'][1]['quantite_par_ha'])} "
            f"kg/ha · SAP {_fa(ma['materiaux'][2]['quantite_par_ha'])} kg/ha · biochar "
            f"{ma['materiaux'][3]['surface_interne_km2_ha']:.0f} km² de surface interne par ha traité",
            "SIMULÉ", ma),
        _eq("EQ-18", "agriculture_abondance.py → ponts_dossier() → C18",
            "P1 ↔ plafond · P2 ↔ photopériode et siècles de sol · P3 ↔ planche la plus basse · "
            "P4 ↔ dettes",
            "4 ponts déclarés comme lectures, chacun borné par une limite",
            "SPÉCIFIÉ", pd),
    ]

    controles = [
        {"id": "C01", "nom": "bilan atomique et massique de la photosynthèse fermés",
         "attendu": "0 / 0", "obtenu": f"{st['desequilibre_atomique']:.0f} / {st['desequilibre_massique']:.2e}",
         "ok": st["desequilibre_atomique"] == 0.0 and st["desequilibre_massique"] < 1e-9
         and abs(st["masse_produits_g"] - (6 * M_CO2 + 6 * M_H2O)) < 1e-9
         and abs(st["carbone_fraction_biomasse"] - M_C / M_CH2O) < 1e-12
         and 0.35 < st["carbone_fraction_biomasse"] < 0.45},
        {"id": "C02", "nom": "deux voies pour l'einstein (hc/λ et eV × N_A·e)",
         "attendu": "0.000000000000", "obtenu": f"{eq2['coherence_deux_voies']:.12e}",
         "ok": eq2["coherence_deux_voies"] < 1e-9
         and 170.0 < eq2["einstein_kJ_par_mol_photons"] < 180.0
         and 0.65 < eq2["rendement_plafond_min"] < 0.72
         and 0.30 < eq2["rendement_plafond_mesure"] < 0.35},
        {"id": "C03", "nom": "l'intégration numérique reproduit Stefan-Boltzmann",
         "attendu": "< 1e-6", "obtenu": f"{sp['ecart_integration_stefan']:.3e}",
         "ok": sp["ecart_integration_stefan"] < 1e-6
         and 0.30 < sp["fraction_energie_PAR"] < 0.45
         and 1400.0 < sp["ppfd_1000_W_m2_hors_atmosphere"] < 2000.0
         and 3.0 < sp["umol_par_joule_dans_la_bande"] < 5.5},
        {"id": "C04", "nom": "le budget PAR dépasse la demande alimentaire de plusieurs ordres",
         "attendu": "0.5 % → 5× à 20×",
         "obtenu": f"{bs['facteurs_de_conversion']['0.5 %']:.1f}×",
         "ok": 3.0 < bs["facteurs_de_conversion"]["0.5 %"] < 30.0
         and bs["energie_PAR_ZJ_par_an"] > 10.0
         and abs(bs["irradiance_hors_atmosphere_W_m2"] - 1361.0) < 2.0},
        {"id": "C05", "nom": "ε déclaré reste sous le plafond quantique",
         "attendu": "< 1", "obtenu": f"{rue['part_du_plafond_C4']:.4f}",
         "ok": rue["part_du_plafond_C4"] < 1.0 and rue["part_du_plafond_C3"] < 1.0
         and rue["plafond_a_8_5_photons_g_par_MJ_PAR"] < rue["plafond_theorique_g_par_MJ_PAR"]
         and abs(rue["plafond_theorique_g_par_MJ_PAR"]
                 - 1e6 / eq2["einstein_kJ_par_mol_photons"] / 1000.0 / PHOTONS_CO2_MIN * M_CH2O) < 1e-9},
        {"id": "C06", "nom": "C4 > C3 > CAM en ε, surcoût quantique cohérent",
         "attendu": f"{EPS_C4_G_MJ / EPS_C3_G_MJ:.2f}", "obtenu": f"{voy['gain_C4_sur_C3']:.2f}",
         "ok": voy["voies"]["C4"]["ε_g_MJ"] > voy["voies"]["C3"]["ε_g_MJ"]
         and 0.5 < voy["part_perdue_par_photorespiration"] < 0.55
         and voy["voies"]["C4"]["wue_relative"] > voy["voies"]["C3"]["wue_relative"]},
        {"id": "C07", "nom": "loi du minimum : plateau exact quand le limitant change",
         "attendu": f"{RENDIMENT_BLE_T_HA * 0.7:.2f} / 0.00",
         "obtenu": f"{lim['y1']:.2f} / {abs(lim['y2'] - lim['y1']):.2e}",
         "ok": set(lim["planches"]) == {"lumière", "azote", "phosphore", "potasse", "eau"}
         and abs(lim["y0"] - RENDIMENT_BLE_T_HA * 0.40) < 1e-12
         and abs(lim["y1"] - RENDIMENT_BLE_T_HA * 0.70) < 1e-12
         and lim["plate_apres_P_x4"] and lim["limitant_depart"] == "phosphore"
         and lim["limitant_apres_P_x4"] == "eau"
         and abs(lim["y3"] - RENDIMENT_BLE_T_HA * 0.80) < 1e-12
         and abs(lim["y4"] - RENDIMENT_BLE_T_HA) < 1e-12},
        {"id": "C08", "nom": "82,25 % d'azote dans NH3 et énergie par kg N",
         "attendu": "0.8224 / 35-40 MJ", "obtenu": f"{az['fraction_N_dans_NH3']:.4f} / {_f(az['MJ_par_kg_N'], 1)} MJ",
         "ok": abs(az["fraction_N_dans_NH3"] - M_N / M_NH3) < 1e-12
         and 35.0 < az["MJ_par_kg_N"] < 40.0
         and 0.5 < az["noue_recuperation_grain"] < 0.7
         and abs(az["energie_azote_GJ_ha"] - AZOTE_APPLIQUE_KG_HA * az["MJ_par_kg_N"] / 1000.0) < 1e-9},
        {"id": "C09", "nom": "ET issue de Rn/L et 1 mm = 10 m³/ha exactement",
         "attendu": "10.000000", "obtenu": f"{ev['m3_par_ha_par_mm']:.6f}",
         "ok": abs(ev["m3_par_ha_par_mm"] - 10.0) < 1e-12
         and 2.0 < ev["mm_par_jour"] < 5.0
         and ev["coherence_avec_eau_1mm"] < 1e-12
         and abs(ev["besoin_litre_par_kg_grain"] - 10.0 * ET_BLE_MM_AN / RENDIMENT_BLE_T_HA) < 1e-9},
        {"id": "C10", "nom": "kWh/m³ identique au dossier EAU et gain du goutte-à-goutte",
         "attendu": "0.000000000000", "obtenu": f"{ir['coherence_identite_rho_g_h']:.12e}",
         "ok": ir["coherence_identite_rho_g_h"] < 1e-12
         and ir["energie_gouttelette_GJ_ha"] < ir["energie_superficielle_GJ_ha"]
         and ir["economie_kWh_par_ha"] > 0.0
         and 2.0 < ir["energie_gouttelette_GJ_ha"] < 6.0},
        {"id": "C11", "nom": "L/kg dérivé converge vers le L/kg déclaré (EAU)",
         "attendu": "< 0.20", "obtenu": f"{vv['ecart_relatif']:.4f}",
         "ok": vv["ecart_relatif"] < 0.20
         and abs(vv["somme_compartiments"] - 100.0) < 1e-12
         and vv["litres_par_kg_derive_agriculture"] > 0.0},
        {"id": "C12", "nom": "ci/ca dans (0,1) et gain proportionnel à ca",
         "attendu": "0.000000000000", "obtenu": f"{dc['proportionnalite_exacte']:.12e}",
         "ok": dc["proportionnalite_exacte"] < 1e-12 and 0.0 < dc["ci_sur_ca"] < 1.0
         and 0.3 < dc["gain_d_efficience_hydrique"] < 0.5
         and dc["wue_indice_actuel"] > dc["wue_indice_preindustriel"]},
        {"id": "C13", "nom": "personnes/ha et ordre de grandeur des rendements",
         "attendu": "3.06", "obtenu": f"{cal['rapport_mais_sur_ble']:.3f}",
         "ok": 2.5 < cal["rapport_mais_sur_ble"] < 3.6
         and 10.0 < cal["ble"]["personnes_par_ha"] < 25.0
         and abs(cal["ble"]["kcal_par_ha"] - RENDIMENT_BLE_T_HA * KCAL_PAR_T_BLE) < 1e-6},
        {"id": "C14", "nom": "surface céréalière < surface cultivable, avec marge",
         "attendu": "> 1.5", "obtenu": f"{sf['marge_cerealiere']:.2f}",
         "ok": 1.5 < sf["marge_cerealiere"] < 5.0
         and sf["surface_avec_elevage_ha"] > sf["surface_ble_ha"]
         and sf["surface_avec_elevage_ha"] < SURFACE_CULTIVABLE_HA},
        {"id": "C15", "nom": "érosion déclarée supérieure à la formation : dette ouverte",
         "attendu": "20", "obtenu": f"{ds['ratio_erosion_sur_formation']:.1f}",
         "ok": abs(ds["ratio_erosion_sur_formation"] - 20.0) < 1e-9
         and abs(ds["masse_horizon_t_ha"] - SOL_PROFONDEUR_M * 1e4 * SOL_MASSE_VOL_T_M3) < 1e-9
         and ds["dette_nette_t_ha_an"] > 0.0
         and 0.1 < ds["mm_par_an_equivalent_erosion"] < 1.0},
        {"id": "C16", "nom": "kWh système > kWh photons, WPE et watts cohérents avec le kWh",
         "attendu": f"{sl['rapport_systeme_sur_minimum']:.3f}",
         "obtenu": f"{sl['W_electrique_m2']:.1f} W/m²",
         "ok": sl["kWh_m2_jour_systeme_led"] > sl["kWh_m2_jour_minimum_photons"]
         and 0.45 < sl["wall_plug_efficiency"] < 0.55
         and 2.0 < sl["rapport_systeme_sur_minimum"] < 2.2
         and 8.0 < sl["kWh_par_kg_tomate_lumiere_seule"] < 20.0
         and abs(sl["W_electrique_m2"] - sl["kWh_m2_jour_systeme_led"] * 1000.0 / PHOTOPERIODE_H)
         < 1e-9
         and sl["W_photon_m2"] < sl["W_electrique_m2"]
         and 30.0 < sl["W_photon_m2"] < 60.0},
        {"id": "C17", "nom": "facteurs stoechiométriques exacts et quantités positives",
         "attendu": "0.4364 / 0.8302", "obtenu": f"{ma['fractions_stoechiometriques']['P_dans_P2O5']:.4f} / "
                                                 f"{ma['fractions_stoechiometriques']['K_dans_K2O']:.4f}",
         "ok": abs(ma["fractions_stoechiometriques"]["N_dans_NH3"] - M_N / M_NH3) < 1e-12
         and abs(ma["fractions_stoechiometriques"]["K2O_dans_KCl"] - 0.6316) < 1e-3
         and all(m["quantite_par_ha"] > 0 for m in ma["materiaux"])
         and len(ma["materiaux"]) == 8},
        {"id": "C18", "nom": "quatre ponts déclarés, chacun borné",
         "attendu": "4", "obtenu": str(len(pd)),
         "ok": len(pd) == 4 and all(p["limite"] and p["agriculture"] for p in pd)},
    ]

    return {
        "version": "1.0",
        "theme": "AGRICULTURE — DU PHOTON À L'ASSIETTE",
        "source": SOURCE,
        "invariants": {
            "c_m_s": C, "h_J_s": H, "k_B_J_K": K_B, "N_A_mol": N_A,
            "sigma_W_m2_K4": SIGMA, "g_m_s2": G0,
            "masses_g_mol": {"CO2": M_CO2, "H2O": M_H2O, "O2": M_O2, "CH2O": M_CH2O,
                             "C6H12O6": M_Glucose, "NH3": M_NH3, "P2O5": M_P2O5,
                             "K2O": M_K2O, "KCl": M_KCL},
        },
        "valeurs_declarees": {
            "rendements_t_ha": {"ble": RENDIMENT_BLE_T_HA, "mais": RENDIMENT_MAIS_T_HA},
            "kcal_par_tonne": {"ble": KCAL_PAR_T_BLE, "mais": KCAL_PAR_T_MAIS},
            "eps_g_par_MJ": {"C3": EPS_C3_G_MJ, "C4": EPS_C4_G_MJ},
            "habergj_par_t_nh3": N_HABER_GJ_T_NH3,
            "azote_applique_kg_ha": AZOTE_APPLIQUE_KG_HA,
            "et_ble_mm_an": ET_BLE_MM_AN,
            "led_umol_par_joule": U_MOL_PAR_JOULE_LED,
            "photons_par_co2_mesures": PHOTONS_CO2_DECLARES,
            "sol": {"profondeur_m": SOL_PROFONDEUR_M, "densite_t_m3": SOL_MASSE_VOL_T_M3,
                    "production_t_ha_an": SOL_PRODUCTION_T_HA_AN,
                    "erosion_t_ha_an": SOL_ÉROSION_T_HA_AN},
            "statut": "valeurs de littérature agronomique, non mesurées dans ce dépôt ; "
                      "les équations qui les utilisent sont calculées et contrôlées",
        },
        "equations": eqs,
        "controles": controles,
        "resume": {
            "equations": len(eqs),
            "controles_ok": sum(1 for c in controles if c["ok"]),
            "controles_total": len(controles),
            "statuts": {s: sum(1 for e in eqs if e["statut"] == s) for s in STATUTS},
            "plafond_quantique_g_par_MJ_PAR": rue["plafond_a_8_5_photons_g_par_MJ_PAR"],
            "einstein_680nm_kJ": eq2["einstein_kJ_par_mol_photons"],
            "ppfd_1000W_mol": sp["ppfd_1000_W_m2_hors_atmosphere"],
            "MJ_par_kg_N_haber": az["MJ_par_kg_N"],
            "kWh_par_m3_irrigation": ir["kWh_par_m3_depuis_eau"],
            "litres_par_kg_ble_derive": vv["litres_par_kg_derive_agriculture"],
            "personnes_par_ha_ble": cal["ble"]["personnes_par_ha"],
            "surface_monde_Mha": sf["surface_ble_ha"] / 1e6,
            "annees_de_sol_reste": ds["annees_avant_horizon_perdu"],
            "kWh_par_kg_tomate_led": sl["kWh_par_kg_tomate_lumiere_seule"],
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
