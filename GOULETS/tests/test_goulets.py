# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2026 IMAM8MAHDI / Astro-Code Ecosystem
# SPDX-License-Identifier: GPL-3.0-only OR AGPL-3.0-only
"""Tests du dossier GOULETS — six instantanés relus, bornes re-mesurées par une autre voie.

Sept exigences, dans l'ordre :

    1. les nombres publiés sont re-mesurés ici par une écriture différente : le jour du
       Pacifique est refait par une table de bornes écrite en dur pour 2026 (et non par la
       règle en dimanches du module), l'empreinte vient d'une digestion par blocs de 4096
       octets, le taux d'emploi est refait en `Fraction` exacte, la marge de disque en
       arithmétique entière (`libre × n // octets`), la somme des octets du stock par
       `functools.reduce` ;
    2. la règle d'heure d'été est contrôlée aux quatre instants de bascule, dans les deux
       sens, et les deux voies rendent le même jour pour chaque publication mesurée ;
    3. non-vacuité : dix mutations, une par contrôle, chacune exigeant un message d'obtenu
       différent et ne faisant rougir que sa propre ligne — plus un octet ajouté sur disque,
       que la table d'empreintes ne peut pas absorber ;
    4. les quatre artefacts sont écrits dans un répertoire temporaire, relus (`json`,
       `csv.reader`, regex pour le SVG), comparés au certificat, et un nombre mué sur disque
       ne passe plus la relecture ;
    5. les deux CSV tiennent le format annoncé : BOM, « ; », CRLF, virgule décimale, et la
       ligne Σ de `cadence.csv` somme aux deux calendriers ; la figure ne mélange pas deux
       unités ;
    6. confidentialité : aucun chemin d'hôte, aucun jeton, aucune trace du journal dans ce
       qui est publié, dans les artefacts, dans la documentation du dossier ou dans le module ;
    7. structure et langage : dix équations plus dix contrôles, racine Merkle recalculée,
       imports de la bibliothèque standard seule, aucun appel réseau, et le mot « inarrêtable »
       n'apparaît que comme citation de la demande, jamais comme revendication.

Bibliothèque standard seule.
    cd ZENODO_DEPOT_ALMIZAN && py -3 -m unittest GOULETS.tests.test_goulets -v
"""

import ast
import copy
import csv
import functools
import hashlib
import io
import json
import re
import sys
import unittest
from datetime import date, datetime, timedelta, timezone
from fractions import Fraction
from pathlib import Path
from tempfile import TemporaryDirectory

RACINE_DEPOT = Path(__file__).resolve().parents[2]
if str(RACINE_DEPOT) not in sys.path:
    sys.path.insert(0, str(RACINE_DEPOT))

from GOULETS import goulets_base as G                                     # noqa: E402

# Voie indépendante pour le Pacifique : les deux bornes 2026 sont écrites en dur ici, à
# l'envers de la règle en dimanches du module. Elles couvrent toute la fenêtre mesurée
# (2026-10-25 au 2026-11-10) ; avant mars, la table rend UTC-7 par défaut, ce qu'aucune
# publication de l'instantané ne rencontre.
BASCULES_2026 = ((datetime(2026, 3, 8, 10, tzinfo=timezone.utc), -7),
                 (datetime(2026, 11, 1, 9, tzinfo=timezone.utc), -8))
STDLIB = {"__future__", "collections", "datetime", "hashlib", "json", "pathlib", "sys",
          "typing"}
INTERDITS = ("prouvé", "démontré", "INVIOLABLE", "certifié", "100 %", "universel", "garanti",
             "certain")
FUITES = ("Administrateur", ".qoder", "C:\\Users", "C:/Users", "AIza", "ya29.", "Bearer",
          "access_token", "refresh_token", "client_secret", "vibe_videos/")
CHAMPS_EQ = ("id", "chemin", "formule", "resultat", "statut", "limite", "detail", "couche",
             "piliers", "depend_de", "fonde_hors_du_dossier")


def sha_par_blocs(chemin: Path, taille: int = 4096) -> str:
    """Digestion bloc à bloc : une autre écriture que le `read_bytes` du module."""
    h = hashlib.sha256()
    with chemin.open("rb") as flux:
        while True:
            morceau = flux.read(taille)
            if not morceau:
                return h.hexdigest()
            h.update(morceau)


def jour_pacifique_en_dur(instant_utc: datetime) -> date:
    """Le décalage de la dernière borne franchie, None avant la première (alors UTC-7)."""
    heures = BASCULES_2026[0][1]
    for borne, h in BASCULES_2026:
        if instant_utc >= borne:
            heures = h
    return (instant_utc + timedelta(hours=heures)).date()


def instants_bruts() -> list:
    out = []
    for p in G.youtube()["publications"]:
        i = datetime.fromisoformat(p["publie_le_utc"].replace("Z", "+00:00"))
        out.append(i if i.tzinfo else i.replace(tzinfo=timezone.utc))
    return sorted(out)


class TestRelecture(unittest.TestCase):
    """Les nombres publiés sont re-mesurés, pas acceptés sur parole."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.m = G.mesurer()
        cls.eqs = {x["id"]: x for x in G.equations(cls.m)}
        cls.cs = {c["id"]: c for c in G.controles(cls.m)}
        cls.cert = G.certificat(cls.m)

    def test_01_tous_les_controles_verts(self) -> None:
        self.assertEqual(len(self.cs), 10)
        self.assertTrue(all(c["ok"] for c in self.cs.values()),
                        [c["id"] for c in self.cs.values() if not c["ok"]])
        self.assertTrue(G.verifier(G.resoudre()))

    def test_02_jours_du_pacifique_refaits_par_la_table_en_dur(self) -> None:
        comptes: dict = {}
        for i in instants_bruts():
            cle = jour_pacifique_en_dur(i).isoformat()
            comptes[cle] = comptes.get(cle, 0) + 1
        self.assertEqual(dict(sorted(comptes.items())), self.m["cadence"]["jours_pacifique"])
        self.assertEqual(sorted(comptes.values(), reverse=True), [10, 8, 4, 1])

    def test_03_emprise_et_lambda_refaits_separement(self) -> None:
        instants = instants_bruts()
        jours = [jour_pacifique_en_dur(i) for i in instants]
        emprise = (max(jours) - min(jours)).days + 1
        self.assertEqual(emprise, self.m["cadence"]["emprise_jours_pacifique"])
        self.assertEqual(emprise, 17)
        self.assertEqual(len(instants), self.m["cadence"]["publiees"])
        self.assertEqual(Fraction(len(instants), emprise), Fraction(23, 17))
        self.assertAlmostEqual(self.m["cadence"]["lambda_par_jour_pacifique"],
                               float(Fraction(23, 17)), places=15)
        self.assertEqual(self.m["cadence"]["jours_actifs_pacifique"], len(set(jours)))
        self.assertAlmostEqual(self.m["cadence"]["devoir"], float(Fraction(4, 17)), places=15)

    def test_04_taux_d_emploi_refait_en_fraction_exacte(self) -> None:
        emp = self.m["emploi"]
        self.assertEqual(Fraction(23, 17) / 10, Fraction(23, 170))
        self.assertAlmostEqual(emp["taux_emploi_effectif"], float(Fraction(23, 170)), places=15)
        self.assertAlmostEqual(emp["taux_emploi_declare"], float(Fraction(23, 17) / 99),
                               places=15)
        self.assertEqual(emp["borne_effective_par_jour"], 10)
        self.assertEqual(emp["borne_declaree_par_jour"], 99)
        self.assertEqual(emp["rapport_des_deux_bornes"], 9.9)
        self.assertIs(emp["aucune_borne_atteinte"], True)

    def test_05_capacite_refaite_dependemment_du_bareme(self) -> None:
        q = G.quotas()
        cout = functools.reduce(
            lambda a, nom: a + q["couts_unites_par_appel"][nom], G.COMPOSANTS_PUBLICATION, 0)
        self.assertEqual(cout, 101)
        self.assertEqual(cout, self.m["capacite"]["cout_par_publication"])
        self.assertEqual(q["reserve_unites_par_jour"] // cout, 99)
        self.assertEqual(self.m["capacite"]["capacite_en_unites"], 99)
        self.assertEqual(self.m["capacite"]["plafond_appels_par_jour"], 100)
        self.assertEqual(self.m["capacite"]["capacite_declaree_par_jour"], 99)
        self.assertIn("10,000 units per day", self.m["capacite"]["citation"])
        self.assertEqual(self.m["capacite"]["reinitialisation"], "at midnight Pacific Time (PT)")

    def test_06_plafond_effectif_recompte_a_la_main(self) -> None:
        par_jour = G.journal_plafond()["par_jour_pacifique"]
        publiees = {d: v["publiees_ce_jour"] for d, v in par_jour.items()}
        refus = sorted(d for d, v in par_jour.items() if v["raisons"])
        self.assertEqual(max(v for v in publiees.values() if v > 0),
                         self.m["plafond"]["max_publiees_un_jour"])
        self.assertEqual(refus, self.m["plafond"]["jours_avec_refus"])
        self.assertEqual([d for d in refus if publiees[d] == 0], ["2026-11-08"])
        self.assertEqual(self.m["plafond"]["jours_refus_sans_publication"], ["2026-11-08"])
        self.assertIs(self.m["plafond"]["loi_temporele_etablie"], False)
        self.assertIn("uploadLimitExceeded", self.m["plafond"]["citation_raison"])
        self.assertEqual(sorted(self.m["plafond"]["raisons_rencontrees"]),
                         ["uploadLimitExceeded", "uploadThumbnailLimitExceeded"])

    def test_07_octets_du_stock_refaits_par_reduire(self) -> None:
        lignes = G.stock()["fichiers"]
        octets = functools.reduce(lambda a, l: a + l["octets"], lignes, 0)
        self.assertEqual(octets, 6_338_999_560)
        self.assertEqual(octets, self.m["stock"]["octets"])
        self.assertEqual(len(lignes), self.m["stock"]["fichiers"])
        self.assertEqual(self.m["stock"]["durees_non_lues"], 0)
        self.assertEqual({d: v["fichiers"] for d, v in self.m["stock"]["dossiers"].items()},
                         {"vibe_videos": 74, "vibe_videos_doublons": 3,
                          "VIDEO_PROMOTION_AL_MIZAN": 1})

    def test_08_marge_de_disque_refaite_en_entiers(self) -> None:
        dis, inv = self.m["disque"], self.m["stock"]
        entier = dis["octets_libres"] * inv["fichiers"] // inv["octets"]
        self.assertEqual(entier, dis["videos_du_gabarit_acceptees"])
        self.assertEqual(entier, 436)
        self.assertGreater(dis["part_libre"], 0)
        self.assertIs(dis["appel_reussi"], True)
        self.assertIs(dis["le_stock_tient"], True)

    def test_09_horizon_des_deux_cotes(self) -> None:
        hor = self.m["horizon"]
        self.assertEqual(hor["fichiers_a_publier"], 78)
        self.assertAlmostEqual(hor["jours_au_plafond_effectif"], 78 / 10, places=12)
        self.assertAlmostEqual(hor["jours_a_cadence_tenue"], 78 * 17 / 23, places=9)
        self.assertLess(hor["jours_au_plafond_effectif"], hor["jours_a_cadence_tenue"])
        self.assertAlmostEqual(hor["jours_a_cadence_tenue"] / hor["jours_au_plafond_effectif"],
                               float(Fraction(170, 23)), places=9)

    def test_10_compteurs_d_audience_refaits(self) -> None:
        aud = self.m["audience"]
        self.assertEqual((aud["vues"], aud["videos"], aud["abonnes"]), (48, 23, 1))
        self.assertEqual(Fraction(aud["vues"], aud["videos"]), Fraction(48, 23))
        self.assertAlmostEqual(aud["vues_par_publication"], float(Fraction(48, 23)), places=12)
        self.assertIs(aud["abonnes_masques"], False)

    def test_11_horodatages_d_une_seule_prise(self) -> None:
        self.assertEqual(sorted(self.m["horodatages"]), sorted(G.PUBLIES))
        for nom, horo in self.m["horodatages"].items():
            self.assertTrue(horo.startswith("2026-11-10"), f"{nom} : {horo}")


class TestHeureDete(unittest.TestCase):
    """La règle en dimanches rend exactement les bornes 2026, dans les deux sens."""

    def test_01_dimanches_trouves(self) -> None:
        self.assertEqual(G._nieme_dimanche(2026, 3, 2), date(2026, 3, 8))
        self.assertEqual(G._nieme_dimanche(2026, 11, 1), date(2026, 11, 1))
        self.assertEqual(G._nieme_dimanche(2027, 3, 2), date(2027, 3, 14))
        self.assertEqual(G._nieme_dimanche(2027, 11, 1), date(2027, 11, 7))

    def test_02_bascules_aux_frontieres(self) -> None:
        cas = ((datetime(2026, 3, 8, 9, 59, tzinfo=timezone.utc), -8),
               (datetime(2026, 3, 8, 10, 0, tzinfo=timezone.utc), -7),
               (datetime(2026, 11, 1, 8, 59, tzinfo=timezone.utc), -7),
               (datetime(2026, 11, 1, 9, 0, tzinfo=timezone.utc), -8),
               (datetime(2026, 11, 10, 23, 22, tzinfo=timezone.utc), -8))
        for instant, heures in cas:
            with self.subTest(instant=instant.isoformat()):
                self.assertEqual(G.decalage_pacifique(instant), timedelta(hours=heures))

    def test_03_decalage_hiver_ete_attendus(self) -> None:
        self.assertEqual(G.HEURE_D_ETE, timedelta(hours=-7))
        self.assertEqual(G.HEURE_D_HIVER, timedelta(hours=-8))

    def test_04_deux_voies_sur_les_instants_publies(self) -> None:
        for i in instants_bruts():
            attendu = -8 if i >= BASCULES_2026[1][0] else -7
            self.assertEqual(G.decalage_pacifique(i), timedelta(hours=attendu), i.isoformat())
            self.assertEqual(i + G.decalage_pacifique(i), i + timedelta(hours=attendu))


class TestNonVacuite(unittest.TestCase):
    """Une mutation par contrôle : la grille doit rougir une fois et une seule par ligne."""

    def setUp(self) -> None:
        self.m = G.mesurer()
        self.base = {c["id"]: c["obtenu"] for c in G.controles(self.m)}

    def applique(self, muter) -> dict:
        copie = copy.deepcopy(self.m)
        muter(copie)
        return {c["id"]: c for c in G.controles(copie)}

    def test_chaque_controle_rougit_une_fois(self) -> None:
        cas = {
            "C01": lambda m: m["empreintes_des_sources"][G.PUBLIES[0]].__setitem__("ok", False),
            "C02": lambda m: m["statistiques"].__setitem__("videoCount", "24"),
            "C03": lambda m: m["cadence"].__setitem__("identiques", True),
            "C04": lambda m: m["durees"].__setitem__("verrou_fournisseur", "disallowed"),
            "C05": lambda m: m["capacite"].__setitem__("cout_par_publication", 100),
            "C06": lambda m: m["plafond"].__setitem__("jours_refus_sans_publication", []),
            "C07": lambda m: m["emploi"].__setitem__("taux_emploi_effectif", 0.001),
            "C08": lambda m: m["audience"].__setitem__("abonnes", 0),
            "C09": lambda m: m["stock"].__setitem__("durees_non_lues", 1),
            "C10": lambda m: m["disque"].__setitem__("videos_du_gabarit_acceptees", 10),
        }
        for id_, muter in cas.items():
            with self.subTest(id_=id_):
                rendu = self.applique(muter)
                self.assertFalse(rendu[id_]["ok"], f"{id_} passe encore après mutation")
                self.assertNotEqual(rendu[id_]["obtenu"], self.base[id_],
                                    f"{id_} mute sans changer le message d'obtenu")
                for autre in cas:
                    if autre != id_:
                        self.assertTrue(rendu[autre]["ok"], f"{autre} rougit pour {id_}")

    def test_un_octet_ajoute_sur_disque_rougit_la_table(self) -> None:
        """Le contrôle d'empreinte lit les octets : un espace final ne passe pas."""
        ancien = G._octets
        G._octets = lambda nom: ancien(nom) + b" "
        try:
            rendu = {c["id"]: c for c in G.controles(G.mesurer())}
        finally:
            G._octets = ancien
        self.assertFalse(rendu["C01"]["ok"])
        self.assertNotEqual(rendu["C01"]["obtenu"], self.base["C01"])
        self.assertTrue(all(c["ok"] for id_, c in rendu.items() if id_ != "C01"),
                        [id_ for id_, c in rendu.items() if id_ != "C01" and not c["ok"]])


class TestArtefacts(unittest.TestCase):
    """Écrits dans un dossier temporaire, relus, comparés — un nombre mué ne passe plus."""

    def setUp(self) -> None:
        self.m = G.mesurer()
        self.tmp = TemporaryDirectory()
        self.vers = Path(self.tmp.name)
        self.rendu = G.ecrire_artefacts(self.m, vers=self.vers)

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def test_quatre_artefacts_present_et_fideles(self) -> None:
        self.assertEqual(sorted(self.rendu),
                         ["bornes.csv", "cadence.csv", "certificat.json", "figures/bornes.svg"])
        for nom, info in self.rendu.items():
            brut = (self.vers / nom).read_bytes()
            self.assertEqual(len(brut), info["octets"], nom)
            self.assertEqual(hashlib.sha256(brut).hexdigest(), info["sha256"], nom)
        self.assertEqual(json.loads((self.vers / "certificat.json").read_bytes()
                                    .decode("utf-8")), G.certificat(self.m))

    def test_cadence_csv_en_format_excel_francais(self) -> None:
        brut = (self.vers / "cadence.csv").read_bytes()
        self.assertTrue(brut.startswith(b"\xef\xbb\xbf"))
        self.assertEqual(brut.count(b"\r\n"), brut.count(b"\n"))
        lignes = list(csv.reader(io.StringIO(brut.decode("utf-8-sig")), delimiter=";"))
        self.assertEqual(lignes[0], ["jour_utc_ou_pacifique", "publiees_jour_utc",
                                     "publiees_jour_pacifique", "refus_enregistre"])
        self.assertTrue(all(len(l) == 4 for l in lignes), lignes)
        self.assertEqual(lignes[-1], ["Σ", "23", "23", "4"])
        jours = {l[0]: (int(l[1]), int(l[2])) for l in lignes[1:-1]}
        self.assertEqual(jours["2026-11-04"], (0, 4))
        self.assertEqual(jours["2026-11-05"], (4, 0))
        self.assertEqual(jours["2026-11-08"], (0, 0))
        refus = {l[0] for l in lignes[1:-1] if l[3] == "vrai"}
        self.assertEqual(refus, set(self.m["plafond"]["jours_avec_refus"]))

    def test_bornes_csv_porte_la_condition_de_rupture(self) -> None:
        lignes = list(csv.reader(io.StringIO(
            (self.vers / "bornes.csv").read_bytes().decode("utf-8-sig")), delimiter=";"))
        self.assertEqual(lignes[0], ["borne", "valeur", "unite", "source", "cadre", "rompee_si"])
        self.assertEqual(len(lignes), 9)
        for l in lignes[1:]:
            self.assertTrue(l[5], f"borne {l[0]} sans condition de rupture")
            self.assertIn(l[3], ("déclaré", "mesuré"), l[0])
        valeurs = {l[0]: l[1] for l in lignes[1:]}
        self.assertEqual(valeurs["capacite_unites"], "99")
        self.assertEqual(valeurs["plafond_effectif"], "10")
        self.assertEqual(valeurs["cadence_tenue"], "1,352941")
        self.assertEqual(valeurs["marge_disque"], "436")
        self.assertEqual(valeurs["duree"], "900,0")

    def test_svg_ne_porte_aucun_mot_en_langue(self) -> None:
        brut = (self.vers / "figures/bornes.svg").read_bytes()
        self.assertEqual(brut.count(b"\r"), 0)
        texte = re.sub(r"<[^>]+>", " ", brut.decode("utf-8"))
        self.assertIsNone(re.search(r"[A-Za-zÀ-ÿ]{4,}", texte), texte)
        self.assertIsNone(re.search(r"[\u0600-\u06FF]", brut.decode("utf-8")))
        self.assertEqual(brut.decode("utf-8").count("<rect"), 4)
        for nombre in ("99.00", "10.00", "1.35"):
            self.assertIn(nombre, brut.decode("utf-8"), nombre)

    def test_la_figure_ne_melange_pas_deux_unites(self) -> None:
        texte = (self.vers / "figures/bornes.svg").read_bytes().decode("utf-8")
        self.assertNotIn("436", texte, "la marge de disque se compte en vidéos, pas en /jour")

    def test_un_nombre_mue_sur_disque_ne_passe_plus(self) -> None:
        chemin = self.vers / "certificat.json"
        brut = chemin.read_bytes()
        self.assertIn(b'"capacite_declaree_par_jour": 99', brut)
        chemin.write_bytes(brut.replace(b'"capacite_declaree_par_jour": 99',
                                        b'"capacite_declaree_par_jour": 98', 1))
        self.assertNotEqual(chemin.read_bytes(), G.octets_certificat(G.certificat(self.m)))
        self.assertNotEqual(hashlib.sha256(chemin.read_bytes()).hexdigest(),
                            self.rendu["certificat.json"]["sha256"])


class TestConfidentialite(unittest.TestCase):
    """Rien de l'hôte, rien du journal, rien d'un jeton ne sort dans ce qui est publié."""

    def test_aucune_fuite_dans_ce_qui_sort(self) -> None:
        chemins = [G.SOURCES / nom for nom in G.PUBLIES]
        chemins += [G.SOURCES / G.F_EMPREINTES]
        chemins += [G.DOSSIER / "SOURCES_ET_PREDECESSEURS.md"]
        chemins += [G.ARTEFACTS / "certificat.json", G.ARTEFACTS / "cadence.csv",
                    G.ARTEFACTS / "bornes.csv", G.ARTEFACTS / "figures" / "bornes.svg"]
        vus = 0
        for chemin in chemins:
            if not chemin.exists():
                continue
            vus += 1
            texte = chemin.read_bytes().decode("utf-8", "replace")
            for motif in FUITES:
                self.assertNotIn(motif, texte, f"{chemin.name} porte {motif !r}")
        self.assertGreaterEqual(vus, 11)

    def test_le_module_ne_nomme_ni_hote_ni_journal(self) -> None:
        source = (G.DOSSIER / "goulets_base.py").read_text(encoding="utf-8")
        for motif in FUITES:
            self.assertNotIn(motif, source, motif)

    def test_seul_l_identifiant_public_de_chaine_circule(self) -> None:
        corps = json.dumps(G.certificat(G.mesurer()), ensure_ascii=False)
        self.assertIn("UCeMs4f4J13F5fvJF1Xt8Nng", corps)
        for motif in ("ya29", "AIza", "token"):
            self.assertNotIn(motif, corps, motif)


class TestStructure(unittest.TestCase):
    """Dix équations, dix contrôles, une racine, des statuts honnêtes, pas de réseau."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.m = G.mesurer()
        cls.eqs = G.equations(cls.m)
        cls.cs = G.controles(cls.m)
        cls.cert = G.certificat(cls.m)

    def test_dix_equations_aux_champs_complets(self) -> None:
        self.assertEqual([x["id"] for x in self.eqs], [f"EQ-{i:02d}" for i in range(1, 11)])
        for x in self.eqs:
            for cle in CHAMPS_EQ:
                self.assertIn(cle, x, f"{x['id']}:{cle}")
            self.assertGreaterEqual(len(x["limite"].strip()), 40, f"{x['id']} limite trop courte")
            self.assertIn("→", x["chemin"], x["id"])
            self.assertIn("goulets_base.py", x["chemin"], x["id"])
            self.assertEqual(x["piliers"], ["P1 UNITE", "P2 BORNE", "P3 CONFRONTATION",
                                           "P4 TRANSMISSION"])
            self.assertEqual(x["couche"], "S1 MESURABLE")
            self.assertIn(x["statut"], ("OPÉRATIONNEL", "SIMULÉ", "SPÉCIFIÉ"))
            self.assertTrue(x["resultat"], x["id"])

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
            self.assertEqual(c["limite"], eqs["EQ-" + c["id"][1:]]["limite"], c["id"])
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
            if len(niveau) % 2:
                niveau.append(niveau[-1])
            niveau = [hashlib.sha256((a + b).encode("utf-8")).hexdigest()
                      for a, b in zip(niveau[0::2], niveau[1::2])]
        self.assertEqual(niveau[0], self.cert["racine_merkle_sha256"])

    def test_racine_d_empreintes_refaite_par_blocs(self) -> None:
        table = json.loads((G.SOURCES / G.F_EMPREINTES).read_bytes().decode("utf-8"))["fichiers"]
        e = self.m["empreintes_des_sources"]
        self.assertEqual(sorted(k for k, v in e.items() if isinstance(v, dict)),
                         sorted(table))
        for nom, info in table.items():
            recalcule = sha_par_blocs(G.SOURCES / nom)
            self.assertEqual(recalcule, info["sha256"], nom)
            self.assertEqual(recalcule, e[nom]["sha256"], nom)
            self.assertEqual((G.SOURCES / nom).stat().st_size, info["octets"], nom)
        racine = hashlib.sha256("".join(f"{k}{sha_par_blocs(G.SOURCES / k)}"
                                        for k in sorted(table)).encode("utf-8")).hexdigest()
        self.assertEqual(racine, e["racine_declaree"])
        self.assertEqual(racine, e["racine_recalculee"])
        self.assertEqual(sorted(e["hors_table"]), [])

    def test_six_sources_tablees_et_une_seule_date_de_prise(self) -> None:
        self.assertEqual(len(G.PUBLIES), 6)
        for nom in G.PUBLIES:
            self.assertTrue((G.SOURCES / nom).exists(), nom)
            self.assertEqual(json.loads((G.SOURCES / nom).read_bytes()
                                         .decode("utf-8"))["mesure_le_utc"][:10], "2026-11-10",
                             nom)

    def test_certificat_porte_quatre_natures_et_six_enonces(self) -> None:
        portee = self.cert["portee_et_limites"]
        self.assertIs(portee["reseau_appelle_par_ce_module"], False)
        self.assertEqual(portee["ecritures_hors_artefacts"], 0)
        self.assertEqual(portee["jetons_consignes"], 0)
        self.assertEqual(portee["predictions_al_mizan_testees"], 0)
        self.assertEqual(len(portee["enonces"]), 6)
        corps = json.dumps(self.cert, ensure_ascii=False)
        for mot in INTERDITS:
            self.assertNotIn(mot, corps, mot)

    def test_le_mot_inarretable_reste_une_citation(self) -> None:
        self.assertEqual(self.cert["demande_originelle"].count("inarrêtable"), 1)
        self.assertEqual(self.cert["requalification"].count("inarrêtable"), 1)
        for cle, valeur in self.cert.items():
            if cle in ("demande_originelle", "requalification"):
                continue
            self.assertNotIn("inarrêtable", json.dumps(valeur, ensure_ascii=False), cle)

    def test_statuts_par_label_de_l_audit(self) -> None:
        con = G.resoudre()["conclusion"]
        self.assertEqual(con["statuts_par_label"],
                         {"OPÉRATIONNEL": 8, "SIMULÉ": 1, "SPÉCIFIÉ": 1})
        self.assertEqual(con["controles_verts"], 10)
        self.assertEqual(con["controles_total"], 10)
        self.assertEqual(con["bornes_par_jour"],
                         {"declaree": 99, "effective": 10, "tenue": 1.3529411764705883})
        self.assertIn("AUCUNE BORNE ATTEINTE", con["verdict_bornes"])
        self.assertEqual(con["goulots_non_plateformes"]["production_en_amont"],
                         "non mesurée par ce dossier")

    def test_bibliotheque_standard_seule_et_aucun_reseau(self) -> None:
        source = (G.DOSSIER / "goulets_base.py").read_text(encoding="utf-8")
        importes = set()
        for n in ast.walk(ast.parse(source)):
            if isinstance(n, ast.Import):
                importes |= {a.name.split(".")[0] for a in n.names}
            elif isinstance(n, ast.ImportFrom) and n.module:
                importes.add(n.module.split(".")[0])
        self.assertEqual(importes - STDLIB, set(), importes - STDLIB)
        for motif in ("requests", "urllib", "socket", "httpx", "subprocess", "smtplib",
                      "ftplib", "asyncio", "zoneinfo", "googleapiclient", "ctypes"):
            self.assertNotIn(motif, importes, motif)
        for motif in ("urlopen", "socket.", "subprocess.", "os.system", "requests.get"):
            self.assertNotIn(motif, source, motif)
        appels = {n.func.id for n in ast.walk(ast.parse(source))
                  if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)}
        for interdit in ("eval", "exec", "compile", "__import__", "input"):
            self.assertNotIn(interdit, appels, interdit)

    def test_determinisme_deux_rejeux_identiques(self) -> None:
        self.assertEqual(G.certificat(G.mesurer())["racine_merkle_sha256"],
                         G.certificat(G.mesurer())["racine_merkle_sha256"])
        m = self.m
        self.assertEqual(G.octets_certificat(G.certificat(m)),
                         G.octets_certificat(G.certificat(m)))
        self.assertEqual(G.octets_cadence(m), G.octets_cadence(m))
        self.assertEqual(G.octets_bornes(m), G.octets_bornes(m))
        self.assertEqual(G.octets_svg(m), G.octets_svg(m))

    def test_la_source_video_n_est_rattachee_que_par_ses_formes(self) -> None:
        v = self.m["video"]
        self.assertTrue(v["titre"].startswith("Le dernier avertissement"))
        self.assertEqual(v["auteur"], "Le Futurologue")
        self.assertEqual(v["duree_s"], 2523)
        self.assertEqual(v["chapitres"], 4)
        self.assertIs(v["croissants"], True)
        self.assertIs(v["dernier_dans_la_duree"], True)
        self.assertEqual(v["transcript"], "non sondé")
        self.assertIn("AUCUNE phrase", v["avertissement"])
        self.assertNotIn("Introduction", json.dumps(self.cert, ensure_ascii=False))


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    unittest.main(verbosity=2)
