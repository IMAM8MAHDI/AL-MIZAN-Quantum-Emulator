# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2026 IMAM8MAHDI / Astro-Code Ecosystem
# SPDX-License-Identifier: GPL-3.0-only OR AGPL-3.0-only
"""Tests du dossier CHIFFRES — décimales certifiées de π, e, √2 et loi des 0,9.

Trois exigences, dans l'ordre :
    1. ce qui est annoncé comme démontré l'est par une inégalité entière re-vérifiée ici ;
    2. ce qui est annoncé comme prédit ne dépend d'AUCUN chiffre — les tests le reprouvent
       en recalculant la table autrement ;
    3. la règle de rejet n'est pas décorative : une chaîne fabriquée pour la violer se
       fait exclure (test_non_vacuite_regle_de_rejet).

Stdlib uniquement. Domaine court : rien ici ne demande les 10⁶ décimales.
    cd CHIFFRES && py -3 -m unittest tests.test_chiffres -v
"""

import json
import math
import sys
import tempfile
import unittest
from collections import Counter
from fractions import Fraction
from pathlib import Path

RACINE_DOSSIER = Path(__file__).resolve().parent.parent
if str(RACINE_DOSSIER) not in sys.path:
    sys.path.insert(0, str(RACINE_DOSSIER))

import generer_chiffres as GEN                                          # noqa: E402
import chiffres_pi as CH                                                # noqa: E402


class TestCertificatsDeChiffres(unittest.TestCase):
    """Ce que le module appelle certifié doit tenir sur une inégalité entière relue ici."""

    PREFIXES = {
        "pi": "14159265358979323846264338327950288419716939937510",
        "e": "71828182845904523536028747135266249775724709369995",
        "racine2": "41421356237309504880168872420969807856967187537694",
    }

    def test_prefixes_publies(self):
        for constante, attendu in self.PREFIXES.items():
            rendu = GEN.decimales(constante, len(attendu))["chiffres"]
            self.assertEqual(rendu, attendu, f"{constante} ne rend pas ses décimales publiées")

    def test_reference_du_module_et_prefixes(self):
        """CHIFFRES_DE_REFERENCE n'est pas décoratif : C01 le compare vraiment."""
        self.assertEqual(set(CH.CHIFFRES_DE_REFERENCE), set(CH.CONSTANTES))
        for constante, attendu in self.PREFIXES.items():
            self.assertEqual(CH.CHIFFRES_DE_REFERENCE[constante], attendu)
        for constante in CH.CONSTANTES:
            chaine = GEN.decimales(constante, 80)["chiffres"]
            ancre = CH.ancre_publiee(chaine, CH.CHIFFRES_DE_REFERENCE[constante])
            self.assertTrue(ancre["identique"] and ancre["ancre_complete"], constante)
            self.assertEqual(ancre["chiffres_comparables"], CH.LONGUEUR_ANCRE)
            self.assertIsNone(ancre["premier_desaccord"])
            # une référence faussée d'un seul chiffre doit être vue à la bonne place
            fake = CH.CHIFFRES_DE_REFERENCE[constante][:20] + \
                ("4" if CH.CHIFFRES_DE_REFERENCE[constante][20] != "4" else "5") + \
                CH.CHIFFRES_DE_REFERENCE[constante][21:]
            percut = CH.ancre_publiee(chaine, fake)
            self.assertFalse(percut["identique"], f"{constante} : ancre faussée non vue")
            self.assertEqual(percut["premier_desaccord"], 20)

    def test_ancre_racine2_par_decimal(self):
        """Troisième voie, hors du dossier : √2 par la racine décimal correcte."""
        from decimal import Decimal, getcontext
        getcontext().prec = 70
        dec = str(Decimal(2).sqrt()).split(".")[1][:60]
        self.assertEqual(dec, GEN.decimales("racine2", 60)["chiffres"][:60])
        self.assertEqual(dec[:50], self.PREFIXES["racine2"])
        self.assertEqual(dec[:50], CH.CHIFFRES_DE_REFERENCE["racine2"])

    def test_certificat_vrai_et_marge_de_garde(self):
        for constante in CH.CONSTANTES:
            d = GEN.decimales(constante, 600)
            self.assertTrue(d["certifie"], f"{constante} : encadrement non certifié")
            self.assertEqual(len(d["chiffres"]), 600)
            self.assertEqual(d["n"], 600)
            self.assertTrue(all("0" <= c <= "9" for c in d["chiffres"]))
            self.assertTrue(0 <= d["marge_chiffres"] <= GEN.GARDE,
                            f"{constante} : garde hors de l'intervalle déclaré")
            # chaque constante a sa propre clé de preuve : aucune ne manque
            if constante == "pi":
                self.assertTrue(d["alternance_valide"] and d["contraction_valide"])
                self.assertGreaterEqual(d["marge_chiffres"], 1)
            elif constante == "e":
                self.assertTrue(d["factorielle_egale"])
                self.assertGreaterEqual(d["marge_chiffres"], 1)
            else:
                self.assertEqual(d["preuve"], "w² ≤ 2·10^(2n) < (w+1)²")
                # l'encadrement de √2 est un seul entier : largeur 1, donc garde 0
                self.assertEqual(d["marge_chiffres"], 0)

    def test_deux_voies_independantes_sur_500_chiffres(self):
        croise = GEN.croiser(500)
        for constante in CH.CONSTANTES:
            cel = croise[constante]
            self.assertTrue(cel["identique"], f"{constante} : les deux voies divergent")
            self.assertIsNone(cel["premier_desaccord"])
            self.assertTrue(cel["certifie_1"] and cel["certifie_2"])

    def test_ratios_chudnovsky_exactes(self):
        ratios = GEN.ratios_chudnovsky(4)
        self.assertTrue(ratios["tout_inferieur_a_un"])
        self.assertTrue(ratios["borne_inferieure_a_un"])
        self.assertGreater(ratios["ratio_max"], 0.0)
        self.assertLess(ratios["ratio_max"], ratios["borne_fermee"])
        self.assertLess(ratios["borne_fermee"], 1.0)
        # la borne fermée se recalcule à la main : 1728·(A+B)/(A·C³)
        attendu = 1728 * (GEN.A_CHUD + GEN.B_CHUD) / (GEN.A_CHUD * GEN.C_CHUD ** 3)
        self.assertAlmostEqual(ratios["borne_fermee"], attendu, places=20)


class TestLoisSansDonnee(unittest.TestCase):
    """Les lois ne reçoivent que des entiers : elles doivent se reproduire à l'identique."""

    def test_algebre_du_neuf_dixiemes(self):
        for k in range(1, 13):
            self.assertEqual(CH.esperance_auto_local(10 ** k + k, k), Fraction(9, 10),
                             f"classe {k} : 9·10^(k−1)·10^(−k) ne fait pas 9/10")
        self.assertTrue(CH.algebre_0_9()["toutes_egales_9_dixiemes"])

    def test_predire_ne_lit_aucun_chiffre(self):
        une = CH.predire(5000)
        deux = CH.predire(5000)
        self.assertEqual(une, deux, "la table annoncée n'est pas reproductible")
        self.assertEqual(une["regles"]["cellules_total"],
                         3 * (10 + 1 + CH.KMAX + 1 + CH.RMAX
                              + len(CH.K_OCCULENCE) + len(CH.SONDES)))
        self.assertEqual(une["regles"]["cellules_total"], 108)
        zero = CH.predire(0)
        self.assertEqual(zero["regles"]["cellules_total"], 108,
                         "la table doit rester définie à n = 0")
        self.assertEqual(zero["auto_local"]["total_attendu"], 0.0)

    def test_candidats_de_classe(self):
        self.assertEqual(CH.candidats_classe(100_005, 5), 90_000)
        self.assertEqual(CH.candidats_classe(20_000, 5), 9_997)
        self.assertEqual(CH.candidats_classe(10, 6), 0)
        for k in (1, 2, 3, 6):
            self.assertEqual(CH.candidats_classe(10 ** 7, k), 9 * 10 ** (k - 1))

    def test_inversion_normale_bilate_re(self):
        for p in (0.5, 0.05, 0.001, 3.33e-5, 1e-9):
            z = CH.z_de_p_bilatere(p)
            self.assertAlmostEqual(CH.p_bilatere_normale(z), p, delta=p * 1e-9)
        self.assertAlmostEqual(CH.z_de_p_bilatere(0.05), 1.959963985, places=6)
        self.assertEqual(CH.p_bilatere_normale(0.0), 1.0)
        with self.assertRaises(ValueError):
            CH.z_de_p_bilatere(0.0)

    def test_poisson_et_bernoulli_bilateres(self):
        self.assertEqual(CH.p_bilatere_poisson(0.0, 0), 1.0)
        self.assertEqual(CH.p_bilatere_poisson(0.0, 3), 0.0)
        self.assertAlmostEqual(CH.p_bilatere_compte(0.9, 1),
                               min(1.0, 2.0 * min(math.exp(-0.9) * 1.9, 1.0 - math.exp(-0.9))),
                               places=12)
        # grande λ : la branche normale doit rester bornée et décroissante en |écart|
        self.assertGreater(CH.p_bilatere_compte(81_000.0, 81_000), 0.99)
        self.assertLess(CH.p_bilatere_compte(81_000.0, 82_500), 1e-6)
        self.assertLess(CH.p_bilatere_compte(81_000.0, 82_500),
                        CH.p_bilatere_compte(81_000.0, 81_500))
        self.assertEqual(CH.p_bilatere_bernoulli(1e-6, False), 1.0)
        self.assertAlmostEqual(CH.p_bilatere_bernoulli(1e-6, True), 2e-6, places=12)

    def test_intervalle_chi2_recalcule_autrement(self):
        for df in (9, 18):
            bas, haut = CH.chi2_intervalle(df)
            self.assertLess(bas, df)
            self.assertLess(df, haut)
            z = _z_bilate_par_bissection(0.001)
            b = 2.0 / (9.0 * df)
            self.assertAlmostEqual(bas, df * (1 - b - z * math.sqrt(b)) ** 3, places=9)
            self.assertAlmostEqual(haut, df * (1 - b + z * math.sqrt(b)) ** 3, places=9)

    def test_attente_geometrique(self):
        loi = CH.loi_attente_geometrique(5, 20_000)
        # 1/p en flottant : 99999.99999999999, pas 1e5 — la comparaison est tolérante
        self.assertAlmostEqual(loi["moyenne_inconditionnelle"], 1e5, delta=1e-5)
        self.assertEqual(loi["fenetres"], 19_996)
        self.assertLess(loi["probabilite_de_presence"], 0.2)
        self.assertGreater(loi["quantile_de_rejet"], 0.0)
        self.assertIsNone(CH.percentile_attendu(None, 5))


def _z_bilate_par_bissection(p):
    """Seuil normal bilatère recalculé sans appeler z_de_p_bilatere — voie indépendante."""
    bas, haut = 0.0, 40.0
    for _ in range(200):
        milieu = 0.5 * (bas + haut)
        if math.erfc(milieu / math.sqrt(2.0)) > p:
            bas = milieu
        else:
            haut = milieu
    return 0.5 * (bas + haut)


class TestMesuresReCalculees(unittest.TestCase):
    """Chaque primitive de mesure est confrontée à une re-écriture naïve, sur chaîne fixe."""

    CHAINE = (GEN.decimales("pi", 4000)["chiffres"]
              + GEN.decimales("e", 4000)["chiffres"][:1000])

    def test_frequence_contre_counter(self):
        compte = CH.mesurer_frequence(self.CHAINE)
        self.assertEqual(sum(compte), len(self.CHAINE))
        self.assertEqual(compte, [Counter(self.CHAINE)[str(d)] for d in range(10)])

    def test_positions_auto_local_contre_balayage_naif(self):
        attendues = [p for p in range(1, len(self.CHAINE) + 1)
                     if self.CHAINE[p - 1:p - 1 + len(str(p))] == str(p)]
        self.assertEqual(CH.positions_auto_local(self.CHAINE), sorted(attendues))
        self.assertTrue(CH.verifier_auto_local(self.CHAINE, attendues))

    def test_runs_contre_decoupage_naif(self):
        mesure = CH.mesurer_runs(self.CHAINE, 7)
        naive = Counter()
        i = 0
        while i < len(self.CHAINE):
            j = i
            while j < len(self.CHAINE) and self.CHAINE[j] == self.CHAINE[i]:
                j += 1
            naive[j - i] += 1
            i = j
        self.assertEqual(sum(naive.values()), 1 + sum(1 for a, b in
                         zip(self.CHAINE, self.CHAINE[1:]) if a != b))
        for r in range(1, 8):
            self.assertEqual(mesure[r], naive[r], f"run de longueur {r}")

    def test_occulence_contre_ensemble(self):
        for k in (1, 2, 3, 4):
            vue = CH.mesurer_occulence(self.CHAINE, [k])[k]
            self.assertEqual(vue, len({self.CHAINE[i:i + k]
                                       for i in range(len(self.CHAINE) - k + 1)}))

    def test_attentes_contre_find(self):
        mesures = CH.mesurer_attentes(self.CHAINE)
        for sonde, position in mesures.items():
            indice = self.CHAINE.find(sonde)
            self.assertEqual(position, None if indice < 0 else indice + 1)

    def test_point_de_feynman_et_position_16470(self):
        pi = GEN.decimales("pi", 20_000)["chiffres"]
        self.assertEqual(pi[0], "1", "la position 1 est la première décimale")
        self.assertEqual(int(pi[16469:16474]), 16470,
                         "16470 ne se relit pas à sa place dans π (question de la vidéo)")
        self.assertIn(16470, CH.positions_auto_local(pi))
        self.assertEqual(CH.mesurer_attentes(pi)["999999"], 762, "point de Feynman")


class TestNonVacuite(unittest.TestCase):
    """Une règle qui ne peut rien exclure ne prédit rien : on la met à l'épreuve."""

    def _confronter(self, chaine):
        pred = CH.predire(len(chaine))
        mesures = {c: CH.mesurer(chaine) for c in CH.CONSTANTES}
        cal = CH.calibrage(2_000, 1_000, 60, 30, CH.GRAINE)
        return CH.confronter(pred, mesures, cal)

    def test_chiffre_surrepresente_exclut_la_cellule(self):
        tranchee = GEN.decimales("pi", 20_000)["chiffres"]
        biaissee = ("7" * 1_400) + tranchee[1_400:]        # 8 % de « 7 » de plus
        conf = self._confronter(biaissee)
        self.assertIn("pi.frequence.7", conf["exclues"],
                      "la règle de rejet n'a rien vu sur un biais évident")

    def test_classe_auto_local_saturee_exclut(self):
        tranchee = list(GEN.decimales("pi", 20_000)["chiffres"])
        # pas à 5 : deux positions auto-localisées de classe 5 qui se touchent se
        # contredisent chiffres à chiffres, un adjacent ne peut donc jamais compter
        for p in range(10_000, 10_050, 5):
            for j, c in enumerate(str(p)):
                tranchee[p - 1 + j] = c
        fabrique = [p for p in range(10_000, 10_050, 5)]
        conf = self._confronter("".join(tranchee))
        self.assertTrue(all("".join(tranchee)[p - 1:p - 1 + 5] == str(p) for p in fabrique),
                        "la fabrication elle-même n'a pas tenu")
        self.assertTrue(any(nom.endswith("auto_local.k5") for nom in conf["exclues"]),
                        "la sur-abondance de classe 5 passe inaperçue")

    def test_grande_lambda_en_branche_normale(self):
        self.assertGreater(CH.p_bilatere_compte(1620.0, 1619.0), 0.9)
        self.assertLess(CH.p_bilatere_compte(1620.0, 1400.0), 1e-6)


class TestDossierComplet(unittest.TestCase):
    """Le dossier entier, tel qu'il est publié : 17 équations, 17 contrôles, 108 cellules."""

    @classmethod
    def setUpClass(cls):
        cls.donnees = CH.resoudre(CH.N_COURT)

    def test_dix_sept_controles_verts(self):
        ids = [c["id"] for c in self.donnees["controles"]]
        self.assertEqual(ids, [f"C{i:02d}" for i in range(1, 18)])
        for controle in self.donnees["controles"]:
            self.assertTrue(controle["ok"],
                            f"{controle['id']} FAIL : {controle['attendu']} / {controle['obtenu']}")

    def test_equations_couvrent_les_dix_chapitres(self):
        eqs = self.donnees["equations"]
        self.assertEqual([e["id"] for e in eqs], [f"EQ-{i:02d}" for i in range(1, 18)])
        vus = {e["chapitre"]["titre"] for e in eqs if e["chapitre"]}
        for debut, titre in CH.VIDEO["chapitres"]:
            self.assertIn(titre, vus, f"chapitre {debut} « {titre} » non rattacé")
        for e in eqs:
            self.assertIn(e["statut"], ("OPÉRATIONNEL", "SIMULÉ", "SPÉCIFIÉ"))
            if e["chapitre"]:
                self.assertIn([e["chapitre"]["debut"], e["chapitre"]["titre"]],
                              CH.VIDEO["chapitres"])

    def test_cent_huit_cellules_et_verdict_global(self):
        conf = self.donnees["confrontation"]
        self.assertEqual(conf["nombre_cellules"], 108)
        self.assertEqual(conf["verdict_global"], "CONTENU")
        self.assertAlmostEqual(conf["exclues_attendues"], 108 * CH.ALPHA, places=12)

    def test_certificats_du_domaine_court(self):
        for constante, certificat in self.donnees["certificats"].items():
            self.assertTrue(certificat["certifie"], constante)

    def test_verifier_retourne_vrai(self):
        self.assertTrue(CH.verifier(self.donnees))


class TestArtefacts(unittest.TestCase):
    """L'écriture hors dépôt : les artefacts relisent exactement la confrontation."""

    def test_cinq_fichets_et_csv_franc(self):
        donnees = CH.resoudre(6_000, 1_500, 750, 40, 20)
        with tempfile.TemporaryDirectory() as tampon:
            rendu = CH.ecrire_artefacts(donnees, Path(tampon))
            self.assertEqual(sorted(rendu), ["confrontation.csv", "confrontation.json",
                                             "etat.json", "mesures.json", "predictions.json"])
            dossier = Path(tampon)
            for nom in rendu:
                self.assertTrue((dossier / nom).exists(), nom)
                self.assertGreater((dossier / nom).stat().st_size, 0)
            octets = (dossier / "confrontation.csv").read_bytes()
            self.assertTrue(octets.startswith(b"\xef\xbb\xbf"), "BOM Excel absent")
            self.assertIn(b"\r\n", octets, "fin de ligne Excel absente")
            # Écrire en octets imposés, pas via `write_text` : la traduction
            # système des fins de ligne rendait le CSV LF sur Linux, CRLF sur Windows.
            self.assertEqual(octets.count(b"\n"), octets.count(b"\r\n"),
                             "un « \\n » sans « \\r » devant : fins de ligne laissées au système")
            for nom in rendu:
                if nom.endswith(".json"):
                    self.assertNotIn(b"\r", (dossier / nom).read_bytes(), nom)
                self.assertEqual(int(rendu[nom].split()[0]), (dossier / nom).stat().st_size,
                                 f"octets annoncés pour {nom}")
            lignes = octets.decode("utf-8-sig").splitlines()
            self.assertEqual(len(lignes), 1 + 108)
            self.assertEqual(lignes[0], "constante;statistique;classe;attendu;obtenu;"
                                        "p_bilatere;verdict")
            self.assertNotIn(".", lignes[1].split(";")[3], "décimale non française")
            contenu = (dossier / "predictions.json").read_text(encoding="utf-8")
            self.assertIn("M90ZAVojI30", contenu, "la source vidéo doit voyager avec les artefacts")
            self.assertIn("Euclidea", contenu)

    def test_le_csv_publie_est_le_rendu_du_module(self):
        """Le CSV déposé dans l'archive n'est pas un fichier tenu à la main : les
        cellules publiées, reformées par le code, redonnent le même contenu.
        Les fins de ligne sont neutralisées ici — ce que l'archive contient dépend
        du checkout ; `test_cinq_fichets_et_csv_franc`, lui, juge l'écriture elle-même."""
        publie = (RACINE_DOSSIER / "artefacts" / "confrontation.csv").read_bytes()
        cellules = json.loads((RACINE_DOSSIER / "artefacts" / "confrontation.json")
                              .read_text(encoding="utf-8"))["confrontation"]["cellules"]
        reconstruit = CH.octets_confrontation_csv(cellules)
        self.assertEqual(reconstruit.replace(b"\r\n", b"\n"), publie.replace(b"\r\n", b"\n"))
        self.assertEqual(len(cellules), 108)


class TestAttributionVideo(unittest.TestCase):
    """Le bloc vidéo est de la métadonnée mesurée : il doit rester exact et borné."""

    def test_metadonnees_mesurees(self):
        self.assertEqual(CH.VIDEO["id"], "M90ZAVojI30")
        self.assertEqual(CH.VIDEO["titre"], "What Is Actually Hiding in the Digits of Pi?")
        self.assertEqual(CH.VIDEO["auteur"], "Euclidea")
        self.assertEqual(CH.VIDEO["duree_s"], 854)
        self.assertTrue(CH.VIDEO["transcript"].startswith("absent"))

    def test_dix_chapitres_croissants_et_inferieurs_a_la_duree(self):
        secondes = []
        for debut, titre in CH.VIDEO["chapitres"]:
            m, s = debut.split(":")
            secondes.append(60 * int(m) + int(s))
            self.assertTrue(titre.strip())
        self.assertEqual(len(CH.VIDEO["chapitres"]), 10)
        self.assertEqual(secondes, sorted(set(secondes)))
        self.assertLess(secondes[-1], CH.VIDEO["duree_s"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
