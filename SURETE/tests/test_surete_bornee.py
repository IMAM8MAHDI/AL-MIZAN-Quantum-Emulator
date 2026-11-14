# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2026 IMAM8MAHDI / Astro-Code Ecosystem
# SPDX-License-Identifier: GPL-3.0-only OR AGPL-3.0-only
"""Tests du dossier SURETE — treize équations re-derivées par d'autres routes.

Six exigences, dans l'ordre :

    1. chaque nombre publié est retrouvé ici par une écriture différente : la boule de mots par
       le comptage longueur par longueur, P₀ par sa série de Taylor, les heures par une
       soustraction de dates, les quatre issues par une énumération de 120 050 atomes
       équiprobables, la pente par une régression linéaire, la disponibilité en `Fraction`
       exacte, 313 000 000 000 000 par sa chaîne de chiffres ;
    2. l'instantané consigné du registre est confronté au registre vivant : `inventaire_parc()`
       recompte module par module, et une dérive du snapshot rougit ici avant de roussir un
       README ;
    3. non-vacuité : le détecteur de lectures extérieures est joué sur trois AST synthétiques
       (auto-lecture par nom, jointure vers un voisin, `open` d'un chemin figé), le critère est
       rejoué sur une liste de garanties mutée, et une limite effacée ou un marqueur d'absolu
       insérés font rougir le contrôle qui doit rougir ;
    4. l'artefact est écrit dans un répertoire temporaire, relu, comparé au certificat, et un
       nombre mué sur disque ne passe plus la relecture ;
    5. structure : treize équations `EQ-01`..`EQ-13` en chaîne continue, treize contrôles dont
       l'identifiant est le dernier segment du chemin de l'équation, statuts et couches pris
       dans les dictionnaires déclarés, quarante caractères de limite par équation ;
    6. ce que le dossier ne dit pas : aucun nom d'entreprise, de produit ou de personne dans les
       champs publiés, aucun horodatage inventé, le transcript tenu pour absent, et le mot
       « preuve » absent de toute conclusion.

Bibliothèque standard seule (plus `FONDATION` pour le recompte du registre).
    cd ZENODO_DEPOT_ALMIZAN && py -3 -m unittest SURETE.tests.test_surete_bornee -v
"""

import ast
import copy
import hashlib
import json
import math
import re
import sys
import unittest
from datetime import datetime, timedelta, timezone
from fractions import Fraction
from pathlib import Path
from tempfile import TemporaryDirectory

RACINE_DEPOT = Path(__file__).resolve().parents[2]
if str(RACINE_DEPOT) not in sys.path:
    sys.path.insert(0, str(RACINE_DEPOT))

from SURETE import surete_bornee_base as B                                   # noqa: E402

FICHIER_MODULE = RACINE_DEPOT / "SURETE" / "surete_bornee_base.py"


class TestDomaineEnumere(unittest.TestCase):
    """EQ-01 et EQ-02 : la boule de mots, son compte, et la non-trivialité de la propriété."""

    @classmethod
    def setUpClass(cls):
        cls.rice = B.rice()
        cls.e = B.enumeration()
        cls.K = int(B.PARAMETRES["profondeur_enumeree"])

    def test_compte_par_longueurs_rejoint_la_forme_ferme(self):
        mots = B.mots_boules(self.K)
        par_longueur = {n: sum(1 for m in mots if len(m) == n) for n in range(self.K + 1)}
        self.assertEqual(par_longueur, {n: 2 ** n for n in range(self.K + 1)})
        self.assertEqual(len(mots), sum(2 ** n for n in range(self.K + 1)))
        self.assertEqual(len(mots), 2 ** (self.K + 1) - 1)
        self.assertEqual(self.e["etats"], len(mots))

    def test_domaine_sans_doublon_et_tous_les_mots_admissibles(self):
        mots = B.mots_boules(self.K)
        self.assertEqual(len(mots), len(set(mots)), "deux occurrences du même mot")
        self.assertTrue(all(re.fullmatch(r"[01]*", m) for m in mots))
        self.assertLessEqual(max(len(m) for m in mots), self.K)
        self.assertIn("", mots)
        self.assertIn("0" * self.K, mots)
        self.assertIn("1" * self.K, mots)

    def test_non_triviale_par_les_deux_machines_rejouees(self):
        r = self.rice
        self.assertEqual(r["acceptes_vide"], 0)
        self.assertEqual(r["acceptes_totale"], r["domaine"])
        self.assertNotIn(r["critique"], [m for m in B.mots_boules(r["K"])
                                        if B.machine_vide(m)])
        self.assertTrue(r["non_triviale"])
        self.assertNotEqual(B.machine_vide(r["critique"]), B.machine_totale(r["critique"]))

    def test_le_vide_et_le_plein_sont_les_seuls_extremes(self):
        for mot in B.mots_boules(6):
            self.assertFalse(B.machine_vide(mot))
            self.assertTrue(B.machine_totale(mot))

    def test_vitesse_relevee_depasse_le_plancher_declare(self):
        e = self.e
        self.assertGreaterEqual(e["vitesses_par_s"], e["plancher"])
        self.assertGreater(e["duree_s"], 0.0)
        self.assertEqual(e["dizaine_vitesse"],
                         10 ** int(math.floor(math.log10(e["vitesses_par_s"]))))
        self.assertAlmostEqual(e["cout_domaine_s"], e["etats"] / e["plancher"], places=9)


class TestPoissonEtCorectif(unittest.TestCase):
    """EQ-03 et EQ-04 : défauts attendus d'une surface, et heures d'une chaîne de correctif."""

    @classmethod
    def setUpClass(cls):
        cls.d = B.defauts_tcb()
        cls.c = B.fenetre_correctif()

    def test_N_par_deux_routes_et_serie_de_taylor(self):
        d, f = Fraction(B.PARAMETRES["densite_defauts_par_ligne"]), \
            Fraction(B.PARAMETRES["fraction_exploitable"])
        for nom, L in B.PARAMETRES["tcb_lignes"].items():
            scenario = self.d["scenarios"][nom]
            self.assertEqual(scenario["attendus"], Fraction(L) * d * f)
            self.assertEqual(scenario["attendus"], Fraction(L, 10 ** 4))
            self.assertEqual(scenario["somme_de_troncons"], scenario["attendus"])
        N = self.d["N_petit"]
        par_serie = sum((-N) ** k / math.factorial(k) for k in range(60))
        self.assertAlmostEqual(self.d["P0_par_exp"], float(par_serie), places=12)

    def test_P0_par_la_definition_de_limite(self):
        N = self.d["N_petit"]
        self.assertAlmostEqual(self.d["P0_par_limite"], math.exp(-N), delta=1e-4)
        self.assertLess(self.d["erreur_relative"], float(B.PARAMETRES["tolerance_relative"]))

    def test_heures_comptees_egalent_la_difference_des_deux_instants(self):
        jours = self.c["jours"]
        origine = datetime(2026, 5, 3, 6, 30, tzinfo=timezone.utc)
        fin = origine + timedelta(days=jours)
        self.assertEqual(self.c["heures_comptees"], self.c["heures_par_multiplication"])
        self.assertEqual(int((fin - origine) / timedelta(hours=1)), jours * 24)
        self.assertEqual(self.c["par_tranche"], dict(B.PARAMETRES["chaine_correctif_jours"]))
        self.assertEqual(sum(self.c["par_tranche"].values()), jours)

    def test_heures_vulnerabilites_par_les_deux_ecritures(self):
        W, n = self.c["heures_par_multiplication"], self.c["exposes_par_an"]
        self.assertEqual(self.c["heure_vulnerabilites"], W * n)
        self.assertEqual(self.c["heure_vulnerabilites"], sum(W for _ in range(n)))
        self.assertEqual(self.c["heure_vulnerabilites"], 14_400)


class TestIntervalles(unittest.TestCase):
    """EQ-05 : ce que produit une addition dont une borne supérieure est absente."""

    def test_majorant_propage_absence_dans_les_deux_ordres(self):
        connue = B.Intervalle(Fraction(360), Fraction(720))
        inconnue = B.Intervalle(Fraction(0), None)
        self.assertIsNone((connue + inconnue).haut)
        self.assertIsNone((inconnue + connue).haut)
        self.assertEqual((connue + inconnue).bas, Fraction(360))
        self.assertEqual((connue + connue).bas, Fraction(720))
        self.assertEqual((connue + connue).haut, Fraction(1440))

    def test_minorant_tenu_quelle_que_soit_linconnue(self):
        i = B.part_non_divulguee()
        self.assertFalse(i["majorant_existe"])
        self.assertEqual(Fraction(i["total"]["bas"]), Fraction(i["connue"]["bas"]))
        self.assertEqual(i["total"]["haut"], None)
        for k in range(0, 15):
            u = Fraction(10 ** k)
            self.assertGreaterEqual((B.Intervalle(Fraction(360), Fraction(720))
                                     + B.Intervalle(u, u)).bas, Fraction(360))
        self.assertEqual(i["echantillons_testes"], 4)

    def test_intervalle_vide_est_refuse(self):
        with self.assertRaises(ValueError):
            B.Intervalle(Fraction(5), Fraction(4))


class TestChainesDeCouches(unittest.TestCase):
    """EQ-06 et EQ-07 : fuite s + (1−s)·a^N, ses quatre issues, son plancher et sa pente."""

    @classmethod
    def setUpClass(cls):
        cls.co = B.couches()

    def test_a_calibre_la_couche_exactement_sur_p(self):
        p, beta = Fraction(B.PARAMETRES["p_couche"]), Fraction(B.PARAMETRES["beta_cause_commune"])
        s = p * beta
        a = (p - s) / (1 - s)
        self.assertEqual(Fraction(self.co["s"]), s)
        self.assertEqual(Fraction(self.co["a"]), a)
        self.assertEqual(s + (1 - s) * a, p)
        self.assertEqual(Fraction(self.co["fuite_une_couche"]), p)
        self.assertTrue(self.co["egale_p"])

    def test_quatre_issues_par_enumeration_d_atomes(self):
        n_commun, n_a = 50, 49
        compte = {"cause commune, les deux tombent": 0, "independant, les deux tombent": 0,
                  "independant, une seule tombe": 0, "independant, aucune ne tombe": 0}
        for u in range(n_commun):
            for v in range(n_a):
                for w in range(n_a):
                    if u == 0:
                        compte["cause commune, les deux tombent"] += 1
                    elif v < 9 and w < 9:
                        compte["independant, les deux tombent"] += 1
                    elif (v < 9) != (w < 9):
                        compte["independant, une seule tombe"] += 1
                    else:
                        compte["independant, aucune ne tombe"] += 1
        total = n_commun * n_a * n_a
        self.assertEqual(sum(compte.values()), total)
        for cle, atomes in compte.items():
            self.assertEqual(Fraction(self.co["issues"][cle]), Fraction(atomes, total), cle)
        self.assertEqual(Fraction(self.co["masse_des_issues"]), 1)
        self.assertEqual(Fraction(self.co["fuite_deux_couches"]),
                         Fraction(compte["cause commune, les deux tombent"]
                                  + compte["independant, les deux tombent"], total))

    def test_plancher_jamais_annule_et_pente_par_regression(self):
        s, a = Fraction(self.co["s"]), Fraction(self.co["a"])

        def fuite(N):
            return s + (1 - s) * a ** N

        table = [fuite(N) for N in range(1, 41)]
        self.assertEqual([str(x) for x in table[:6]], self.co["table"])
        self.assertTrue(all(table[i] > table[i + 1] for i in range(39)))
        self.assertGreater(fuite(400), s)
        xs = list(range(1, 41))
        ys = [math.log10(float(fuite(N) - s)) for N in range(1, 41)]
        n = len(xs)
        pente = (n * sum(x * y for x, y in zip(xs, ys)) - sum(xs) * sum(ys)) \
            / (n * sum(x * x for x in xs) - sum(xs) ** 2)
        self.assertAlmostEqual(pente, math.log10(float(a)), places=9)
        self.assertAlmostEqual(self.co["erreur_pente"], 0.0, places=9)


class TestDisponibilite(unittest.TestCase):
    """EQ-08 : deux routes exactes, et ce que l'approximation usuelle fait vraiment."""

    @classmethod
    def setUpClass(cls):
        cls.di = B.disponibilite()

    def test_A_et_temps_perdu_en_rationnels_exacts(self):
        mtbf, mttr, T = (Fraction(B.PARAMETRES[k]) for k in ("mtbf_h", "mttr_h", "heures_par_an"))
        A = mtbf / (mtbf + mttr)
        self.assertEqual(Fraction(self.di["A"]), A)
        self.assertEqual(Fraction(self.di["heures_par_A"]), (1 - A) * T)
        self.assertEqual(Fraction(self.di["heures_directes"]), T * mttr / (mtbf + mttr))
        self.assertEqual(Fraction(self.di["heures_par_A"]), Fraction(self.di["heures_directes"]))
        self.assertEqual(Fraction(self.di["heures_par_A"]), Fraction(8760, 4381))

    def test_approximation_majeure_de_peu(self):
        mtbf, mttr = (Fraction(B.PARAMETRES[k]) for k in ("mtbf_h", "mttr_h"))
        self.assertTrue(self.di["approximation_majore"])
        self.assertGreater(self.di["approximation_flottante"], float(Fraction(8760, 4381)))
        self.assertLess(self.di["erreur_relative"], 1e-3)
        self.assertAlmostEqual(self.di["neufs"], -math.log10(float(mttr / (mtbf + mttr))), places=9)
        self.assertAlmostEqual(self.di["neufs"], math.log10(4381.0), places=9)


class TestCritereSurEnonce(unittest.TestCase):
    """EQ-09 : le critère porte sur des énoncés écrits ici, et se laisse falsifier."""

    def test_classement_attendu_apres_lecture_a_la_main(self):
        cr = B.critere_obsolescence()
        self.assertEqual(cr["hors_critere"], ["G1", "G2", "G3"])
        self.assertEqual([r["id"] for r in cr["rendues"] if r["au_critere"]], ["G4", "G5", "G6"])
        self.assertEqual(cr["n"], len(B.GARANTIES_DECLAREES))
        self.assertTrue(cr["accord"])

    def test_une_borne_nulle_suffit_a_mettre_hors_critere(self):
        original = B.GARANTIES_DECLAREES
        try:
            B.GARANTIES_DECLAREES = [{"id": "X1", "enonce": "borne nulle, procédure publique",
                                      "borne": "0", "procedure_publique": True},
                                     {"id": "X2", "enonce": "borne non nulle, procédure absente",
                                      "borne": "1/7", "procedure_publique": False},
                                     {"id": "X3", "enonce": "les deux", "borne": "1/7",
                                      "procedure_publique": True}]
            cr = B.critere_obsolescence()
            self.assertEqual(cr["hors_critere"], ["X1", "X2"])
            self.assertEqual(cr["par_les_nombres"], ["X1"])
            self.assertFalse(cr["accord"])
        finally:
            B.GARANTIES_DECLAREES = original

    def test_trois_garanties_sont_celles_du_depot_et_sans_attribution(self):
        enonces = " ".join(g["enonce"] for g in B.GARANTIES_DECLAREES).lower()
        for interdit in ("microsoft", "bancal", "franceinfo", "windows", "azure"):
            self.assertNotIn(interdit, enonces)


class TestCoutPourUnTiers(unittest.TestCase):
    """EQ-10 : le détecteur est joué sur des arbres synthétiques, pas sur sa seule cible."""

    def test_auto_lecture_par_nom_comptee_interieure(self):
        arbre = ast.parse('chemin = Path(__file__).resolve()\nx = chemin.read_text()\n')
        self.assertEqual([r["sur_le_module"] for r in B.lectures_du_fichier(arbre)], [True])

    def test_jointure_vers_un_voisin_comptee_exterieure(self):
        arbre = ast.parse('chemin = Path(__file__).resolve()\n'
                          'x = (chemin.parent / "voisin.txt").read_text()\n')
        self.assertEqual([r["sur_le_module"] for r in B.lectures_du_fichier(arbre)], [False])

    def test_open_de_chemin_fixe_compte_exterieur(self):
        arbre = ast.parse('with open("C:/Windows/win.ini") as f:\n    pass\n'
                          'with open(chemin) as g:\n    pass\n'
                          'chemin = Path(__file__)\n')
        releve = B.lectures_du_fichier(arbre)
        self.assertEqual([r["sur_le_module"] for r in releve], [False, True])

    def test_module_reel_n_importe_que_de_la_stdlib_et_ne_lit_rien_d_exterieur(self):
        ti = B.cout_pour_un_tiers()
        stdlib = set(getattr(sys, "stdlib_module_names", ()))
        self.assertEqual(ti["hors_stdlib"], [])
        self.assertEqual(ti["reseau"], [])
        self.assertEqual(ti["lectures_exterieures"], 0)
        self.assertEqual(ti["n_imports"], len(ti["imports"]))
        self.assertTrue(set(ti["imports"]) <= stdlib)
        source = FICHIER_MODULE.read_text(encoding="utf-8")
        for n in ast.walk(ast.parse(source)):
            if isinstance(n, ast.Import):
                self.assertTrue({x.name.split(".")[0] for x in n.names} <= stdlib)

    def test_imports_recomptes_par_un_second_ast(self):
        arbre = ast.parse(FICHIER_MODULE.read_text(encoding="utf-8"))
        racines = set()
        for n in ast.walk(arbre):
            if isinstance(n, ast.Import):
                racines |= {a.name.split(".")[0] for a in n.names}
            elif isinstance(n, ast.ImportFrom) and n.level == 0 and n.module:
                racines.add(n.module.split(".")[0])
        self.assertEqual(sorted(racines), sorted(B.cout_pour_un_tiers()["imports"]))


class TestRegistreConsigne(unittest.TestCase):
    """EQ-11 : l'instantané recopié est confronté au registre vivant du dépôt."""

    @classmethod
    def setUpClass(cls):
        cls.re = B.registre_consigne()

    def test_instantane_interne_coherent(self):
        self.assertEqual(self.re["somme"], self.re["total_publie"])
        self.assertEqual(self.re["entrees"], self.re["modules_annonces"])
        self.assertEqual(self.re["minimum"], 10)
        self.assertEqual(self.re["maximum"], 21)

    def test_instantane_confronte_au_parc_vivant(self):
        from FONDATION import fondation_base as FB
        vivant = {}
        for dossier in FB.DOSSIERS_EQUATIONS:
            for p in sorted((RACINE_DEPOT / dossier).rglob("*.py")):
                if "__pycache__" in p.parts or p.name not in FB.MODULES_PRINCIPAUX:
                    continue
                texte = p.read_text(encoding="utf-8", errors="replace")
                vivant[f"{dossier}/{p.name}"] = len(set(re.findall(r'"EQ-\d\d"', texte)))
        consigne = B.PARAMETRES["registre_consigne"]["equations_par_module"]
        self.assertEqual(sorted(vivant), sorted(consigne), "le snapshot et le parc divergent")
        self.assertEqual(vivant, consigne)
        inventaire = FB.inventaire_parc()
        self.assertEqual(sum(vivant.values()), sum(v["equations"] for v in inventaire.values()))
        self.assertIn("SURETE/surete_bornee_base.py", vivant)
        self.assertEqual(vivant["SURETE/surete_bornee_base.py"], 13)

    def test_cles_du_snapshot_sont_des_chemins_de_module_reels(self):
        for cle in B.PARAMETRES["registre_consigne"]["equations_par_module"]:
            self.assertTrue((RACINE_DEPOT / cle).is_file(), cle)
            self.assertEqual(len(cle.split("/")), 2, cle)


class TestSocle313T(unittest.TestCase):
    """EQ-12 : une capacité d'adressage n'est pas un délai de cassage."""

    @classmethod
    def setUpClass(cls):
        cls.so = B.socle()

    def test_le_nombre_par_sa_chaine_de_chiffres(self):
        N = self.so["N"]
        self.assertEqual(str(313) + "0" * 12, str(N))
        self.assertEqual(self.so["chiffres"], 15)
        self.assertEqual(self.so["N_par_factorisation"], N)
        self.assertTrue(self.so["coherent"])

    def test_313_est_premier_par_test_de_division(self):
        self.assertEqual(self.so["racine_carree"], math.isqrt(313))
        self.assertEqual(self.so["diviseurs_trouves"], [])
        self.assertTrue(self.so["premier"])
        self.assertTrue(all(313 % d for d in range(2, math.isqrt(313) + 1)))

    def test_delai_a_plancher_exactement_deux_routes(self):
        N, v, annee = self.so["N"], self.so["vitesse"], int(B.PARAMETRES["annee_s"])
        self.assertEqual(Fraction(self.so["annees_exactes"]), Fraction(N, v * annee))
        self.assertAlmostEqual(self.so["secondes"], float(Fraction(N, v)), delta=1.0)
        self.assertGreater(self.so["annees"], 1.0)


class TestAutoApplication(unittest.TestCase):
    """EQ-13 : le critère est retourné contre le module lui-même, et l'instrument n'est pas vide."""

    def test_treize_limites_et_zero_marqueur(self):
        eqs = B.equations(B.mesurer())
        auto = B.auto_controle(eqs)
        self.assertEqual(auto["avec_limite"], 13)
        self.assertEqual(auto["total"], 13)
        self.assertEqual(auto["absus_releves"], {})
        self.assertGreater(len(B.MARQUEURS_ABSOLUS), 0)

    def test_un_marqueur_d_absolu_est_releve_s_il_est_ecrit(self):
        faux = [{"id": "EQ-99", "resultat": "le système est sécurisé à 100 %", "formule": "",
                 "statut": "OPÉRATIONNEL", "limite": "x" * 40}]
        auto = B.auto_controle(faux)
        self.assertEqual(list(auto["absus_releves"]), ["EQ-99"])
        self.assertEqual(auto["absus_releves"]["EQ-99"], ["100 %"])

    def test_une_limite_effacee_compte_moins_de_treize(self):
        eqs = copy.deepcopy(B.equations(B.mesurer()))
        eqs[0]["limite"] = "courte"
        self.assertEqual(B.auto_controle(eqs)["avec_limite"], 12)

    def test_racine_stable_entre_deux_mesures_distinctes(self):
        une = B.racine_equations(B.equations(B.mesurer()))
        deux = B.racine_equations(B.equations(B.mesurer()))
        self.assertEqual(une, deux)
        self.assertEqual(len(une), 64)
        m = B.mesurer()
        eqs = B.equations(m)
        cert = B.certificat(eqs, B.controles(m, eqs))
        # aucune horloge d'exécution dans le certificat : « duree_s » y est la durée déclarée de
        # la vidéo (métadonnée publique), pas un temps mesuré sur l'hôte.
        self.assertNotIn("duree", sorted(cert))
        self.assertEqual(cert["source"]["duree_s"], B.SOURCE["duree_s"])
        self.assertNotIn("mesure_le", str(cert))
        self.assertEqual(cert["controles_verts"], cert["controles"])
        self.assertEqual(B.resoudre()["certificat"]["controles"], 13)

    def test_racine_bouge_si_un_seul_resultat_change(self):
        eqs = copy.deepcopy(B.equations(B.mesurer()))
        avant = B.racine_equations(eqs)
        eqs[7]["resultat"] += " "
        self.assertNotEqual(B.racine_equations(eqs), avant)

    def test_racine_recalculee_a_la_main_sur_une_feuille(self):
        eqs = B.equations(B.mesurer())
        feuilles = [hashlib.sha256(
            f"{e['id']}|{e['formule']}|{e['resultat']}|{e['statut']}|{e['limite']}"
            .encode("utf-8")).hexdigest() for e in eqs]
        self.assertEqual(len(feuilles), 13)
        niveau = list(feuilles)
        while len(niveau) > 1:
            if len(niveau) % 2:
                niveau.append(niveau[-1])
            niveau = [hashlib.sha256((a + b).encode("utf-8")).hexdigest()
                      for a, b in zip(niveau[0::2], niveau[1::2])]
        self.assertEqual(niveau[0], B.racine_equations(eqs))


class TestAssemblage(unittest.TestCase):
    """Structure du contrat : chaîne continue, chemins, statuts, vérificateur, artefact."""

    @classmethod
    def setUpClass(cls):
        cls.donnees = B.resoudre()

    def test_treize_equations_en_chaine_continue(self):
        eqs = self.donnees["equations"]
        self.assertEqual([e["id"] for e in eqs], [f"EQ-{i:02d}" for i in range(1, 14)])
        self.assertEqual(len({e["id"] for e in eqs}), 13)

    def test_treize_controles_dont_l_identifiant_clot_chemin(self):
        eqs, cs = self.donnees["equations"], self.donnees["controles"]
        self.assertEqual([c["id"] for c in cs], [f"C{i:02d}" for i in range(1, 14)])
        self.assertEqual(len(eqs), len(cs))
        for e, c in zip(eqs, cs):
            self.assertEqual(e["chemin"].split("→")[-1].strip(), c["id"], e["id"])

    def test_statuts_couches_et_piliers_pris_des_dictionnaires_declares(self):
        for e in self.donnees["equations"]:
            self.assertIn(e["statut"], B.STATUTS)
            self.assertIn(e["couche"], B.COUCHES)
            self.assertEqual(e["piliers"], ["P1 UNITE", "P2 BORNE", "P3 CONFRONTATION",
                                           "P4 TRANSMISSION"])
            self.assertGreaterEqual(len(e["limite"]), 40, e["id"])
            self.assertTrue(e["resultat"] and e["formule"])
            self.assertTrue(e["fonde_hors_du_dossier"] or e["depend_de"], e["id"])

    def test_tous_les_controles_verts_et_verifier_true(self):
        self.assertTrue(B.verifier(self.donnees))
        self.assertEqual(self.donnees["certificat"]["controles_verts"], 13)
        for c in self.donnees["controles"]:
            self.assertTrue(c["ok"], f"{c['id']} : {c['attendu']} / {c['obtenu']}")
            self.assertTrue(c["nom"] and c["attendu"] and c["obtenu"], c["id"])

    def test_verifier_rouge_des_qu_un_controle_est_mu(self):
        faux = copy.deepcopy(self.donnees)
        faux["controles"][4]["ok"] = False
        self.assertFalse(B.verifier(faux))

    def test_aucun_nom_de_produit_ni_horodatage_dans_les_champs_publies(self):
        interdit = ("microsoft", "bancal", "franceinfo", "windows", "azure", "amazon", "google")
        for e in self.donnees["equations"]:
            texte = " ".join(str(e[k]) for k in
                             ("chemin", "formule", "resultat", "statut", "limite")).lower()
            for nom in interdit:
                self.assertNotIn(nom, texte, e["id"])
        for c in self.donnees["controles"]:
            self.assertNotRegex(c["obtenu"], r"\b\d{1,2}:\d{2}\b", c["id"])

    def test_la_source_ne_revendique_aucune_citation(self):
        s = self.donnees["source"]
        self.assertEqual(s["chapitres_publics"], 0)
        self.assertEqual(s["sonde_transcript_octets"], {"json3": 0, "srv3": 0, "xml": 0})
        self.assertIn("absent", s["transcript"])
        self.assertEqual(len(s["ce_que_la_video_n_a_pas_fourni"]), 3)
        self.assertNotIn("preuve", self.donnees["conclusion"].get("titre", "").lower())

    def test_certificat_et_artefact_identiques_apres_relecture(self):
        cert = self.donnees["certificat"]
        with TemporaryDirectory() as temporaires:
            B.ARTEFACTS = Path(temporaires)
            try:
                ecrit = B.ecrire_artefacts(cert)
                relu = json.loads((Path(temporaires) / "certificat.json").read_text("utf-8"))
                self.assertEqual(relu, cert)
                self.assertEqual(list(ecrit), ["certificat.json"])
                chemin = Path(temporaires) / "certificat.json"
                octets = chemin.read_bytes()
                octets_mués = octets.replace(b'"controles_verts": 13', b'"controles_verts": 12')
                chemin.write_bytes(octets_mués)
                self.assertNotEqual(json.loads(chemin.read_text("utf-8")), cert)
            finally:
                B.ARTEFACTS = FICHIER_MODULE.parent / "artefacts"

    def test_certificat_ne_porte_aucune_mesure_d_hote(self):
        cert = self.donnees["certificat"]
        self.assertEqual(cert["module"], "SURETE/surete_bornee_base.py")
        self.assertEqual(cert["equations"], 13)
        self.assertEqual(cert["controles"], 13)
        self.assertEqual(sum(cert["statuts_par_label"].values()), 13)
        self.assertEqual(cert["parametres_declares"],
                         sorted(k for k in B.PARAMETRES if k != "registre_consigne"))
        self.assertNotIn("mesure_le", json.dumps(cert["source"]))


if __name__ == "__main__":
    unittest.main(verbosity=2)
