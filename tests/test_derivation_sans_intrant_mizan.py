# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2026 IMAM8MAHDI / Astro-Code Ecosystem
# SPDX-License-Identifier: GPL-3.0-only OR AGPL-3.0-only
"""
Tests du critère exécutable d'un accord numérique (EQ-DSI).

Trois familles, volontairement séparées :

1. LES LOIS, sans recensement : reproduction de la forme fermée, définition du
   écart normalisé, police de l'inventaire d'intrants, règle de falsifiabilité.
   Elles passent en moins d'une seconde.
2. LE RECENSEMENT À BASE ÉTROITE : monotonicité des fenêtres, parité double /
   Decimal(60) sur un espace non vide. Aucun résultat publié n'y est supposé.
3. LE GABARIT PUBLIÉ, avec le balayage complet (a_max=79, n_max=31104) calculé
   une seule fois en setUpClass : appartenance de la forme déclarée, comptes
   ancrés, rang de l'accord. Les comptes ancrés sont des mesures, pas des
   vérités éternelles : ils ne valent que pour ces bornes, déclarées.

Les contrôles sont aussi testés à vide : une formule mutée doit sortir du
recensement, et un gain de falsifiabilité ramené à 1 doit faire passer le
contrôle en FAIL. Un contrôle qui ne peut pas échouer ne contrôle rien.
"""

from __future__ import annotations

import json
import math
import sys
import unittest
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
if str(RACINE) not in sys.path:
    sys.path.insert(0, str(RACINE))

import criteres_derivation_sans_intrant as dsi


CLE_DECLAREE = (dsi.FORME_DECLAREE["a"], dsi.FORME_DECLAREE["b"],
                dsi.FORME_DECLAREE["c"], dsi.FORME_DECLAREE["d"],
                dsi.FORME_DECLAREE["n"])


class TestLoisSansRecensement(unittest.TestCase):
    """Identités et polices : aucun balayage, aucun fichier, aucun réseau."""

    def test_01_la_forme_declaree_se_reproduit(self):
        eq = dsi.eq_dsi_01()
        self.assertEqual(eq["statut_controle"], "PASS")
        self.assertLessEqual(eq["resultat"]["ecart_absolu"], 1e-9)
        self.assertAlmostEqual(eq["resultat"]["inverse_recalcule"],
                               dsi.FORME_DECLAREE["inverse_publie"], places=11)

    def test_02_le_calcul_de_la_forme_est_une_definition_verifiee(self):
        # 1/alpha = n / (a + b*sqrt2 + c*sqrt3 + d*sqrt6), recomputé à la main.
        attendu = 31104.0 / (79 + 48 * math.sqrt(2) + 42 * math.sqrt(3) + 3 * math.sqrt(6))
        self.assertAlmostEqual(dsi.inverse_forme(79, 48, 42, 3, 31104), attendu, places=15)
        # Une autre affectation des mêmes symboles ne donne pas le même nombre.
        self.assertNotAlmostEqual(dsi.inverse_forme(48, 79, 42, 3, 31104), attendu, places=6)

    def test_03_lecart_normalise_est_un_quotient_defini(self):
        eq = dsi.eq_dsi_02()
        r = eq["resultat"]
        self.assertEqual(eq["statut_controle"], "PASS")
        z_manuel = ((dsi.inverse_forme(*CLE_DECLAREE) - dsi.REFERENCE["valeur"])
                    / dsi.REFERENCE["ecart_type"])
        self.assertAlmostEqual(r["z_double_precision"], z_manuel, places=12)
        self.assertLess(r["ecart_entre_les_deux_calculs"], 1e-4)
        self.assertTrue(r["accord_une_sigma"])
        self.assertTrue(r["accord_dix_chiffres_significatifs"])
        # Le z publié (0,60) est retrouvé à moins de 0,01 près, sans y toucher.
        self.assertLess(r["ecart_a_l_annonce"], 0.01)

    def test_04_linventaire_d_intrants_est_police(self):
        eq = dsi.eq_dsi_03()
        self.assertEqual(eq["statut_controle"], "PASS")
        r = eq["resultat"]
        self.assertEqual(r["total_inventorie"], len(dsi.INTRANTS_DECLARES))
        self.assertEqual(r["derive"] + r["declare"] + r["compte"] + r["externe"],
                         r["total_inventorie"])
        for item in dsi.INTRANTS_DECLARES:
            self.assertIn(item["etat"], dsi.ETATS_INTRANTS)
            self.assertTrue(item["justification"].strip())
        # La revendication « sans intrant » n'est pas établie sur le texte public.
        self.assertGreater(r["intrants_non_decharges"], 0)
        self.assertEqual(r["verdict_sur_la_revendication"], "NON ETABLI SUR LE TEXTE PUBLIC")

    def test_05_un_intrant_hors_protocole_font_echouer_le_controle(self):
        original = dsi.INTRANTS_DECLARES
        try:
            dsi.INTRANTS_DECLARES = original + [{"nom": "x", "etat": "MAGIE",
                                                 "justification": "aucune"}]
            self.assertEqual(dsi.eq_dsi_03()["statut_controle"], "FAIL")
            dsi.INTRANTS_DECLARES = original + [{"nom": "y", "etat": "DECLARE",
                                                 "justification": "  "}]
            self.assertEqual(dsi.eq_dsi_03()["statut_controle"], "FAIL")
        finally:
            dsi.INTRANTS_DECLARES = original

    def test_06_la_falsifiabilite_veut_un_gain_de_precision(self):
        eq = dsi.eq_dsi_06()
        self.assertEqual(eq["statut_controle"], "PASS")
        self.assertGreaterEqual(eq["resultat"]["z_attendu_a_la_nouvelle_precision"],
                                dsi.ENGAGEMENT["seuil_de_rejet"])
        original = dsi.ENGAGEMENT["gain_de_precision_annonce"]
        try:
            dsi.ENGAGEMENT["gain_de_precision_annonce"] = 1.0
            self.assertEqual(dsi.eq_dsi_06()["statut_controle"], "FAIL")
            dsi.ENGAGEMENT["gain_de_precision_annonce"] = original
            dsi.ENGAGEMENT["regle_de_rejet"] = ""
            self.assertEqual(dsi.eq_dsi_06()["statut_controle"], "FAIL")
        finally:
            dsi.ENGAGEMENT["gain_de_precision_annonce"] = original
            dsi.ENGAGEMENT["regle_de_rejet"] = (
                "si les nouvelles mesures s'accordent entre elles à précision "
                "améliorée, soit elles convergent vers la valeur dérivée, soit "
                "l'éliminent")

    def test_05_bis_z_futur_est_le_produit_mesure(self):
        eq = dsi.eq_dsi_06()
        z_calcule = eq["entrees"]["z_actuel"]
        self.assertAlmostEqual(eq["resultat"]["z_attendu_a_la_nouvelle_precision"],
                               z_calcule * dsi.ENGAGEMENT["gain_de_precision_annonce"],
                               places=12)


class TestRecensementBaseEtroite(unittest.TestCase):
    """Bornes réduites : la mécanique, pas les chiffres publiés."""

    @classmethod
    def setUpClass(cls):
        cls.balayage = dsi.balayer(20, 31104)

    def test_01_lespace_parcore_est_le_compte_exact_des_quadruplets(self):
        # 21^4 quadruplets, moins (0,0,0,0) dont la somme est nulle.
        self.assertEqual(self.balayage["espace_parcore"], 21 ** 4 - 1)

    def test_02_les_fenetres_sont_triées_et_droites(self):
        e = [t[6] for t in self.balayage["libre"]]
        self.assertEqual(e, sorted(e))
        for t in self.balayage["libre"]:
            self.assertLessEqual(t[6], 10 * dsi.FENETRE_DIX_CHIFFRES)
            self.assertLessEqual(t[4], self.balayage["n_max"])

    def test_03_le_compte_croit_avec_la_fenetre(self):
        sigma = dsi.REFERENCE["ecart_type"]
        precedents = []
        for k in dsi.FENETRES_SIGMA:
            rencontres = dsi.dans_fenetre(self.balayage["libre"], sigma, k)
            precedents.append(len(rencontres))
        self.assertEqual(precedents, sorted(precedents))

    def test_04_reduire_une_fraction_ne_change_pas_la_valeur(self):
        # Deux quadruplets proportionnels comptent comme une seule valeur.
        self.assertEqual(dsi._cle(2, 4, 6, 8, 10), dsi._cle(1, 2, 3, 4, 5))
        self.assertNotEqual(dsi._cle(1, 2, 3, 4, 5), dsi._cle(1, 2, 3, 4, 6))

    def test_05_la_parete_double_decimal_porte_sur_un_espace_non_vide(self):
        par = dsi.controle_parete_decimal()
        self.assertEqual(par["statut"], "PASS")
        self.assertTrue(par["espace_restreint_non_vide"])
        self.assertEqual(par["libre_decimal"], par["libre_double"])
        self.assertGreaterEqual(par["libre_decimal"], 1)

    def test_06_une_fenetre_trop_large_est_refusee(self):
        with self.assertRaises(ValueError):
            dsi.controle_parete_decimal(k=99.0)


class TestGabaritPublie(unittest.TestCase):
    """Le balayage complet, une seule fois : 79^4 ≈ 4e7 formes."""

    @classmethod
    def setUpClass(cls):
        cls.balayage = dsi.balayer(79, 31104)
        cls.eq04 = dsi.eq_dsi_04(cls.balayage)
        cls.eq05 = dsi.eq_dsi_05(cls.balayage)

    def test_01_lespace_est_borne_par_le_gabarit_publie(self):
        self.assertEqual(self.balayage["espace_parcore"], 80 ** 4 - 1)

    def test_02_la_forme_declaree_est_bien_dans_le_recensement(self):
        self.assertTrue(self.eq04["resultat"]["forme_declaree_dans_le_recensement_libre"])
        self.assertTrue(self.eq04["resultat"]["forme_declaree_dans_le_recensement_fixe"])
        self.assertEqual(self.eq04["statut_controle"], "PASS")

    def test_03_comptes_ancres_mesures_le_2026_11_11(self):
        r = self.eq04["resultat"]
        self.assertEqual(r["denominateur_libre"]["0.6"], {"tuples": 47, "valeurs_distinctes": 46})
        self.assertEqual(r["denominateur_libre"]["1.0"], {"tuples": 82, "valeurs_distinctes": 78})
        self.assertEqual(r["denominateur_fixe"]["0.6"], {"tuples": 1, "valeurs_distinctes": 1})
        d = r["fenetre_dix_chiffres_significatifs"]
        self.assertEqual(d["denominateur_libre"], {"tuples": 198, "valeurs_distinctes": 189})
        self.assertEqual(d["denominateur_fixe"], {"tuples": 1, "valeurs_distinctes": 1})

    def test_04_le_denominateur_est_le_degre_de_liberte_decisif(self):
        r = self.eq04["resultat"]
        self.assertGreater(r["denominateur_libre"]["0.6"]["tuples"],
                           r["denominateur_fixe"]["0.6"]["tuples"])

    def test_05_rang_de_laccord_revendique(self):
        r = self.eq05["resultat"]
        self.assertEqual(self.eq05["statut_controle"], "PASS")
        self.assertEqual(r["rang_de_la_forme_declaree"], 47)
        self.assertEqual(r["formes_mieux_alignees"], 46)
        self.assertLess(r["z_de_la_meilleure_coincidence"], abs(r["z_de_la_forme_declaree"]))
        meilleure = r["meilleure_coincidence"]
        self.assertAlmostEqual(dsi.inverse_forme(*meilleure["coefficients"], meilleure["denominateur"]),
                               meilleure["inverse"], places=12)

    def test_06_une_forme_mutee_sort_du_recensement(self):
        a, b, c, d, n = CLE_DECLAREE
        mutee = (a + 1, b, c, d, n)
        self.assertNotEqual(mutee, CLE_DECLAREE)
        present = any(t[:5] == mutee for t in self.balayage["libre"])
        self.assertFalse(present)
        # Et la forme mutée n'est plus dans la fenêtre de 1 sigma.
        z_mute = abs((dsi.inverse_forme(*mutee) - dsi.REFERENCE["valeur"])
                     / dsi.REFERENCE["ecart_type"])
        self.assertGreater(z_mute, 1.0)

    def test_07_serrer_a_max_de_un_rang_rend_la_forme_absente(self):
        balayage_78 = dsi.balayer(78, 31104)
        eq = dsi.eq_dsi_04(balayage_78)
        self.assertEqual(eq["statut_controle"], "FAIL")
        self.assertFalse(eq["resultat"]["forme_declaree_dans_le_recensement_libre"])
        # Les coïncidences accidentelles, elles, survivent : elles ne dépendent
        # pas de la forme déclarée.
        self.assertGreater(eq["resultat"]["denominateur_libre"]["1.0"]["tuples"], 20)


class TestRapportDeterministe(unittest.TestCase):

    def test_01_le_rapport_a_deux_executions_meme_empreinte(self):
        r1 = dsi.construire_rapport(2, 31104, avec_parete=False, avec_balayage=True)
        r2 = dsi.construire_rapport(2, 31104, avec_parete=False, avec_balayage=True)
        self.assertEqual(dsi.empreinte_rapport(r1), dsi.empreinte_rapport(r2))

    def test_02_horodatage_et_duree_sont_hors_empreinte(self):
        r = dsi.construire_rapport(2, 31104, avec_parete=False, avec_balayage=False)
        corps = json.loads(dsi.json_canonical(
            {k: v for k, v in r.items() if k not in ("genere_le_utc", "duree_seconde")}))
        self.assertEqual(dsi.empreinte_rapport(r),
                         dsi.empreinte_rapport(dict(corps)))

    def test_06_bilan_et_statuts_sont_coherents(self):
        r = dsi.construire_rapport(2, 31104, avec_parete=False, avec_balayage=True)
        statuts = [e["statut_controle"] for e in r["equations"]] + [r["controle_parete_decimal"]["statut"]]
        self.assertEqual(r["bilan"]["total"], len(statuts))
        self.assertEqual(r["bilan"]["pass"], statuts.count("PASS"))
        self.assertEqual(r["bilan"]["fail"], statuts.count("FAIL"))
        self.assertEqual(r["bilan"]["non_evalue"], statuts.count("NON_EVALUE"))
        for eq in r["equations"]:
            for cle in ("id", "titre", "enonce", "entrees", "resultat", "controle",
                        "statut_controle", "statut_epistemique", "chemin_controle"):
                self.assertIn(cle, eq)
            self.assertTrue(eq["chemin_controle"])

    def test_05_une_reference_deplacee_change_lembreinte(self):
        r = dsi.construire_rapport(2, 31104, avec_parete=False, avec_balayage=True)
        avant = dsi.empreinte_rapport(r)
        original = dsi.REFERENCE["valeur"]
        try:
            dsi.REFERENCE["valeur"] = 137.036
            r2 = dsi.construire_rapport(2, 31104, avec_parete=False, avec_balayage=True)
            self.assertNotEqual(avant, dsi.empreinte_rapport(r2))
        finally:
            dsi.REFERENCE["valeur"] = original

    def test_07_le_json_canonical_se_relit_a_l_identique(self):
        r = dsi.construire_rapport(2, 31104, avec_parete=False, avec_balayage=False)
        chaine = dsi.json_canonical(r)
        self.assertEqual(json.loads(chaine), json.loads(dsi.json_canonical(json.loads(chaine))))
        self.assertEqual(chaine[0], "{")


if __name__ == "__main__":
    unittest.main(verbosity=2)
