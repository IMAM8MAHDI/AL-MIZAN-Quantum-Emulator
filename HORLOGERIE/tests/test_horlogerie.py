# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2026 IMAM8MAHDI / Astro-Code Ecosystem
# SPDX-License-Identifier: GPL-3.0-only OR AGPL-3.0-only
"""Tests du dossier HORLOGERIE — ce que le certificat d'horloge tient, et ce qu'il ne tient pas.

Quatre exigences, dans l'ordre :
    1. les cinq nombres (dx, dy, dz, dz_brut, dt) sont re-dérivés ICI par une arithmétique
       écrite autrement que dans le module : aucune égalité n'est acceptée sur parole ;
    2. le vérificateur autonome est vert sur le fichier écrit, puis ROUGE sur des copies mutées
       et RESCELLÉES — re-sceller ne sauve pas une valeur fausse, et le contrôle censé voir la
       mutation est nommé précisément (non-vacuité) ;
    3. une référence citée depuis une autre ligne ne peut pas dériver en silence : l'identité
       12 × lunaison = lunaisons_12 et l'accord fraction ↔ décimale citée sont des contrôles,
       et la fraction fautive du 2026-11-09 (8 884 173/25 000) est testée comme refusée ;
    4. les verdicts astronomiques DÉFAVORABLES restent défavorables : un test qui les rendrait
       plus doux en retouchant le seuil est un test cassé, pas un module corrigé.

Stdlib uniquement pour le vérificateur ; le producteur, lui, importe le dépôt.
    cd ZENODO_DEPOT_ALMIZAN && py -3 -m unittest HORLOGERIE.tests.test_horlogerie -v
"""

import copy
import hashlib
import json
import math
import sys
import unittest
from decimal import getcontext
from fractions import Fraction
from pathlib import Path

RACINE_DEPOT = Path(__file__).resolve().parents[2]
if str(RACINE_DEPOT) not in sys.path:
    sys.path.insert(0, str(RACINE_DEPOT))

from HORLOGERIE import horlogerie as HOR                                    # noqa: E402
from HORLOGERIE import verifier_certificats as VER                          # noqa: E402
from HORLOGERIE import calibrer_horloge_almizan as CAL                      # noqa: E402

CERT = HOR.certificat()          # déterministe : aucun nombre d'hôte n'y entre
REFS = {r["id"]: r for r in HOR.REFERENCES}

# Le certificat scelle l'arithmétique ; la mesure de rythme, elle, sort à part. Les équations
# qui parlent de τ sont donc jouées avec une mesure fictive : ce test ne dépend d'aucun hôte.
MESURE_FICTIVE = {"tau_mediane_ns": 900.0, "tau_min_ns": 880.0, "tau_max_ns": 1_100.0,
                  "tau_eam_ns": 12.0, "serie_de": 5_000, "series": 5,
                  "periode_hypothetique_ns": CERT["periode"]["flottant"],
                  "ratio_tau_sur_periode": 900.0 / CERT["periode"]["flottant"],
                  "verdict_mesure": "LECTURE HERTZ RÉFUTÉE SUR CETTE MACHINE",
                  "hote": {"systeme": "test", "python": "test", "processeur": "test"},
                  "formule": "tau = T / N", "portee": "mesuré · dépend du matériel"}


def resceller(cert: dict) -> dict:
    """Recalcule empreintes, englobe et racine : la mutation survit au re-scelllement."""
    empreintes = {c: hashlib.sha256(HOR.canonique(cert[c])).hexdigest()
                  for c in VER.CLES_SOUS_CERTIFICAT}
    cert["empreintes_souche"] = empreintes
    cert["englobe"] = sorted(empreintes)
    cert["racine_merkle_sha256"] = hashlib.sha256(HOR.canonique(empreintes)).hexdigest()
    return cert


def echoues(cert: dict) -> set:
    return {x["id"] for x in VER.verifier(cert) if not x["ok"]}


class TestArithmetiqueReEcriteIci(unittest.TestCase):
    """Les cinq nombres tombent sur des rationnels précis, par une voie de calcul différente."""

    def test_dx_et_dy_par_produits_de_fractions(self):
        dx = (Fraction(5, 2) * Fraction(8766, 12)) * (Fraction(3, 2) * Fraction(1461, 2) / 168) \
             * (Fraction(3, 2) * Fraction(168, 24)) * Fraction(24, 60)
        dy = (Fraction(5, 2) * Fraction(8496, 12)) * (Fraction(3, 2) * Fraction(708, 168)) \
             * (Fraction(3, 2) * Fraction(168, 24)) * Fraction(24, 60)
        self.assertEqual((dx.numerator, dx.denominator), (6_403_563, 128))
        self.assertEqual((dy.numerator, dy.denominator), (93_987, 2))
        self.assertEqual(float(dx), 50_027.8359375)
        self.assertEqual(float(dy), 46_993.5)

    def test_dz_dz_brut_et_dt(self):
        dz = Fraction(216_000) * 250 * Fraction(5, 2)
        brut = (Fraction(300 * 8640, 12) * Fraction(50 * 720, 144)
                * Fraction(30 * 144, 24) * Fraction(24, 60))
        self.assertEqual(dz, 135_000_000)
        self.assertEqual(brut, 3_888_000_000)
        self.assertEqual(brut / dz, Fraction(144, 5))
        self.assertEqual(HOR.rationnaux()["dt"], Fraction(17_292_418_731, 128))
        self.assertEqual(Fraction(17_292_418_731, 128), 135_097_021 + Fraction(43, 128))

    def test_le_certificat_porte_les_memes_nombres(self):
        for nom, attendu in (("dx", Fraction(6_403_563, 128)), ("dy", Fraction(93_987, 2)),
                             ("dz", Fraction(135_000_000)),
                             ("dz_brut", Fraction(3_888_000_000)),
                             ("dt", Fraction(17_292_418_731, 128))):
            v = CERT["rationnels"][nom]
            with self.subTest(nombre=nom):
                self.assertEqual(Fraction(v["numerateur"], v["denominateur"]), attendu)
                self.assertEqual(v["flottant"], repr(float(attendu)))
                self.assertTrue(v["reduit"])

    def test_identites_toutes_vraies_et_le_produit_croise_ecrit(self):
        for identite in CERT["identites"]:
            with self.subTest(identite=identite["id"]):
                self.assertTrue(identite["vraie"])
        somme = next(i for i in CERT["identites"] if i["id"] == "somme")
        self.assertEqual(somme["second_membre"], "17292418731/128")
        self.assertEqual(somme["produit_croise"].count("17292418731"), 2)
        self.assertTrue(somme["produit_croise"].endswith("2213429597568"))

    def test_denominateur_minimal_et_periode_sur_quarante_rangs(self):
        dt = Fraction(17_292_418_731, 128)
        self.assertEqual(dt.denominator, 2 ** 7)
        self.assertEqual(dt.numerator % 2, 1)
        self.assertEqual(math.gcd(dt.numerator, dt.denominator), 1)
        getcontext().prec = 60
        self.assertEqual(CERT["periode"]["valeur_ns"][:12], "7.4020877004")
        self.assertEqual(len(CERT["periode"]["valeur_ns"].replace(".", "")), HOR.PRECISION)
        self.assertEqual(Fraction(CERT["periode"]["fraction"]) * dt, 10 ** 9)


class TestGardeDesSourcesCitees(unittest.TestCase):
    """Une valeur citée depuis une autre ligne doit rester cohérente avec sa source."""

    def test_douze_lunaisons_egal_douze_fois_le_mois_synodique(self):
        self.assertEqual(VER.F(REFS["lunaisons_12"]["jours"]),
                         12 * VER.F(REFS["lunaison"]["jours"]))

    def test_chaque_fraction_rend_la_decimale_citee(self):
        for ref in HOR.REFERENCES:
            with self.subTest(reference=ref["id"]):
                self.assertEqual(VER.F(ref["jours"]), VER.D(ref["decite"]))

    def test_la_copie_fautive_du_2026_11_09_est_refusee_meme_rescellee(self):
        fautive = Fraction(8_884_173, 25_000)          # 355,36692 : écrit une fois par erreur
        self.assertNotEqual(fautive, 12 * VER.F(REFS["lunaison"]["jours"]))
        mutile = copy.deepcopy(CERT)
        for r in mutile["astronomie"]["references"]:
            if r["id"] == "lunaisons_12":
                r["jours"] = f"{fautive.numerator}/{fautive.denominator}"
                r["decite"] = "355,36692"
        rendu = echoues(resceller(mutile))
        self.assertNotIn("V02", rendu, "re-scellé, le scellement devrait passer")
        self.assertIn("V16", rendu)

    def test_ecarter_une_decimale_de_sa_source_seul_suffit_a_faire_tomber_v16(self):
        mute = copy.deepcopy(CERT)
        for r in mute["astronomie"]["references"]:
            if r["id"] == "lunaison":
                r["decite"] = "29,5306"                # la fraction reste, la citation bouge
        self.assertIn("V16", echoues(resceller(mute)))

    def test_lecart_lunaire_reel_vaut_environ_huit_heures_quarante_neuf_minutes(self):
        e = (Fraction(354) - VER.F(REFS["lunaisons_12"]["jours"])) * 86400
        self.assertEqual(e, Fraction(-3_964_464, 125))
        self.assertAlmostEqual(abs(float(e)) / 3600, 8.810, places=3)
        self.assertEqual(round(abs(float(e))), 31_716)          # ≈ 8 h 49 min par an


class TestVerificateurAutonome(unittest.TestCase):
    """Le vérificateur ne doit rien au dépôt : ni import, ni exécution de ses modules."""

    def test_aucun_import_du_depot(self):
        rendu = VER.imports_de(HOR.VERIFICATEUR)
        self.assertEqual(rendu["autres"], [])
        self.assertTrue(rendu["stdlib"])
        self.assertNotIn("bibliotheques", rendu["autres"] + rendu["stdlib"])

    def test_une_cle_manquante_courtcircuite_la_lecture(self):
        for cle in VER.CLES_SOUS_CERTIFICAT:
            mute = copy.deepcopy(CERT)
            mute.pop(cle)
            with self.subTest(cle=cle):
                rendu = VER.verifier(mute)
                self.assertEqual(len(rendu), 1)
                self.assertEqual(rendu[0]["id"], "V01")
                self.assertFalse(rendu[0]["ok"])

    def test_mutation_par_mutation_le_controle_nomme_tombe_apres_rescelllement(self):
        # rescelle=False : la mutation EST le scellement, le recalculer l'effacerait.
        cas = [
            ("numerateur de dx +1", lambda c: c["rationnels"]["dx"].__setitem__(
                "numerateur", CERT["rationnels"]["dx"]["numerateur"] + 1), {"V04", "V05"}, True),
            ("semence du soleil 8765 h", lambda c: c["derivation"]["semences"]["soleil"]
                .__setitem__("annee_h", "8765"), {"V04"}, True),
            ("racine recopiée fausse", lambda c: c.__setitem__("racine_merkle_sha256", "0" * 64),
             {"V03"}, False),
            ("empreinte d'un sous-certificat écrasée", lambda c: c["empreintes_souche"]
                .__setitem__("unites", "0" * 64), {"V02"}, False),
            ("seuil conforme porté à 10 000 s/an", lambda c: c["astronomie"]["seuils"]
                .__setitem__("conforme_s_par_an", 10_000), {"V11"}, True),
            ("verdict d'une paire réécrit à la main", lambda c: c["astronomie"]["resultats"][1]
                .__setitem__("verdict", "CONFORME"), {"V11"}, True),
            ("écart d'une paire récrit à la main", lambda c: c["astronomie"]["resultats"][2]
                .__setitem__("ecart_s_par_an", "1/1"), {"V10"}, True),
            ("verdict d'un cycle adouci", lambda c: c["astronomie"]["par_cycle"]["Terre"]
                .__setitem__("verdict", "CONFORME"), {"V12"}, True),
            ("variante de sensibilité remplacée par la valeur de référence",
             lambda c: c["astronomie"]["sensibilite"].__setitem__(
                 "lunaison_alternee", REFS["lunaison"]["jours"]), {"V13"}, True),
            ("deux limites effacées", lambda c: c.__setitem__("limites", CERT["limites"][:2]),
             {"V15"}, True),
            ("période tronquée d'un rang", lambda c: c["periode"].__setitem__(
                "valeur_ns", CERT["periode"]["valeur_ns"][:-1]), {"V09"}, True),
            ("unité retenue vidée", lambda c: c["unites"].__setitem__("lecture_retenue", ""),
             {"V14"}, True),
        ]
        for nom, muter, attendus, rescelle in cas:
            mute = copy.deepcopy(CERT)
            muter(mute)
            rendu = echoues(resceller(mute) if rescelle else mute)
            with self.subTest(cas=nom):
                self.assertTrue(attendus <= rendu, f"{nom} : manque {sorted(attendus - rendu)}")

    def test_resceller_une_copie_fidele_ne_rienne_change(self):
        self.assertEqual(echoues(resceller(copy.deepcopy(CERT))), set())


class TestCertificatEcrit(unittest.TestCase):
    """Le fichier du dossier, tel qu'il est sur disque, doit se relire vert."""

    def test_fichier_present_conforme_et_octet_pour_octet_reproductible(self):
        self.assertTrue(HOR.CERTIFICAT.exists(),
                        "lancer d'abord : py -3 HORLOGERIE/horlogerie.py --ecrit")
        sur_disque = json.loads(HOR.CERTIFICAT.read_text(encoding="utf-8"))
        self.assertEqual([x["id"] for x in VER.verifier(sur_disque) if not x["ok"]], [])
        self.assertEqual(sur_disque["racine_merkle_sha256"], CERT["racine_merkle_sha256"])
        self.assertEqual(HOR.octets_certificat(CERT), HOR.CERTIFICAT.read_bytes(),
                         "le fichier écrit n'est pas ce que le module produit : non déterministe")

    def test_le_certificat_ne_contient_aucun_nombre_d_hote(self):
        blob = json.dumps(CERT, ensure_ascii=False, sort_keys=True)
        for cle in ("mediane", "tau_", "hote", "perf_counter"):
            self.assertNotIn(cle, blob, f"{cle} : une mesure d'hôte est entrée dans le scellé")

    def test_csv_francais_octets_pour_octets(self):
        octets = HOR.octets_csv_astro(CERT["astronomie"])
        self.assertTrue(octets.startswith(b"\xef\xbb\xbf"))
        self.assertEqual(octets.count(b"\n"), octets.count(b"\r\n"))
        self.assertEqual(octets, HOR.CSV_ASTRO.read_bytes())
        lignes = octets.decode("utf-8-sig").splitlines()
        self.assertEqual(len(lignes), 1 + len(HOR.PAIRES))
        self.assertEqual(lignes[0], "cycle;reference;nature;declare_jours;reference_jours;"
                                    "ecart_s_an;verdict")
        champ = lignes[1].split(";")[5]
        self.assertNotIn(".", champ)
        self.assertIn(",", champ)


class TestVerdictsDefavorablesConserves(unittest.TestCase):
    """Les verdicts qui font mal à AL-MIZAN sont testés comme malfaits, pas recalibrés."""

    def test_terre_et_lune_hors_tolerance_soleil_signale(self):
        par = CERT["astronomie"]["par_cycle"]
        self.assertEqual(par["Terre"]["verdict"], "HORS TOLÉRANCE")
        self.assertEqual(par["Lune"]["verdict"], "HORS TOLÉRANCE")
        self.assertEqual(par["Soleil"]["verdict"], "ÉCART SIGNALÉ")

    def test_aucune_des_six_ephemerides_mesurees_ne_passe_sous_les_soixante_secondes(self):
        mesures = [x for x in CERT["astronomie"]["resultats"]
                   if x["nature_reference"] == "éphéméride mesurée"]
        self.assertEqual(len(mesures), 6)
        self.assertTrue(all(x["verdict"] != "CONFORME" for x in mesures))
        self.assertTrue(all(abs(x["ecart_s_arrondi"]) > 600 for x in mesures))

    def test_les_deux_conformes_sont_des_calendriers_nommes_comme_tels(self):
        conformes = {(x["cycle"], x["reference"]) for x in CERT["astronomie"]["resultats"]
                     if x["verdict"] == "CONFORME"}
        self.assertEqual(conformes, {("Soleil", "annee_julienne"),
                                     ("Lune", "annee_lunaire_civile")})
        for _, reference in conformes:
            self.assertIn(REFS[reference]["nature"],
                          ("définition exacte", "convention de calendrier"))

    def test_le_verdict_par_cycle_est_le_pire_de_ses_paires(self):
        pire = {"CONFORME": 0, "ÉCART SIGNALÉ": 1, "HORS TOLÉRANCE": 2}
        astro = CERT["astronomie"]
        for cycle in astro["par_cycle"]:
            siennes = [x["verdict"] for x in astro["resultats"] if x["cycle"] == cycle]
            with self.subTest(cycle=cycle):
                self.assertEqual(astro["par_cycle"][cycle]["verdict"],
                                 max(siennes, key=lambda v: pire[v]))

    def test_neuf_paires_gelees_sur_six_references(self):
        astro = CERT["astronomie"]
        self.assertEqual(len(astro["paires"]), 9)
        self.assertEqual(len(astro["references"]), 6)
        self.assertEqual(len(astro["empreinte_du_gel"]), 64)
        self.assertLess(VER.F(astro["seuils"]["conforme_s_par_an"]),
                        VER.F(astro["seuils"]["signale_s_par_an"]))


class TestMesureDeRythme(unittest.TestCase):
    """τ est une mesure bornée et déclarée comme telle, jamais une constante."""

    def test_bornes_et_portee_declaree(self):
        m = CAL.mesurer(ticks=400, series=3)
        self.assertLessEqual(m["minimum_ns"], m["mediane_ns"])
        self.assertLessEqual(m["mediane_ns"], m["maximum_ns"])
        self.assertGreater(m["mediane_ns"], 0)
        self.assertEqual(len(m["echantillons"]), 3)
        self.assertEqual(m["ticks_par_serie"], 400)
        self.assertIn("dépend du matériel", m["portee"])

    def test_le_tour_complet_du_budget_est_positive_et_en_secondes(self):
        m = CAL.mesurer(ticks=400, series=3)
        self.assertGreater(m["tour_complet_du_budget_s"], 0)
        self.assertAlmostEqual(m["tour_complet_du_budget_s"],
                               m["budget_kernel_dt"] * m["mediane_ns"] * 1e-9, places=3)

    def test_le_cli_refuse_un_echantillon_trop_petit(self):
        argv = list(sys.argv)
        try:
            for options in (["--ticks", "10", "--series", "7"],
                            ["--ticks", "1000", "--series", "2"]):
                sys.argv = ["calibrer_horloge_almizan.py"] + options
                with self.subTest(options=options):
                    self.assertEqual(CAL.main(), 2)
        finally:
            sys.argv = argv


class TestPiliersEtLimites(unittest.TestCase):
    """Le dossier se range sous les mêmes piliers que FONDATION et CHIFFRES."""

    def equations(self):
        return HOR.equations(CERT, MESURE_FICTIVE)

    def controles(self):
        return HOR.controles({x["id"]: x for x in self.equations()}, CERT, MESURE_FICTIVE)

    def test_quinze_equations_puis_quinze_controles_sans_trou_ni_doublon(self):
        self.assertEqual([x["id"] for x in self.equations()],
                         [f"EQ-{i:02d}" for i in range(1, 16)])
        self.assertEqual([x["id"] for x in self.controles()],
                         [f"C{i:02d}" for i in range(1, 16)])

    def test_statut_limite_et_chemin_sur_toutes_les_equations(self):
        for x in self.equations():
            with self.subTest(equation=x["id"]):
                self.assertIn(x["statut"], ("OPÉRATIONNEL", "SIMULÉ", "SPÉCIFIÉ"))
                self.assertGreaterEqual(len(x["limite"]), 40)
                self.assertIn("→", x["chemin"])
                self.assertTrue(x["piliers"])
                self.assertTrue(x["resultat"])

    def test_controles_verts_attendu_obtenu_non_vides(self):
        for c in self.controles():
            with self.subTest(controle=c["id"]):
                self.assertTrue(c["attendu"].strip())
                self.assertTrue(c["obtenu"].strip())
                self.assertIsInstance(c["ok"], bool)
        self.assertTrue(all(c["ok"] for c in self.controles()),
                        "tous les contrôles doivent être verts sur cet dépôt")

    def test_les_limites_du_certificat_sont_nombres_et_serieuses(self):
        self.assertGreaterEqual(len(CERT["limites"]), 3)
        for limite in CERT["limites"]:
            self.assertGreaterEqual(len(limite), 40)

    def test_attribution_de_la_video_sans_transcript_invente(self):
        src = CERT["attribution"]
        self.assertEqual(src["video_id"], "qa8IsnneG0c")
        self.assertEqual(len(src["chapitres_verbatims"]), src["chapitres_publics"])
        self.assertEqual(src["duree_s"], 593)
        self.assertIn("absent", src["transcript"])
        dernier = src["chapitres_verbatims"][-1]["debut"]
        minutes, secondes = (int(v) for v in dernier.split(":"))
        self.assertLessEqual(minutes * 60 + secondes, src["duree_s"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
