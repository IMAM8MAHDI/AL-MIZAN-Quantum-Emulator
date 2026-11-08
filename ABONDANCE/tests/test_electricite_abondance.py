# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2026 IMAM8MAHDI / Astro-Code Ecosystem
# SPDX-License-Identifier: GPL-3.0-only OR AGPL-3.0-only
"""Tests du dossier ÉLECTRICITÉ d'ABONDANCE (unittest, stdlib uniquement).

Les valeurs attendues sont calculées ici, à partir des constantes du SI et des
formes fermées de la physique : elles ne sont pas recopiées du module testé.
"""

from __future__ import annotations

import math
import sys
import unittest
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
if str(RACINE) not in sys.path:
    sys.path.insert(0, str(RACINE))

import electricite_abondance as M  # noqa: E402

EPS0 = 8.8541878128e-12      # F/m
E_CHARGE = 1.602176634e-19   # C, valeur définie
C_VIDE = 299792458.0         # m/s, valeur définie
MU0 = 1.25663706212e-06      # N/A², CODATA 2018


def eq(id_: str) -> dict:
    return {e["id"]: e for e in M.resoudre()["equations"]}[id_]["detail"]


class TestElectrostatique(unittest.TestCase):
    def test_k_de_coulomb_vient_de_epsilon_zero(self):
        d = eq("EQ-01")
        self.assertAlmostEqual(d["ke_m2_c2"], 1.0 / (4.0 * math.pi * EPS0), places=3)
        self.assertLess(d["ke_par_mu0_c2"] / d["ke_m2_c2"], 1.0000000001)
        self.assertGreater(d["ke_par_mu0_c2"] / d["ke_m2_c2"], 0.9999999999)

    def test_un_coulomb_compte_des_avatars_d_electron(self):
        self.assertAlmostEqual(eq("EQ-01")["electrons_par_coulomb"] / (1.0 / E_CHARGE),
                               1.0, places=12)

    def test_condensateur_deux_écritures_de_l_energie(self):
        d = eq("EQ-02")
        self.assertAlmostEqual(d["energie_J"], 0.5 * d["capacite_F"] * d["tension_V"] ** 2,
                               places=15)
        self.assertAlmostEqual(d["energie_par_QV_J"], 0.5 * d["charge_C"] * d["tension_V"],
                               places=15)
        self.assertLess(abs(d["coherence"]), 1e-12)

    def test_mu0_n_est_plus_4pi_dix_moins_sept(self):
        d = eq("EQ-06")
        self.assertAlmostEqual(d["mu0"] / MU0, 1.0, places=12)
        self.assertAlmostEqual(d["mu0_historique_4pi_e_7"] / (4.0 * math.pi * 1e-7),
                               1.0, places=15)
        self.assertLess(d["ecart_relatif"], 1e-8)


class TestCircuit(unittest.TestCase):
    def test_trois_ecritures_de_puissance_coincident(self):
        d = eq("EQ-04")
        self.assertEqual(d["ecart_max_W"], 0.0)
        self.assertEqual(d["kwh_en_j"], 3.6e6)

    def test_kirchhoff_referme_le_noeud_et_le_bilan(self):
        d = eq("EQ-05")
        self.assertEqual(d["somme_noeud_exacte"], "0")
        self.assertEqual(d["bilan_puissance_exact"], "0")
        self.assertAlmostEqual(d["I2_A"] + d["I3_A"], d["I_total_A"], places=12)
        self.assertAlmostEqual(d["repartition_i2_sur_itotale"], d["I2_A"] / d["I_total_A"],
                               places=12)

    def test_un_kilowattheure_vaut_trois_mega_joules(self):
        self.assertAlmostEqual(eq("EQ-04")["P_UI_W"] / eq("EQ-04")["P_I2R_W"], 1.0,
                               places=12)


class TestElectromagnetisme(unittest.TestCase):
    def test_faraday_rms_sur_pic_est_un_sur_racine_deux(self):
        self.assertAlmostEqual(eq("EQ-07")["ratio_rms_sur_pic"], 1.0 / math.sqrt(2.0),
                               places=12)

    def test_derivation_numerique_suite_analytique(self):
        d = eq("EQ-07")
        self.assertLess(d["ecart_relatif_derivation"], 1e-6)

    def test_impedance_du_vide(self):
        d = eq("EQ-09")
        self.assertAlmostEqual(d["v_exacte_c"], C_VIDE, places=6)
        self.assertAlmostEqual(d["z0_ohm"], 376.730313668, delta=1e-4)

    def test_energies_champ_coherentes_dans_le_meme_volume(self):
        d = eq("EQ-08")
        self.assertLess(abs(d["coherence_volume"]), 1e-12)
        self.assertGreater(d["ratio_mag_sur_elec"], 0.0)


class TestAlternatif(unittest.TestCase):
    def test_aire_de_sin_carre_sur_une_periode_est_pi(self):
        d = eq("EQ-10")
        self.assertAlmostEqual(d["aire_sin2_sur_periode"], math.pi, delta=1e-9)
        self.assertAlmostEqual(d["aire_attendue_pi"], math.pi, places=15)
        self.assertAlmostEqual(d["ratio_rms_sur_crete"], 1.0 / math.sqrt(2.0), places=12)

    def test_tri_phase_racine_trois_et_phasores_nuls(self):
        d = eq("EQ-11")
        self.assertAlmostEqual(d["ratio_ligne_sur_phase"], math.sqrt(3.0), places=12)
        self.assertLess(abs(d["somme_phasores"]), 1e-9)
        self.assertAlmostEqual(d["P_trois_fois_phase_W"] / d["P_formule_sqrt3_W"], 1.0,
                               places=12)

    def test_transformateur_conserve_la_puissance_apparente(self):
        d = eq("EQ-12")
        self.assertLess(abs(d["conservation_S"]), 1e-12)
        self.assertAlmostEqual(d["rapport_spires"], d["rapport_tensions"], places=12)
        self.assertAlmostEqual(d["I_primaire_A"] * d["rapport_spires"],
                               d["I_secondaire_A"], places=6)


class TestTransport(unittest.TestCase):
    def test_pertes_en_inverse_du_carre_de_la_tension(self):
        d = eq("EQ-13")
        self.assertEqual(d["attendu_en_inverse_carre"], d["ratios_pertes"])
        self.assertEqual(d["ecart_max"], 0.0)
        self.assertEqual(d["gain_400V_vers_400kV"], 1e6)
        self.assertEqual(M.resoudre()["resume"]["pertes_1GW_a_400kV_W"], 312500.0)

    def test_chute_hydro_gene_par_metre_cube(self):
        d = eq("EQ-14")
        self.assertEqual(d["J_par_m3"], 1000.0 * 9.80665 * 100.0)
        self.assertAlmostEqual(d["kWh_par_m3"], 980665.0 / 3.6e6, places=12)
        self.assertLess(abs(d["coherence_par_m3"]), 1e-12)


class TestPlafonds(unittest.TestCase):
    def test_betz_seize_sur_vingt_sept(self):
        d = eq("EQ-15")
        self.assertAlmostEqual(d["cp_max"], 16.0 / 27.0, places=12)
        self.assertAlmostEqual(d["seize_sur_vingt_sept"], 16.0 / 27.0, places=15)
        self.assertAlmostEqual(d["a_max_bissection"], 1.0 / 3.0, delta=1e-7)
        self.assertLess(abs(d["derivee_nulle_en_a_star"]), 1e-6)
        self.assertAlmostEqual(d["puissance_max_capturable_W"] / d["puissance_disponible_W"],
                               16.0 / 27.0, places=9)

    def test_carnot_800_sur_300(self):
        d = eq("EQ-16")
        self.assertAlmostEqual(d["eta_carnot"], 1.0 - 300.0 / 800.0, places=12)
        self.assertAlmostEqual(d["somme_eta_plus_rejet"], 1.0, places=12)
        self.assertLess(d["ratio_meilleur_sur_carnot"], 1.0000000001)

    def test_seuil_d_absorption_d_un_semiconducteur(self):
        d = eq("EQ-17")
        self.assertAlmostEqual(d["constante_eV_nm"], 1239.841984, delta=1e-3)
        self.assertAlmostEqual(d["lambda_seuil_si_nm"], d["constante_eV_nm"] / 1.12,
                               delta=1e-3)


class TestStockageEtReseaux(unittest.TestCase):
    def test_equivalences_de_stockage(self):
        d = eq("EQ-18")
        for cle, wh in d["Wh_par_kg"].items():
            self.assertAlmostEqual(d["kWh_par_kg"][cle], wh / 1000.0, places=9)
        self.assertAlmostEqual(d["Wh_par_kg"]["dihydrogene LHV"] * 3600.0, 1.2e8, delta=1e3)
        self.assertAlmostEqual(d["Wh_par_kg"]["essence PCI"] * 3600.0, 4.6e7, delta=1e3)

    def test_bcs_et_zero_pertes_en_supra(self):
        d = eq("EQ-19")
        self.assertAlmostEqual(d["gap_ybco_meV"] / d["gap_nbti_meV"], 10.0, places=6)
        self.assertAlmostEqual(d["rapport_verifie"], 3.53, places=2)
        self.assertEqual(d["pertes_ohmiques_supra_W"], 0.0)
        self.assertAlmostEqual(d["k_B_eV_K"], 8.617333262e-05, delta=1e-12)

    def test_budget_solaire_de_la_planete(self):
        d = eq("EQ-20")
        self.assertAlmostEqual(d["section_terre_m2"] / (math.pi * 6371000.0 ** 2), 1.0,
                               places=6)
        self.assertAlmostEqual(d["irradiance_hors_atmosphere_W_m2"], 1361.0, delta=2.0)
        self.assertGreater(d["ratio_interceptee_sur_consommee"], 9000.0)
        self.assertLess(d["ratio_interceptee_sur_consommee"], 9300.0)


class TestChemins(unittest.TestCase):
    def test_chaque_chemin_nomme_une_fonction_reelle(self):
        for e in M.resoudre()["equations"]:
            module, fonction, controle = [x.strip() for x in e["chemin"].split("→")]
            self.assertEqual(module, "electricite_abondance.py")
            self.assertTrue(fonction.endswith("()"), e["chemin"])
            self.assertTrue(callable(getattr(M, fonction[:-2], None)), e["chemin"])
            self.assertEqual(controle, "C" + e["id"][3:])

    def test_statuts_dans_le_vocabulaire_declare(self):
        admissibles = {"OPÉRATIONNEL", "SIMULÉ", "SPÉCIFIÉ"}
        for e in M.resoudre()["equations"]:
            self.assertIn(e["statut"], admissibles)


class TestAssemblage(unittest.TestCase):
    def test_tous_les_controles(self):
        donnees = M.resoudre()
        self.assertEqual(donnees["resume"]["equations"], 21)
        self.assertEqual(donnees["resume"]["controles_ok"], 21)
        self.assertEqual(donnees["resume"]["controles_total"], 21)
        self.assertTrue(M.verifier(donnees))

    def test_controles_tous_recus(self):
        for c in M.resoudre()["controles"]:
            self.assertTrue(c["ok"], c["id"])

    def test_ids_uniques_et_sequentiels(self):
        ids = [e["id"] for e in M.resoudre()["equations"]]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(ids[0], "EQ-01")
        self.assertEqual(ids[-1], "EQ-21")
        self.assertEqual(ids, ["EQ-%02d" % n for n in range(1, 22)])

    def test_verifier_refuse_un_controle_manquant(self):
        donnees = M.resoudre()
        donnees["controles"][0]["ok"] = False
        self.assertFalse(M.verifier(donnees))


if __name__ == "__main__":
    unittest.main()
