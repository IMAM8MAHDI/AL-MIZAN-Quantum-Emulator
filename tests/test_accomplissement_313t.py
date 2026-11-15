# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2026 IMAM8MAHDI / Astro-Code Ecosystem
# SPDX-License-Identifier: GPL-3.0-only OR AGPL-3.0-only
"""Tests du registre EQ-TLU (accomplissement_313t_mizan.py) — 313 T poids visés.

Règle de la maison : un test ne recopie pas la valeur affichée, il la retrouve par
une autre route. Les radices sont multipliées dans un autre ordre, la décomposition
de base est confrontée à `divmod` et au formatage décimal de Python, la partition
des 313 fibres est mesurée par une somme télescopique et par une série explicite,
le quantile χ² est recalculé par la forme close -2 ln(1-p) quand ddl = 2, et la
taille de la grille est décomptée à la main.

`observer()` coûte une grosse minute (313 000 ancres hachées deux fois, deux
mesures de débit, registre du socle chargé) : il est joué une seule fois par la
classe qui en a besoin et partagé. Les attaques viennent du banc de fixtures du
module — un contrôle qui ne rouge jamais ne contrôle rien.

Copie adaptée de la suite de l'atelier, qui compte 44 tests ; elle en rend 43 ici.
Le test écarté est celui de la publication : il lisait
`oeuvre_universelle/manifeste_anteriorite.py`, ses `GLOBS_SELECTIONNES` et les noms
des trois pages sous `web_cloud/`, trois objets que ce dépôt n'embarque pas. Il n'est
pas remplacé par un équivalent : le sceau d'ici est celui de
`FONDATION/OUTILS/sceller_manifeste.py`, pris sur les blobs git et régénéré après
chaque commit de contenu, si bien qu'une assertion d'appartenance serait rouge entre
le commit et le rescellement — une vérification qui ne peut pas être verte au moment
où elle sert ne vérifie rien. Aucun import d'atelier ne subsiste : la suite ne lit que
le module et le socle. Les quarante-trois autres méthodes sont recopiées sans un octet
de changement. Le compte réellement rejoué (`Ran 43 tests`, `OK`, mesuré dans ce dépôt)
est consigné dans `README_DEPOT.md`.
"""

import contextlib
import hashlib
import io
import json
import math
import sys
import unittest
from fractions import Fraction as Q
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
if str(RACINE) not in sys.path:
    sys.path.insert(0, str(RACINE))

import accomplissement_313t_mizan as tlu                            # noqa: E402
import reseau_poids_sparse_mizan as socle                           # noqa: E402


class TestArithmetiqueDesRadices(unittest.TestCase):
    def test_produit_des_radices_redonne_la_capacite_declaree(self):
        self.assertEqual(tlu.produit(tlu.RADICES), tlu.CAPACITE)
        self.assertEqual(tlu.CAPACITE, socle.CAPACITE_POIDS)
        self.assertEqual(313 * (10 ** 6 * 10 ** 6), tlu.CAPACITE)   # autre groupement

    def test_treize_radices_une_de_313_douze_de_dix(self):
        self.assertEqual(len(tlu.RADICES), 13)
        self.assertEqual(tlu.RADICES[0], 313)
        self.assertEqual(set(tlu.RADICES[1:]), {10})

    def test_factorisation_reconstruite_par_une_autre_route(self):
        f = tlu.factoriser(tlu.CAPACITE)
        self.assertEqual(dict(f), {2: 12, 5: 12, 313: 1})
        r = 1
        for base, expo in f:
            r *= base ** expo
        self.assertEqual(r, tlu.CAPACITE)
        self.assertEqual(tlu.ECHELLE, 2 ** 12 * 5 ** 12)

    def test_313_est_premier_teste_par_divisions_completes(self):
        self.assertTrue(tlu.est_premier_6k(313))
        self.assertTrue(all(313 % d for d in range(2, 18)))          # floor(sqrt(313)) = 17
        self.assertEqual(313 % 2, 1)
        self.assertEqual(313 % 5, 3)

    def test_hors_boite_rejete_adresse_et_chiffre(self):
        for adresse in (tlu.CAPACITE, tlu.CAPACITE + 1, -1):
            with self.assertRaises(tlu.NomInvalide):
                tlu.nommer(adresse)
        with self.assertRaises(tlu.NomInvalide):
            tlu.slot((313,) + (0,) * 12)                             # radix du prefixe
        with self.assertRaises(tlu.NomInvalide):
            tlu.slot((0, 10) + (0,) * 11)                             # radix d'un chiffre
        with self.assertRaises(tlu.NomInvalide):
            tlu.slot((0,) * 12)                                       # taille wrong


class TestBijectionNomAdresse(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.exhaustif = tlu.bijectif_exhaustif()
        cls.interfaces = tlu.controles_interfaces()

    def test_exhaustif_sur_la_boite_reduite_dans_les_deux_sens(self):
        e = self.exhaustif
        self.assertEqual(e["taille_boite"], 31_300 * 10)
        self.assertEqual(e["retours_identiques"], e["taille_boite"])
        self.assertEqual(e["noms_inverses"], e["taille_boite"])
        self.assertEqual(e["hors_boite"], 0)

    def test_pointes_croisees_avec_la_conversion_decimale_de_python(self):
        i = self.interfaces
        self.assertEqual(i["pointes_identiques"], len(i["pointes"]))
        self.assertEqual(i["pointes_retour"], len(i["pointes"]))
        self.assertEqual(i["pointes_deuxieme_route"], len(i["pointes"]))
        for adresse in (0, 1, 10 ** 12 - 1, 10 ** 12, tlu.CAPACITE - 1):
            self.assertEqual(tlu.slot(tlu.nommer(adresse)), adresse)
            self.assertEqual(tlu.nommer(adresse), tlu.nommer_par_str(adresse))

    def test_le_prefixe_est_le_quotient_par_lechelle(self):
        for adresse in self.interfaces["pointes"]:
            self.assertEqual(tlu.nommer(adresse)[0], adresse // 10 ** 12)
            self.assertLess(tlu.nommer(adresse)[0], 313)

    def test_deux_adresses_distinctes_deux_noms_canoniques_distincts(self):
        adresses = list(range(0, 5000, 7))
        noms = [tlu.nom_canonique(tlu.nommer(a)) for a in adresses]
        self.assertEqual(len(set(noms)), len(adresses))
        self.assertTrue(all(b"\x1f" in n for n in noms))

    def test_deux_mille_adresses_interieures_conformes(self):
        i = self.interfaces
        self.assertEqual(i["interne_conformes"], i["interne_testees"])
        self.assertEqual(i["interne_testees"], 2_000)


class TestPartitionEnFibres(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.p = tlu.partition_fibres()

    def test_313_fibres_de_un_billion(self):
        self.assertEqual(self.p["fibres"], 313)
        self.assertEqual(self.p["debut"], 0)
        self.assertEqual(self.p["fin"], tlu.CAPACITE)

    def test_recouvrement_par_trois_identites_entieres(self):
        p = self.p
        self.assertEqual(p["somme_mesures"], tlu.CAPACITE)
        self.assertEqual(p["telescope"], tlu.CAPACITE)
        self.assertEqual(p["produit_constant"], tlu.CAPACITE)
        self.assertTrue(p["recouvre_capacite"])
        # quatrième route, écrite ici : une somme explicite de 313 termes
        self.assertEqual(sum(10 ** 12 for _ in range(313)), tlu.CAPACITE)

    def test_contiguite_stricte_entre_fibres_voisines(self):
        debut = [c * 10 ** 12 for c in range(313)]
        fin = [d + 10 ** 12 for d in debut]
        self.assertEqual(sum(1 for k in range(312) if fin[k] == debut[k + 1]), 312)
        self.assertEqual(self.p["contiguite_verifiee"], 312)
        self.assertEqual(self.p["contiguite_verifiee"], self.p["fibres"] - 1)

    def test_chaque_fibre_garde_son_prefixe_de_bout_en_bout(self):
        self.assertEqual(self.p["fibres_ancres"], 313)
        for c in (0, 1, 156, 311, 312):
            self.assertEqual(tlu.nommer(c * 10 ** 12)[0], c)
            self.assertEqual(tlu.nommer((c + 1) * 10 ** 12 - 1)[0], c)


class TestLoiDePoids(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.l = tlu.loi_poids()

    def test_la_loi_est_totale_stable_et_bornee(self):
        self.assertEqual(self.l["dans_support"], self.l["dessins"])
        self.assertEqual(self.l["stables"], self.l["dessins"])
        self.assertEqual(self.l["distincts"], self.l["dessins"])
        for a in (0, 1, 7, 10 ** 12, tlu.CAPACITE - 1):
            w = tlu.poids(a)
            self.assertGreaterEqual(w, 0.0)
            self.assertLessEqual(w, 1.0)

    def test_adresses_voisines_ne_partagent_pas_leur_poids(self):
        ecart = sum(1 for i in range(500) if tlu.poids(i) != tlu.poids(i + 1))
        self.assertEqual(ecart, 500)
        self.assertEqual(self.l["suivants_distincts"], self.l["dessins"])

    def test_uniformite_encadree_ni_biaisee_ni_elephant(self):
        l = self.l
        self.assertTrue(l["borne_basse"] < l["chi2"] < l["borne_haute"],
                        "chi2=%s borne=%s..%s" % (l["chi2"], l["borne_basse"], l["borne_haute"]))
        self.assertGreater(l["case_min"], 0)
        self.assertGreater(l["case_max"], l["attendu_par_case"])
        self.assertLess(l["case_min"], l["attendu_par_case"])
        self.assertGreaterEqual(l["attendu_par_case"], 5.0)

    def test_le_quantile_chi2_de_deux_implementations_se_recouvrent(self):
        l = self.l
        self.assertLess(l["ecart_haut_relatif"], 1e-9)
        self.assertEqual(round(l["seuil_socle_haut"], 4), round(l["borne_haute"], 4))
        self.assertEqual(round(l["seuil_socle_bas"], 4), round(l["borne_basse"], 4))

    def test_wilson_hilferty_valide_contre_la_forme_close_en_ddl_2(self):
        exact = -2.0 * math.log(1.0 - 0.99)
        self.assertAlmostEqual(self.l["ddl2_formule_exacte"], round(exact, 6), places=6)
        self.assertLess(abs(self.l["ddl2_wilson_hilferty"] - exact) / exact, 1e-2)


class TestCeQueLeRegistreNomme(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.n = tlu.nommables_registre()

    def test_nommables_strictement_inferieurs_a_la_capacite(self):
        # « nommables » est auto-référent : il se calcule sur le tableau maître et sur
        # l'arbre scellé, donc il bouge dès qu'une strate ou qu'un module est ajouté —
        # 396 594 148 860 le 14/11/2026 à 21:19:36Z (470 entrées × 42 strates),
        # 439 851 337 926 à 21:49:03Z (482 × 43), 440 618 966 788 à 21:58:24Z (6 314
        # tranches). Le test n'épingle donc que la borne et l'identité du produit : la
        # valeur exacte n'a de sens qu'accompagnée de sa date, ailleurs.
        a = self.n["axes"]
        self.assertEqual(self.n["nommables"],
                         a["entrees"] * a["strates"] * a["colonnes"] * a["symboles"] * a["tranches"])
        self.assertLess(self.n["nommables"], tlu.CAPACITE)
        self.assertGreater(self.n["nommables"], 10 ** 9)

    def test_le_produit_des_axes_est_invariant_a_ordre(self):
        a = self.n["axes"]
        route_a = a["entrees"] * a["strates"] * a["colonnes"] * a["symboles"] * a["tranches"]
        route_b = (a["entrees"] * a["strates"]) * (a["colonnes"] * a["symboles"]) * a["tranches"]
        route_c = a["tranches"] * a["symboles"] * a["colonnes"] * a["strates"] * a["entrees"]
        self.assertEqual({route_a, route_b, route_c}, {self.n["nommables"]})

    def test_ratio_exact_reconstruit_bout_a_bout(self):
        r = self.n["ratio_exact"]
        self.assertEqual(r.numerator * tlu.CAPACITE, r.denominator * self.n["nommables"])
        self.assertLess(r, 1)
        self.assertGreater(self.n["facteur_manquant"], 1.0)
        self.assertEqual(Q(self.n["nommables"], tlu.CAPACITE) * tlu.CAPACITE,
                         self.n["nommables"])

    def test_trois_nombres_restent_distincts(self):
        self.assertEqual(
            len({tlu.CAPACITE, self.n["nommables"], self.n["materialises_socle_publie"]}), 3)
        self.assertLess(self.n["materialises_socle_publie"], self.n["plafond_socle"])
        self.assertEqual(self.n["materialises_socle_publie"], 175_509)


class TestMargesDeMachine(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.m = tlu.mesures_machine()

    def test_dense_bf16_et_float64_calcules_non_recopies(self):
        self.assertEqual(tlu.DENSE_BF16_OCTETS, 2 * tlu.CAPACITE)
        self.assertEqual(tlu.DENSE_FLOAT64_OCTETS, 8 * tlu.CAPACITE)
        self.assertEqual(tlu.DENSE_FLOAT64_OCTETS, 4 * tlu.DENSE_BF16_OCTETS)
        self.assertEqual(tlu.DENSE_BF16_OCTETS, socle.DENSE_BF16_OCTETS)

    def test_le_dense_depasse_la_machine_mesuree(self):
        self.assertGreater(self.m["marge_bf16_sur_disque"], 1.0)
        self.assertGreater(self.m["marge_ram"], 1.0)
        self.assertLess(self.m["slots_tenants_en_ram"], tlu.CAPACITE)
        self.assertGreater(self.m["disque_libre_octets"], 0)
        self.assertTrue(self.m["ram"]["disponible"])

    def test_debit_deux_tailles_qui_se_recouvrent(self):
        d = tlu.mesurer_debit(20_000, 60_000)
        self.assertTrue(0.5 <= d["rapport_debits"] <= 2.0, str(d["rapport_debits"]))
        self.assertGreater(d["debit_retenu"], 0.0)
        self.assertGreater(d["temps_enumere_annees"], 1.0)
        self.assertAlmostEqual(d["temps_enumere_seconde"] / d["seconde_annee"],
                               d["temps_enumere_annees"], delta=1e-6)


class TestGrilleAncrage(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # deux chiffres significatifs : 31 300 ancres, même arithmétique, dixième du coût
        cls.g = tlu.grille_ancrage(2, recalculer=True)

    def test_taille_par_trois_routes_denumeration(self):
        self.assertEqual(self.g["taille_par_division"], 31_300)
        self.assertEqual(self.g["taille_par_produit"], 31_300)
        self.assertEqual(self.g["taille_denomeree"], 31_300)
        self.assertTrue(self.g["divisible_exactement"])
        self.assertEqual(self.g["occupation"], Q(1, 10 ** 10))

    def test_racines_de_64_hexadecimales_et_reproduites(self):
        self.assertEqual(len(self.g["racine_merkle"]), 64)
        self.assertEqual(len(self.g["racine_simple"]), 64)
        int(self.g["racine_merkle"], 16)
        int(self.g["racine_simple"], 16)
        self.assertTrue(self.g["racine_reproduite"])
        self.assertTrue(self.g["racine_simple_reproduite"])

    def test_adresses_croissantes_et_poids_dans_le_support(self):
        self.assertTrue(self.g["adresses_strictement_croissantes"])
        self.assertTrue(self.g["toutes_dans_capacite"])
        self.assertTrue(self.g["poids_dans_zero_un"])
        self.assertTrue(self.g["poids_distincts_sur_echantillon"])

    def test_la_racine_merkle_depend_de_ordre_des_adresses(self):
        f = [hashlib.sha256(bytes([i])).digest() for i in range(4)]
        droit = b"".join(f)
        permute = b"".join([f[1], f[0], f[2], f[3]])
        self.assertNotEqual(tlu.racine_merkle(bytearray(droit)),
                            tlu.racine_merkle(bytearray(permute)))

    def test_racine_merkle_vide_et_niveau_impair(self):
        self.assertEqual(tlu.racine_merkle(bytearray()), hashlib.sha256(b"").hexdigest())
        trois = [hashlib.sha256(bytes([i])).digest() for i in range(3)]
        attendu = hashlib.sha256(
            hashlib.sha256(trois[0] + trois[1]).digest()
            + hashlib.sha256(trois[2] + trois[2]).digest()).hexdigest()
        self.assertEqual(tlu.racine_merkle(bytearray(b"".join(trois))), attendu)
        with self.assertRaises(ValueError):
            tlu.racine_merkle(bytearray(b"ab"))

    def test_grille_complete_telle_que_publiee(self):
        n = tlu.CAPACITE // tlu.PAS_GRILLE
        self.assertEqual(n, 313_000)
        self.assertEqual(Q(n, tlu.CAPACITE), Q(1, 10 ** 9))
        self.assertGreater(n, socle.PLAFOND_MATERIALISES)


class TestRegistreEtCertificat(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.obs = tlu.observer()
        cls.rapport = tlu.evaluer(cls.obs)

    def test_neuf_equations_numerotees_sans_trou(self):
        ids = [e["id"] for e in self.rapport["equations"]]
        self.assertEqual(ids, [f"EQ-TLU-{i:02d}" for i in range(1, 10)])
        self.assertEqual(len(set(ids)), 9)

    def test_neuf_controles_pass_et_champs_renseignes(self):
        self.assertEqual(self.rapport["compte"], {"PASS": 9, "FAIL": 0, "INCONCLUSIF": 0})
        limites = tlu.limites()
        for e in self.rapport["equations"]:
            self.assertIn(e["statut"], tlu.STATUTS)
            self.assertTrue(e["forme"].strip())
            self.assertIn(e["id"], limites)
            self.assertGreater(len(limites[e["id"]]), 40)
            numerique = e["id"].split("-")[-1]
            self.assertTrue(e["chemin_controle"].endswith("→ C" + numerique), e["id"])

    def test_racine_recalculee_hors_du_module(self):
        attendu = hashlib.sha256("\n".join(
            f"{e['id']}|{e['statut']}" for e in self.rapport["equations"]).encode("utf-8")).hexdigest()
        self.assertEqual(self.rapport["racine"], attendu)
        mutile = [dict(e) for e in self.rapport["equations"]]
        mutile[5]["statut"] = "FAIL"
        autre = hashlib.sha256("\n".join(
            f"{e['id']}|{e['statut']}" for e in mutile).encode("utf-8")).hexdigest()
        self.assertNotEqual(attendu, autre)
        self.assertEqual(len(self.rapport["racine"]), 64)

    def test_banc_de_mutation_capte_neuf_attaques_sur_neuf(self):
        m = tlu.verifier_mutations(self.obs)
        self.assertEqual(m["testees"], 9)
        self.assertEqual(m["captees"], 9)
        for identifiant, entree in m["par_equation"].items():
            self.assertEqual(entree["normal"], "PASS", identifiant)
            self.assertNotEqual(entree["mute"], "PASS", identifiant)
        self.assertEqual(set(m["par_equation"]), {e["id"] for e in self.rapport["equations"]})

    def test_le_sens_volume_ne_passe_jamais_declare_accompli(self):
        for e in self.rapport["equations"]:
            if e["id"] == "EQ-TLU-09":
                self.assertTrue(e["valeur"]["sens"]["volume"].startswith("non accompli"))
                self.assertTrue(e["valeur"]["clos"] and e["valeur"]["couvert"])
                self.assertFalse(e["valeur"]["grille_ancee"] > tlu.CAPACITE)
            if e["id"] == "EQ-TLU-06":
                self.assertIs(e["valeur"]["accompli_comme_volume"], False)

    def test_grille_de_observation_a_313_000_ancres_hachees_deux_fois(self):
        g = self.obs["grille"]
        self.assertEqual(g["taille_denomeree"], 313_000)
        self.assertEqual(Q(g["occupation"]), Q(1, 10 ** 9))
        self.assertTrue(g["racine_reproduite"] and g["racine_simple_reproduite"])
        self.assertLess(g["pic_tracemalloc_octets"], 128 * 1024 * 1024)
        self.assertGreater(g["debit_grille_par_seconde"], 1_000)

    def test_cadre_publie_ni_cle_test_ni_echantillon_cache(self):
        c = tlu.cadre_de(self.obs, self.rapport)
        self.assertEqual(c["registre"], "EQ-TLU")
        self.assertEqual(c["capacite_poids"], tlu.CAPACITE)
        self.assertEqual(c["produit_radices"], tlu.CAPACITE)
        self.assertEqual(len(c["radices"]), 13)
        self.assertEqual(c["accompli"], {"volume": False, "structure": True, "fonction": True})
        # valeur auto-référente (voir test_nommables_strictement_inferieurs_a_la_capacite) :
        # ce que le cadre doit publier, c'est le produit des axes lu au même instant.
        self.assertEqual(c["adresses_nommables"], tlu.nommables_registre()["nommables"])
        self.assertEqual(c["grille_ancee"], 313_000)
        self.assertEqual(len(c["racine_grille"]), 64)
        for cle in ("disque_libre_octets", "ram_libre_octets", "slots_tenants_en_ram"):
            self.assertGreater(c[cle], 0)
            self.assertLess(c[cle], tlu.DENSE_BF16_OCTETS)


class TestInterfaceUtilisateur(unittest.TestCase):
    def test_nommer_poids_appelables_sur_une_adresse_quelconque(self):
        for adresse in (0, 1, 42, 10 ** 11, tlu.CAPACITE - 1):
            self.assertEqual(tlu.slot(tlu.nommer(adresse)), adresse)
            self.assertIsInstance(tlu.poids(adresse), float)

    def test_adresses_dessin_toujours_dans_la_boite(self):
        draws = tlu.adresses_dessin(500)
        self.assertEqual(len(draws), 500)
        self.assertTrue(all(0 <= a < tlu.CAPACITE for a in draws))
        self.assertEqual(len(set(draws)), 500)

    def test_le_pas_de_la_grille_divise_la_capacite_sans_reste(self):
        self.assertEqual(tlu.CAPACITE % tlu.PAS_GRILLE, 0)
        self.assertEqual(tlu.CAPACITE // tlu.PAS_GRILLE, 313_000)

    def test_cli_nommer_et_poids_sur_une_adresse(self):
        rendu = []
        for argv in (["--nommer", "312999999999999"], ["--poids", "0"]):
            sortie = io.StringIO()
            with contextlib.redirect_stdout(sortie):
                self.assertEqual(tlu.main(argv), 0)
            rendu.append(json.loads(sortie.getvalue()))
        self.assertEqual(rendu[0]["adresse"], 312999999999999)
        self.assertEqual(rendu[0]["nom"], list(tlu.nommer(312999999999999)))
        self.assertEqual(rendu[1]["poids"], tlu.poids(0))


if __name__ == "__main__":
    unittest.main(verbosity=2)
