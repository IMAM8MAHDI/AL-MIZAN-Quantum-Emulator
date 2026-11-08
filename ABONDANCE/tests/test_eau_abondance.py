# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2026 IMAM8MAHDI / Astro-Code Ecosystem
# SPDX-License-Identifier: GPL-3.0-only OR AGPL-3.0-only
"""Tests du dossier EAU d'ABONDANCE (unittest, stdlib uniquement).

Les grandeurs attendues sont recalculées dans ce fichier à partir des formes
fermées de l'hydrostatique, de la thermodynamique et des constantes du SI ;
elles ne sont pas recopiées du module testé.
"""

from __future__ import annotations

import math
import sys
import unittest
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
if str(RACINE) not in sys.path:
    sys.path.insert(0, str(RACINE))

import eau_abondance as M  # noqa: E402

R_AIR = 8.314462618        # J/(mol·K)
G = 9.80665                # m/s², convention
T_25C = 298.15             # K
RHO_EAU = 1000.0           # kg/m³
RHO_GLACE = 917.0          # kg/m³
RHO_EAU_DE_MER = 1025.0    # kg/m³


def eq(id_: str) -> dict:
    return {e["id"]: e for e in M.resoudre()["equations"]}[id_]["detail"]


class TestReserve(unittest.TestCase):
    def test_l_eau_douce_faisonne_la_planete(self):
        d = eq("EQ-01")
        self.assertEqual(d["fermeture_des_volumes"], 0.0)
        self.assertAlmostEqual(d["douce_pct"] + d["sale_pct"], 100.0, places=10)
        self.assertAlmostEqual(d["douce_km3"] / d["total_km3"] * 100.0, d["douce_pct"],
                               places=6)

    def test_la_repartition_des_compartiments_somme_a_cent(self):
        d = eq("EQ-01")
        self.assertAlmostEqual(d["somme_repartition"], 100.0, places=6)
        self.assertGreater(d["debit_renouvelable_km3_an"], 0.0)


class TestHydrostatique(unittest.TestCase):
    def test_la_convention_des_cent_metres_et_l_eau_a_vingt_cinq_degres(self):
        d = eq("EQ-02")
        self.assertAlmostEqual(d["J_par_m3_convention_std"], RHO_EAU * G * 100.0, places=6)
        self.assertLess(d["J_par_m3_eau_douce_25C"], d["J_par_m3_convention_std"])
        self.assertGreater(d["J_par_m3_eau_de_mer"], d["J_par_m3_convention_std"])
        self.assertEqual(d["coherence_avec_elec"], 0.0)

    def test_dix_metres_d_eau_font_deux_atmospheres_absolues(self):
        d = eq("EQ-02")
        self.assertAlmostEqual(d["P_a_10m_Pa"], 10.0 * d["force_par_m2_a_1m_N"], places=9)
        self.assertAlmostEqual(d["atm_a_10m"], 1.0 + d["P_a_10m_Pa"] / 101325.0, places=9)

    def test_glace_flottante_part_immergee(self):
        d = eq("EQ-03")
        self.assertAlmostEqual(d["part_immergee_glace"], RHO_GLACE / RHO_EAU_DE_MER,
                               places=12)
        self.assertAlmostEqual(d["part_immergee_glace"] + d["part_emergee_glace"], 1.0,
                               places=12)
        self.assertEqual(d["equilibre"], 0.0)


class TestEcoulement(unittest.TestCase):
    def test_continuite_ne_perd_aucun_debit(self):
        d = eq("EQ-04")
        self.assertEqual(d["max_ecart"], 0.0)
        self.assertAlmostEqual(d["rapport_sections"],
                               d["rapport_v_max_sur_v_min"], places=6)

    def test_torricelli_vracine_de_2gh(self):
        d = eq("EQ-05")
        self.assertEqual(d["attendu_g"], G)
        self.assertAlmostEqual(d["v10m_m_s"], math.sqrt(2.0 * G * 10.0), places=9)
        self.assertAlmostEqual(d["dPE_dh"], G, places=6)
        self.assertAlmostEqual(d["kg_par_m3_par_v2_sur_2"], 1.0, places=12)


class TestPompage(unittest.TestCase):
    def test_le_pompage_ne_pretend_pas_battre_la_borne(self):
        d = eq("EQ-06")
        self.assertLess(d["ratio_pompage_sur_borne_dessalement"], 1.0)
        self.assertGreater(d["rendement_declare"], 0.0)
        self.assertLess(d["rendement_declare"], 1.0)


class TestOsmose(unittest.TestCase):
    def test_deux_voies_de_pressione_osmotique(self):
        d = eq("EQ-07")
        self.assertLess(d["ecart_relatif_deux_voies"], 0.03)
        self.assertGreater(d["pi_ideale_bar"], 30.0)
        self.assertLess(d["pi_ideale_bar"], 31.0)
        self.assertAlmostEqual(d["x_eau"] + d["fraction_molaire_sel"], 1.0, places=12)

    def test_vant_hoff_et_loi_des_gaz_par_m3(self):
        d = eq("EQ-07")
        self.assertAlmostEqual(d["pi_ideale_Pa"],
                               d["c_osm_osm_par_m3"] * R_AIR * T_25C, places=3)

    def test_le_travail_minimum_suivant_le_nombre_de_moles(self):
        d = eq("EQ-08")
        self.assertAlmostEqual(d["J_par_mol_eau"],
                               R_AIR * T_25C * math.log(1.0 / d["x_eau"]), places=6)
        self.assertAlmostEqual(d["kWh_par_m3"], d["J_par_m3"] / 3.6e6, places=12)
        self.assertAlmostEqual(d["kWh_par_m3"], M.resoudre()["resume"]["travail_minimum_kWh_m3"],
                               places=12)

    def test_la_borne_est_un_minimum_pas_une_usine(self):
        d = eq("EQ-09")
        self.assertEqual(d["residus_bilan_max"], 0.0)
        self.assertGreater(d["sec_pratique_declare_kWh_m3"],
                           M.resoudre()["resume"]["travail_minimum_kWh_m3"])
        self.assertTrue(d["limite"])


class TestVapeur(unittest.TestCase):
    def test_magnus_et_clausius_s_accordent_a_25_degres(self):
        d = eq("EQ-10")
        self.assertLess(d["ecart_relatif_25C"], 0.03)
        self.assertGreater(d["magnus_25C_hPa"], 31.0)
        self.assertLess(d["magnus_25C_hPa"], 32.0)

    def test_un_millimetre_de_pluie_est_un_litre_par_metre_carre(self):
        self.assertEqual(eq("EQ-10")["pluie_de_1mm_en_L_par_m2"], 1.0)

    def test_evaporer_un_metre_cube_exige_deux_centimes_de_megawatt_heure(self):
        d = eq("EQ-10")
        self.assertAlmostEqual(d["equivalent_kWh_par_m3"], d["evaporer_1_m3_exige_J"] / 3.6e6,
                               places=9)
        self.assertGreater(d["equivalent_kWh_par_m3"], 600.0)


class TestCycles(unittest.TestCase):
    def test_le_bilan_planetaire_se_ferme(self):
        d = eq("EQ-11")
        self.assertEqual(d["cloture_planetaire"], 0.0)
        self.assertEqual(d["solde_terre"], 0.0)
        self.assertEqual(d["solde_ocean"], 0.0)

    def test_les_mm_par_an_sont_des_flux_divises_par_leur_surface(self):
        d = eq("EQ-11")
        km3 = d["km3_par_an"]
        terre = km3["precip_terre"] * 1e9 / (M.SURFACE_TERRE_KM2 * 1e6) * 1e3
        ocean = (km3["precip_ocean"] * 1e9
                 / ((M.SURFACE_RACINE_KM2 - M.SURFACE_TERRE_KM2) * 1e6) * 1e3)
        planete = (km3["precip_terre"] + km3["precip_ocean"]) * 1e9 / (M.SURFACE_RACINE_KM2 * 1e6) * 1e3
        self.assertAlmostEqual(d["mm_par_an_sur_terre_emergee"], terre, places=9)
        self.assertAlmostEqual(d["mm_par_an_planete"], planete, places=9)
        self.assertLess(terre, planete)
        self.assertLess(planete, ocean)
        self.assertAlmostEqual(M.resoudre()["resume"]["precipitations_terre_mm_par_an"],
                               d["mm_par_an_sur_terre_emergee"], places=9)


class TestEauVirtuelle(unittest.TestCase):
    def test_le_litrage_par_metre_cube_est_exact(self):
        d = eq("EQ-12")
        self.assertAlmostEqual(d["litres_par_m3"], 1000.0, places=6)
        self.assertGreater(d["ratio_agricole_sur_domestique"], 1.0)
        self.assertAlmostEqual(d["litres_par_personne_par_jour"],
                               d["litres_par_personne_par_an"] / 365.0, places=6)

    def test_conductivite_et_salinite_sont_reciproques(self):
        d = eq("EQ-13")
        self.assertAlmostEqual(d["reciproque"], d["facteur_declare"], places=12)
        self.assertAlmostEqual(d["EC_seuil_potable_dS_m"],
                               d["seuil_potable_g_kg"] / d["facteur_declare"], places=9)
        self.assertAlmostEqual(d["conductivite_eau_de_mer_S_m"],
                               d["EC_eau_de_mer_dS_m"] / 10.0, places=6)


class TestStockageGravitaireEau(unittest.TestCase):
    def test_le_kilometre_cube_sous_cent_metres(self):
        d = eq("EQ-14")
        self.assertEqual(d["J_par_m3"], RHO_EAU * G * 100.0)
        self.assertAlmostEqual(d["energie_J"], RHO_EAU * G * 100.0 * 1000.0 ** 3, places=3)
        self.assertAlmostEqual(d["energie_GWh"], d["energie_J"] / 3.6e12, places=9)
        self.assertEqual(d["identique_a_electricite_hydro"], 0.0)
        self.assertAlmostEqual(d["energie_GWh"], 272.40694444444443, places=6)


class TestChemins(unittest.TestCase):
    def test_chaque_chemin_nomme_une_fonction_reelle(self):
        for e in M.resoudre()["equations"]:
            module, fonction, controle = [x.strip() for x in e["chemin"].split("→")]
            self.assertEqual(module, "eau_abondance.py")
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
        self.assertEqual(donnees["resume"]["equations"], 15)
        self.assertEqual(donnees["resume"]["controles_ok"], 15)
        self.assertEqual(donnees["resume"]["controles_total"], 15)
        self.assertTrue(M.verifier(donnees))

    def test_controles_tous_recus(self):
        for c in M.resoudre()["controles"]:
            self.assertTrue(c["ok"], c["id"])

    def test_ids_uniques_et_sequentiels(self):
        ids = [e["id"] for e in M.resoudre()["equations"]]
        self.assertEqual(ids, ["EQ-%02d" % n for n in range(1, 16)])

    def test_resume_ancre_les_quatre_nombres_cites(self):
        r = M.resoudre()["resume"]
        self.assertAlmostEqual(r["pompage_50m_kWh_m3"], 0.208915172008547, places=12)
        self.assertAlmostEqual(r["pression_osmotique_ideale_bar"], 30.435517945580315,
                               places=12)
        self.assertAlmostEqual(r["energie_1km3_sous_100m_GWh"], 272.40694444444443, places=9)
        self.assertAlmostEqual(r["eau_virtuelle_L_par_personne_par_jour"],
                               2201.3698630136987, places=9)

    def test_verifier_refuse_un_controle_manquant(self):
        donnees = M.resoudre()
        donnees["controles"][0]["ok"] = False
        self.assertFalse(M.verifier(donnees))


if __name__ == "__main__":
    unittest.main()
