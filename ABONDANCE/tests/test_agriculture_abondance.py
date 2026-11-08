# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2026 IMAM8MAHDI / Astro-Code Ecosystem
# SPDX-License-Identifier: GPL-3.0-only OR AGPL-3.0-only
"""Tests du dossier AGRICULTURE d'ABONDANCE (unittest, stdlib uniquement).

Les valeurs attendues sont recalculées ici à partir des constantes du SI, des
poids atomiques déclarés et des formes fermées de la photochimie ; elles ne
sont pas recopiées du module testé.
"""

from __future__ import annotations

import math
import sys
import unittest
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
if str(RACINE) not in sys.path:
    sys.path.insert(0, str(RACINE))

import agriculture_abondance as M  # noqa: E402

# ── Constantes du SI (valeurs définies) ─────────────────────────────────────
C_VIDE = 299792458.0
H_PLANCK = 6.62607015e-34
K_B = 1.380649e-23
N_A = 6.02214076e23
E_CHARGE = 1.602176634e-19
KWH_J = 3.6e6
G = 9.80665
RHO_EAU_25C = 997.0                 # kg/m³ à 25 °C — declaration partagée avec le dossier EAU
SIGMA = 2.0 * math.pi ** 5 * K_B ** 4 / (15.0 * H_PLANCK ** 3 * C_VIDE ** 2)

# ── Poids atomiques déclarés (IUPAC 2021, g/mol) ────────────────────────────
M_C, M_H, M_O = 12.011, 1.008, 15.999
M_N, M_P, M_K, M_CL = 14.007, 30.974, 39.098, 35.45
M_CO2 = M_C + 2.0 * M_O
M_H2O = 2.0 * M_H + M_O
M_O2 = 2.0 * M_O
M_CH2O = M_C + 2.0 * M_H + M_O
M_Glucose = 6.0 * M_C + 6.0 * M_H2O
M_NH3 = M_N + 3.0 * M_H
M_P2O5 = 2.0 * M_P + 5.0 * M_O
M_K2O = 2.0 * M_K + M_O
M_KCL = M_K + M_CL

LAMBDA = 680e-9
E_PHOTON_J = H_PLANCK * C_VIDE / LAMBDA
EINSTEIN_KJ = E_PHOTON_J * N_A / 1000.0


def eq(id_):
    return {e["id"]: e for e in M.resoudre()["equations"]}[id_]["detail"]


def proche(test, a, b, tol=1e-12, msg=None):
    """Écart relatif : seul test correct pour les grandeurs d'ordre 10⁻¹⁹."""
    denom = max(abs(a), abs(b))
    test.assertLess(abs(a - b) / (denom if denom else 1.0), tol, msg)


class TestStoechiometrie(unittest.TestCase):
    def test_le_bilan_atomique_se_ferme_atome_par_atome(self):
        d = eq("EQ-01")
        self.assertEqual(d["desequilibre_atomique"], 0.0)
        self.assertEqual(d["atomes_reactifs"], {"C": 6.0, "H": 12.0, "O": 18.0})
        self.assertEqual(d["atomes_reactifs"], d["atomes_produits"])

    def test_la_masse_ne_depend_pas_de_l_ecriture(self):
        d = eq("EQ-01")
        self.assertAlmostEqual(d["masse_reactifs_g"], 6.0 * M_CO2 + 6.0 * M_H2O, places=9)
        self.assertAlmostEqual(d["masse_produits_g"], M_Glucose + 6.0 * M_O2, places=9)
        self.assertAlmostEqual(d["masse_reactifs_g"], d["masse_produits_g"], places=9)
        self.assertEqual(d["desequilibre_massique"], 0.0)

    def test_les_ratios_de_fixation_sortent_des_masses_molaires(self):
        d = eq("EQ-01")
        proche(self, d["co2_par_g_biomasse"], M_CO2 / M_CH2O)
        proche(self, d["o2_par_g_biomasse"], M_O2 / M_CH2O)
        proche(self, d["carbone_fraction_biomasse"], M_C / M_CH2O)
        self.assertLess(0.35, d["carbone_fraction_biomasse"])
        self.assertGreater(0.45, d["carbone_fraction_biomasse"])

    def test_l_ecart_co2_o2_mesure_le_carbone_de_la_biomasse(self):
        d = eq("EQ-01")
        proche(self, d["co2_par_g_biomasse"] - d["o2_par_g_biomasse"],
               d["carbone_fraction_biomasse"])
        self.assertGreater(d["co2_par_g_biomasse"], 1.0)


class TestExigenceQuantique(unittest.TestCase):
    def test_un_einstein_de_rouge_680(self):
        d = eq("EQ-02")
        proche(self, d["e_photon_J"], E_PHOTON_J)
        self.assertAlmostEqual(d["einstein_kJ_par_mol_photons"], EINSTEIN_KJ, places=9)
        self.assertAlmostEqual(d["einstein_kJ_par_mol_photons"], 175.92142005690735, places=6)

    def test_deux_voies_independantes_donnent_le_meme_einstein(self):
        d = eq("EQ-02")
        proche(self, d["e_photon_eV"], E_PHOTON_J / E_CHARGE)
        proche(self, d["einstein_par_eV_kJ"], d["e_photon_eV"] * N_A * E_CHARGE / 1000.0)
        self.assertEqual(d["coherence_deux_voies"], 0.0)

    def test_le_plafond_est_l_energie_chimique_divisee_par_le_prix_photon(self):
        d = eq("EQ-02")
        chimie = 2870.0 / 6.0
        self.assertAlmostEqual(d["energie_min_kj_par_mol_co2"], 4.0 * EINSTEIN_KJ, places=9)
        self.assertAlmostEqual(d["energie_declaree_kj_par_mol_co2"], 8.5 * EINSTEIN_KJ, places=9)
        self.assertAlmostEqual(d["energie_chimie_kj_par_mol_co2"], chimie, places=9)
        self.assertAlmostEqual(d["rendement_plafond_min"], chimie / (4.0 * EINSTEIN_KJ), places=12)
        self.assertAlmostEqual(d["rendement_plafond_mesure"],
                               chimie / (8.5 * EINSTEIN_KJ), places=12)
        self.assertLess(d["rendement_plafond_mesure"], d["rendement_plafond_min"])
        self.assertAlmostEqual(d["surcout_photons"], 8.5 / 4.0, places=12)


class TestSpectrePAR(unittest.TestCase):
    def test_l_integration_retrouve_stefan_boltzmann(self):
        d = eq("EQ-03")
        self.assertAlmostEqual(d["exitance_stefan_W_m2"], SIGMA * 5772.0 ** 4, places=3)
        self.assertLess(d["ecart_integration_stefan"], 1e-6)
        proche(self, d["ecart_integration_stefan"],
               abs(d["exitance_integree_W_m2"] - d["exitance_stefan_W_m2"])
               / d["exitance_stefan_W_m2"], 1e-9)

    def test_la_bande_compte_moins_de_photons_que_d_energie(self):
        d = eq("EQ-03")
        self.assertLess(d["fraction_photons_PAR"], d["fraction_energie_PAR"])
        self.assertLess(0.30, d["fraction_energie_PAR"])
        self.assertGreater(d["fraction_energie_PAR"], d["fraction_photons_PAR"])
        self.assertLess(0.10, d["fraction_photons_PAR"])

    def test_le_nombre_de_photons_par_joule_decoule_de_la_longueur_d_onde_effective(self):
        d = eq("EQ-03")
        self.assertAlmostEqual(d["ppfd_1000_W_m2_hors_atmosphere"],
                               1000.0 * d["umol_par_joule_de_rayonnement_total"], places=9)
        proche(self, d["umol_par_joule_dans_la_bande"],
               1e6 / (N_A * H_PLANCK * C_VIDE / (d["lambda_effectif_bande_nm"] * 1e-9)), 1e-6)
        self.assertLess(500.0, d["lambda_effectif_bande_nm"])
        self.assertGreater(600.0, d["lambda_effectif_bande_nm"])
        self.assertAlmostEqual(d["umol_par_joule_dans_la_bande"], 4.566609040967909, places=6)


class TestBudgetSolaireAgricole(unittest.TestCase):
    def test_le_par_agricole_est_une_surface_velee_par_une_irradiance(self):
        d = eq("EQ-04")
        self.assertEqual(d["surface_cultivable_m2"], 1.4e9 * 1e4)
        self.assertAlmostEqual(d["puissance_PAR_W"], 220.0 * 0.45 * d["surface_cultivable_m2"],
                               places=3)
        self.assertAlmostEqual(d["energie_PAR_J_par_an"],
                               d["puissance_PAR_W"] * 365.0 * 86400.0, places=3)

    def test_la_demande_alimentaire_est_en_joules_pas_en_calories(self):
        d = eq("EQ-04")
        self.assertAlmostEqual(d["demande_alimentaire_J_par_an"],
                               8.0e9 * 2100.0 * 365.0 * 4184.0, places=3)
        self.assertLess(d["demande_alimentaire_ZJ_par_an"], d["energie_PAR_ZJ_par_an"])

    def test_la_conversion_est_lineaire_en_rendement(self):
        d = eq("EQ-04")
        f = d["facteurs_de_conversion"]
        proche(self, f["0.5 %"] / f["0.2 %"], 2.5, 1e-9)
        proche(self, f["1.0 %"] / f["0.5 %"], 2.0, 1e-9)
        attendue = (220.0 * 0.45 * 1.4e13 * 365.0 * 86400.0 * 0.02
                    / (8.0e9 * 2100.0 * 365.0 * 4184.0))
        self.assertAlmostEqual(f["2.0 %"], attendue, places=6)
        self.assertGreater(f["2.0 %"], 1.0)


class TestMonteithRUE(unittest.TestCase):
    def test_le_plafond_de_Monteith_ne_depasse_pas_le_plafond_quantique(self):
        d = eq("EQ-05")
        self.assertAlmostEqual(d["einstein_kJ"], EINSTEIN_KJ, places=9)
        plafond = 1e6 / (EINSTEIN_KJ * 1000.0) / 4.0 * M_CH2O
        self.assertAlmostEqual(d["plafond_theorique_g_par_MJ_PAR"], plafond, places=9)
        self.assertAlmostEqual(d["plafond_a_8_5_photons_g_par_MJ_PAR"],
                               plafond * 4.0 / 8.5, places=9)
        self.assertLess(d["part_du_plafond_C4"], 1.0)
        self.assertLess(d["part_du_plafond_C3"], d["part_du_plafond_C4"])

    def test_eps_global_se_convertit_en_eps_sur_le_par_absorbe(self):
        d = eq("EQ-05")
        self.assertAlmostEqual(d["eps_C3_rapporte_au_PAR"], 1.5 / 0.45, places=12)
        self.assertAlmostEqual(d["eps_C4_rapporte_au_PAR"], 3.0 / 0.45, places=12)
        self.assertAlmostEqual(d["biomasse_par_jour_g_m2"], 20.0 * 1.5 * 0.85, places=12)


class TestVoiesPhotosynthetiques(unittest.TestCase):
    def test_le_gain_c4_est_un_rapport_de_rendement_pas_de_chimie(self):
        d = eq("EQ-06")
        self.assertAlmostEqual(d["gain_C4_sur_C3"], 3.0 / 1.5, places=12)
        self.assertEqual(d["surcout_quantique_feuille"], 8.5 / 4.0)
        self.assertAlmostEqual(d["part_perdue_par_photorespiration"], 1.0 - 4.0 / 8.5, places=12)

    def test_les_voies_sont_ordonnées_en_epsilon_et_en_efficience_eau(self):
        v = eq("EQ-06")["voies"]
        self.assertLess(v["C3"]["ε_g_MJ"], v["C4"]["ε_g_MJ"])
        self.assertLess(v["CAM"]["ε_g_MJ"], v["C3"]["ε_g_MJ"])
        self.assertLess(v["C4"]["compensation_CO2_ppm"], v["C3"]["compensation_CO2_ppm"])
        self.assertLess(v["C3"]["wue_relative"], v["CAM"]["wue_relative"])


class TestLoiDuMinimum(unittest.TestCase):
    def test_une_planche_basse_borne_tout_le_baril(self):
        d = eq("EQ-07")
        self.assertAlmostEqual(d["y0"], 3.5 * 0.40, places=12)
        self.assertEqual(d["limitant_depart"], "phosphore")
        self.assertAlmostEqual(d["y1"], 3.5 * 0.70, places=12)
        self.assertEqual(d["limitant_apres_P_x4"], "eau")

    def test_doubler_un_facteur_non_limitant_ne_change_rien(self):
        d = eq("EQ-07")
        self.assertTrue(d["plate_apres_P_x4"])
        self.assertEqual(d["y2"] - d["y1"], 0.0)
        self.assertAlmostEqual(d["y3"], 3.5 * 0.80, places=12)
        self.assertAlmostEqual(d["y4"], 3.5, places=12)
        self.assertEqual([s["rendement_t_ha"] for s in d["serie"]],
                         [d["y0"], d["y1"], d["y2"], d["y3"], d["y4"]])

    def test_une_planche_remplie_ne_deborde_pas(self):
        d = eq("EQ-07")
        self.assertLess(d["y3"], d["y4"])
        self.assertEqual(set(d["planches"]), {"lumière", "azote", "phosphore", "potasse", "eau"})
        self.assertAlmostEqual(d["y4"], d["rendement_max_t_ha"], places=12)
        self.assertLess(d["saut_attendu_apres_P"], d["y4"])


class TestAzoteHaberBosch(unittest.TestCase):
    def test_l_ammoniac_tient_82_pour_cent_d_azote(self):
        d = eq("EQ-08")
        proche(self, d["M_NH3_g_mol"], M_NH3)
        proche(self, d["fraction_N_dans_NH3"], M_N / M_NH3)
        self.assertAlmostEqual(d["fraction_N_dans_NH3"], 0.8224414303329224, places=12)

    def test_le_gj_par_tonne_d_ammoniaque_devient_le_mj_par_kilo_d_azote(self):
        d = eq("EQ-08")
        self.assertAlmostEqual(d["MJ_par_kg_N"], 31.0 / (M_N / M_NH3), places=9)
        self.assertAlmostEqual(d["MJ_par_kg_N"], 37.69265367316341, places=6)
        self.assertAlmostEqual(d["energie_azote_GJ_ha"], 120.0 * d["MJ_par_kg_N"] / 1000.0, places=9)
        self.assertAlmostEqual(d["nh3_kg_ha"], 120.0 / (M_N / M_NH3), places=9)

    def test_la_nue_sort_du_bilan_d_azote_du_grain(self):
        d = eq("EQ-08")
        self.assertAlmostEqual(d["azote_du_grain_kg_ha"], 3.5 * 1000.0 * 0.12 / 5.7, places=9)
        self.assertAlmostEqual(d["noue_recuperation_grain"], d["azote_du_grain_kg_ha"] / 120.0,
                               places=12)
        self.assertLess(d["noue_recuperation_grain"], 1.0)
        self.assertAlmostEqual(d["energie_azote_kwh_par_t_grain"],
                               d["energie_azote_GJ_ha"] * 1000.0 / 3.5 / 3.6, places=9)


class TestEvapotranspiration(unittest.TestCase):
    def test_un_millimetre_sur_un_hectare_fait_dix_metres_cube(self):
        d = eq("EQ-09")
        self.assertEqual(d["m3_par_ha_par_mm"], 10.0)
        self.assertEqual(d["coherence_avec_eau_1mm"], 0.0)
        self.assertEqual(d["L_J_kg"], M.EAU.L_CHALEUR_LATENTE)
        self.assertAlmostEqual(d["besoin_m3_ha_an"], 500.0 * 10.0, places=9)

    def test_le_flux_de_vapeur_suivant_le_bilan_d_energie(self):
        d = eq("EQ-09")
        proche(self, d["flux_kg_m2_s"], 100.0 / d["L_J_kg"], 1e-12)
        proche(self, d["mm_par_jour"], d["flux_kg_m2_s"] * 86400.0 * 1000.0 / RHO_EAU_25C, 1e-12)
        self.assertAlmostEqual(d["besoin_litre_par_kg_grain"],
                               10.0 * 500.0 / 3.5, places=9)
        self.assertAlmostEqual(d["energie_evaporer_ha_J"],
                               5000.0 * RHO_EAU_25C * d["L_J_kg"], places=3)


class TestEnergieIrrigation(unittest.TestCase):
    def test_le_kilowatt_heure_par_metre_cube_vient_du_dossier_eau(self):
        d = eq("EQ-10")
        self.assertEqual(M.EAU.RHO_EAU_DOUCE, RHO_EAU_25C)
        self.assertAlmostEqual(d["kWh_par_m3_depuis_eau"],
                               RHO_EAU_25C * G * 50.0 / KWH_J / 0.65, places=12)
        self.assertEqual(d["coherence_identite_rho_g_h"], 0.0)
        self.assertAlmostEqual(d["kWh_par_m3_depuis_eau"],
                               M.resoudre()["resume"]["kWh_par_m3_irrigation"], places=12)

    def test_le_gouttelette_preleve_moins_et_coute_moins(self):
        d = eq("EQ-10")
        self.assertAlmostEqual(d["eau_prelevee_gouttelette_m3_ha"], 5000.0 / 0.90, places=9)
        self.assertAlmostEqual(d["eau_prelevee_superficielle_m3_ha"], 5000.0 / 0.60, places=9)
        proche(self, d["energie_gouttelette_GJ_ha"],
               d["kWh_par_m3_depuis_eau"] * d["eau_prelevee_gouttelette_m3_ha"] * KWH_J / 1e9, 1e-12)
        self.assertLess(d["energie_gouttelette_GJ_ha"], d["energie_superficielle_GJ_ha"])
        self.assertGreater(d["economie_kWh_par_ha"], 0.0)
        proche(self, d["ratio_irrigation_sur_azote"],
               d["energie_gouttelette_GJ_ha"] / eq("EQ-08")["energie_azote_GJ_ha"], 1e-12)


class TestEauVirtuelle(unittest.TestCase):
    def test_les_deux_chemins_convergent_a_moins_de_vingt_pour_cent(self):
        d = eq("EQ-11")
        self.assertAlmostEqual(d["litres_par_kg_derive_agriculture"], 10.0 * 500.0 / 3.5, places=9)
        self.assertEqual(d["litres_par_kg_declareEAU"],
                         M.EAU.eau_par_aliment()["litres_par_kg"]["blé"])
        proche(self, d["ecart_relatif"],
               abs(d["litres_par_kg_declareEAU"] - d["litres_par_kg_derive_agriculture"])
               / d["litres_par_kg_declareEAU"], 1e-12)
        self.assertLess(d["ecart_relatif"], 0.20)

    def test_les_compartiments_se_somment_en_un_selon(self):
        d = eq("EQ-11")
        self.assertEqual(d["verte_pct"] + d["bleue_pct"] + d["grise_declare_pct"], 100.0)
        self.assertEqual(d["somme_compartiments"], 100.0)
        self.assertAlmostEqual(d["litres_par_personne_an"], d["litres_par_kg_declareEAU"] * 90.0,
                               places=9)
        self.assertAlmostEqual(d["m3_par_personne_an"],
                               d["litres_par_personne_an"] / 1000.0, places=12)


class TestDiscriminationCarbone(unittest.TestCase):
    def test_delta_donne_ci_sur_ca_par_la_forme_de_farquhar(self):
        d = eq("EQ-12")
        self.assertAlmostEqual(d["ci_sur_ca"], (19.5 - 4.4) / (27.0 - 4.4), places=12)
        self.assertLess(0.0, d["ci_sur_ca"])
        self.assertLess(d["ci_sur_ca"], 1.0)

    def test_le_gain_d_efficience_est_exactement_le_ratio_de_co2(self):
        d = eq("EQ-12")
        proche(self, d["wue_indice_actuel"], 420.0 * (1.0 - d["ci_sur_ca"]), 1e-12)
        proche(self, d["wue_indice_preindustriel"], 300.0 * (1.0 - d["ci_sur_ca"]), 1e-12)
        self.assertAlmostEqual(d["gain_d_efficience_hydrique"], 420.0 / 300.0 - 1.0, places=12)
        self.assertLess(d["proportionnalite_exacte"], 1e-12)
        self.assertGreater(d["wue_indice_actuel"], d["wue_indice_preindustriel"])


class TestCaloriesParHectare(unittest.TestCase):
    def test_les_personnes_par_hectare_sortent_des_seules_kilocalories(self):
        d = eq("EQ-13")
        proche(self, d["ble"]["kcal_par_ha"], 3.5 * 3.4e6, 1e-12)
        proche(self, d["ble"]["personnes_par_ha"], 3.5 * 3.4e6 / (2100.0 * 365.0), 1e-12)
        proche(self, d["mais"]["personnes_par_ha"], 10.0 * 3.65e6 / (2100.0 * 365.0), 1e-12)
        self.assertAlmostEqual(d["ble"]["personnes_par_ha"], 15.525114155251142, places=9)

    def test_le_ratio_ne_depend_que_des_rendements_declares(self):
        d = eq("EQ-13")
        proche(self, d["rapport_mais_sur_ble"],
               d["mais"]["personnes_par_ha"] / d["ble"]["personnes_par_ha"], 1e-12)
        proche(self, d["rapport_mais_sur_ble"], (10.0 * 3.65e6) / (3.5 * 3.4e6), 1e-12)
        proche(self, d["ble"]["jours_personne_par_ha"], d["ble"]["kcal_par_ha"] / 2100.0, 1e-12)
        self.assertAlmostEqual(d["kcal_par_kg_ble"], 3400.0, places=9)


class TestSurfaceNourrirLeMonde(unittest.TestCase):
    def test_la_surface_cerealiere_est_la_demande_divisee_par_l_hectare(self):
        d = eq("EQ-14")
        self.assertAlmostEqual(d["demande_kcal_par_an"], 8.0e9 * 2100.0 * 365.0, places=3)
        self.assertAlmostEqual(d["surface_ble_ha"], d["demande_kcal_par_an"] / (3.5 * 3.4e6),
                               places=3)
        self.assertAlmostEqual(d["surface_mais_ha"], d["demande_kcal_par_an"] / (10.0 * 3.65e6),
                               places=3)
        self.assertAlmostEqual(d["surface_ble_ha"] / 1e6, 515.2941176470589, places=6)

    def test_l_elevage_multiplie_la_surface_par_l_indice_de_conversion(self):
        d = eq("EQ-14")
        attendue = (d["surface_ble_ha"] * 0.75 + d["surface_ble_ha"] * 0.25 * 6.0)
        self.assertAlmostEqual(d["surface_avec_elevage_ha"], attendue, places=3)
        self.assertGreater(d["surface_avec_elevage_ha"], d["surface_ble_ha"])
        self.assertLess(d["surface_avec_elevage_ha"], d["surface_cultivable_disponible_ha"])
        self.assertGreater(d["marge_cerealiere"], 1.0)


class TestDetteDeSol(unittest.TestCase):
    def test_l_horizon_pese_sa_densite_fois_sa_profondeur_fois_dix_mille(self):
        d = eq("EQ-15")
        self.assertAlmostEqual(d["masse_horizon_t_ha"], 0.30 * 1e4 * 1.3, places=9)
        self.assertAlmostEqual(d["annees_avant_horizon_perdu"], 3900.0 / 10.0, places=9)
        self.assertAlmostEqual(d["annees_pour_reformer_l_horizon"], 3900.0 / 0.5, places=9)

    def test_l_erosion_est_un_debit_la_formation_un_stock(self):
        d = eq("EQ-15")
        self.assertAlmostEqual(d["ratio_erosion_sur_formation"], 10.0 / 0.5, places=12)
        self.assertGreater(d["dette_nette_t_ha_an"], 0.0)
        self.assertAlmostEqual(d["mm_par_an_equivalent_erosion"],
                               10.0 / (1e4 * 1.3) * 1000.0, places=9)
        self.assertLess(d["mm_par_an_equivalent_erosion"], 1.0)


class TestSerreLed(unittest.TestCase):
    def test_le_minimum_est_le_prix_en_photons_du_dli(self):
        d = eq("EQ-16")
        proche(self, d["einstein_J_par_mol_photons"], E_PHOTON_J * N_A, 1e-12)
        self.assertAlmostEqual(d["kWh_m2_jour_minimum_photons"], 15.0 * E_PHOTON_J * N_A / KWH_J,
                               places=9)
        self.assertAlmostEqual(d["dli_mol_m2_jour"], 15.0, places=12)

    def test_le_systeme_led_paye_plus_que_le_minimum_et_le_wpe_le_dit(self):
        d = eq("EQ-16")
        self.assertAlmostEqual(d["kWh_m2_jour_systeme_led"], 15.0e6 / 2.8 / KWH_J, places=9)
        proche(self, d["wall_plug_efficiency"],
               E_PHOTON_J * N_A / (1e6 / 2.8), 1e-12)
        self.assertGreater(d["kWh_m2_jour_systeme_led"], d["kWh_m2_jour_minimum_photons"])
        self.assertAlmostEqual(d["kWh_par_kg_tomate_lumiere_seule"],
                               d["kWh_m2_jour_systeme_led"] * 365.0 / 40.0, places=9)
        self.assertAlmostEqual(d["kWh_par_kg_tomate_lumiere_seule"], 13.578869047619047, places=6)

    def test_les_watts_sont_le_kilowatt_heure_sur_la_photoperiode(self):
        d = eq("EQ-16")
        self.assertAlmostEqual(d["ppfd_umol_m2_s"], 15.0e6 / (16.0 * 3600.0), places=9)
        proche(self, d["W_photon_m2"], d["ppfd_umol_m2_s"] * 1e-6 * d["einstein_J_par_mol_photons"],
               1e-12)
        self.assertAlmostEqual(d["W_electrique_m2"],
                               d["kWh_m2_jour_systeme_led"] * 1000.0 / 16.0, places=9)
        self.assertLess(d["W_photon_m2"], d["W_electrique_m2"])


class TestMateriaux(unittest.TestCase):
    def test_les_quantites_se_derivent_des_equations_precedentes(self):
        d = eq("EQ-17")
        m = {x["equation"]: x["quantite_par_ha"] for x in d["materiaux"]}
        self.assertAlmostEqual(m["géométrie × densité déclarée"], 30e-6 * 1e4 * 920.0, places=9)
        self.assertAlmostEqual(m["EQ-09 (1 mm = 10 m³/ha)"], 20.0 * 10.0 * 1000.0 / 300.0, places=9)
        self.assertAlmostEqual(m["EQ-08"], 120.0 / (M_N / M_NH3), places=9)
        self.assertEqual(len(d["materiaux"]), 8)

    def test_les_facteurs_stoechiometriques_sont_exactes(self):
        f = eq("EQ-17")["fractions_stoechiometriques"]
        proche(self, f["N_dans_NH3"], M_N / M_NH3)
        proche(self, f["P_dans_P2O5"], 2.0 * M_P / M_P2O5)
        proche(self, f["K_dans_K2O"], 2.0 * M_K / M_K2O)
        proche(self, f["K2O_dans_KCl"], M_K2O / (2.0 * M_KCL))
        proche(self, f["C_dans_CH2O"], M_C / M_CH2O)

    def test_le_biochar_compte_sa_surface_et_le_p2o5_sa_roche(self):
        d = eq("EQ-17")
        biochar = next(x for x in d["materiaux"] if "biochar" in x["materiau"])
        self.assertAlmostEqual(biochar["surface_interne_m2_ha"], 10.0 * 1e6 * 200.0, places=3)
        self.assertAlmostEqual(biochar["surface_interne_km2_ha"], 2000.0, places=9)
        minerai = next(x for x in d["materiaux"] if "phosphaté" in x["materiau"])
        self.assertAlmostEqual(minerai["quantite_par_ha"],
                               25.0 / (2.0 * M_P / M_P2O5) / 0.30, places=9)
        kcl = next(x for x in d["materiaux"] if "KCl" in x["materiau"])
        self.assertAlmostEqual(kcl["quantite_par_ha"], 30.0 / (2.0 * M_K / M_K2O) / 0.60, places=9)
        self.assertTrue(all(x["quantite_par_ha"] > 0.0 for x in d["materiaux"]))


class TestPontsDossier(unittest.TestCase):
    def test_quatre_ponts_et_quatre_limites(self):
        p = eq("EQ-18")
        self.assertEqual(len(p), 4)
        self.assertEqual([x["pilier"][:2] for x in p], ["P1", "P2", "P3", "P4"])
        for pont in p:
            for cle in ("pilier", "dossier", "agriculture", "limite"):
                self.assertTrue(pont[cle].strip())

    def test_chaque_pilier_rappelle_une_equation_du_dossier(self):
        p = eq("EQ-18")
        self.assertIn("EQ-02", p[0]["agriculture"])
        self.assertIn("EQ-16", p[1]["agriculture"])
        self.assertIn("EQ-07", p[2]["agriculture"])
        self.assertIn("EQ-15", p[3]["agriculture"])


class TestChemins(unittest.TestCase):
    def test_chaque_chemin_nomme_une_fonction_reelle(self):
        for e in M.resoudre()["equations"]:
            module, fonction, controle = [x.strip() for x in e["chemin"].split("→")]
            self.assertEqual(module, "agriculture_abondance.py")
            self.assertTrue(fonction.endswith("()"), e["chemin"])
            self.assertTrue(callable(getattr(M, fonction[:-2], None)), e["chemin"])
            self.assertEqual(controle, "C" + e["id"][3:])

    def test_statuts_dans_le_vocabulaire_declare(self):
        for e in M.resoudre()["equations"]:
            self.assertIn(e["statut"], set(M.STATUTS))


class TestAssemblage(unittest.TestCase):
    def test_tous_les_controles(self):
        donnees = M.resoudre()
        self.assertEqual(donnees["resume"]["equations"], 18)
        self.assertEqual(donnees["resume"]["controles_ok"], 18)
        self.assertEqual(donnees["resume"]["controles_total"], 18)
        self.assertTrue(M.verifier(donnees))

    def test_controles_tous_recus(self):
        for c in M.resoudre()["controles"]:
            self.assertTrue(c["ok"], c["id"])

    def test_ids_uniques_et_sequentiels(self):
        ids = [e["id"] for e in M.resoudre()["equations"]]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(ids, ["EQ-%02d" % n for n in range(1, 19)])

    def test_resume_ancre_les_nombres_cites(self):
        donnees = M.resoudre()
        r, e = donnees["resume"], {x["id"]: x["detail"] for x in donnees["equations"]}
        self.assertEqual(r["einstein_680nm_kJ"], e["EQ-02"]["einstein_kJ_par_mol_photons"])
        self.assertEqual(r["plafond_quantique_g_par_MJ_PAR"],
                         e["EQ-05"]["plafond_a_8_5_photons_g_par_MJ_PAR"])
        self.assertEqual(r["MJ_par_kg_N_haber"], e["EQ-08"]["MJ_par_kg_N"])
        self.assertEqual(r["litres_par_kg_ble_derive"], e["EQ-11"]["litres_par_kg_derive_agriculture"])
        self.assertEqual(r["annees_de_sol_reste"], e["EQ-15"]["annees_avant_horizon_perdu"])

    def test_verifier_refuse_un_controle_manquant(self):
        donnees = M.resoudre()
        donnees["controles"][0]["ok"] = False
        self.assertFalse(M.verifier(donnees))


if __name__ == "__main__":
    unittest.main(verbosity=2)
