# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2026 IMAM8MAHDI / Astro-Code Ecosystem
# SPDX-License-Identifier: GPL-3.0-only OR AGPL-3.0-only
"""Tests du laboratoire — l'écran ne doit rien à la machine qui le regarde.

Quatre exigences, dans l'ordre :
    1. la fermeture de la trajectoire est re-calculée ICI, en entiers, par une arithmétique
       écrite à part : le résidu doit valoir 0 à chaque pas, et la période commune doit être
       exactement le ppcm des trois périodes d'axes ;
    2. le repère porte quatorze coordonnées nommées, chacune sourcée, et les douze qui viennent
       du dépôt sont re-derivées indépendamment du module : un nombre sans source est une faute ;
    3. l'instrument de stabilité est rendu coupable avant d'être cru : il doit retrouver le
       bruit qu'il injecte, sur plusieurs graines, et son calcul est comparé à une valeur
       faite à la main ;
    4. les octets écrits sont les mêmes sur n'importe quelle machine : les nombres d'hôte
       s'affichent et n'entrent pas dans les artefacts scellés.

    cd ZENODO_DEPOT_ALMIZAN && py -3 -m unittest HORLOGERIE.tests.test_laboratoire -v
"""

import json
import math
import subprocess
import sys
import tempfile
import unittest
from fractions import Fraction
from pathlib import Path

RACINE_DEPOT = Path(__file__).resolve().parents[2]
if str(RACINE_DEPOT) not in sys.path:
    sys.path.insert(0, str(RACINE_DEPOT))

from HORLOGERIE import horlogerie as HOR                                    # noqa: E402
from HORLOGERIE import laboratoire as LAB                                   # noqa: E402

DEN = 128
STATUTS_ADMIS = {"opérationnel", "spécifié", "simulé", "mesuré", "déclaré · non vérifié"}


def pgcd(a: int, b: int) -> int:
    while b:
        a, b = b, a % b
    return a


def ppcm(*nombres: int) -> int:
    r = 1
    for n in nombres:
        r = r * n // pgcd(r, n)
    return r


class TestEntiers(unittest.TestCase):
    """Le même rationnel rendu entier : la conversion ne doit rien perdre."""

    def test_conversion_exacte_sur_les_cinq_compteurs(self):
        u = LAB.unites()
        self.assertEqual(set(u), {"dx", "dy", "dz", "dz_brut", "dt"})
        for cle, valeur in u.items():
            self.assertEqual(Fraction(valeur, DEN), HOR.rationnaux()[cle], cle)

    def test_identite_dtn_se_tient_en_entiers(self):
        u = LAB.unites()
        self.assertEqual(u["dt"], u["dx"] + u["dy"] + u["dz"])
        self.assertEqual(u["dt"], 17_292_418_731)

    def test_conversion_refusee_si_l_echelle_derive(self):
        """Non-vacuité : le contrôle d'échelle de unites() n'est pas décoratif."""
        d = dict(LAB.HOR.rationnaux())
        d["dz"] = d["dz"] + Fraction(1, 256)          # hors du dénominateur commun
        self.addCleanup(setattr, LAB.HOR, "rationnaux", LAB.HOR.rationnaux)
        LAB.HOR.rationnaux = lambda: d
        with self.assertRaises(AssertionError):
            LAB.unites()


class TestFermeture(unittest.TestCase):
    """La trajectoire jouée pas à pas : x + y + z − k·dt, en entiers."""

    def test_residu_nul_a_chaque_pas(self):
        for pas in (1, 2, 7, 512, 4096):
            t = LAB.trajectoire(pas)
            self.assertEqual(t["residu_max_absolu"], 0, pas)
            self.assertEqual(t["residus_non_nuls"], 0, pas)
            self.assertEqual(t["pas"], pas)

    def test_periodes_d_axe_recalculees_par_pgcd(self):
        u, f = LAB.unites(), LAB.fermeture()
        for axe in ("dx", "dy", "dz"):
            self.assertEqual(f["periode_par_axe"][axe], u["dt"] // pgcd(u[axe], u["dt"]), axe)

    def test_fermeture_commune_egale_ppcm_des_axes(self):
        f = LAB.fermeture()
        commun = ppcm(*f["periode_par_axe"].values())
        self.assertEqual(f["periode_commune"], commun)
        self.assertEqual(f["periode_commune"], 640_459_953)
        self.assertEqual(f["dt_en_entiers"] // f["periode_commune"], 27)
        self.assertEqual(f["dt_en_entiers"] % f["periode_commune"], 0)

    def test_points_de_figure_sous_dt(self):
        """Le budget de points est tenu : la figure ne reçoit pas 100 000 sommets."""
        for pas in (7, 512, 1000, 4096, 100_000):
            t = LAB.trajectoire(pas, echantillons=512)
            dt = t["fermeture"]["dt_en_entiers"]
            self.assertLessEqual(len(t["points"]), 513, pas)
            self.assertGreaterEqual(len(t["points"]), 2, pas)
            for k, uu, vv, ww in t["points"]:
                self.assertGreaterEqual(k, 1)
                for v in (uu, vv, ww):
                    self.assertLessEqual(0, v)
                    self.assertLess(v, dt)

    def test_pas_negatif_refuse(self):
        with self.assertRaises(ValueError):
            LAB.trajectoire(0)


class TestRepere(unittest.TestCase):
    """Quatorze coordonnées nommées, aucune inventée."""

    def test_quatorze_coordonnees(self):
        rep = LAB.reperes()
        self.assertEqual(len(rep), 14)
        self.assertEqual([c["id"] for c in rep], list(range(1, 15)))
        self.assertEqual(len({c["nom"] for c in rep}), 14)

    def test_chaque_coordonnee_a_une_source_et_un_statut(self):
        for c in LAB.reperes():
            self.assertTrue(c["source"].strip(), c["nom"])
            self.assertIn(c["statut"], STATUTS_ADMIS, c["nom"])
            self.assertTrue(c["role"].strip(), c["nom"])

    def test_les_douze_nombres_du_depot_sont_les_bons(self):
        """Re-dérivation indépendante : le repère ne recopie pas le module, il dit la même chose."""
        r = HOR.rationnaux()
        rep = {c["nom"]: c for c in LAB.reperes()}
        for nom, cle in (("t", "dt"), ("x", "dx"), ("y", "dy"), ("z", "dz"),
                         ("z_brut", "dz_brut")):
            self.assertEqual(Fraction(rep[nom]["valeur"]), r[cle], nom)
        for ref in HOR.REFERENCES:
            self.assertIn(ref["id"], rep, ref["id"])
            self.assertEqual(Fraction(rep[ref["id"]]["valeur"]), Fraction(ref["jours"]), ref["id"])

    def test_l_hypothese_de_lecture_hertz_reste_specifiee(self):
        rep = {c["nom"]: c for c in LAB.reperes()}
        self.assertEqual(rep["1 / dt"]["statut"], "spécifié")
        self.assertNotIn("opérationnel", json.dumps(rep["1 / dt"], ensure_ascii=False))

    def test_tau_passe_de_simule_a_mesure_avec_la_machine(self):
        sans = {c["nom"]: c for c in LAB.reperes()}
        self.assertEqual(sans["tau"]["statut"], "simulé")
        faux = {"tau_mediane_ns": 900.0, "ratio_sur_specifie": 121.6, "fenetres": 3}
        avec = {c["nom"]: c for c in LAB.reperes(faux)}
        self.assertEqual(avec["tau"]["statut"], "mesuré")
        self.assertEqual(avec["tau"]["valeur"], "900.0000")
        self.assertEqual(avec["tau / (1 / dt)"]["valeur"], "121.6000")

    def test_le_repere_n_est_revendique_comme_dimension_physique(self):
        for c in LAB.reperes():
            self.assertNotIn("dimension", c["role"] + c["source"])
        self.assertIn("aucune dimension physique nouvelle", LAB.PORTEE_REPERE)


class TestInstrument(unittest.TestCase):
    """L'écart-type d'Allan, commencé sur une valeur faite à la main."""

    def test_adev_sur_suite_elementaire(self):
        # y = (0, 1) : un seul incrément de 1 → σ² = 1/(2·1) · 1 = 0,5
        self.assertAlmostEqual(LAB.adev([0.0, 1.0]), math.sqrt(0.5), places=12)
        # y = (1, 1, 1) : aucun incrément → σ = 0
        self.assertEqual(LAB.adev([1.0, 1.0, 1.0]), 0.0)

    def test_adev_refuse_une_seule_fenetre(self):
        with self.assertRaises(ValueError):
            LAB.adev([1.0])
        with self.assertRaises(ValueError):
            LAB.fenetres([1000.0])

    def test_fenetres_centre_reduit(self):
        y = LAB.fenetres([1000.0, 2000.0])
        self.assertEqual(sum(y), 0.0)
        self.assertAlmostEqual(y[0], -1 / 3, places=12)     # (1000 − 1500) / 1500
        self.assertAlmostEqual(y[1], 1 / 3, places=12)

    def test_instrument_retrouve_le_bruit_injecte(self):
        for graine in (20261109, 1, 7, 424242, 999983):
            s = LAB.simuler_horloge(pas=4000, eps=1e-3, graine=graine)
            self.assertTrue(s["recupere"], graine)
            self.assertLess(s["ecart_relatif"], 0.15, graine)

    def test_instrument_signale_un_bruit_faux(self):
        """Non-vacuité : l'intervalle vient de l'amplitude DECLARÉE, pas du nombre mesuré."""
        s = LAB.simuler_horloge(pas=4000, eps=0.05, graine=20261109)
        self.assertTrue(s["recupere"])
        fausse_declamation = LAB.bande_attendue(0.5, s["pas"])
        self.assertFalse(fausse_declamation["borne_basse"] <= s["adev_mesure"]
                         <= fausse_declamation["borne_haute"])
        inverse = LAB.bande_attendue(1e-3, s["pas"])
        self.assertFalse(inverse["borne_basse"] <= s["adev_mesure"] <= inverse["borne_haute"])

    def test_bande_attendue_calculee_a_part(self):
        b = LAB.bande_attendue(1e-3, 4000)
        self.assertAlmostEqual(b["relatif"], 5.0 / (2.0 * math.sqrt(3999)), places=12)
        self.assertAlmostEqual(b["borne_basse"] + b["borne_haute"], 2e-3, places=15)

    def test_simulation_refuse_des_bornes_absurdes(self):
        with self.assertRaises(ValueError):
            LAB.simuler_horloge(pas=10)
        with self.assertRaises(ValueError):
            LAB.simuler_horloge(eps=0.9)

    def test_simulation_est_reproductible_par_graine(self):
        a = LAB.simuler_horloge(pas=500, eps=2e-3, graine=1234)
        b = LAB.simuler_horloge(pas=500, eps=2e-3, graine=1234)
        self.assertEqual(a, b)


class TestControlesDuRapport(unittest.TestCase):
    """Le rapport complet, sur une machine quelconque : cinq contrôles, tous verts."""

    def test_cinq_controles_verts(self):
        r = LAB.laboratoire(pas=1000)
        self.assertEqual(r["nombre_controles"], 5)
        self.assertEqual(r["controles_verts"], 5)
        self.assertEqual(r["verdict"], "LABORATOIRE CONFORME")
        for c in r["controles"]:
            self.assertTrue(c["vrai"], c["id"])

    def test_un_controle_rouge_fait_basculer_le_verdict(self):
        """Non-vacuité du verdict : faux L01, et le rapport doit le dire nommément."""
        vrais = dict(trajectoire=LAB.trajectoire, simuler_horloge=LAB.simuler_horloge)
        self.addCleanup(lambda: [setattr(LAB, k, v) for k, v in vrais.items()])
        t = LAB.trajectoire(600)
        LAB.trajectoire = lambda *a, **k: {**t, "residus_non_nuls": 1}
        r = LAB.laboratoire(pas=600)
        self.assertEqual(r["verdict"], "LABORATOIRE EN DÉFAUT")
        self.assertEqual(r["controles_verts"], 4)
        self.assertEqual([c["id"] for c in r["controles"] if not c["vrai"]], ["L01"])

    def test_le_rapport_porte_les_limites_specifiques(self):
        r = LAB.laboratoire(pas=500)
        self.assertIn("aucune synchronisation physique", r["ce_que_ce_n_est_pas"])
        self.assertIn("convention de listing", r["portee_repere"])
        self.assertIsNone(r["stabilite_hote"])

    def test_aucun_chiffre_d_hote_dans_un_rapport_scelle(self):
        corps = json.dumps(LAB.laboratoire(pas=300), ensure_ascii=False, sort_keys=True)
        self.assertNotIn("perf_counter", corps)
        self.assertNotIn("platform", corps)


class TestOctetsEcrits(unittest.TestCase):
    """Les quatre livrables : format Excel français, et identiques d'une exécution à l'autre."""

    def test_csv_trajectoire_en_format_excel_francais(self):
        t = LAB.trajectoire(64)
        octets = LAB.octets_csv_trajectoire(t)
        self.assertTrue(octets.startswith(b"\xef\xbb\xbf"))
        self.assertNotIn(b"\n", octets.replace(b"\r\n", b""))
        lignes = octets.decode("utf-8-sig").splitlines()
        self.assertEqual(lignes[0], "k;u;v;w;u_sur_dt;v_sur_dt;w_sur_dt")
        self.assertEqual(len(lignes), 1 + len(t["points"]))
        self.assertIn(",", lignes[1].split(";")[4])

    def test_csv_stabilite_porte_les_grandeurs_et_les_statuts(self):
        octets = LAB.octets_csv_stabilite(LAB.simuler_horloge(pas=800, eps=2e-3, graine=5))
        lignes = octets.decode("utf-8-sig").splitlines()
        self.assertEqual(lignes[0], "grandeur;valeur;statut")
        tete = {l.split(";")[0] for l in lignes[1:]}
        for cle in ("pas", "eps_injecte", "adev_mesure", "graine", "recupere"):
            self.assertIn(cle, tete)
        self.assertIn("simulé", octets.decode("utf-8-sig"))

    def test_svg_trois_projections_et_aucun_texte_de_langue(self):
        octets = LAB.svg_trajectoire(LAB.trajectoire(256))
        texte = octets.decode("utf-8")
        self.assertTrue(texte.startswith("<svg xmlns="))
        self.assertEqual(texte.count("<polyline"), 3)
        for titre in ("(u/dt, v/dt)", "(u/dt, w/dt)", "(v/dt, w/dt)"):
            self.assertIn(titre, texte)
        self.assertFalse(any("؀" <= ch <= "ۿ" for ch in texte))

    def test_ecrire_produit_quatre_fichiers_non_vides_et_stables(self):
        r = LAB.laboratoire(pas=128)
        with tempfile.TemporaryDirectory() as tmp:
            chemins = LAB.ecrire(r, Path(tmp))
            self.assertEqual(len(chemins), 4)
            premier = {nom: p.read_bytes() for nom, p in ((n, Path(c))
                                                           for n, c in chemins.items())}
            for nom, octets in premier.items():
                self.assertGreater(len(octets), 40, nom)
            second = LAB.ecrire(LAB.laboratoire(pas=128), Path(tmp))
            for nom, chemin in second.items():
                self.assertEqual(Path(chemin).read_bytes(), premier[nom], nom)

    def test_ecrire_ne_scelle_aucun_nombre_d_hote(self):
        faux = {"fenetres": 3, "ticks_par_fenetre": 100, "tau_mediane_ns": 900.0,
                "tau_minimum_ns": 800.0, "tau_maximum_ns": 1000.0, "adev_relatif": 0.1,
                "ratio_sur_specifie": 121.6, "statut": "mesuré", "taus_ns": [800.0, 900.0, 1000.0]}
        r = LAB.laboratoire(pas=64, direct=faux)
        with tempfile.TemporaryDirectory() as tmp:
            chemin = Path(LAB.ecrire(r, Path(tmp))["json"])
            octets = chemin.read_bytes()
        corps = json.loads(octets.decode("utf-8"))
        self.assertIsNone(corps["stabilite_hote"])
        for trace in ("900.0000", "121.6000", '"taus_ns"', "ticks_par_fenetre"):
            self.assertNotIn(trace, octets.decode("utf-8"), trace)
        self.assertIn("n'entrent pas dans les octets scellés", corps["mesure_hote_ecrite"])
        self.assertEqual({c["nom"]: c["statut"] for c in corps["repere"] if c["nom"] == "tau"}
                         ["tau"], "simulé")


class TestLigneDeCommande(unittest.TestCase):
    """Les codes de sortie : 0 seulement quand le laboratoire est conforme."""

    def _lancer(self, *arguments: str) -> subprocess.CompletedProcess:
        return subprocess.run([sys.executable, "HORLOGERIE/laboratoire.py", *arguments],
                              cwd=RACINE_DEPOT, capture_output=True, text=True,
                              encoding="utf-8", timeout=300)

    def test_rc_zero_et_verdict(self):
        p = self._lancer("--pas", "256")
        self.assertEqual(p.returncode, 0, p.stderr[-400:])
        self.assertIn("LABORATOIRE CONFORME", p.stdout)
        self.assertIn("aucune dimension physique nouvelle", p.stdout)

    def test_json_integral_sort_sur_stdout(self):
        p = self._lancer("--pas", "128", "--json")
        self.assertEqual(p.returncode, 0, p.stderr[-400:])
        r = json.loads(p.stdout)
        self.assertEqual(len(r["repere"]), 14)
        self.assertEqual(r["trajectoire"]["residus_non_nuls"], 0)

    def test_en_direct_refuse_trop_petit(self):
        p = self._lancer("--en-direct", "--ticks", "10")
        self.assertNotEqual(p.returncode, 0)
        self.assertIn("bornes", p.stderr)


if __name__ == "__main__":
    unittest.main(verbosity=2)
