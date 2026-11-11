# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2026 IMAM8MAHDI / Astro-Code Ecosystem
# SPDX-License-Identifier: GPL-3.0-only OR AGPL-3.0-only
"""Tests du dossier QPU_DISTANT — un job IBM relu sans qiskit, sans réseau, sans parole.

Sept exigences, dans l'ordre :
    1. les nombres publiés sont re-mesurés ici par une écriture différente : le SHA-256 vient
       d'une digestion par blocs de 4096 octets (et non d'un `read_bytes` unique), les mots de
       2 bits sont reconstruits par `divmod` (et non par une mise en forme), la parité et
       l'écart-type viennent d'une `Fraction` exacte, et la valeur p de l'asymétrie d'une
       convolution binomiale en `Fraction` (et non de `math.comb`) ;
    2. les valeurs littérales de l'audit scellé du fournisseur sont redites telles quelles dans
       `AUDIT` et retombent exactement sur celles du module : le dépôt scellé ne dépend d'aucun
       fichier hors dépôt, il en porte les nombres ;
    3. les deux empreintes internes (parc, sonde de support) se recalculent, et la règle de
       calcul est redémontrée dans le test au lieu d'être déléguée au module ;
    4. non-vacuité : dix mutations, une par contrôle, chacune exigeant un message d'obtenu
       différent et ne faisant rougir que sa propre ligne — la grille n'est pas décorative ;
    5. les quatre artefacts sont écrits dans un répertoire temporaire, relus (`json`,
       `csv.reader`, regex pour le SVG), comparés au certificat, et un nombre mué sur disque ne
       passe plus la relecture ;
    6. confidentialité : aucun identifiant de compte ne subsiste dans les fichiers publiés, les
       artefacts ni la documentation du dossier, et le module ne le rencontre qu'une fois,
       comme motif de recherche ;
    7. structure et langage : dix équations plus dix contrôles, racine Merkle recalculée à
       partir des nœuds publiés, imports de la bibliothèque standard seule, aucun appel réseau,
       et `qubit_physique_local = False` reste faux dans le certificat.

Bibliothèque standard seule.
    cd ZENODO_DEPOT_ALMIZAN && py -3 -m unittest QPU_DISTANT.tests.test_qpu_distant -v
"""

import ast
import copy
import csv
import hashlib
import io
import json
import math
import re
import sys
import unittest
from fractions import Fraction
from pathlib import Path
from tempfile import TemporaryDirectory

RACINE_DEPOT = Path(__file__).resolve().parents[2]
if str(RACINE_DEPOT) not in sys.path:
    sys.path.insert(0, str(RACINE_DEPOT))

from QPU_DISTANT import qpu_distant_base as Q                       # noqa: E402

JETON_COMPTE = "IBM" + "id"          # construit : ce fichier ne porte pas le motif
STDLIB = {"__future__", "ast", "base64", "datetime", "hashlib", "io", "json", "math", "pathlib",
          "re", "sys", "typing", "zlib"}
INTERDITS = ("prouvé", "démontré", "INVIOLABLE", "certifié", "100 %", "universel", "garanti",
             "certain")

# L'audit scellé du fournisseur, hors dépôt : ses nombres sont redits ici littéralement.
AUDIT = {
    "compteurs": {"11": 108, "00": 126, "01": 22},
    "tirages": 256,
    "p_mesuree": 0.9140625,
    "sigma_tirage": 0.01751698351040244,
    "somme_eps_mediane": 0.03705172947376342,
    "borne_mediane": 0.9258965410524731,
    "somme_eps_support": 0.044284500166297244,
    "borne_support": 0.9114309996674055,
    "ecart_mediane_en_sigma": -0.6755752807237312,
    "ecart_support_en_sigma": 0.15022565563481882,
    "empreinte_support": "f0fec1699c8c645163964c0e082b7e007f5b4fd36c2b3df4565d1c1e5c03dfc9",
    "empreinte_parc": "8dc4cb80b6c5cd92c6a7eebcf9d256d0782b1fa30a24abb4c02d91654d93baf4",
    "sha256_zip": "7a137a17fe6b243c269a41136f486aa863d31f92de7d8db7a6b0154abba1fd63",
    "valeur_p_asymetrie": 4.76837158203125e-07,
    "octets_bloc_qpy": 6277,
}


def sha_par_blocs(chemin: Path, taille: int = 4096) -> str:
    """Voie indépendante : digestion bloc à bloc, empreinte bâtie sans lire tout le fichier."""
    h = hashlib.sha256()
    with chemin.open("rb") as flux:
        while True:
            morceau = flux.read(taille)
            if not morceau:
                return h.hexdigest()
            h.update(morceau)


def mots_des_tirs(brut: bytes, bits: int) -> dict:
    """Compte des mots reconstruits chiffre par chiffre par `divmod`, sans `format`."""
    decalage = 10 + int.from_bytes(brut[8:10], "little")
    compte: dict = {}
    for valeur in brut[decalage:]:
        chiffres, reste = [], valeur
        while len(chiffres) < bits:
            reste, chiffre = divmod(reste, 2)
            chiffres.append(str(chiffre))
        compte["".join(reversed(chiffres))] = compte.get("".join(reversed(chiffres)), 0) + 1
    return compte


def p_asymetrie_par_convolution(a: int, b: int) -> Fraction:
    """Loi exacte de Binom(n, 1/2) par n convolutions de (1/2, 1/2) : aucun `math.comb`."""
    loi = [Fraction(1)]
    for _ in range(a + b):
        loi = ([loi[0] / 2] + [loi[i] / 2 + loi[i + 1] / 2 for i in range(len(loi) - 1)]
               + [loi[-1] / 2])
    return 2 * sum(loi[:min(a, b) + 1], Fraction(0))


def array_base64_du_resultat() -> str:
    donnee = json.loads((Q.SOURCES / Q.F_RESULT).read_bytes().decode("utf-8"))
    champs = donnee["__value__"]["pub_results"][0]["__value__"]["data"]["__value__"]
    return champs["fields"][champs["field_names"][0]]["__value__"]["array"]["__value__"]


class TestRelecture(unittest.TestCase):
    """Les nombres publiés sont re-mesurés, pas acceptés sur parole."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.m = Q.mesurer()
        cls.eqs = {x["id"]: x for x in Q.equations(cls.m)}
        cls.cs = {c["id"]: c for c in Q.controles(cls.m)}
        cls.cert = Q.certificat(cls.m)

    def test_01_tous_les_controles_verts(self) -> None:
        self.assertEqual(len(self.cs), 10)
        self.assertTrue(all(c["ok"] for c in self.cs.values()),
                        [c["id"] for c in self.cs.values() if not c["ok"]])
        self.assertTrue(Q.verifier(Q.resoudre()))

    def test_02_compteurs_remesures_par_divmod(self) -> None:
        brut = Q.debase_zlib(array_base64_du_resultat())
        descr, forme, valeurs = Q.npy(brut)
        self.assertEqual((descr, forme, len(valeurs)), ("|u1", [256, 1], 256))
        self.assertEqual(mots_des_tirs(brut, 2), AUDIT["compteurs"])
        self.assertEqual(self.m["compteurs"], AUDIT["compteurs"])
        self.assertEqual(sum(self.m["compteurs"].values()), AUDIT["tirages"])
        self.assertEqual(len(bytes(valeurs)), 256)

    def test_03_parite_exacte_en_fraction(self) -> None:
        pair = sum(v for k, v in self.m["compteurs"].items() if k.count("1") % 2 == 0)
        self.assertEqual(Fraction(pair, 256), Fraction(117, 128))
        self.assertEqual(self.m["parite"]["p_exacte"], f"{pair}/256")
        self.assertEqual(float(Fraction(pair, 256)), AUDIT["p_mesuree"])
        self.assertEqual(self.m["parite"]["p_mesuree"], AUDIT["p_mesuree"])
        variance = Fraction(pair, 256) * (1 - Fraction(pair, 256)) / 256
        self.assertAlmostEqual(math.sqrt(float(variance)), AUDIT["sigma_tirage"], places=15)
        self.assertEqual(self.m["parite"]["sigma_tirage"], AUDIT["sigma_tirage"])

    def test_04_asymetrie_valeur_p_exacte_sans_comb(self) -> None:
        a, b = self.m["compteurs"].get("01", 0), self.m["compteurs"].get("10", 0)
        self.assertEqual((a, b), (22, 0))
        exact = p_asymetrie_par_convolution(a, b)
        self.assertEqual(exact, Fraction(2, 2 ** 22))
        self.assertEqual(float(exact), self.m["asymetrie"]["valeur_p"])
        self.assertEqual(self.m["asymetrie"]["valeur_p"], AUDIT["valeur_p_asymetrie"])
        self.assertIn("asymétrie non imputable", self.m["asymetrie"]["conclusion"])

    def test_05_enveloppes_reconstituees_en_fractions(self) -> None:
        e1, e2 = self.m["enveloppe_mediane"], self.m["enveloppe_support"]
        somme_med = sum((Fraction(x["erreur"]) * x["n"] for x in e1["detail"].values()),
                        Fraction(0))
        somme_sup = sum((Fraction(x["erreur"]) * x["n"] for x in e2["detail"].values()),
                        Fraction(0))
        self.assertAlmostEqual(float(somme_med), AUDIT["somme_eps_mediane"], places=15)
        self.assertAlmostEqual(float(somme_sup), AUDIT["somme_eps_support"], places=15)
        self.assertAlmostEqual(float(1 - 2 * somme_med), e1["borne_basse"], places=15)
        self.assertAlmostEqual(float(1 - 2 * somme_sup), e2["borne_basse"], places=15)
        self.assertEqual(e1["borne_basse"], AUDIT["borne_mediane"])
        self.assertEqual(e2["borne_basse"], AUDIT["borne_support"])
        self.assertLess(e2["borne_basse"], e1["borne_basse"])
        self.assertLess(e2["borne_basse"], self.m["parite"]["p_mesuree"])
        self.assertGreater(e1["borne_basse"], self.m["parite"]["p_mesuree"])

    def test_06_verdicts_de_l_audit(self) -> None:
        v1, v2 = self.m["verdicts"]["mediane_machine"], self.m["verdicts"]["support_reel"]
        self.assertIs(v1["recue"], False)
        self.assertIs(v2["recue"], True)
        self.assertEqual(v1["ecart_en_sigma"], AUDIT["ecart_mediane_en_sigma"])
        self.assertEqual(v2["ecart_en_sigma"], AUDIT["ecart_support_en_sigma"])
        self.assertIs(v1["recue_a_3sigma"], True)

    def test_07_sha256_par_blocs_et_non_recopie(self) -> None:
        self.assertEqual(sha_par_blocs(Q.SOURCES / Q.F_RESULT),
                         self.m["lecture"]["sha256_membre_result"])
        self.assertEqual(self.m["lecture"]["sha256_membre_result"],
                         self.cert["empreintes"]["sha256_membre_result_registre"])
        self.assertEqual(sha_par_blocs(Q.SOURCES / Q.F_INFOS),
                         self.cert["empreintes"]["sha256_info_netoyee"])
        self.assertEqual(sha_par_blocs(Q.SOURCES / Q.F_REGISTRE),
                         json.loads((Q.SOURCES / Q.F_EMPREINTES).read_bytes()
                                    .decode("utf-8"))["fichiers"][Q.F_REGISTRE]["sha256"])

    def test_08_empreintes_internes_recalculees(self) -> None:
        """La règle du sceau interne est redémontrée, pas déléguée au module."""
        corps = json.dumps({k: v for k, v in self.m["calibrage"].items() if k != "empreinte_parc"},
                           sort_keys=True, ensure_ascii=False)
        self.assertEqual(hashlib.sha256(corps.encode("utf-8")).hexdigest(), AUDIT["empreinte_parc"])
        support = {k: v for k, v in self.m["support"].items()
                   if k not in ("horodatage_utc", "empreinte_support")}
        corps2 = json.dumps(support, sort_keys=True, ensure_ascii=False)
        self.assertEqual(hashlib.sha256(corps2.encode("utf-8")).hexdigest(),
                         AUDIT["empreinte_support"])
        self.assertEqual(self.m["empreintes"]["empreinte_support_recalculee"],
                         self.m["empreintes"]["empreinte_support_declaree"])
        self.assertEqual(Q.empreinte_parc_recalculee(self.m["calibrage"]),
                         self.m["empreintes"]["empreinte_parc_declaree"])

    def test_09_simulation_stdlib_reproduit_bell(self) -> None:
        simu = self.m["simulation"]
        self.assertEqual(simu["distribution"], [0.5, 0.0, 0.0, 0.5])
        self.assertEqual(simu["qubits_actifs"], 2)
        self.assertEqual(simu["dimensions"], 4)
        self.assertAlmostEqual(simu["norme"], 1.0, places=12)
        self.assertEqual(self.m["support_physique"], [0, 1])
        self.assertEqual(simu["operations_unitaires"], 10)

    def test_10_le_bloc_qpy_est_lie_au_registre(self) -> None:
        brut = Q.bloc_qpy()
        self.assertEqual(len(brut), self.m["empreintes"]["octets_bloc_qpy_recalcules"])
        self.assertEqual(Q._sha(brut), self.m["empreintes"]["sha256_bloc_qpy_registre"])
        self.assertEqual(len(brut), AUDIT["octets_bloc_qpy"])


class TestNonVacuite(unittest.TestCase):
    """Une mutation par contrôle : la grille doit rougir une fois et une seule par ligne."""

    def setUp(self) -> None:
        self.m = Q.mesurer()
        self.base = {c["id"]: c["obtenu"] for c in Q.controles(self.m)}

    def applique(self, muter) -> dict:
        copie = copy.deepcopy(self.m)
        muter(copie)
        return {c["id"]: c for c in Q.controles(copie)}

    def test_chaque_controle_rougit_une_fois(self) -> None:
        cas = {
            "C01": lambda m: m["empreintes_des_sources"][Q.F_RESULT].__setitem__("ok", False),
            "C02": lambda m: m["lecture"].__setitem__("sha256_membre_result", "0" * 64),
            "C03": lambda m: m["empreintes"].__setitem__("sha256_bloc_qpy_recalcule", "1" * 64),
            "C05": lambda m: m["compteurs"].__setitem__("00", m["compteurs"]["00"] - 1),
            "C06": lambda m: m["lecture"].__setitem__("num_bits", 3),
            "C07": lambda m: m["compte_portes"].pop("cz"),
            "C08": lambda m: m["simulation"].__setitem__("distribution", [0.25, 0, 0, 0.25]),
            "C09": lambda m: m["empreintes"].__setitem__("empreinte_parc_recalculee", "2" * 64),
            "C10": lambda m: (m["enveloppe_mediane"].__setitem__("borne_basse", 0.50),
                                 m["enveloppe_support"].__setitem__("borne_basse", 0.40)),
        }
        autres = tuple(cas)
        for id_, muter in cas.items():
            with self.subTest(id_=id_):
                rendu = self.applique(muter)
                self.assertFalse(rendu[id_]["ok"], f"{id_} passe encore après mutation")
                self.assertNotEqual(rendu[id_]["obtenu"], self.base[id_],
                                    f"{id_} mute sans changer le message d'obtenu")
                for autre in autres:
                    if autre != id_:
                        self.assertTrue(rendu[autre]["ok"], f"{autre} rougit pour {id_}")

    def test_qdc04_le_motif_de_compte_est_cherche_pour_vrai(self) -> None:
        ancien = Q._octets
        Q._octets = lambda nom: ancien(nom) + f'"{JETON_COMPTE}-0000"'.encode("utf-8")
        try:
            rendu = {c["id"]: c for c in Q.controles(self.m)}
        finally:
            Q._octets = ancien
        self.assertFalse(rendu["C04"]["ok"])
        self.assertNotEqual(rendu["C04"]["obtenu"], self.base["C04"])


class TestArtefacts(unittest.TestCase):
    """Écrits, relus, comparés — et un nombre mué sur disque ne passe plus."""

    def setUp(self) -> None:
        self.m = Q.mesurer()
        self.tmp = TemporaryDirectory()
        self.vers = Path(self.tmp.name)
        self.rendu = Q.ecrire_artefacts(self.m, vers=self.vers)

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def test_quatre_artefacts_present_et_fideles(self) -> None:
        self.assertEqual(sorted(self.rendu),
                         ["certificat.json", "compteurs.csv", "figures/frontieres.svg",
                          "frontieres.csv"])
        for nom, info in self.rendu.items():
            brut = (self.vers / nom).read_bytes()
            self.assertEqual(len(brut), info["octets"], nom)
            self.assertEqual(hashlib.sha256(brut).hexdigest(), info["sha256"], nom)
        cert = json.loads((self.vers / "certificat.json").read_bytes().decode("utf-8"))
        self.assertEqual(cert, Q.certificat(self.m))

    def test_csv_en_format_excel_francais(self) -> None:
        for nom in ("compteurs.csv", "frontieres.csv"):
            brut = (self.vers / nom).read_bytes()
            self.assertTrue(brut.startswith(b"\xef\xbb\xbf"), nom)
            self.assertEqual(brut.count(b"\r\n"), brut.count(b"\n"), nom)
            lignes = list(csv.reader(io.StringIO(brut.decode("utf-8-sig")), delimiter=";"))
            self.assertTrue(all(len(ligne) == len(lignes[0]) for ligne in lignes), nom)
            self.assertGreater(len(lignes), 2, nom)
        compteurs = list(csv.reader(io.StringIO(
            (self.vers / "compteurs.csv").read_bytes().decode("utf-8-sig")), delimiter=";"))
        self.assertEqual({ligne[0]: int(ligne[1]) for ligne in compteurs[1:-1]},
                         self.m["compteurs"])
        self.assertEqual(compteurs[-1][0], "Σ")
        self.assertEqual(int(compteurs[-1][1]), 256)
        frontieres = list(csv.reader(io.StringIO(
            (self.vers / "frontieres.csv").read_bytes().decode("utf-8-sig")), delimiter=";"))
        self.assertEqual(frontieres[0],
                         ["enveloppe", "source", "somme_eps", "borne_basse", "p_mesuree",
                          "recue", "ecart_en_sigma"])
        self.assertEqual({ligne[0]: ligne[5] for ligne in frontieres[1:]},
                         {"mediane_machine": "faux", "support_reel": "vrai"})
        self.assertEqual({ligne[0]: float(ligne[3].replace(",", "."))
                          for ligne in frontieres[1:]}["support_reel"], AUDIT["borne_support"])

    def test_svg_ne_porte_aucun_mot_en_langue(self) -> None:
        brut = (self.vers / "figures/frontieres.svg").read_bytes()
        self.assertEqual(brut.count(b"\r"), 0)
        self.assertIsNone(re.search(r"[A-Za-zÀ-ÿ]{4,}", re.sub(r"<[^>]+>", " ",
                                                                brut.decode("utf-8"))))
        self.assertIsNone(re.search(r"[\u0600-\u06FF]", brut.decode("utf-8")))
        self.assertEqual(brut.decode("utf-8").count("<rect"), 4)
        for nombre in ("0.914062", "0.911431", "0.925897"):
            self.assertIn(nombre, brut.decode("utf-8"), nombre)

    def test_un_nombre_mue_sur_disque_ne_passe_plus(self) -> None:
        chemin = self.vers / "certificat.json"
        brut = chemin.read_bytes()
        self.assertIn(b"0.9140625", brut)
        chemin.write_bytes(brut.replace(b"0.9140625", b"0.9140626", 1))
        self.assertNotEqual(chemin.read_bytes(), Q.octets_certificat(Q.certificat(self.m)))
        self.assertNotEqual(hashlib.sha256(chemin.read_bytes()).hexdigest(),
                            self.rendu["certificat.json"]["sha256"])


class TestConfidentialite(unittest.TestCase):
    """Le compte n'apparaît pas ; seul son préfixe d'empreinte circule."""

    def test_aucun_identifiant_de_compte_dans_ce_qui_sort(self) -> None:
        chemins = [Q.SOURCES / nom for nom in Q.PUBLIES]
        chemins += [Q.DOSSIER / "SOURCES_ET_PREDECESSEURS.md"]
        chemins += [Q.ARTEFACTS / "certificat.json", Q.ARTEFACTS / "compteurs.csv",
                    Q.ARTEFACTS / "frontieres.csv", Q.ARTEFACTS / "figures" / "frontieres.svg"]
        vus = 0
        for chemin in chemins:
            if not chemin.exists():
                continue
            vus += 1
            self.assertNotIn(JETON_COMPTE, chemin.read_bytes().decode("utf-8", "replace"),
                             chemin.name)
        self.assertGreaterEqual(vus, 9)
        module = (Q.DOSSIER / "qpu_distant_base.py").read_text(encoding="utf-8")
        self.assertEqual(module.count(JETON_COMPTE), 1,
                         "le motif ne doit servir qu'à compter les fuites")

    def test_la_redaction_de_l_archive_est_attestee(self) -> None:
        reg = Q.registre()
        self.assertIn("user_id", reg["redaction"]["motif"])
        self.assertEqual(len(reg["redaction"]["empreinte_compte_sha256_12"]), 12)
        self.assertEqual(reg["redaction"]["archive_originale_non_publiee"]["statut"].count(
            "non reproductible"), 1)
        self.assertEqual(reg["redaction"]["archive_originale_non_publiee"]["sha256_zip"],
                         AUDIT["sha256_zip"])
        self.assertIs(reg["redaction"]["bloc_qpy_conserve"], True)
        self.assertIs(reg["redaction"]["membre_result_publie_verbatim"], True)


class TestStructure(unittest.TestCase):
    """Dix équations, dix contrôles, une racine, des statuts honnêtes, pas de réseau."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.m = Q.mesurer()
        cls.eqs = Q.equations(cls.m)
        cls.cs = Q.controles(cls.m)
        cls.cert = Q.certificat(cls.m)

    def test_dix_equations_aux_champs_complets(self) -> None:
        self.assertEqual([x["id"] for x in self.eqs], [f"EQ-{i:02d}" for i in range(1, 11)])
        for x in self.eqs:
            for cle in ("id", "chemin", "formule", "resultat", "statut", "limite", "detail",
                        "couche", "piliers", "depend_de", "fonde_hors_du_dossier"):
                self.assertIn(cle, x, f"{x['id']}:{cle}")
            self.assertTrue(x["limite"], f"{x['id']} affiche un résultat sans limite")
            self.assertIn("qpu_distant_base.py", x["chemin"])
            self.assertEqual(x["piliers"], ["P1 UNITE", "P2 BORNE", "P3 CONFRONTATION",
                                           "P4 TRANSMISSION"])
            self.assertEqual(x["couche"], "S2 REGULARITE")
            self.assertIn(x["statut"], ("OPÉRATIONNEL", "SIMULÉ", "SPÉCIFIÉ"))

    def test_dependances_antecedeantes_et_sans_cycle(self) -> None:
        ordre = [x["id"] for x in self.eqs]
        for x in self.eqs:
            self.assertNotIn(x["id"], x["depend_de"])
            self.assertTrue(all(d in ordre[:ordre.index(x["id"])] for d in x["depend_de"]),
                            f"{x['id']} dépend d'une équation plus tardive")

    def test_controles_adosses_aux_equations(self) -> None:
        self.assertEqual([c["id"] for c in self.cs], [f"C{i:02d}" for i in range(1, 11)])
        eqs = {x["id"]: x for x in self.eqs}
        for c in self.cs:
            self.assertEqual(c["limite"], eqs["EQ-" + c["id"][1:]]["limite"])
            self.assertTrue(c["attendu"] and c["obtenu"], c["id"])

    def test_racine_merkle_recalculee_depuis_les_noeuds_publies(self) -> None:
        noeuds = self.cert["equations"]
        self.assertEqual(len(noeuds), 10)
        for n in noeuds:
            self.assertIsNone(n["resultat"])
            self.assertIsNone(n["detail"])
            self.assertIsNone(n["limite"])
        niveau = [hashlib.sha256(json.dumps(n, sort_keys=True, ensure_ascii=False)
                                 .encode("utf-8")).hexdigest() for n in noeuds]
        while len(niveau) > 1:
            niveau = [hashlib.sha256((niveau[i] + (niveau[i + 1] if i + 1 < len(niveau)
                                                   else niveau[i])).encode("utf-8")).hexdigest()
                      for i in range(0, len(niveau), 2)]
        self.assertEqual(niveau[0], self.cert["racine_merkle_sha256"])

    def test_certificat_porte_les_limites_et_le_statut_du_qubit(self) -> None:
        portee = self.cert["portee_et_limites"]
        self.assertIs(portee["qubit_physique_local"], False)
        self.assertIs(portee["reseau_appelle_par_ce_module"], False)
        self.assertEqual(portee["executions_locales"], 0)
        self.assertEqual(portee["predictions_al_mizan_testees"], 0)
        self.assertEqual(portee["ecritures_hors_artefacts"], 0)
        self.assertEqual(len(portee["enonces"]), 4)
        corps = json.dumps(self.cert, ensure_ascii=False)
        for mot in INTERDITS:
            self.assertNotIn(mot, corps, mot)

    def test_statuts_par_label_de_l_audit(self) -> None:
        con = Q.resoudre()["conclusion"]
        self.assertEqual(con["statuts_par_label"],
                         {"OPÉRATIONNEL": 6, "SIMULÉ": 1, "SPÉCIFIÉ": 3})
        self.assertEqual(con["controles_verts"], 10)
        self.assertEqual(con["controles_total"], 10)
        self.assertIs(con["verdict_enveloppes"]["mediane_machine"], False)
        self.assertIs(con["verdict_enveloppes"]["support_reel"], True)

    def test_bibliotheque_standard_seule_et_aucun_reseau(self) -> None:
        source = (Q.DOSSIER / "qpu_distant_base.py").read_text(encoding="utf-8")
        importes = set()
        for n in ast.walk(ast.parse(source)):
            if isinstance(n, ast.Import):
                importes |= {a.name.split(".")[0] for a in n.names}
            elif isinstance(n, ast.ImportFrom) and n.module:
                importes.add(n.module.split(".")[0])
        self.assertEqual(importes - STDLIB, set(), importes - STDLIB)
        # « qiskit » et « numpy » ont le droit d'être nommés dans les limites : ce qui est
        # interdit, c'est qu'ils soient importés ou que le module ouvre un socket.
        for motif in ("requests", "urllib", "socket", "httpx", "subprocess", "smtplib",
                      "ftplib", "asyncio"):
            self.assertNotIn(motif, importes, motif)
        for motif in ("urlopen", "socket.", "subprocess.", "os.system", "requests.get",
                      "import qiskit", "from qiskit", "import numpy", "from numpy"):
            self.assertNotIn(motif, source, motif)
        appels = {n.func.id for n in ast.walk(ast.parse(source))
                  if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)}
        for interdit in ("eval", "exec", "compile", "__import__", "input"):
            self.assertNotIn(interdit, appels, interdit)

    def test_determinisme_deux_rejeux_identiques(self) -> None:
        self.assertEqual(Q.certificat(Q.mesurer())["racine_merkle_sha256"],
                         Q.certificat(Q.mesurer())["racine_merkle_sha256"])
        self.assertEqual(Q.octets_certificat(Q.certificat(self.m)),
                         Q.octets_certificat(Q.certificat(self.m)))
        self.assertEqual(Q.octets_svg(self.m), Q.octets_svg(self.m))
        self.assertEqual(Q.octets_frontieres(self.m), Q.octets_frontieres(self.m))

    def test_sources_toutes_tablees_et_sans_surplus(self) -> None:
        e = self.m["empreintes_des_sources"]
        self.assertEqual(sorted(e["hors_table"]), [])
        self.assertEqual(sorted(k for k, v in e.items() if isinstance(v, dict)),
                         sorted(Q.PUBLIES))
        self.assertTrue(all(v["ok"] for k, v in e.items() if isinstance(v, dict)))
        for nom, v in e.items():
            if not isinstance(v, dict):
                continue
            self.assertEqual(v["sha256"], sha_par_blocs(Q.SOURCES / nom), nom)
            self.assertEqual(v["octets"], (Q.SOURCES / nom).stat().st_size, nom)

    def test_registre_et_result_s_accordent_sur_le_circuit(self) -> None:
        reg = self.m["registre"]
        releve: dict = {}
        for g in reg["portes"]:
            releve[g["nom"]] = releve.get(g["nom"], 0) + 1
        self.assertEqual(dict(sorted(releve.items())), self.m["compte_portes"])
        self.assertEqual(reg["circuit"]["operations"], len(reg["portes"]))
        self.assertEqual(reg["circuit"]["clbits"], self.m["lecture"]["num_bits"])
        self.assertEqual(reg["circuit"]["qubits_registre"], 156)
        self.assertEqual(reg["job"]["id"], "dbpkmr0ou4as73ctrm80")
        self.assertEqual(reg["job"]["backend"], "ibm_marrakesh")
        self.assertEqual(reg["job"]["tirs"], self.m["lecture"]["tirs_declares"])
        self.assertEqual(self.m["compte_portes"], {"cz": 1, "measure": 2, "rz": 6, "sx": 3})


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    unittest.main(verbosity=2)
