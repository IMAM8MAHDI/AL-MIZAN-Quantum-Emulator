# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2026 IMAM8MAHDI / Astro-Code Ecosystem
# SPDX-License-Identifier: GPL-3.0-only OR AGPL-3.0-only
"""Tests du dossier FONDATION — un axiome posé hors matrice, quatre piliers, dix-huit nœuds.

Trois exigences, dans l'ordre :

  1. ce qui est annoncé comme calculé est RE-CALCULÉ ici, formule réécrite à la main dans ce
     fichier, et non rappelée depuis le module ;
  2. la prédiction gelée est testée STRUCTURELLEMENT : sa signature, son digest, et le fait
     qu'elle ne bouge pas quand on lui injecte des résultats publiés ;
  3. aucune garde n'est décorative : chaque contrôle est mis à l'épreuve sur une copie
     fabriquée pour le violer (cycle dans le graphe, doublon dans le registre, import tiers,
     comparateur lu, hypothèse théorique doublée).

Stdlib uniquement. La vidéo ne fournit ici que sa propre métadonnée mesurée : aucun de ses
termes ne sert de nombre.

    cd FONDATION && py -3 -m unittest tests.test_fondation -v
"""

import inspect
import json
import math
import sys
import tempfile
import unittest
from pathlib import Path

RACINE_DOSSIER = Path(__file__).resolve().parent.parent
if str(RACINE_DOSSIER) not in sys.path:
    sys.path.insert(0, str(RACINE_DOSSIER))

import fondation_base as FB                                          # noqa: E402

BR_SM, DBR_SM = 8.4e-11, 1.0e-11
N_K18, SES18 = 2.7e12, 0.839e-11
N_K22, SES22 = 2.85e12, 8.48e-12


class TestAxiomeEtPiliers(unittest.TestCase):
    """L'axiome ne doit fournir AUCUN nombre : c'est la seule chose qu'on lui demande."""

    def test_axiome_ne_fournit_aucun_nombre(self):
        self.assertEqual(FB.AXIOME["nombres_fournis_par_l_axiome"], 0)
        self.assertIs(FB.AXIOME["hors_matrice"], True)
        self.assertTrue(FB.AXIOME["statut"].startswith("SPÉCIFIÉ"))
        self.assertEqual(len(FB.AXIOME["ce_que_ca_ne_veut_pas_dire"]), 3)

    def test_quatre_piliers_trois_couches_trois_statuts(self):
        self.assertEqual(sorted(FB.PILIERS),
                         ["P1 UNITE", "P2 BORNE", "P3 CONFRONTATION", "P4 TRANSMISSION"])
        self.assertEqual(sorted(FB.COUCHES),
                         ["S1 MESURABLE", "S2 REGULARITE", "S3 HORS_MATRICE"])
        self.assertEqual(sorted(FB.STATUTS), ["OPÉRATIONNEL", "SIMULÉ", "SPÉCIFIÉ"])

    def test_la_video_ne_fournit_aucun_nombre(self):
        """Aucun chiffre de DECLARE/COMPARE ne vient de la chaîne : les deux blocs s'excluent."""
        texte = json.dumps({"declare": FB.DECLARE, "compare": FB.COMPARE},
                           ensure_ascii=False, default=str)
        for marque in ("5pP1e69T3HQ", "Nocturne", "YouTube", "youtube"):
            self.assertNotIn(marque, texte)
        self.assertEqual(FB.SOURCE["chapitres_publics"], 0)
        self.assertTrue(FB.SOURCE["transcript"].startswith("absent"))
        self.assertEqual(len(FB.SOURCE["avertissements_sonde"]), 3)
        self.assertEqual(FB.SOURCE["duree_s"], 8018)


class TestDisciplineSource(unittest.TestCase):
    """Ce que la chaîne a fourni se vérifie dans son texte ; ce qu'elle n'a pas fourni s'écrit."""

    def test_extraits_sont_des_sous_chaines_du_texte_mesure(self):
        d = FB.discipline_sources()
        self.assertEqual(d["extraits_non_trouves"], [])
        self.assertEqual(len(d["extraits_verbatimes"]), len(FB.SOURCE["extraits_description"]))
        self.assertTrue(all(d["extraits_verbatimes"].values()))
        self.assertEqual(d["horodatages_cites"], [])
        self.assertEqual(d["chapitres_publics"], 0)
        self.assertEqual(set(d["transcript_octets"].values()), {0})
        self.assertLess(d["caracteres_retenus"], d["caracteres_mesures"])
        self.assertEqual(FB.SOURCE["description_verbatim"][:24], "En septembre 2024, l’exp")

    def test_extrait_invente_et_horodatage_pret_ex_se_voient(self):
        """Non-vacuité : une phrase inventée et un minutage prêté à la vidéo doivent ressortir."""
        original = FB.SOURCE
        try:
            FB.SOURCE = dict(original,
                             extraits_description=list(original["extraits_description"])
                             + ["le CERN a mesuré 42 événements exacts"])
            d = FB.discipline_sources()
            self.assertEqual(len(d["extraits_non_trouves"]), 1,
                             "une phrase pretée à la chaîne passe inapercue")
            FB.SOURCE = dict(original, description_verbatim=original["description_verbatim"]
                             + "\n3:14 — chapitre inventé")
            d2 = FB.discipline_sources()
            self.assertEqual(d2["horodatages_cites"], ["3:14"],
                             "un minutage écrit dans le texte mesuré n'est pas relevé")
        finally:
            FB.SOURCE = original
        d3 = FB.discipline_sources()
        self.assertEqual(d3["horodatages_cites"], [])
        self.assertEqual(d3["extraits_non_trouves"], [])


class TestGraphe(unittest.TestCase):
    """Le graphe est revérifié par un tri topologique de Kahn, voie indépendante de la DFS."""

    def test_tri_topologique_de_kahn(self):
        noeuds = sorted(FB.NOEUDS)
        degres = {n: len(FB.NOEUDS[n]["depend"]) for n in noeuds}
        file = [n for n in noeuds if degres[n] == 0]
        ordre = []
        while file:
            n = file.pop(0)
            ordre.append(n)
            for m in noeuds:
                if n in FB.NOEUDS[m]["depend"]:
                    degres[m] -= 1
                    if degres[m] == 0:
                        file.append(m)
        self.assertEqual(len(ordre), 18, "Kahn ne débloque que " + str(len(ordre)) + " nœuds")
        self.assertEqual(sorted(ordre), noeuds)
        position = {n: i for i, n in enumerate(ordre)}
        for n in noeuds:
            for src in FB.NOEUDS[n]["depend"]:
                self.assertLess(position[src], position[n], f"{src} après {n} dans l'ordre de Kahn")
        g = FB.graphe_dependances()
        self.assertTrue(g["acyclique"])
        self.assertEqual(g["noeuds"], 18)
        self.assertEqual(g["atteignables"], 18)
        self.assertEqual(g["racines"], ["EQ-01"])
        self.assertEqual(g["self_references"], [])

    def test_dependances_toujours_vers_un_numero_inferieur(self):
        for n, d in FB.NOEUDS.items():
            self.assertEqual(d["depend"], sorted(d["depend"]), n)
            for src in d["depend"]:
                self.assertLess(int(src[3:]), int(n[3:]), f"{n} dépend de {src}")
            self.assertTrue(d["depend"] == [] or all(s in FB.NOEUDS for s in d["depend"]), n)
            for p in d["piliers"]:
                self.assertIn(p, FB.PILIERS, n)
            self.assertIn(d["couche"], FB.COUCHES, n)

    def test_racines_fondees_hors_du_dossier(self):
        g = FB.graphe_dependances()
        self.assertTrue(g["racines_fondees_dehors"])
        for n in FB.NOEUDS:
            if not FB.NOEUDS[n]["depend"]:
                self.assertTrue(FB.NOEUDS[n]["externe"], f"{n} : racine sans source extérieure")

    def test_douze_cases_pilier_couche_habitees(self):
        g = FB.graphe_dependances()
        m = g["matrice_pilier_couche"]
        self.assertEqual(len(m), 4)
        self.assertEqual(g["cases_vides"], [])
        self.assertEqual(sum(len(v) for ligne in m.values() for v in ligne.values()),
                         sum(len(FB.NOEUDS[n]["piliers"]) for n in FB.NOEUDS))
        self.assertEqual(g["couche_vide"], [])

    def test_cycle_inject_se_voit(self):
        """Non-vacuité : une dépendance circulaire fabriquée doit lever `cycle`."""
        original = FB.NOEUDS
        try:
            copie = {k: dict(v, depend=list(v["depend"])) for k, v in original.items()}
            copie["EQ-01"]["depend"].append("EQ-18")
            FB.NOEUDS = copie
            g = FB.graphe_dependances()
            self.assertFalse(g["acyclique"], "le cycle EQ-01 → EQ-18 → EQ-01 passe inaperçu")
            self.assertTrue(g["cycle"])
        finally:
            FB.NOEUDS = original
        self.assertTrue(FB.graphe_dependances()["acyclique"])


class TestRegistre(unittest.TestCase):
    """P1 UNITE : une grandeur, une valeur, une unité, une source — et le registre ferme."""

    def test_registre_egal_declare(self):
        r = FB.registre_grandeurs()
        self.assertEqual(r["entrees"], r["noms_uniques"])
        self.assertEqual(r["doublons_en_conflit"], [])
        self.assertEqual(r["unites_vide"], [])
        self.assertEqual(r["valeurs_non_numeriques"], [])
        self.assertEqual(r["hors_declare"], [])
        self.assertEqual(r["declare_sans_entree"], [])

    def test_valeurs_recalculees_a_la_main(self):
        attendu = {"BR_sm": 8.4e-11, "dBR_sm": 1.0e-11, "N_K_2016_2018": 2.7e12,
                   "SES_2016_2018": 0.839e-11, "N_K_2021_2022": 2.85e12,
                   "SES_2021_2022": 8.48e-12, "secondaires_par_s": 1.0e9,
                   "fraction_K_plus": 0.06, "annees_prises_2016_2018": 3.0,
                   "rejection_mu": 1.0e7, "rejection_pi0": 1.0e8,
                   "rejection_autres_canaux": 1.0e4, "seuil_observation": 5.0,
                   "z_declare_2024": 1.7}
        self.assertEqual(sorted(FB.DECLARE), sorted(attendu))
        for nom, valeur in attendu.items():
            self.assertEqual(FB.DECLARE[nom], valeur, nom)

    def test_doublon_en_conflit_se_voit(self):
        """Non-vacuité : la même grandeur déclarée deux fois est dénoncée."""
        table = [("BR_sm", 8.4e-11, "1", "JHEP 11 (2015) 33"),
                 ("BR_sm", 9.9e-11, "1", "autre source"),
                 ("N_K_2016_2018", 2.7e12, "désintégrations", "arXiv:2103.15389")]
        r = FB.registre_grandeurs(table)
        self.assertEqual(r["doublons_en_conflit"], ["BR_sm"])
        self.assertEqual(r["entrees"], 3)
        self.assertEqual(r["noms_uniques"], 2)

    def test_unite_vide_et_valeur_non_numerique_se_voient(self):
        table = [("z_declare_2024", 1.7, "", "arXiv:2412.12015"),
                 ("seuil_observation", "cinq", "sigma", "communauté")]
        r = FB.registre_grandeurs(table)
        self.assertEqual(r["unites_vide"], ["z_declare_2024"])
        self.assertEqual(r["valeurs_non_numeriques"], ["seuil_observation"])

    def test_prediction_et_comparateur_disjoints(self):
        cle_pred = set(FB.prediction_gel(FB.DECLARE)["variables_libres"])
        cle_comp = set(FB.cle_comparateur())
        self.assertEqual(cle_pred & cle_comp, set())
        self.assertIn("desintegrations_ordinaires", cle_comp)
        self.assertIn("N_exp_SM", cle_comp)
        self.assertNotIn("source", cle_comp)
        self.assertNotIn("verbe_publie", cle_comp)


class TestPrimitives(unittest.TestCase):
    """Quatre primitives, chacune re-vérifiée par une voie écrite ici."""

    TABLE_P = {1.0: 0.158_655_253_9, 2.0: 0.022_750_131_9, 3.0: 0.001_349_898_0,
               5.0: 2.866_515_7e-7}

    def test_p_seuil_contre_table_publiee(self):
        for z, p in self.TABLE_P.items():
            self.assertAlmostEqual(FB.p_seuil(z), p, delta=p * 1e-6, msg=f"z={z}")

    def test_p_seuil_deux_ecritures(self):
        for z in (0.5, 1.0, 1.7, 2.5, 3.5, 5.0, 6.34):
            self.assertAlmostEqual(FB.p_seuil(z), 0.5 * (1.0 - math.erf(z / math.sqrt(2.0))),
                                   places=15)
            self.assertAlmostEqual(FB.z_de_p_seuil(FB.p_seuil(z)), z, places=6)
        self.assertAlmostEqual(FB.p_seuil(0.0), 0.5, places=15)
        with self.assertRaises(ValueError):
            FB.z_de_p_seuil(0.7)
        with self.assertRaises(ValueError):
            FB.z_de_p_seuil(0.0)

    def test_signification_lima_formule_reecrite(self):
        for n, b in ((20.0, 7.03), (51.0, 18.0), (100.0, 40.0), (12.5, 3.0)):
            attendu = math.sqrt(2.0 * (n * math.log(n / b) - n + b))
            self.assertAlmostEqual(FB.signification_lima(n, b), attendu, places=12)
        for n, b in ((9.0, 9.0), (5.0, 9.0), (0.0, 3.0)):
            self.assertEqual(FB.signification_lima(n, b), 0.0)

    def test_evenements_requis_se_referme_sur_cinq(self):
        for fond in (1.0, 7.03, 18.0, 120.0):
            s = FB.evenements_requis(fond, 5.0)
            self.assertGreater(s, 0.0)
            self.assertAlmostEqual(FB.signification_lima(fond + s, fond), 5.0, places=6)
            self.assertLess(FB.evenements_requis(fond, 3.0), s, "le seuil n'est pas monotone")

    def test_intervalle_ordinaires_decroissant(self):
        bas, haut = FB.intervalle_ordinaires(13.0e-11, 3.3e-11, 3.0e-11)
        self.assertLess(bas, haut)
        self.assertAlmostEqual(bas, 1.0 / 1.63e-10 - 1.0, places=3)
        self.assertAlmostEqual(haut, 1.0 / 1.0e-10 - 1.0, delta=1.0)


class TestPredictionGelee(unittest.TestCase):
    """P3 : la prédiction ne voit le comparateur ni par sa signature, ni par son digest."""

    def test_signature_d_un_seul_parametre(self):
        self.assertEqual(list(inspect.signature(FB.prediction_gel).parameters), ["declares"])

    def test_valeurs_recalculees_a_la_main(self):
        a18 = 1.0 / (N_K18 * SES18)
        attendu = {"acceptance_2016_2018": a18,
                   "n_signal_2016_2018": N_K18 * BR_SM * a18,
                   "kaons_par_seconde": 1.0e9 * 0.06}
        gel = FB.prediction_gel(FB.DECLARE)
        for cle, valeur in attendu.items():
            self.assertAlmostEqual(gel["valeurs"][cle], valeur,
                                   delta=abs(valeur) * 1e-12, msg=cle)
        self.assertAlmostEqual(a18, 0.0441443, places=6)
        self.assertAlmostEqual(attendu["n_signal_2016_2018"], 10.0119, places=4)
        self.assertFalse(gel["a_lu_le_comparateur"])
        self.assertEqual(gel["cle_interdites_trouvees"], [])

    def test_digest_insensible_aux_resultats_injectes(self):
        pur = FB.prediction_gel(FB.DECLARE)
        fausse = FB.prediction_gel(dict(FB.DECLARE, candidates=10 ** 9, fond=0.0, BR=1.0,
                                       p_value=1.0, desintegrations_ordinaires=42,
                                       N_exp_SM=99.0, d_fond=(1.0, 2.0)))
        self.assertEqual(pur["digest"], fausse["digest"],
                         "la prédiction a bougé en lisant le comparateur")
        self.assertEqual(pur["valeurs"], fausse["valeurs"])
        self.assertTrue(fausse["a_lu_le_comparateur"])
        self.assertEqual(fausse["cle_interdites_trouvees"],
                         sorted(["BR", "N_exp_SM", "candidates", "d_fond",
                                 "desintegrations_ordinaires", "fond", "p_value"]))

    def test_digest_sensible_aux_hypotheses(self):
        de = FB.prediction_gel(FB.DECLARE)
        autre = FB.prediction_gel(dict(FB.DECLARE, BR_sm=BR_SM * 2.0))
        self.assertNotEqual(de["digest"], autre["digest"],
                            "doubler le taux théorique ne change rien : rien n'est calculé")
        self.assertAlmostEqual(autre["valeurs"]["n_signal_2016_2018"],
                               de["valeurs"]["n_signal_2016_2018"] * 2.0, places=9)


class TestArithmetiqueNA62(unittest.TestCase):
    """Chaque chiffre publié repris par le module est recalculé ici, formule réécrite."""

    def test_cloture_des_acceptations(self):
        a18, a22 = 1.0 / (N_K18 * SES18), 1.0 / (N_K22 * SES22)
        c9 = FB.eq09_cloture_acceptance()
        self.assertAlmostEqual(c9["acceptance_2016_2018"], a18, places=15)
        self.assertAlmostEqual(c9["acceptance_2021_2022"], a22, places=15)
        self.assertAlmostEqual(c9["rapport_acceptances"], a22 / a18, places=12)
        self.assertAlmostEqual(a22 / a18, 0.93731, places=5)
        n_calcule = N_K18 * BR_SM * a18
        self.assertAlmostEqual(c9["n_attendu_calcule"], n_calcule, places=9)
        self.assertAlmostEqual(n_calcule, 10.0119, places=4)
        self.assertLess(c9["ecart_relatif"], 0.01)

    def test_prediction_contre_exces_2021(self):
        c10 = FB.eq10_prediction_gelee()
        prevu = BR_SM / SES18
        sigma = math.sqrt(prevu + 7.03)
        self.assertAlmostEqual(c10["prevu"], prevu, places=9)
        self.assertAlmostEqual(c10["observe_excess"], 20 - 7.03, places=10)
        self.assertAlmostEqual(c10["ecart_en_sigma"], (20 - 7.03 - prevu) / sigma, places=9)
        self.assertLess(abs(c10["ecart_en_sigma"]), 2.0)

    def test_signification_2021_sous_cinq_sigma(self):
        c11 = FB.eq11_signification_2021()
        z_lima = math.sqrt(2 * (20 * math.log(20 / 7.03) - (20 - 7.03)))
        self.assertAlmostEqual(c11["z_lima"], z_lima, places=10)
        self.assertLess(z_lima, 5.0)
        self.assertLess(c11["z_publiee"], 5.0)
        self.assertTrue(c11["les_deux_sous_cinq_sigma"])
        self.assertIn("evidence", c11["verbe"])
        self.assertIn("pas une observation", c11["verbe"])

    def test_seuil_cinq_sigma_2024(self):
        c12 = FB.eq12_seuil_cinq_sigma()
        self.assertAlmostEqual(c12["excess_requis"], FB.evenements_requis(18.0, 5.0), places=9)
        self.assertGreater(c12["marge"], 0.0)
        z_lima = math.sqrt(2 * (51 * math.log(51 / 18.0) - 33.0))
        self.assertAlmostEqual(c12["z_lima"], z_lima, places=10)
        self.assertGreater(c12["z_publiee"], 5.0)
        self.assertTrue(c12["les_deux_au_dessus_de_cinq"])

    def test_confrontation_2024_et_non_chevauchement(self):
        c13 = FB.eq13_confrontation_2024()
        z_sup = (13.0e-11 - BR_SM) / math.sqrt((3.3e-11) ** 2 + DBR_SM ** 2)
        z_inf = (13.0e-11 - BR_SM) / math.sqrt((3.0e-11) ** 2 + DBR_SM ** 2)
        self.assertAlmostEqual(c13["z_branches"][0], z_sup, places=12)
        self.assertAlmostEqual(c13["z_branches"][1], z_inf, places=12)
        self.assertLess(max(z_sup, z_inf), 1.7)
        self.assertFalse(c13["chevauchement_a_un_sigma"],
                         "le module annonce un chevauchement que les nombres ne donnent pas")
        self.assertGreater(c13["intervalle_observe"][0], c13["intervalle_sm"][1])

    def test_mise_a_jour_2026_sous_un_sigma(self):
        c14 = FB.eq14_confrontation_2026()
        z = (9.6e-11 - BR_SM) / math.sqrt((1.9e-11) ** 2 + DBR_SM ** 2)
        self.assertAlmostEqual(c14["z_contre_sm"], z, places=12)
        self.assertLess(max(c14["z_contre_sm"], c14["z_branche_inf"]), 1.0)
        self.assertTrue(c14["sous_un_sigma"])

    def test_budget_de_fond(self):
        c15 = FB.eq15_budget_fond()
        requise = 2.7e12 / 7.03
        self.assertAlmostEqual(c15["suppression_totale_requise"], requise, places=6)
        self.assertEqual(c15["chaine_declaree_mu_x_pi0"], 1.0e15)
        self.assertAlmostEqual(c15["marge_en_ordres_de_grandeur"], math.log10(1e15 / requise),
                               places=9)
        self.assertGreater(c15["marge_en_ordres_de_grandeur"], 3.0)
        self.assertTrue(c15["chainement_suffisant"])

    def test_geometrie_donne_une_borne_inferieure(self):
        c16 = FB.eq16_geometrie()
        produits = 1.0e9 * 0.06 * 3.0 * 3.15576e7
        self.assertAlmostEqual(c16["fraction_dans_volume_fiduciel"], 2.7e12 / produits, places=12)
        self.assertAlmostEqual(c16["un_sur"], produits / 2.7e12, places=6)
        self.assertLess(c16["fraction_dans_volume_fiduciel"], 1.0)
        self.assertIn("MINORÉE", c16["hypothese_temps_utile"])

    def test_loi_racine_n_ne_surprend_pas(self):
        c17 = FB.eq17_loi_racine_n()
        self.assertAlmostEqual(c17["sigma_poisson_2021"], math.sqrt(20) / 12.97, places=12)
        self.assertAlmostEqual(c17["sigma_poisson_2024"], math.sqrt(51) / 33.0, places=12)
        self.assertAlmostEqual(c17["erreur_publiee_relative_2021"], 4.0 / 10.6, places=12)
        self.assertAlmostEqual(c17["erreur_publiee_relative_2024"], 3.3 / 13.0, places=12)
        self.assertTrue(c17["surcroit_dans_les_deux"])
        self.assertGreater(c17["sur_2021"], 0.0)
        self.assertGreater(c17["sur_2024"], 0.0)
        self.assertLess(c17["gain_mesure"], c17["gain_prevu_racine_n"])
        self.assertAlmostEqual(c17["gain_prevu_racine_n"], math.sqrt(33.0 / 12.97), places=12)
        self.assertLess(c17["rapport_gains"], 1.0)

    def test_ordinaires_contre_communique(self):
        c8 = FB.eq08_ordinaires_par_rare()
        self.assertAlmostEqual(c8["centre_modele_standard"], 1.0 / BR_SM - 1.0, places=3)
        self.assertAlmostEqual(c8["taux_implicite_du_communique"], 1.0e-10, places=20)
        self.assertTrue(c8["communique_dans_intervalle_2024"])
        self.assertFalse(c8["communique_dans_intervalle_sm"],
                         "l'intervalle SM contient le compte arrondi : la limite écrite est fausse")


class TestTransmission(unittest.TestCase):
    """P4 : stdlib ou module local, rien d'autre — et la garde voit un import tiers."""

    def test_imports_du_module_sont_stdlib(self):
        ici = FB.imports_de(str(RACINE_DOSSIER / "fondation_base.py"))
        self.assertEqual(ici["tiers"], [])
        self.assertIn("math", ici["stdlib"])
        self.assertIn("__future__", ici["stdlib"])
        self.assertEqual(ici["local"], [])

    def test_import_tiers_se_voit(self):
        """Non-vacuité : un import ni stdlib ni local doit ressortir en `tiers`."""
        with tempfile.TemporaryDirectory() as tampon:
            temoin = Path(tampon) / "temoin_import.py"
            temoin.write_text("import numpyzz_epreuve\nfrom scipyzz_epreuve import stats\n"
                              "import math\nfrom pathlib import Path\n", encoding="utf-8")
            bilan = FB.imports_de(str(temoin))
        self.assertEqual(sorted(bilan["tiers"]), ["numpyzz_epreuve", "scipyzz_epreuve"])
        self.assertIn("math", bilan["stdlib"])
        self.assertIn("pathlib", bilan["stdlib"])

    def test_module_local_se_resout_dans_le_depot(self):
        with tempfile.TemporaryDirectory() as tampon:
            temoin = Path(tampon) / "temoin_local.py"
            temoin.write_text("import chiffres_pi\nfrom electricite_abondance import X\n",
                              encoding="utf-8")
            bilan = FB.imports_de(str(temoin))
        self.assertEqual(sorted(bilan["local"]), ["chiffres_pi", "electricite_abondance"])
        self.assertEqual(bilan["tiers"], [])
        self.assertTrue((FB.RACINE / bilan["resolu_local"]["chiffres_pi"]).exists())

    def test_parc_entier_sans_tiers(self):
        parc = FB.imports_parc()
        self.assertEqual(sorted(parc), ["ABONDANCE", "CHIFFRES", "FONDATION",
                                        "HORLOGERIE", "bibliotheques", "code"])
        for dossier, bilan in parc.items():
            self.assertGreater(bilan["fichiers"], 0, dossier)
            self.assertEqual(bilan["tiers"], [], dossier)

    def test_inventaire_cohere_entre_modules(self):
        inv = FB.inventaire_parc()
        self.assertEqual(inv["ABONDANCE"]["equations"], 54)
        self.assertEqual(inv["CHIFFRES"]["equations"], 17)
        self.assertEqual(inv["FONDATION"]["equations"], 18)
        for d, v in inv.items():
            self.assertTrue(v["present"], d)
            self.assertEqual(v["equations"], v["controles"], d)
            self.assertGreater(v["tests"], 0, f"{d} : un dossier sans tests ne se rejoue pas")
            self.assertGreater(len(v["modules"]), 0, d)


class TestDossierComplet(unittest.TestCase):
    """Le dossier entier : dix-huit équations, dix-huit contrôles, une limite partout."""

    @classmethod
    def setUpClass(cls):
        cls.donnees = FB.resoudre()

    def test_dix_huit_controles_verts(self):
        ids = [c["id"] for c in self.donnees["controles"]]
        self.assertEqual(ids, [f"C{i:02d}" for i in range(1, 19)])
        for c in self.donnees["controles"]:
            self.assertTrue(c["ok"], f"{c['id']} FAIL : {c['attendu']} / {c['obtenu']}")
        self.assertTrue(FB.verifier(self.donnees))

    def test_equations_en_chaine_et_limites_non_vides(self):
        eqs = self.donnees["equations"]
        self.assertEqual([e["id"] for e in eqs], [f"EQ-{i:02d}" for i in range(1, 19)])
        for e in eqs:
            self.assertTrue(e["limite"], f"{e['id']} : aucune limite écrite")
            self.assertTrue(e["chemin"].startswith("fondation_base.py"), e["id"])
            self.assertIn(e["statut"], FB.STATUTS)
            self.assertIn(e["couche"], FB.COUCHES)
            self.assertTrue(e["piliers"])
            self.assertTrue(e["resultat"])
            self.assertTrue(e["fonde_hors_du_dossier"] or e["depend_de"],
                            f"{e['id']} : ni source extérieure, ni prédécesseur")

    def test_chaque_controle_porte_la_limite_de_son_equation(self):
        eqs = {e["id"]: e for e in self.donnees["equations"]}
        self.assertEqual(len(eqs), 18)
        for c in self.donnees["controles"]:
            self.assertEqual(c["limite"], eqs["EQ-" + c["id"][1:]]["limite"], c["id"])

    def test_conclusion_et_verdict(self):
        concl = self.donnees["conclusion"]
        self.assertEqual(concl["controles_verts"], 18)
        self.assertEqual(concl["controles_total"], 18)
        self.assertEqual(concl["equations"], 18)
        self.assertEqual(concl["verdict"], "BASE EN CONFORMITÉ AVEC SES QUATRE PILIERS")
        self.assertEqual(sum(concl["statuts_par_label"].values()), 18)
        self.assertIn("aucune preuve universelle", concl["limite_globale"])

    def test_statuts_attendus_par_equation(self):
        eqs = {e["id"]: e for e in self.donnees["equations"]}
        self.assertEqual(eqs["EQ-01"]["statut"], "SPÉCIFIÉ")
        self.assertEqual(eqs["EQ-18"]["statut"], "SPÉCIFIÉ")
        self.assertEqual(eqs["EQ-16"]["statut"], "SIMULÉ")
        self.assertEqual(eqs["EQ-18"]["detail"]["refutation"],
                         FB.eq18_limite_de_la_base()["refutation"])


class TestArtefacts(unittest.TestCase):
    """Six artefacts, relus après écriture dans un dossier temporaire hors dépôt."""

    def test_six_fichiers_et_csv_franc(self):
        donnees = FB.resoudre()
        with tempfile.TemporaryDirectory() as tampon:
            rendu = FB.ecrire_artefacts(donnees, Path(tampon))
            self.assertEqual(sorted(rendu), sorted(FB.ARTIFACTS))
            self.assertEqual(len(FB.ARTIFACTS), 6)
            dossier = Path(tampon)
            for nom in rendu:
                self.assertTrue((dossier / nom).exists(), nom)
                self.assertGreater((dossier / nom).stat().st_size, 0)
            octets = (dossier / "confrontation.csv").read_bytes()
            self.assertTrue(octets.startswith(b"\xef\xbb\xbf"), "BOM Excel absent")
            self.assertIn(b"\r\n", octets)
            lignes = octets.decode("utf-8-sig").splitlines()
            self.assertEqual(len(lignes), 19)
            self.assertEqual(lignes[0], "equation;statut;couche;piliers;resultat;limite")
            for ligne in lignes[1:]:
                self.assertEqual(len(ligne.split(";")), 6)
            gel = json.loads((dossier / "gel.json").read_text(encoding="utf-8"))
            self.assertEqual(gel["digest"], donnees["gel"]["digest"])
            self.assertIn("comparateur_lu_ensuite", gel)
            base = json.loads((dossier / "base.json").read_text(encoding="utf-8"))
            self.assertEqual(base["axiome"]["nombres_fournis_par_l_axiome"], 0)
            etat = json.loads((dossier / "etat.json").read_text(encoding="utf-8"))
            self.assertEqual(len(etat["controles"]), 18)
            inventaire = json.loads((dossier / "inventaire.json").read_text(encoding="utf-8"))
            self.assertEqual(inventaire["parc"]["ABONDANCE"]["equations"], 54)


if __name__ == "__main__":
    unittest.main(verbosity=2)
