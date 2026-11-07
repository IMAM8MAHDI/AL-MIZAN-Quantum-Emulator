# -*- coding: utf-8 -*-
"""Tests du noyau encapsulé horloge_noyau (lecture/exécution autorisées)."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

SYSTEME = Path(__file__).resolve().parents[2]
if str(SYSTEME) not in sys.path:
    sys.path.insert(0, str(SYSTEME))

from bibliotheques.lib_informe import (
    MatriceLogiqueComplexe,
    POLE_MATIERE_NEGATIF,
    POLE_MATIERE_POSITIF,
    Q_DEGRE_MECOIS,
    Q_DEGRE_MEDINOIS,
    synchroniser_etats_matiere_aux_cinq_familles,
)
from bibliotheques.lib_physique import (
    ETAT_ORIGINE_HELIUM,
    ETATS_HYDROGENE,
    ETATS_LUNE,
    ETATS_TERRE,
    MAGNITUDE_ETAT_MATIERE_LUNE,
    MAGNITUDE_ETAT_MATIERE_SOLEIL,
    MAGNITUDE_ETAT_MATIERE_TERRE,
    cataloguer_valeurs_etats_matiere_nommes,
)
from horloge_noyau.architecture_informe_couche_matiere_table_mizan import (
    ARCHITECTURE_FIGEE,
    SYNCHRONISATION_HARMONIQUE_TRINITE,
    TRAJECTOIRE_ZERO_EXPANSION,
    cataloguer_tous_les_etats_de_matiere,
    confirmer_harmonie_et_prouver_justesse,
)
from horloge_noyau.verrou import (
    NoyauVerrouilleError,
    refuser_ecriture,
    statut_verrou,
    verifier_integrite,
)


class TestSyncNiveauxTable(unittest.TestCase):
    def test_pole_negatif_niveaux_impairs(self):
        s = synchroniser_etats_matiere_aux_cinq_familles(POLE_MATIERE_NEGATIF)
        self.assertEqual(s.niveaux_table_actifs, (1, 3))

    def test_pole_positif_niveaux_pairs(self):
        s = synchroniser_etats_matiere_aux_cinq_familles(POLE_MATIERE_POSITIF)
        self.assertEqual(s.niveaux_table_actifs, (2, 4))


class TestZeroExpansionEtHorloge(unittest.TestCase):
    def test_trajectoire_zero_expansion(self):
        traj = TRAJECTOIRE_ZERO_EXPANSION
        self.assertEqual(traj["trajectoire"], "ZERO_VERS_EXPANSION")
        self.assertTrue(traj["point_zero"]["est_origine"])

    def test_q_degre(self):
        self.assertEqual(Q_DEGRE_MECOIS, 2304)
        self.assertEqual(Q_DEGRE_MEDINOIS, 1536)

    def test_valeurs_etats(self):
        self.assertEqual(sum(e.valeur for e in ETATS_HYDROGENE) + ETAT_ORIGINE_HELIUM.valeur, MAGNITUDE_ETAT_MATIERE_SOLEIL)
        self.assertEqual(sum(e.valeur for e in ETATS_TERRE), MAGNITUDE_ETAT_MATIERE_TERRE)
        self.assertEqual(sum(e.valeur for e in ETATS_LUNE), MAGNITUDE_ETAT_MATIERE_LUNE)
        self.assertGreaterEqual(len(cataloguer_valeurs_etats_matiere_nommes()["terre_313"]["etats"]), 7)

    def test_horloge_deduite_du_noyau(self):
        from horloge_noyau.horloge_logique_mizan import (
            CYCLE_DX_SOLAIRE,
            CYCLE_DY_LUNAIRE,
            CYCLE_DZ_QUANTIQUE,
            CYCLE_DT_KERNEL,
            HORLOGE_LOGIQUE,
            PPCM_CYCLES_TRINITE,
            BASE_HARMONIQUE,
            AMPLITUDE_HARMONIQUE,
        )
        lien = HORLOGE_LOGIQUE.lien_avec_noyau()
        self.assertTrue(lien["pas_valeurs_arbitraires"])
        self.assertEqual(lien["point_zero"], "COMPLEXE = LA TABLE")
        self.assertAlmostEqual(CYCLE_DX_SOLAIRE, 50027.8359375, places=6)
        self.assertAlmostEqual(CYCLE_DY_LUNAIRE, 46993.5, places=6)
        self.assertAlmostEqual(CYCLE_DZ_QUANTIQUE, 135000000.0, places=6)
        self.assertAlmostEqual(
            CYCLE_DT_KERNEL,
            CYCLE_DX_SOLAIRE + CYCLE_DY_LUNAIRE + CYCLE_DZ_QUANTIQUE,
            places=6,
        )
        self.assertEqual(PPCM_CYCLES_TRINITE, 12)
        self.assertEqual(BASE_HARMONIQUE, 19)
        self.assertEqual(AMPLITUDE_HARMONIQUE, 9)
        v = confirmer_harmonie_et_prouver_justesse(+313)
        self.assertTrue(v.preuve_ensemble_juste)
        self.assertTrue(v.couches_ok.get("horloge_deduite_du_noyau"))

    def test_poupees_et_catalogue(self):
        arch = ARCHITECTURE_FIGEE.figer(persister=False)
        self.assertEqual(arch.poupees_russes["trajectoire_calcul"], "ZERO_VERS_EXPANSION")
        self.assertGreaterEqual(len(cataloguer_tous_les_etats_de_matiere()), 40)
        self.assertEqual(SYNCHRONISATION_HARMONIQUE_TRINITE["origine_calcul"], "COMPLEXE_POINT_ZERO")


class TestVerrouLectureOkEcritureBloquee(unittest.TestCase):
    def test_integrite_lisible(self):
        info = verifier_integrite()
        self.assertTrue(info["integrite"])
        self.assertTrue(info["lecture_execution"])
        self.assertFalse(info["ecriture"])

    def test_refuser_ecriture(self):
        with self.assertRaises(NoyauVerrouilleError):
            refuser_ecriture("tentative")

    def test_statut(self):
        st = statut_verrou()
        self.assertTrue(st["lecture"])
        self.assertTrue(st["execution"])
        self.assertFalse(st["ecriture"])


if __name__ == "__main__":
    unittest.main()
