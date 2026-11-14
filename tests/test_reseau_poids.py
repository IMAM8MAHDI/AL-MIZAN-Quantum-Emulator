# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2026 IMAM8MAHDI / Astro-Code Ecosystem
# SPDX-License-Identifier: GPL-3.0-only OR AGPL-3.0-only
"""Tests du socle 313T (reseau_poids_sparse_mizan.py), copie de la suite de l'atelier.

Un test ne recopie pas la valeur affichée : il la retrouve par une autre route —
test de primalité en 6k±1 indépendant de celui du module, formule fermée du χ² à
2 degrés de liberté, recomposition par bases mixtes du quintuplet décompilé, comptage
à la main d'une fenêtre de symboles. Plusieurs tests attaquent les contrôles à rebours
(banc de fixtures de mutation) : un instrument qui ne rouge jamais ne contrôle rien.

`observer()` coûte environ trois secondes (200 000 hachages, un sous-processus, une
matérialisation du registre) : il est joué une seule fois par classe et partagé.

Copie adaptée de la suite de l'atelier, qui compte 37 tests. Six d'entre eux
contrôlent la publication — ils lisent `web_cloud/`, le générateur des trois pages
et le dictionnaire `PAGES_PUBLIQUES` de la passerelle, trois fichiers que ce dépôt
n'embarque pas — et restent donc du côté atelier. Les deux tests de publication
qui n'attaquent que le module sont conservés, d'où la classe `TestCadrePublic`.
Sont aussi retirés les deux imports de la passerelle et du générateur, puis `json`
et `re`, devenus sans usage. Aucun autre octet ne change ; les 31 tests réellement
rejoués ici (mesuré, `Ran 31 tests`, `OK`) sont consignés dans `README_DEPOT.md`.
"""

import hashlib
import math
import sys
import unittest
from fractions import Fraction as Q
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
if str(RACINE) not in sys.path:
    sys.path.insert(0, str(RACINE))

import reseau_poids_sparse_mizan as socle                            # noqa: E402

AXES_SYNTHETIQUES = {"entrees": 7, "strates": 5, "colonnes": 3,
                     "symboles": 11, "tranches": 13}


def _premiers_par_essais(n: int) -> bool:
    """Primalité par une autre route que socle.est_premier : diviseurs de forme 6k±1."""
    if n < 2:
        return False
    if n in (2, 3):
        return True
    if n % 2 == 0 or n % 3 == 0:
        return False
    d = 5
    while d * d <= n:
        if n % d == 0 or n % (d + 2) == 0:
            return False
        d += 6
    return True


class TestArithmetiqueDuCardinal(unittest.TestCase):
    def test_313_est_premier_par_une_autre_route(self):
        self.assertTrue(_premiers_par_essais(socle.CONSTANTE_C))
        self.assertEqual(socle.CONSTANTE_C, 313)
        self.assertFalse(any(socle.CONSTANTE_C % d == 0 for d in range(2, 18)))

    def test_factorisation_recompose_exactement_313_trillion(self):
        attendu = 313 * 2 ** 12 * 5 ** 12
        self.assertEqual(attendu, socle.CAPACITE_POIDS)
        self.assertEqual(socle.produit_facteurs(socle.factorisation(socle.CAPACITE_POIDS)),
                         attendu)
        expo = dict(socle.factorisation(socle.CAPACITE_POIDS))
        self.assertEqual((expo[2], expo[5], expo[313]), (12, 12, 1))

    def test_capacite_strictement_sous_2_la_64(self):
        self.assertLess(socle.CAPACITE_POIDS, socle.ESPACE_HACHAGE)
        self.assertEqual(socle.ESPACE_HACHAGE, 2 ** 64)
        # majorant vérifié à la main : 313e12 < 2^49 < 2^64
        self.assertLess(socle.CAPACITE_POIDS, 2 ** 49)

    def test_dense_bf16_vaut_deux_octets_par_poids(self):
        self.assertEqual(socle.DENSE_BF16_OCTETS, 2 * socle.CAPACITE_POIDS)
        self.assertEqual(socle.DENSE_BF16_OCTETS, 626_000_000_000_000)


class TestStatistiqueRecalculee(unittest.TestCase):
    def test_quantile_normale_sur_des_valeurs_connues(self):
        self.assertAlmostEqual(socle.quantile_normale(0.5), 0.0, places=12)
        self.assertAlmostEqual(socle.quantile_normale(0.975), 1.959963985, delta=1e-6)
        for p_hors_intervalle in (0.0, 1.0, -0.2):
            with self.assertRaises(ValueError):
                socle.quantile_normale(p_hors_intervalle)

    def test_seuil_chi2_a_deux_ddl_contre_la_formule_exacte(self):
        # pour 2 degrés de liberté, P(X <= x) = 1 - e^(-x/2) : la racine est fermée
        exact = -2.0 * math.log(1.0 - 0.99)
        self.assertAlmostEqual(socle.seuil_chi2(2, 0.99), exact, delta=0.02)

    def test_seuil_chi2_croissant_en_ddl_et_en_p(self):
        seuils = [socle.seuil_chi2(ddl) for ddl in (10, 100, 255, 1000)]
        self.assertEqual(seuils, sorted(seuils))
        self.assertLess(socle.seuil_chi2(255, 0.95), socle.seuil_chi2(255, 0.99))

    def test_borne_anniversaire_exacte_en_ratients(self):
        self.assertEqual(socle.borne_anniversaire(2, 4), 0.25)
        self.assertEqual(socle.borne_anniversaire(1, socle.CAPACITE_POIDS), 0.0)
        n, module = 10 ** 6, 10 ** 6
        self.assertEqual(socle.borne_anniversaire(n, module), float(Q(n * (n - 1), 2 * module)))
        # sur l'échantillon publié, l'espérance reste de l'ordre de 10^-4
        attente = socle.borne_anniversaire(200_000, socle.CAPACITE_POIDS)
        self.assertLess(attente, 1e-4)
        self.assertGreater(attente, 1e-5)


class TestAdressage(unittest.TestCase):
    def test_cle_canonique_separe_par_le_caractere_invisible(self):
        self.assertEqual(socle.cle(1, 0, 0, 7, 3), b"1\x1f0\x1f0\x1f7\x1f3")
        self.assertEqual(socle.cle(1, 0, 0, 7, 3).count(socle.SEPARATEUR), 4)
        self.assertNotEqual(socle.cle(11, 0, 0, 7, 3), socle.cle(1, 10, 0, 7, 3))

    def test_champs_hors_domaine_refuses(self):
        for mauvais in ((0, 0, 0, 7, 3), (1, 0, socle.NB_COLONNES, 7, 3),
                        (1, 0, 0, socle.NB_SYMBOLES, 3), (1, -1, 0, 7, 3)):
            with self.assertRaises(ValueError):
                socle.cle(*mauvais)

    def test_adresser_deterministe_et_dans_plage(self):
        c = socle.cle(42, 3, 5, 200, 9)
        self.assertEqual(socle.adresser(c), socle.adresser(c))
        self.assertTrue(0 <= socle.adresser(c) < socle.CAPACITE_POIDS)
        for i in range(200):
            self.assertLess(socle.adresser(socle.cle(i + 1, 0, 0, i % 259, i), 10 ** 6), 10 ** 6)

    def test_decompiler_recompose_le_rang_par_bases_mixtes(self):
        produit = 1
        for v in AXES_SYNTHETIQUES.values():
            produit *= v
        for i in range(produit):
            e, s, col, sym, tr = socle.decompiler(i, AXES_SYNTHETIQUES)
            reconstruit = ((e - 1) + AXES_SYNTHETIQUES["entrees"]
                           * (s + AXES_SYNTHETIQUES["strates"]
                              * (col + AXES_SYNTHETIQUES["colonnes"]
                                 * (sym + AXES_SYNTHETIQUES["symboles"] * tr))))
            self.assertEqual(reconstruit, i)
            # slot_de et adresser(cle(...)) sont la même fonction sous deux écritures
            self.assertEqual(socle.slot_de(e, s, col, sym, tr, 10 ** 9),
                             socle.adresser(socle.cle(e, s, col, sym, tr), 10 ** 9))

    def test_decompiler_est_injectif_sur_un_echantillon(self):
        self.assertEqual(len({socle.decompiler(i, AXES_SYNTHETIQUES) for i in range(1000)}), 1000)


class TestReseauSparse(unittest.TestCase):
    def test_le_plafond_refuse_sans_toucher_ce_qui_est_garde(self):
        r = socle.ReseauPoidsSparse(plafond=6)
        gardes = refuses = 0
        for i in range(20):
            try:
                r.ecrire(i, 1.0)
                gardes += 1
            except socle.PlafondMaterialise:
                refuses += 1
        self.assertEqual((gardes, refuses, r.materialises), (6, 14, 6))
        self.assertEqual(r.ecritures_refusees, 14)
        self.assertEqual(sorted(r.poids), list(range(6)))

    def test_reecriture_d_un_slot_ne_change_pas_le_compte(self):
        r = socle.ReseauPoidsSparse(plafond=10)
        self.assertTrue(r.ecrire(3, 0.25))
        self.assertFalse(r.ecrire(3, 0.75))
        self.assertEqual(r.materialises, 1)
        self.assertEqual(r.lire(3), 0.75)
        self.assertIsNone(r.lire(4))

    def test_occupation_et_empreinte(self):
        r = socle.ReseauPoidsSparse(capacite=100, plafond=10)
        self.assertEqual(r.occupation, 0.0)
        r.ecrire(7, 0.5)
        self.assertAlmostEqual(r.occupation, 1 / 100, places=15)
        empreinte_avant = r.empreinte()
        self.assertEqual(len(empreinte_avant), 64)
        r.ecrire(7, r.lire(7) + 0.25)
        self.assertNotEqual(empreinte_avant, r.empreinte())

    def test_valeur_poids_comptee_a_la_main(self):
        ids = [3] * 64 + [5] * 32
        self.assertEqual(socle.valeur_poids(ids, 3, 0), 1.0)
        self.assertEqual(socle.valeur_poids(ids, 5, 0), 0.0)
        self.assertEqual(socle.valeur_poids(ids, 5, 1), 1.0)
        fenetre = [1, 1, 2, 3] + [0] * 60
        self.assertEqual(socle.valeur_poids(fenetre, 1, 0), 2 / 64)
        self.assertEqual(socle.valeur_poids(ids, 3, 9), 0.0)


class TestAxesEtPlan(unittest.TestCase):
    def test_adresses_nommables_egal_produit_des_axes(self):
        self.assertEqual(socle.adresses_nommables(AXES_SYNTHETIQUES), 7 * 5 * 3 * 11 * 13)
        axes = socle.axes_registre()
        self.assertEqual(axes["colonnes"], socle.NB_COLONNES)
        self.assertEqual(axes["symboles"], socle.NB_SYMBOLES)
        produit = 1
        for nom in ("entrees", "strates", "colonnes", "symboles", "tranches"):
            self.assertGreater(axes[nom], 0)
            produit *= axes[nom]
        self.assertEqual(produit, socle.adresses_nommables(axes))

    def test_plan_de_crissance_cohèrent_sur_des_axes_synthétiques(self):
        plan = socle.plan_de_crissance(AXES_SYNTHETIQUES)
        nommables = 7 * 5 * 3 * 11 * 13
        self.assertEqual(plan["adresses_nommables"], nommables)
        self.assertAlmostEqual(plan["facteur_manquant"], socle.CAPACITE_POIDS / nommables)
        par_entree = 5 * 3 * 11 * 13
        self.assertEqual(plan["entrees_pour_egaliser"], -(-socle.CAPACITE_POIDS // par_entree))
        self.assertEqual(plan["entrees_a_ecrire"], plan["entrees_pour_egaliser"] - 7)

    def test_le_registre_nomme_moins_que_la_capacite_declaree(self):
        axes = socle.axes_registre()
        self.assertLess(socle.adresses_nommables(axes), socle.CAPACITE_POIDS)
        self.assertGreater(socle.plan_de_crissance(axes)["facteur_manquant"], 1.0)


class TestRecouvrementDeQuestions(unittest.TestCase):
    def test_une_question_se_recouvre_elle_meme_a_un(self):
        rec = socle.recouvrement("combien de poids le registre nomme-t-il",
                                 "combien de poids le registre nomme-t-il")
        self.assertAlmostEqual(rec["similarite"], 1.0, delta=1e-12)
        self.assertGreater(rec["slots_a"], 0)
        self.assertEqual(rec["slots_a"], rec["slots_b"])

    def test_question_disjointe_ne_partage_aucun_slot(self):
        ref = "combien de paramètres dans le réseau de zéro"
        vide = socle.question_disjointe(ref)
        self.assertEqual(len(vide), 12)
        rec = socle.recouvrement(vide, ref)
        self.assertEqual(rec["slots_communs"], 0)
        self.assertEqual(rec["similarite"], 0.0)

    def test_indices_question_sont_bornes_en_poids(self):
        sparse = socle.indices_question("la lune a-t-elle une magnitude scellée")
        self.assertTrue(sparse)
        for v in sparse.values():
            self.assertTrue(0.0 < v <= 1.0)

    def test_question_vide_ne_produit_aucun_slot(self):
        self.assertEqual(socle.indices_question(""), {})
        self.assertEqual(socle.recouvrement("", "x")["slots_communs"], 0)


class TestAssemblage(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rapport = socle.controler()

    def test_neuf_equations_numerotees_sans_trou(self):
        identifiants = [e["id"] for e in self.rapport["equations"]]
        self.assertEqual(identifiants, [f"EQ-PS-{i:02d}" for i in range(1, 10)])
        self.assertEqual(len(set(identifiants)), 9)

    def test_neuf_controles_pass_et_compte_coherent(self):
        self.assertEqual(self.rapport["compte"], {"PASS": 9, "FAIL": 0, "INCONCLUSIF": 0})
        for e in self.rapport["equations"]:
            self.assertIn(e["statut"], socle.STATUTS)
            self.assertTrue(e["forme"].strip())
            self.assertTrue(e["chemin_controle"].strip())
            self.assertIn(e["id"], socle.limites())
            self.assertGreater(len(socle.limites()[e["id"]]), 40)

    def test_racine_recalculee_hors_du_module(self):
        attendu = hashlib.sha256("\n".join(
            f"{e['id']}|{e['statut']}" for e in self.rapport["equations"]).encode("utf-8")).hexdigest()
        self.assertEqual(self.rapport["racine"], attendu)
        self.assertEqual(len(self.rapport["racine"]), 64)
        # une seule équation qui rouge déplace la racine
        mutile = [dict(e) for e in self.rapport["equations"]]
        mutile[4]["statut"] = "FAIL"
        autre = hashlib.sha256("\n".join(
            f"{e['id']}|{e['statut']}" for e in mutile).encode("utf-8")).hexdigest()
        self.assertNotEqual(attendu, autre)

    def test_le_module_ne_lit_aucun_poids_externe(self):
        cadre = self.rapport["cadre"]
        self.assertEqual(cadre["materialises"],
                         self.rapport["equations"][4]["valeur"]["materialises"])
        self.assertLessEqual(cadre["materialises"], socle.PLAFOND_MATERIALISES)
        self.assertEqual(len(cadre["empreinte_reseau"]), 64)
        sept = self.rapport["equations"][6]["valeur"]
        self.assertFalse(sept["poids_lus_par_ce_module"])
        self.assertEqual(sept["materialises_apres_64_tentatives"] + sept["ecritures_refusees"], 64)
        for chemin in socle.inventaire_poids_sur_disque():
            self.assertIn(Path(chemin).suffix.lower(), socle.EXTENSIONS_POIDS, chemin)

    def test_banc_de_mutation_capte_huit_attaques_sur_huit(self):
        mutations = socle.verifier_mutations()
        self.assertEqual(mutations["testees"], 8)
        self.assertEqual(mutations["captees"], 8)
        for identifiant, entree in mutations["par_equation"].items():
            self.assertEqual(entree["normal"], "PASS", identifiant)
            self.assertNotEqual(entree["mute"], "PASS", identifiant)
        # limite publiée : EQ-PS-02 ne porte aucune fixture
        self.assertNotIn("EQ-PS-02", socle.MUTATIONS)
        self.assertEqual(set(socle.MUTATIONS),
                         {e["id"] for e in self.rapport["equations"]} - {"EQ-PS-02"})


class TestCadrePublic(unittest.TestCase):
    """Les deux tests de publication qui n'attaquent que le module.

    Les six autres — balisage des trois pages et égalité des deux copies JSON,
    câblage des routes et du sitemap, copie servie, carte du portail, lien depuis
    la page EQ-SA, absence de balise ``{…}`` non résolue — lisent des fichiers
    que ce dépôt n'embarque pas et se rejouent du côté atelier.
    """

    def test_cadre_publie_ne_porte_ni_cle_test_ni_echantillon(self):
        cadre = socle.controler(echantillons=20_000, croiser_processus=False)["cadre"]
        self.assertNotIn("cle_test", cadre)
        self.assertNotIn("echantillon", cadre)
        self.assertEqual(cadre["module"], "reseau_poids_sparse_mizan.py")
        self.assertEqual(cadre["capacite_poids"], socle.CAPACITE_POIDS)

    def test_les_trois_nombres_ne_se_confondent_pas(self):
        cadre = socle.controler(echantillons=20_000, croiser_processus=False)["cadre"]
        self.assertEqual(
            len({cadre["capacite_poids"], cadre["adresses_nommables"], cadre["materialises"]}), 3)
        self.assertLess(cadre["materialises"], cadre["plafond_materialises"])
        self.assertLess(cadre["adresses_nommables"], cadre["capacite_poids"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
