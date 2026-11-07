# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2026 IMAM8MAHDI / Astro-Code Ecosystem
# SPDX-License-Identifier: GPL-3.0-only OR AGPL-3.0-only
"""Tests de l'émulateur quantique AL-MIZAN (unittest, stdlib uniquement)."""

from __future__ import annotations

import math
import sys
import unittest
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
for _p in (RACINE, RACINE / "code"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

from noyau_statevector import (  # noqa: E402
    ModeleBruit,
    Operation,
    SimulateurVecteurEtat,
    executer_counts,
)
from frontend_qasm import (  # noqa: E402
    CIRCUITS_CANONIQUES,
    charger_circuit,
    evaluer_angle,
    parser_openqasm,
)
from attenuation_zne import extrapolation_richardson, PointZne  # noqa: E402
from noyau_matrice_densite import (  # noqa: E402
    SimulateurMatriceDensite,
    comparer_vecteur_densite,
)
from metriques import (  # noqa: E402
    concurrence_2q,
    entropie_intrication_2q,
    vecteur_bloch,
)
from rendu_circuit import dessiner_circuit  # noqa: E402
from algorithmes import (  # noqa: E402
    _table_permutation_mod,
    energie_exacte_h2,
    esperance_hamiltonien,
    shor_factoriser,
    vqe_h2,
)
from generateur_gds import (  # noqa: E402
    construire_tuile_steane,
    ecrire_gds,
    verifier_drc,
)
from conjecture_point_carre import (  # noqa: E402
    certificat_point_carre,
    est_carre_parfait,
    plus_grand_facteur_carre,
    verifier_pc1,
    verifier_pc3,
)
from certificats.arbre_savoir import construire_arbre  # noqa: E402
from certificats.n05_hodge import _hodge_tore  # noqa: E402
from certificats.n06_bsd import _certificat_courbe, _points_mod_p  # noqa: E402
from certificats.n07_poincare import _octaedre, _rang_gf2  # noqa: E402
import ponts_systeme  # noqa: E402


class TestVecteurEtat(unittest.TestCase):
    def test_etat_initial(self):
        sim = SimulateurVecteurEtat(3)
        self.assertEqual(sim.probabilites(), {0: 1.0})

    def test_porte_x_inverse(self):
        sim = SimulateurVecteurEtat(1)
        sim.porte("x", (0,))
        self.assertAlmostEqual(sim.probabilite_1(0), 1.0)

    def test_h_deux_fois_identite(self):
        sim = SimulateurVecteurEtat(1)
        sim.porte("h", (0,))
        sim.porte("h", (0,))
        self.assertAlmostEqual(sim.probabilites()[0], 1.0)

    def test_bell_intrication(self):
        sim = SimulateurVecteurEtat(2, graine=1)
        sim.porte("h", (0,))
        sim.porte("cx", (0, 1))
        probas = sim.probabilites()
        self.assertAlmostEqual(probas[0b00], 0.5)
        self.assertAlmostEqual(probas[0b11], 0.5)
        self.assertEqual(len(probas), 2)

    def test_swap(self):
        sim = SimulateurVecteurEtat(2)
        sim.porte("x", (0,))
        sim.porte("swap", (0, 1))
        self.assertAlmostEqual(sim.probabilite_1(1), 1.0)
        self.assertAlmostEqual(sim.probabilite_1(0), 0.0)

    def test_ccx_toffoli(self):
        sim = SimulateurVecteurEtat(3)
        sim.porte("x", (0,))
        sim.porte("x", (1,))
        sim.porte("ccx", (0, 1, 2))
        self.assertAlmostEqual(sim.probabilite_1(2), 1.0)

    def test_mesure_effondrement(self):
        sim = SimulateurVecteurEtat(1)
        sim.porte("x", (0,))
        self.assertEqual(sim.mesurer_qubit(0), 1)
        self.assertAlmostEqual(sim.probabilite_1(0), 1.0)

    def test_counts_bell_statistiques(self):
        ops, n = parser_openqasm(CIRCUITS_CANONIQUES["BELL"])
        counts = executer_counts(ops, n, 400, graine=42)
        total = sum(counts.values())
        self.assertEqual(total, 400)
        self.assertEqual(set(counts), {"00", "11"})
        self.assertGreater(counts["00"], 100)
        self.assertGreater(counts["11"], 100)

    def test_bruit_depolarisant_degrade(self):
        ops, n = parser_openqasm(CIRCUITS_CANONIQUES["BELL"])
        propre = executer_counts(ops, n, 400, graine=1)
        bruyant = executer_counts(ops, n, 400, ModeleBruit(0.3), graine=1)
        # Le bruit introduit des états hors {00, 11}
        hors = sum(v for k, v in bruyant.items() if k not in ("00", "11"))
        self.assertGreater(hors, 0)
        self.assertEqual(set(propre), {"00", "11"})


class TestFrontendQasm(unittest.TestCase):
    def test_evaluer_angle(self):
        self.assertAlmostEqual(evaluer_angle("pi"), math.pi)
        self.assertAlmostEqual(evaluer_angle("pi/2"), math.pi / 2)
        self.assertAlmostEqual(evaluer_angle("3*pi/4"), 3 * math.pi / 4)
        self.assertAlmostEqual(evaluer_angle("-0.5"), -0.5)

    def test_parse_bell(self):
        ops, n = parser_openqasm(CIRCUITS_CANONIQUES["BELL"])
        self.assertEqual(n, 2)
        self.assertEqual([o.nom for o in ops], ["h", "cx", "measure"])

    def test_grover_amplifie_11(self):
        ops, n = parser_openqasm(CIRCUITS_CANONIQUES["GROVER"])
        counts = executer_counts(ops, n, 200, graine=7)
        self.assertGreater(counts.get("11", 0), 150)

    def test_ghz3(self):
        ops, n = parser_openqasm(CIRCUITS_CANONIQUES["GHZ"])
        counts = executer_counts(ops, n, 200, graine=3)
        self.assertEqual(set(counts), {"000", "111"})

    def test_qft_sexecute(self):
        ops, n = parser_openqasm(CIRCUITS_CANONIQUES["QFT"])
        counts = executer_counts(ops, n, 100, graine=5)
        self.assertEqual(sum(counts.values()), 100)

    def test_charger_circuit_canonique(self):
        ops, n, nom = charger_circuit("bell")
        self.assertEqual(nom, "BELL")
        self.assertEqual(n, 2)

    def test_erreur_ligne_inconnue(self):
        with self.assertRaises(Exception):
            parser_openqasm('OPENQASM 2.0;\nqreg q[1];\nfoobar q[0];\n')


class TestZne(unittest.TestCase):
    def test_richardson_lineaire(self):
        # observable parfaitement linéaire f(λ) = 1 - 0.1λ → f(0) = 1
        points = [PointZne(1.0, 0.01, 0.9, 100),
                  PointZne(2.0, 0.02, 0.8, 100),
                  PointZne(3.0, 0.03, 0.7, 100)]
        self.assertAlmostEqual(extrapolation_richardson(points), 1.0)


class TestMatriceDensite(unittest.TestCase):
    def test_etat_pur_sans_bruit(self):
        ops, n = parser_openqasm(CIRCUITS_CANONIQUES["BELL"])
        res = comparer_vecteur_densite(ops, n)
        self.assertAlmostEqual(res["purete_tr_rho2"], 1.0, places=6)
        self.assertAlmostEqual(res["entropie_von_neumann_bits"], 0.0, places=6)
        self.assertAlmostEqual(res["fidelite_vs_ideal"], 1.0, places=6)
        self.assertAlmostEqual(res["probabilites_exactes"]["00"], 0.5)
        self.assertAlmostEqual(res["probabilites_exactes"]["11"], 0.5)

    def test_bruit_reduit_purete(self):
        ops, n = parser_openqasm(CIRCUITS_CANONIQUES["BELL"])
        res = comparer_vecteur_densite(ops, n, ModeleBruit(0.2))
        self.assertLess(res["purete_tr_rho2"], 1.0 - 1e-6)
        self.assertGreater(res["entropie_von_neumann_bits"], 1e-6)
        self.assertLess(res["fidelite_vs_ideal"], 1.0)

    def test_trace_conservee(self):
        sim = SimulateurMatriceDensite(2)
        sim.executer([Operation("h", (0,)), Operation("cx", (0, 1))],
                     ModeleBruit(0.5, 0.3), dephasage=0.4)
        tr = sum(sim.rho[i * sim.dim + i] for i in range(sim.dim)).real
        self.assertAlmostEqual(tr, 1.0, places=9)


class TestMetriques(unittest.TestCase):
    def test_bloch_etat_zero(self):
        sim = SimulateurVecteurEtat(1)
        x, y, z = vecteur_bloch(sim.etat, 1, 0)
        self.assertAlmostEqual(z, 1.0)
        self.assertAlmostEqual(x, 0.0)

    def test_bloch_etat_plus(self):
        sim = SimulateurVecteurEtat(1)
        sim.porte("h", (0,))
        x, y, z = vecteur_bloch(sim.etat, 1, 0)
        self.assertAlmostEqual(x, 1.0)
        self.assertAlmostEqual(z, 0.0, places=9)

    def test_concurrence_bell(self):
        sim = SimulateurVecteurEtat(2)
        sim.porte("h", (0,))
        sim.porte("cx", (0, 1))
        self.assertAlmostEqual(concurrence_2q(sim.etat), 1.0, places=6)
        self.assertAlmostEqual(entropie_intrication_2q(sim.etat), 1.0, places=6)

    def test_concurrence_produit(self):
        sim = SimulateurVecteurEtat(2)
        self.assertAlmostEqual(concurrence_2q(sim.etat), 0.0, places=9)


class TestRenduCircuit(unittest.TestCase):
    def test_dessin_bell(self):
        ops, n = parser_openqasm(CIRCUITS_CANONIQUES["BELL"])
        dessin = dessiner_circuit(ops, n)
        self.assertIn("q[0]", dessin)
        self.assertIn("q[1]", dessin)
        self.assertIn("H", dessin)
        self.assertIn("●", dessin)
        self.assertIn("⊕", dessin)


class TestCircuitsAvances(unittest.TestCase):
    def test_dj_oracle_equilibre(self):
        ops, n = parser_openqasm(CIRCUITS_CANONIQUES["DJ"])
        counts = executer_counts(ops, n, 100, graine=9)
        # Oracle équilibré → q[0] = 1 (bit LSB) : bitstrings *1
        self.assertTrue(all(k[-1] == "1" for k in counts))

    def test_teleportation(self):
        ops, n = parser_openqasm(CIRCUITS_CANONIQUES["TELEPORTATION"])
        counts = executer_counts(ops, n, 100, graine=4)
        self.assertEqual(sum(counts.values()), 100)

    def test_qpe_sexecute(self):
        ops, n = parser_openqasm(CIRCUITS_CANONIQUES["QPE"])
        counts = executer_counts(ops, n, 100, graine=2)
        self.assertEqual(sum(counts.values()), 100)


class TestAlgorithmes(unittest.TestCase):
    def test_vqe_sous_energie_exacte(self):
        res = vqe_h2(essais=150)
        # L'énergie VQE ne peut pas passer sous l'exacte (principe variationnel)
        self.assertGreaterEqual(res["energie_vqe_ha"],
                                res["energie_exacte_ha"] - 1e-9)
        self.assertLess(res["ecart_mha"], 100.0)

    def test_energie_exacte_h2(self):
        # Valeurs propres de la matrice 4×4 construite terme à terme
        self.assertAlmostEqual(energie_exacte_h2(), -1.9152835505, places=6)

    def test_esperance_etat_00(self):
        e = esperance_hamiltonien([1 + 0j, 0j, 0j, 0j])
        self.assertAlmostEqual(e, -1.0524 + 0.3979 - 0.3979 - 0.0113, places=6)

    def test_shor_15(self):
        res = shor_factoriser(15, 7)
        self.assertEqual(res["facteurs"], [3, 5])
        self.assertIn(4, res["periodes_candidats"])

    def test_table_permutation_bijective(self):
        t = _table_permutation_mod(7, 15, 4)
        self.assertEqual(sorted(t[:15]), list(range(15)))

    def test_permutation_unitaire(self):
        # ×7 mod 15 sur registre 4q contrôlé par q0 : la norme est conservée
        sim = SimulateurVecteurEtat(5)
        sim.porte("x", (1,))
        ops = [Operation("perm", (1, 2, 3, 4), (), (0,),
                         _table_permutation_mod(7, 15, 4))]
        sim.executer(ops)
        total = sum(abs(a) ** 2 for a in sim.etat)
        self.assertAlmostEqual(total, 1.0)


class TestGds(unittest.TestCase):
    def test_gds_binaire_valide(self):
        import struct
        import tempfile
        rects, textes = construire_tuile_steane()
        with tempfile.TemporaryDirectory() as d:
            chemin = Path(d) / "test.gds"
            ecrire_gds(chemin, rects, textes)
            brut = chemin.read_bytes()
        # Structure TLV : chaque enregistrement = u16 longueur + u8 type + u8 dtype
        pos = 0
        types = []
        while pos < len(brut):
            longueur, rtype, _ = struct.unpack(">HBB", brut[pos:pos + 4])
            self.assertGreaterEqual(longueur, 4)
            types.append(rtype)
            pos += longueur
        self.assertEqual(pos, len(brut))
        self.assertEqual(types[0], 0x00)   # HEADER
        self.assertEqual(types[-1], 0x04)  # ENDLIB
        self.assertIn(0x08, types)         # BOUNDARY

    def test_drc_detecte_violations(self):
        from generateur_gds import Rect, L_QUBIT
        rects = [Rect(L_QUBIT, 0, 0, 0.1, 5),      # trop étroit
                 Rect(L_QUBIT, 10, 0, 15, 5),
                 Rect(L_QUBIT, 15.2, 0, 20, 5)]    # espacement 0.2 < min
        res = verifier_drc(rects)
        self.assertGreaterEqual(res["nb_violations"], 2)


class TestConjecturePointCarre(unittest.TestCase):
    def test_est_carre_parfait(self):
        self.assertTrue(est_carre_parfait(2304))   # 48²
        self.assertTrue(est_carre_parfait(9))
        self.assertFalse(est_carre_parfait(1536))
        self.assertFalse(est_carre_parfait(0 - 4))

    def test_plus_grand_facteur_carre(self):
        self.assertEqual(plus_grand_facteur_carre(6403563), (1461, 3))
        self.assertEqual(plus_grand_facteur_carre(93987), (177, 3))
        self.assertEqual(plus_grand_facteur_carre(135000000), (3000, 15))
        self.assertEqual(plus_grand_facteur_carre(7), (1, 7))

    def test_pc1_unicite_j(self):
        res = verifier_pc1()
        self.assertTrue(res["verdict"])
        self.assertEqual(res["points_fixes"], [{"echelon": 0, "lettre": "J"}])

    def test_pc3_signature_cycles(self):
        res = verifier_pc3()
        self.assertTrue(res["verdict"])
        for nom, d in res["cycles"].items():
            self.assertTrue(d["signature_carree"], f"{nom} sans carré")

    def test_certificat_global_et_sceau(self):
        c = certificat_point_carre()
        self.assertTrue(c["verdict_global"])
        self.assertEqual(len(c["sceau_sha256"]), 64)


class TestArbreSavoir(unittest.TestCase):
    def test_arbre_complet(self):
        a = construire_arbre()
        self.assertEqual(a["nb_branches"], 10)
        self.assertEqual(len(a["sceau_global_sha256"]), 64)
        statuts = {b["id_branche"]: b["statut"] for b in a["branches"]}
        self.assertIn(statuts["N7"], ("DEJA_DEMONTRE", "NON_DECIDABLE"))

    def test_hodge_tore(self):
        h = _hodge_tore()
        self.assertEqual(h["h11"], 1)
        self.assertTrue(h["classes_11_integrales"])

    def test_bsd_hasse(self):
        c = _certificat_courbe("test", -1, 0, borne_p=23)
        self.assertTrue(c["hasse_respectee_partout"])
        self.assertGreater(c["premiers_testes"], 0)
        # Vérification directe : #E(F5) pour y²=x³−x = 8 (a_5 = −2)
        self.assertEqual(_points_mod_p(-1, 0, 5), 8)

    def test_poincare_octaedre(self):
        d1, d2, v, e, f = _octaedre()
        self.assertEqual((v, e, f), (6, 12, 8))
        self.assertEqual(v - e + f, 2)
        self.assertEqual((e - _rang_gf2(d1)) - _rang_gf2(d2), 0)

    def test_rigueur_intervalle_zero1(self):
        from certificats.rigueur_intervalle import certificats_zeros_ligne
        r = certificats_zeros_ligne([(14.0, 14.4)])
        self.assertTrue(r[0]["certifie"])
        self.assertIn("theoreme", r[0])


class TestPontsSysteme(unittest.TestCase):
    def test_transducteur_bell_pivot_j(self):
        """Bell (50/50 sur |00>,|11>) → espérance 0 → lettre pivot J."""
        res = ponts_systeme.traduire_deterministe(
            {"|00>": 0.5, "|11>": 0.5}, "BELL", 0.99, 1.0)
        if not res.get("disponible"):
            self.skipTest("transducteur indisponible")
        t = res["traduction"]
        self.assertEqual(t["chiffre_socle"], 0)
        self.assertEqual(t["lettre_socle"], "J")

    def test_qec_module_charge(self):
        if ponts_systeme.charger_module_qec() is None:
            self.skipTest("qubit_logique_mizan indisponible")
        demo = ponts_systeme.demonstration_correction_poids_un()
        self.assertTrue(demo["tous_poids_un_corriges"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
