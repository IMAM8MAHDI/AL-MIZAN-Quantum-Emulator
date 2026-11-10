# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2026 IMAM8MAHDI / Astro-Code Ecosystem
# SPDX-License-Identifier: GPL-3.0-only OR AGPL-3.0-only
"""Tests du dossier REDACTION — la mesure est re-dérivée et chaque contrôle est éprouvé vide.

Six exigences, dans l'ordre :
    1. la couverture numérique des trois langues est re-calculée ICI par une écriture différente
       (découpage par indices de chaîne, `collections.Counter`) : 89/56/55 avant, 89/89/89 après ;
    2. l'artefact d'instrument est re-produit : lire les entités HTML sans les décoder rend
       exactement 49 et 48, ce que la session de sonde avait annoncé ;
    3. non-vacuité : sur une copie mutée du corpus, le contrôle nommé ROUGIT — retirer la span
       calcul, changer un nombre, effacer un chemin, toucher un obtenu, remplacer la coupe arabe,
       raccourcir toute la prose, retirer une page, ajouter une balise `<dfn>`, retirer la garde
       du moteur ;
    4. les verdicts défavorables restent écrits : 89 lignes de contrôle non traduites, zéro balise
       de définition, des phrases au-dessus du seuil, et aucune de ces lignes n'est déclarée réglée ;
    5. la vidéo n'a fourni que des titres : horodatages croissants, dernier chapitres sous la
       durée, aucun contenu parlé cité, attribution « déclaré · non vérifié » ;
    6. déterminisme, racine Merkle et artefacts : deux exécutions concordent, changer un nœud
       change la racine, le CSV reste UTF-8 BOM, séparateur « ; », CRLF, treize colonnes.

Stdlib uniquement.
    cd ZENODO_DEPOT_ALMIZAN && py -3 -m unittest REDACTION.tests.test_redaction -v
"""

import collections
import copy
import hashlib
import html
import json
import re
import shutil
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

RACINE_DEPOT = Path(__file__).resolve().parents[2]
if str(RACINE_DEPOT) not in sys.path:
    sys.path.insert(0, str(RACINE_DEPOT))

from REDACTION import redaction_mizan as RD                            # noqa: E402

CERT = RD.certificat()
EQS = {e["id"]: e for e in RD.equations(CERT)}
CS = {c["id"]: c for c in RD.controles(EQS, CERT)}
HORS_NOEUDS = {"source", "empreinte_execution", "rejoue_identique", "limites", "attribution",
               "racine_merkle_sha256"}
CELLULE = re.compile(r"(?s)<t[dh][^>]*>(.*?)</t[dh]>")
QUATRIEME_TAG = re.compile(r"(?s)(<t[dh][^>]*>)(.*?)(</t[dh]>)")


# ─── voie indépendante de mesure (aucune fonction du module réutilisée) --------

def span_brute(cellule: str, nom: str) -> str:
    """Contenu brut d'une span, par indices — pas de regex, pas de `_brut`."""
    marque = '<span class="' + nom + '">'
    i = cellule.find(marque)
    if i < 0:
        return ""
    j = cellule.find("</span>", i)
    return re.sub(r"\s+", " ", cellule[i + len(marque):j]).strip()


def compte_nombres(texte: str, decoder: bool = True) -> collections.Counter:
    """Nombres d'un texte brut de span. `decoder` ne pilote que les entités HTML ;
    la virgule décimale française est normalisée dans les deux routes."""
    if decoder:
        texte = html.unescape(texte)
    out: collections.Counter = collections.Counter()
    for n in re.findall(r"\d[\d.,]*", texte):
        n = n.strip(".,").replace(",", ".")
        if n:
            out[n] += 1
    return out


def inclut(grand: collections.Counter, petit: collections.Counter) -> bool:
    return all(grand.get(k, 0) >= v for k, v in petit.items())


def trios_independants() -> dict:
    trio: dict = {}
    for p in sorted(RACINE_DEPOT.glob("*/artefacts/pages/*.html")):
        rel = p.relative_to(RACINE_DEPOT).as_posix()
        base = re.sub(r"_(en|ar)$", "", rel.split("/")[-1][:-5])
        lg = "ar" if rel.endswith("_ar.html") else "en" if rel.endswith("_en.html") else "fr"
        trio.setdefault(f"{rel.split('/')[0]}/{base}", {})[lg] = rel
    return trio


def quatrieme_cellule(texte: str, cid: str) -> str:
    for mor in texte.split("<tr>")[1:]:
        c = CELLULE.findall(mor.split("</tr>")[0])
        if c and re.sub(r"\s+", "", c[0]) == cid:
            return c[3] if len(c) > 3 else ""
    return ""


def ids_equations(texte: str) -> list:
    out = []
    for mor in texte.split("<tr>")[1:]:
        c = CELLULE.findall(mor.split("</tr>")[0])
        if c:
            cid = re.sub(r"\s+", "", c[0])
            if re.match(r"^EQ-\d+$", cid):
                out.append(cid)
    return out


def couverture_independante(decoder: bool = True):
    sans = dict.fromkeys(RD.LANGUES, 0)
    avec = dict.fromkeys(RD.LANGUES, 0)
    total = 0
    for chemin, d in sorted(trios_independants().items()):
        if len(d) != 3:
            continue
        texte = {lg: (RACINE_DEPOT / p).read_text(encoding="utf-8") for lg, p in d.items()}
        for cid in ids_equations(texte["fr"]):
            total += 1
            ref = compte_nombres(span_brute(quatrieme_cellule(texte["fr"], cid), "lecture"), decoder)
            for lg in RD.LANGUES:
                cel = quatrieme_cellule(texte[lg], cid)
                sans[lg] += inclut(compte_nombres(span_brute(cel, "lecture"), decoder), ref)
                avec[lg] += inclut(compte_nombres(" ".join(
                    (span_brute(cel, "lecture"), span_brute(cel, "calcul"))), decoder), ref)
    return total, sans, avec


# ─── mutation d'une ligne du fixture ------------------------------------------

def muter_ligne(texte: str, cid: str, fonction) -> str:
    """Contenu de la quatrième cellule de la ligne `cid` remplacé par `fonction(cellule)`.

    Les balises des cellules sont recopiées telles quelles : une mutation qui détruirait
    `</td>` ou `</tr>` ne prouverait rien sur le contrôle visé, elle détruirait le parsing."""
    for m in re.finditer(r"(?s)<tr>.*?</tr>", texte):
        ligne = m.group(0)
        cellules = CELLULE.findall(ligne)
        if not cellules or re.sub(r"\s+", "", cellules[0]) != cid:
            continue
        assert len(cellules) >= 4, f"{cid} : ligne à {len(cellules)} cellules"
        rang = 0

        def rendre(i):
            nonlocal rang
            rang += 1
            return i.group(1) + (fonction(i.group(2)) if rang == 4 else i.group(2)) + i.group(3)

        return texte[:m.start()] + QUATRIEME_TAG.sub(rendre, ligne) + texte[m.end():]
    raise AssertionError(f"{cid} introuvable dans le fixture")


class Fixture(unittest.TestCase):
    """Chaque test travaille sur sa propre copie des 21 pages ; le dépôt n'est pas touché."""

    def setUp(self):
        self._td = TemporaryDirectory(prefix="redaction-fixture-")
        self.racine = Path(self._td.name)
        self.pages: dict = {}
        for p in RD.pages_publiees():
            dest = self.racine / p["chemin"]
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(RD.RACINE / p["chemin"], dest)
            self.pages[p["chemin"]] = dest
        # le moteur est copié sous la même racine : les mesures qui l'ouvrent rendent
        # un chemin relatif à la racine détournée, et la baseline ne lève plus
        self.moteur = self.racine / RD.MOTEUR.relative_to(RD.RACINE)
        self.moteur.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(RD.MOTEUR, self.moteur)

    def tearDown(self):
        self._td.cleanup()

    def lire(self, chemin: str) -> str:
        return self.pages[chemin].read_text(encoding="utf-8")

    def ecrire(self, chemin: str, texte: str) -> None:
        self.pages[chemin].write_text(texte, encoding="utf-8")

    def controles(self) -> dict:
        """Re-mesure le fixture avec le module, RACINE et MOTEUR détournés, puis la rend."""
        racine0, moteur0 = RD.RACINE, RD.MOTEUR
        RD.RACINE, RD.MOTEUR = self.racine, self.moteur
        RD._LUC.clear()
        try:
            etat = RD.noeuds_certificat()
            eqs = {e["id"]: e for e in RD.equations(etat)}
            return {c["id"]: c for c in RD.controles(eqs, etat)}
        finally:
            RD.RACINE, RD.MOTEUR = racine0, moteur0
            RD._LUC.clear()


class TestReDerivation(unittest.TestCase):
    """Les deux chiffres annoncés par le dossier sont re-obtenus ici par une autre écriture."""

    def test_couverture_avant_et_apres_re_derivees(self):
        total, sans, avec = couverture_independante()
        h = CERT["harmonisation"]
        self.assertEqual(total, h["total"])
        self.assertEqual(sans, h["sans_ligne"])
        self.assertEqual(avec, h["avec_ligne"])
        self.assertEqual((total, sans, avec),
                         (89, {"fr": 89, "en": 56, "ar": 55}, {"fr": 89, "en": 89, "ar": 89}))

    def test_artefact_d_entite_re_produit(self):
        total, sans_brut, _ = couverture_independante(decoder=False)
        self.assertEqual(total, 89)
        self.assertEqual(sans_brut, CERT["harmonisation"]["sans_decodage_entites"])
        self.assertEqual(sans_brut, {"fr": 89, "en": 49, "ar": 48})

    def test_le_rang_des_badges_ne_depend_pas_de_la_langue(self):
        b = CERT["badges"]
        self.assertEqual(b["totaux_par_langue"], {"fr": 178, "en": 178, "ar": 178})
        self.assertEqual(b["trios_alignes"], b["trios"])
        self.assertTrue(set(b["exemples_mots"]["ar"]) - set(b["exemples_mots"]["fr"]),
                        "l'arabe porte d'autres mots de statut que le français")

    def test_les_lignes_de_controle_sont_comptees_depuis_le_html(self):
        lc = CERT["lignes_de_controle"]
        self.assertEqual(lc["total"], 89)
        self.assertEqual(sum(lc["par_dossier"].values()), 89)
        self.assertEqual(lc["trois_cellules_identiques"], 89)


class TestNonVacuite(Fixture):
    """Chaque mutation ci-dessous doit faire rougir le contrôle qu'elle nomme."""

    def test_baseline_du_fixture_est_verte(self):
        cs = self.controles()
        self.assertEqual(len(cs), 16)
        self.assertEqual([k for k, c in cs.items() if not c["ok"]], [],
                         "la copie conforme du corpus doit rendre les seize contrôles verts")

    def test_retirer_la_span_calcul_fait_rougir_c06(self):
        c = "ABONDANCE/artefacts/pages/agriculture_en.html"
        self.ecrire(c, RD.SPAN["calcul"].sub("", self.lire(c)))
        self.assertFalse(self.controles()["C06"]["ok"])

    def test_changer_un_nombre_de_la_ligne_calculée_fait_rougir_c07(self):
        c = "CHIFFRES/artefacts/pages/chiffres_en.html"
        self.ecrire(c, self.lire(c).replace('class="calcul">1', 'class="calcul">11', 1))
        self.assertFalse(self.controles()["C07"]["ok"])

    def test_retirer_une_page_fait_rougir_c01(self):
        self.pages["FONDATION/artefacts/pages/fondation_ar.html"].unlink()
        self.assertFalse(self.controles()["C01"]["ok"])

    def test_ajouter_une_sixieme_cellule_fait_rougir_c02(self):
        c = "ABONDANCE/artefacts/pages/eau_en.html"
        texte = self.lire(c)
        mor = next(m for m in texte.split("<tr>")[1:] if "EQ-03" in m.split("</tr>")[0])
        self.ecrire(c, texte.replace(mor, mor.replace("</tr", "<td>x</td></tr", 1), 1))
        self.assertFalse(self.controles()["C02"]["ok"])

    def test_deplacer_une_classe_de_badge_fait_rougir_c03(self):
        c = "ABONDANCE/artefacts/pages/electricite_en.html"
        self.ecrire(c, self.lire(c).replace('<span class="statut o">',
                                            '<span class="statut p">', 1))
        self.assertFalse(self.controles()["C03"]["ok"])

    def test_effacer_un_chemin_machine_fait_rougir_c04(self):
        c = "CHIFFRES/artefacts/pages/chiffres_en.html"
        self.ecrire(c, muter_ligne(self.lire(c), "EQ-17", lambda c3: RD.SPAN["chemin"].sub(
            '<span class="chemin">chemin efface</span>', c3)))
        self.assertFalse(self.controles()["C04"]["ok"])

    def test_enlever_les_nombres_d_une_lecture_fait_rougir_c05(self):
        c = "ABONDANCE/artefacts/pages/agriculture_en.html"

        def aveugle(c3):
            return RD.SPAN["lecture"].sub(
                lambda m: '<span class="lecture">' + re.sub(r"\d", "#", m.group(1)) + "</span>", c3)

        self.ecrire(c, muter_ligne(self.lire(c), "EQ-01", aveugle))
        self.assertFalse(self.controles()["C05"]["ok"])

    def test_toucher_un_obtenu_fait_rougir_c08(self):
        c = "FONDATION/artefacts/pages/fondation_en.html"
        self.ecrire(c, muter_ligne(self.lire(c), "C01", lambda c3: c3 + " (muté)"))
        self.assertFalse(self.controles()["C08"]["ok"])

    def test_raccourcir_toute_la_prose_fait_rougir_c09(self):
        for chemin in self.pages:
            self.ecrire(chemin, RD.BLOC_PROSE.sub(
                lambda m: f"<{m.group(1)}>un deux trois</{m.group(1)}>", self.lire(chemin)))
        self.assertFalse(self.controles()["C09"]["ok"])

    def test_remplacer_la_coupe_arabe_fait_rougir_c10(self):
        for chemin in [c for c in self.pages if c.endswith("_ar.html")]:
            self.ecrire(chemin, self.lire(chemin).replace("؛", "."))
        self.assertFalse(self.controles()["C10"]["ok"])

    def test_tableau_avant_toute_prose_fait_rougir_c11(self):
        for chemin in self.pages:
            self.ecrire(chemin, self.lire(chemin).replace("<body>", "<body><table></table>", 1))
        self.assertFalse(self.controles()["C11"]["ok"])

    def test_ajouter_une_balise_dfn_fait_rougir_c12(self):
        c = "ABONDANCE/artefacts/pages/index_en.html"
        self.ecrire(c, self.lire(c).replace("</body>", "<p><dfn>torsion</dfn></p></body>", 1))
        self.assertFalse(self.controles()["C12"]["ok"])

    def test_ne_pas_decoder_les_entites_fait_rougir_c16(self):
        for chemin in [c for c in self.pages if c.endswith(".html")
                       and not c.endswith(("_en.html", "_ar.html"))]:
            self.ecrire(chemin, self.lire(chemin).replace("&#x27;", "'"))
        self.assertFalse(self.controles()["C16"]["ok"])

    def test_moteur_sans_garde_fait_rougir_c13(self):
        texte = RD.MOTEUR.read_text(encoding="utf-8")
        self.assertIn("ligne calculée absente", texte)
        copie = self.racine / "moteur_mute.py"
        copie.write_text(texte.replace("ligne calculée absente", "ligne pas controlee"),
                         encoding="utf-8")
        racine0, moteur0 = RD.RACINE, RD.MOTEUR
        RD.RACINE, RD.MOTEUR = self.racine, copie
        RD._LUC.clear()
        try:
            self.assertFalse(RD.garde_moteur()["garde_de_ligne_calculee"])
            etat = RD.noeuds_certificat()
            cs = {c["id"]: c for c in RD.controles(EQS, etat)}
            self.assertFalse(cs["C13"]["ok"])
        finally:
            RD.RACINE, RD.MOTEUR = racine0, moteur0
            RD._LUC.clear()


class TestSeuilDeFormeNonVacue(unittest.TestCase):
    """La règle de forme que le module s'applique à lui-même doit pouvoir le manquer."""

    def test_une_formule_de_quarante_mots_depasse_le_seuil(self):
        eqs = copy.deepcopy(list(EQS.values()))
        eqs[0]["formule"] = "mot " * 40
        au = RD.autoforme(eqs, list(CS.values()))
        self.assertGreaterEqual(au["au_dessus_du_seuil"], 1)
        self.assertEqual(au["seuil"], RD.SEUIL_PHRASE)
        self.assertTrue(CS["C14"]["ok"], "sur le module réel, la règle est tenue")

    def test_le_seuil_n_est_derive_d_aucune_echelle_publiee(self):
        self.assertEqual(EQS["EQ-14"]["statut"], "SPÉCIFIÉ")
        self.assertIn("choix d'auteur", EQS["EQ-14"]["limite"])
        unused = CERT["source"]["ce_que_ce_module_n_utilise_pas"]
        self.assertTrue(any("Flesch" in u or "lisibilité" in u for u in unused))


class TestVerdictsDefavorables(unittest.TestCase):
    def test_le_deficit_de_traduction_reste_compte(self):
        self.assertEqual(CERT["lignes_de_controle"]["total"], 89)
        self.assertEqual(CERT["lignes_de_controle"]["titres_arabes_en_page_arabe"], 0)
        self.assertTrue(CS["C08"]["ok"],
                        "C08 est vert parce que le déficit est écrit, pas parce qu'il est vide")

    def test_aucune_definition_installee_et_c_est_ecrit(self):
        self.assertEqual(CERT["definitions"]["dfn"], 0)
        self.assertEqual(CERT["definitions"]["abbr"], 0)
        self.assertIn("aucun", CERT["definitions"]["mecanisme"])

    def test_les_ouvertures_ne_sont_pas_declarees_reglees(self):
        ou = CERT["ouvertures"]
        self.assertGreaterEqual(ou["nb"], 5)
        self.assertEqual(ou["remplies_dans_ce_lot"], 0)
        self.assertTrue(all(isinstance(l, str) and len(l) > 20 for l in ou["liste"]))

    def test_aucune_allegation_absolue_dans_les_enonces(self):
        interdits = ("compris par tous les humains", "preuve universelle", "démontré globalement",
                     "100 %", "INVIOLABLE", "intelligible pour tout le monde sans exception")
        texte = json.dumps({"limites": CERT["limites"],
                            "eq": {k: v["limite"] + v["resultat"] for k, v in EQS.items()},
                            "c": {k: v["nom"] + v["verifie"] for k, v in CS.items()}},
                           ensure_ascii=False)
        for mot in interdits:
            self.assertNotIn(mot.lower(), texte.lower(), mot)


class TestVideoEtAttribution(unittest.TestCase):
    def test_la_video_n_a_fourni_que_des_titres_de_chapitres(self):
        v = CERT["source"]["video"]
        self.assertEqual(v["id"], "iuVxYHTJrhU")
        self.assertIn("absent", v["transcript"])
        self.assertEqual(len(v["chapitres"]), 12)
        secondes = [int(c["debut"].split(":")[0]) * 60 + int(c["debut"].split(":")[1])
                    for c in v["chapitres"]]
        self.assertEqual(secondes, sorted(secondes))
        self.assertLess(secondes[0], secondes[-1])
        self.assertLessEqual(secondes[-1], v["duree_s"])
        self.assertEqual(len(v["ce_que_la_video_n_a_pas_fourni"]), 3)

    def test_l_attribution_reste_declaree_non_verifiee(self):
        self.assertIn("déclaré · non vérifié", CERT["attribution"]["statut_de_la_demande"])
        self.assertEqual(CERT["attribution"]["auteur"], CERT["source"]["auteur"])


class TestDeterminismeEtSceau(unittest.TestCase):
    def test_deux_executions_meme_empreinte(self):
        self.assertTrue(CERT["rejoue_identique"])
        self.assertEqual(RD.certificat()["empreinte_execution"], CERT["empreinte_execution"])

    def test_la_racine_change_si_un_noeud_change(self):
        def racine(noeuds):
            return hashlib.sha256(RD.canonique(
                {k: hashlib.sha256(RD.canonique(noeuds[k])).hexdigest()
                 for k in sorted(noeuds)})).hexdigest()

        noeuds = {k: v for k, v in CERT.items() if k not in HORS_NOEUDS}
        self.assertEqual(racine(noeuds), CERT["racine_merkle_sha256"])
        for cle, sous_cle, valeur in (("harmonisation", "total", 90),
                                      ("lignes_de_controle", "total", 12),
                                      ("definitions", "dfn", 3),
                                      ("moteur", "css_calcul", 0)):
            mute = copy.deepcopy(noeuds)
            mute[cle][sous_cle] = valeur
            self.assertNotEqual(racine(mute), CERT["racine_merkle_sha256"], cle)


class TestPiliersEtArtefacts(unittest.TestCase):
    def test_quatre_piliers_ok(self):
        from FONDATION.OUTILS import audit_piliers as AP
        rendu = AP.auditer(RACINE_DEPOT / "REDACTION" / "redaction_mizan.py")
        self.assertEqual(rendu["verdict"], "CONFORME")
        self.assertEqual({p["etat"] for p in rendu["piliers"].values()}, {"OK"})
        self.assertEqual(rendu["equations"], rendu["controles"])

    def test_resoudre_ne_laisse_aucun_controle_rouge(self):
        donnees = RD.resoudre()
        self.assertTrue(RD.verifier(donnees))
        self.assertEqual(donnees["conclusion"]["controles_verts"], 16)
        self.assertEqual(donnees["conclusion"]["controles_total"], 16)
        self.assertEqual(donnees["conclusion"]["statuts_par_label"]["OPÉRATIONNEL"], 13)
        self.assertEqual(donnees["conclusion"]["couverture_sans"]["en"], 56)

    def test_artefacs_bom_separateur_crlf_et_racine(self):
        with TemporaryDirectory() as td:
            rendu = RD.ecrire_artefacts(CERT, Path(td))
            self.assertEqual(len(rendu), 3)
            octets = (Path(td) / "mesures_par_page.csv").read_bytes()
            self.assertEqual(octets[:3], b"\xef\xbb\xbf")
            self.assertIn(b";", octets)
            self.assertEqual(octets.count(b"\n"), octets.count(b"\r\n"),
                             "toute fin de ligne est CRLF, aucune ligne isolée en LF")
            lignes = octets.decode("utf-8-sig").strip().split("\r\n")
            self.assertEqual(len(lignes), 22)
            self.assertEqual(len(lignes[0].split(";")), 13)
            charge = json.loads((Path(td) / "certificat.json").read_bytes())
            self.assertEqual(charge["racine_merkle_sha256"], CERT["racine_merkle_sha256"])
            regles = (Path(td) / "regles_harmonisation.md").read_text(encoding="utf-8")
            self.assertTrue(regles.startswith("# REDACTION"))
            self.assertIn("89", regles)


if __name__ == "__main__":
    unittest.main(verbosity=2)
