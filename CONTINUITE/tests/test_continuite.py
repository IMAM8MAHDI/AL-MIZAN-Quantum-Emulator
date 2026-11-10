# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2026 IMAM8MAHDI / Astro-Code Ecosystem
# SPDX-License-Identifier: GPL-3.0-only OR AGPL-3.0-only
"""Tests du dossier CONTINUITE — le théorème est re-dérivé, pas recopié.

Six exigences, dans l'ordre :
    1. ρ, le pas de bascule 42 et le point fixe 61/500 sont re-calculés ICI par une écriture
       différente (puissances entières d'exposants 12, puis comparaison croisée) : aucune égalité
       n'est acceptée sur parole ;
    2. l'identité de télescopage est éprouvée sur une suite géométrique étrangère au dépôt
       (raison 1/2) : si elle ne tenait qu'à ρ, ce serait une coïncidence, pas un théorème ;
    3. le rôle du clampage est isolé : sur la même contraction sans borne basse déclarée, il n'y
       a plus de point fixe dans D — le théorème dépend donc bien d'une déclaration humaine ;
    4. non-vacuité : une copie du catalogue dont une échelle est déplacée fait ROUGIR le contrôle
       C03, et le contrôle nommé est rapporté ;
    5. les verdicts défavorables restent défavorables : les croix du plan global sont comptées, et
       aucun énoncé de ce dossier ne peut les requalifier ;
    6. déterminisme et racine Merkle : deux exécutions concordent, et changer une semence change
       la racine (sinon le sceau ne scelle rien).

Stdlib uniquement.
    cd ZENODO_DEPOT_ALMIZAN && py -3 -m unittest CONTINUITE.tests.test_continuite -v
"""

import copy
import hashlib
import json
import sys
import unittest
from decimal import Decimal, getcontext
from fractions import Fraction
from pathlib import Path

RACINE_DEPOT = Path(__file__).resolve().parents[2]
if str(RACINE_DEPOT) not in sys.path:
    sys.path.insert(0, str(RACINE_DEPOT))

from CONTINUITE import continuite_base as CONT                # noqa: E402
from bibliotheques import lib_almizan_extension as EXT        # noqa: E402

CERT = CONT.certificat()
EQS = {e["id"]: e for e in CONT.equations(CERT)}
MIZAN, REF = Fraction(249, 400), Fraction(61, 500)
BRACKET = (Fraction(96126, 100000), Fraction(96127, 100000))
HORS_NOEUDS = frozenset({"source", "empreinte_execution", "rejoue_identique", "limites",
                         "attribution", "racine_merkle_sha256"})


def comparaison_entiere(k: int):
    """(gauche, droite) de la comparaison qui décide x_k < 61/500 — écriture indépendante."""
    return 249 ** (12 + k) * 500 ** 12, 400 ** (12 + k) * 61 ** 12


def sort_entier(k: int) -> bool:
    gauche, droite = comparaison_entiere(k)
    return gauche < droite


def premier_pas_hors_D(rho: Fraction) -> int:
    """Premier k tel que MIZAN·rho^k < LIGNE_REF, en rationnels exacts — aucun flottant."""
    x = MIZAN
    for k in range(1, 300):
        x *= rho
        if x < REF:
            return k
    raise AssertionError("la chaîne ne sort jamais de D : le bracket est faux")


def noeuds_de(cert):
    return {k: v for k, v in cert.items() if k not in HORS_NOEUDS}


def racine_depuis(noeuds):
    """Re-écrit ici la formule de `certificat()` : racine des empreintes de nœuds triés."""
    return hashlib.sha256(CONT.canonique(
        {c: hashlib.sha256(CONT.canonique(noeuds[c])).hexdigest() for c in sorted(noeuds)}
    )).hexdigest()


class TestReDerivationEntiere(unittest.TestCase):
    """ρ, n* et le point fixe sont prouvés ici par une autre écriture que celle du module."""

    def test_rho_encadre_par_une_autre_ecriture(self):
        getcontext().prec = 60
        r = (Decimal(249) / Decimal(400)) ** (Decimal(1) / Decimal(12))
        bas, haut = BRACKET
        self.assertLess(bas, r)
        self.assertGreaterEqual(haut, r)
        # voie entière pure : douzièmes puissances comparées, aucun flottant n'intervient
        self.assertLess(96126 ** 12 * 400, 249 * 10 ** 60)
        self.assertGreaterEqual(96127 ** 12 * 400, 249 * 10 ** 60)
        self.assertEqual((CERT["rho"]["inferieur"], CERT["rho"]["superieur"]),
                         ("96126/100000", "96127/100000"))

    def test_pas_de_bascule_re_prouve_par_entiers(self):
        self.assertEqual(CERT["chaine"]["pas_de_sortie"], 42)
        self.assertFalse(sort_entier(41))
        self.assertTrue(sort_entier(42))
        # franchi une fois, le seuil ne se reperd pas : le compte n'est pas un choix
        self.assertTrue(all(sort_entier(k) for k in range(42, 60)))

    def test_le_pas_42_ne_depend_pas_du_sens_du_bracket(self):
        for rho in BRACKET:
            self.assertEqual(premier_pas_hors_D(rho), 42, str(rho))

    def test_point_fixe_est_la_borne_basse_declaree(self):
        self.assertEqual(CERT["point_fixe"]["point_fixe"], "61/500")
        for rho in BRACKET:
            self.assertEqual(max(REF, min(MIZAN, rho * REF)), REF, str(rho))

    def test_unicite_par_absurdite_sur_la_grille(self):
        for rho in BRACKET:
            fixes = [x for k in range(1, 1024)
                     for x in [REF + (MIZAN - REF) * k / 1024]
                     if max(REF, min(MIZAN, rho * x)) == x]
            self.assertEqual(fixes, [], str(rho))


class TestTheoremeStructurel(unittest.TestCase):
    """Le télescopage et la contraction ne dépendent ni de ρ ni des semences du dépôt."""

    def test_telescopage_sur_une_suite_etrangere(self):
        getcontext().prec = 60
        x = [Decimal(7) * Decimal("0.5") ** k for k in range(21)]
        somme = sum(x[k - 1] - x[k] for k in range(1, 21))
        self.assertEqual(somme, x[0] - x[20])

    def test_telescopage_du_module_tombe_juste_sur_42_pas(self):
        te = CERT["telescage"]
        self.assertEqual(te["N"], 42)
        self.assertTrue(te["identique"])
        self.assertEqual(Decimal(te["ecart_absolu"]), Decimal(0))
        self.assertEqual(te["somme_des_sauts"], te["difference_des_bords"])

    def test_sans_clamp_la_chaine_quitte_D_et_n_y_revient_jamais(self):
        """Le point fixe vient du clampage déclaré par l'auteur, pas de la contraction seule."""
        for rho in BRACKET:
            self.assertEqual(premier_pas_hors_D(rho), 42, str(rho))
            x = MIZAN * rho ** 42
            for _ in range(150):
                x *= rho
            self.assertLess(x, REF, str(rho))     # rien ne le retient : il descend sans fin

    def test_queue_encode_par_les_deux_tiers(self):
        q = CERT["queue"]
        valeur = Decimal(q["valeur_decimal"])
        bas = Fraction(*[int(u) for u in q["borne_basse"].split("/")])
        haut = Fraction(*[int(u) for u in q["borne_haute"].split("/")])
        self.assertTrue(q["encadrement_valide"])
        self.assertLess(bas, haut)
        self.assertLess(float(bas), float(valeur))
        self.assertGreater(float(haut), float(valeur))
        self.assertLess(4.90, float(valeur))      # la valeur publiée n'est pas un nombre rond
        self.assertGreater(4.92, float(valeur))


class TestNonVacuite(unittest.TestCase):
    """Déplacer une échelle du catalogue scellé doit faire ROUGIR C03 du module."""

    def controles_avec(self, catalogue):
        vrai = EXT.LES_27_FORMES_ETENDUES
        EXT.LES_27_FORMES_ETENDUES = catalogue
        try:
            etat = CONT.etat_complet()
            return {c["id"]: c for c in CONT.controles(EQS, etat)}
        finally:
            EXT.LES_27_FORMES_ETENDUES = vrai

    def test_deplacer_une_echelle_de_un_pour_cent_fait_rougir_c03(self):
        avant = self.controles_avec(EXT.LES_27_FORMES_ETENDUES)
        self.assertTrue(avant["C03"]["ok"], "C03 doit être vert sur le catalogue réel")
        catalogue = copy.deepcopy(EXT.LES_27_FORMES_ETENDUES)
        nouvelle = round(catalogue[7].echelle_mizan * 1.01, 8)
        object.__setattr__(catalogue[7], "echelle_mizan", nouvelle)
        apres = self.controles_avec(catalogue)
        self.assertFalse(apres["C03"]["ok"], "une échelle déplacée de 1 % doit rougir C03")
        derive = float(apres["C03"]["obtenu"].split("dérive max")[1].split("·")[0].strip())
        self.assertGreater(derive, 1e-3)

    def test_le_seuil_de_c03_n_est_pas_inatteignable(self):
        derive = Decimal(CERT["catalogue"]["derive_maximale"])
        self.assertLess(derive, Decimal("5e-9"))
        self.assertGreater(derive, Decimal(0))

    def test_c09_et_c10_numerent_reelement(self):
        self.assertEqual(CERT["point_fixe"]["candidats_fixes_sur_grille"], ["61/500"])
        self.assertEqual(len(CERT["point_fixe"]["absorptions_par_noeud"]), 27)
        self.assertEqual(CERT["point_fixe"]["depts_hors_D"], [])


class TestVerdictsDefavorables(unittest.TestCase):
    """Les croix du plan global restent des croix ; ce dossier ne les requalifie pas."""

    def test_les_lignes_a_croix_sont_toujours_comptees(self):
        compte = CONT.ecarts_ouverts()["lignes_a_croix"]
        self.assertGreater(compte, 0)
        self.assertEqual(CERT["ecarts_ouverts"]["lignes_a_croix"], compte)
        self.assertGreaterEqual(CERT["ecarts_ouverts"]["goulots"], 1)

    def test_une_croix_n_est_devenue_aucune_coche(self):
        self.assertEqual(CONT.ecarts_ouverts()["coches"], CERT["ecarts_ouverts"]["coches"])

    def test_aucun_enonce_ne_pretend_remplir_un_goulot(self):
        interdits = ("démontré globalement", "preuve universelle", "goulot rempli",
                     "résolu pour tout", "100 %", "INVIOLABLE")
        texte = (json.dumps(CERT["limites"], ensure_ascii=False)
                 + " ".join(CERT["source"]["ce_que_ce_module_n_utilise_pas"])
                 + " ".join(e["limite"] for e in EQS.values()))
        for mot in interdits:
            self.assertNotIn(mot.lower(), texte.lower(), mot)

    def test_la_bande_epsilon_reste_declaree_non_mesuree(self):
        self.assertIn("aucun instrument", CERT["bande_epsilon"]["statut_de_la_bande"])
        self.assertEqual({e["statut"] for e in EQS.values()} - {"OPÉRATIONNEL"}, {"SPÉCIFIÉ"})
        self.assertEqual(sum(1 for e in EQS.values() if e["statut"] == "SPÉCIFIÉ"), 2)


class TestAntecedentEau(unittest.TestCase):
    """Le piège formel est testé : la somme des produits vaut 3Q, pas Q."""

    def test_produits_section_par_section(self):
        ea = CERT["antecedent_eau"]
        self.assertTrue(ea["identique_al_debit"])
        self.assertTrue(ea["somme_est_triple_debit"])
        self.assertEqual(ea["somme_des_produits"], "30/1")
        self.assertEqual(set(ea["produits"]), {"10/1"})

    def test_les_nombres_sont_ceux_lus_dans_abondance(self):
        from ABONDANCE import eau_abondance as EAU
        lu = EAU.continuite()
        ea = CERT["antecedent_eau"]
        self.assertEqual([float(Fraction(s)) for s in ea["sections"]], lu["sections_m2"])
        self.assertEqual(float(Fraction(ea["debit"])), lu["debit_m3_s"])
        self.assertEqual([float(Fraction(v)) for v in ea["vitesses"]], lu["vitesses_m_s"])


class TestPiliersEtTransmission(unittest.TestCase):
    def test_quatre_piliers_ok(self):
        from FONDATION.OUTILS import audit_piliers as AP
        rendu = AP.auditer(RACINE_DEPOT / "CONTINUITE" / "continuite_base.py")
        self.assertEqual(rendu["verdict"], "CONFORME")
        self.assertEqual({p["etat"] for p in rendu["piliers"].values()}, {"OK"})
        self.assertEqual(rendu["equations"], rendu["controles"])

    def test_resoudre_ne_laisse_aucun_controle_rouge(self):
        donnees = CONT.resoudre()
        self.assertTrue(CONT.verifier(donnees))
        self.assertEqual(donnees["conclusion"]["controles_verts"],
                         donnees["conclusion"]["controles_total"])
        self.assertEqual(donnees["conclusion"]["pas_de_bascule"], 42)

    def test_deux_executions_meme_empreinte(self):
        self.assertTrue(CERT["rejoue_identique"])
        self.assertEqual(CONT.certificat()["empreinte_execution"], CERT["empreinte_execution"])

    def test_la_racine_change_si_un_noeud_change(self):
        noeuds = noeuds_de(CERT)
        self.assertEqual(racine_depuis(noeuds), CERT["racine_merkle_sha256"])
        for cle, sous_cle, valeur in (("chaine", "pas_de_sortie", 41),
                                      ("bande_epsilon", "epsilon", "22/1000"),
                                      ("telescage", "somme_des_sauts", "0.5")):
            mute = copy.deepcopy(noeuds)
            mute[cle][sous_cle] = valeur
            self.assertNotEqual(racine_depuis(mute), CERT["racine_merkle_sha256"], cle)

    def test_artefacs_ecrivables_sans_ecraser_le_sceau(self):
        from tempfile import TemporaryDirectory
        with TemporaryDirectory() as td:
            rendu = CONT.ecrire_artefacts(CERT, Path(td))
            self.assertEqual(len(rendu), 3)
            octets = (Path(td) / "chaine_de_pas.csv").read_bytes()
            self.assertEqual(octets[:3], b"\xef\xbb\xbf")
            self.assertIn(b";", octets)
            self.assertIn(b"\r\n", octets)
            texte = (Path(td) / "enonce_theoreme.md").read_text(encoding="utf-8")
            self.assertTrue(texte.startswith("# CONTINUIT"))
            self.assertIn("42", texte)
            charge = json.loads((Path(td) / "certificat.json").read_bytes())
            self.assertEqual(charge["racine_merkle_sha256"], CERT["racine_merkle_sha256"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
