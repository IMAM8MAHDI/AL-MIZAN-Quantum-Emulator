# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2026 IMAM8MAHDI / Astro-Code Ecosystem
# SPDX-License-Identifier: GPL-3.0-only OR AGPL-3.0-only
"""Tests du dossier CONSTRUCTION — les cotes sont re-derivées, pas recopiées.

Six exigences, dans l'ordre :
    1. les quarante-trois cotes sont re-calculées ICI par une écriture différente : la racine
       douzième vient d'une racine entière de Newton (et non d'une bissection), l'arrondi au
       multiple de 0,01 mm vient d'un `divmod` sur les entiers du numérateur (et non d'un
       `(v/pas + 1/2) // 1`), et la masse vient d'une échelle d'entiers séparée ;
    2. le théorème est testé hors du dépôt : la même fabrique de cotes, appliquée à un rapport
       1/2, rend une pile géométrique cohérente — ce n'est donc pas ρ qui fait marcher le code ;
    3. les quatre artefacts sont relus sur disque par `csv.reader` et par regex, puis comparés au
       calcul : ce que le dossier publie est ce que le dossier a calculé ;
    4. non-vacuité : seize mutations, une par contrôle, nommées ROUGIT — retirer une borne,
       décréter une cote indéterminée, déplacer le clamp, changer une tolérance, inverser le
       facteur de cascade, retirer un rectangle, rendre la pile portable, remplir une mesure,
       faire exister un prototype, franchir une limite ;
    5. les verdicts défavorables restent écrits : la pile ne se porte pas, quarante et un crans
       restent indéterminés à cinq décimales, zéro prototype, cinq limites ouvertes aucune remplie ;
    6. déterminisme, racine Merkle et bornes de langage : deux exécutions concordent, changer un
       nœud change la racine, et aucune phrase ne prétend décrire un objet réel.

Stdlib uniquement.
    cd ZENODO_DEPOT_ALMIZAN && py -3 -m unittest CONSTRUCTION.tests.test_construction -v
"""

import copy
import csv
import hashlib
import io
import json
import re
import sys
import unittest
from fractions import Fraction
from pathlib import Path
from tempfile import TemporaryDirectory

RACINE_DEPOT = Path(__file__).resolve().parents[2]
if str(RACINE_DEPOT) not in sys.path:
    sys.path.insert(0, str(RACINE_DEPOT))

from CONSTRUCTION import construction_base as CB                              # noqa: E402

CERT = CB.certificat()
EQS = {e["id"]: e for e in CB.equations(CERT)}
CS = {c["id"]: c for c in CB.controles(EQS, CERT)}
HORS_NOEUDS = frozenset({"source", "empreinte_execution", "taille_octets", "rejoue_identique",
                         "limites", "attribution", "racine_merkle_sha256"})

MIZAN, LIGNE_REF = Fraction(249, 400), Fraction(61, 500)
CADRE, PAS = Fraction(1000), Fraction(1, 100)      # millimètres, puis centièmes de millimètre
EPAISSEUR = 8                                      # mm — déclaré
DENSITE = (157, 20)                                # kg/dm³ — déclaré


# ─── voie indépendante : racine douzième par Newton, arrondi par divmod --------

def iroot(n: int, k: int) -> int:
    """Plus grand entier r tel que r^k ≤ n — méthode de Newton sur des entiers."""
    if n < 2:
        return n
    x = 1 << (n.bit_length() // k + 1)
    while True:
        y = ((k - 1) * x + n // x ** (k - 1)) // k
        if y >= x:
            return x
        x = y


def borne_rho(decimales: int):
    """(a, a+1, 10^n) avec (a/10^n)^12 < 249/400 ≤ ((a+1)/10^n)^12 — aucune bissection."""
    m = 10 ** decimales
    n_cible = 249 * m ** 12
    a = iroot(n_cible // 400, 12)
    while (a + 1) ** 12 * 400 < n_cible:
        a += 1
    while a ** 12 * 400 >= n_cible:
        a -= 1
    return a, a + 1, m


def fmt(v: Fraction, dec: int) -> str:
    """Écriture décimale half-up d'un rationnel positif, par divmod sur ses entiers."""
    m = 10 ** dec
    q, r = divmod(v.numerator * m, v.denominator)
    if 2 * r >= v.denominator:
        q += 1
    return f"{q // m}.{q % m:0{dec}d}"


def rang(v: Fraction, pas: Fraction) -> int:
    """Rang entier du multiple de `pas` le plus proche, par divmod — pas de (v/pas + 1/2) // 1."""
    u = v / pas
    q, r = divmod(u.numerator, u.denominator)
    return q + (1 if 2 * r >= u.denominator else 0)


def fabrique(decimales: int = 15, pas: Fraction = PAS, contraction=None):
    """(cotes, indeterminees, clampees) pour n'importe quel rapport — le module n'est pas appelé.

    `contraction` remplace ρ par un autre rapport : la fabrique ne change pas d'écriture, seule la
    suite géométrique change. C'est ce qui permet de tester la structure hors du dépôt."""
    a, b, m = borne_rho(decimales)
    bas = haut = Fraction(contraction) if contraction is not None else Fraction(a, m)
    if contraction is None:
        haut = Fraction(b, m)
    c_min = CADRE * LIGNE_REF
    cotes, indeterminees, clampees = [], [], []
    for k in range(CB.NB_CRANS):
        bas_k, haut_k = CADRE * MIZAN * bas ** k, CADRE * MIZAN * haut ** k
        bas_v, haut_v = max(c_min, bas_k), max(c_min, haut_k)
        if haut_k <= c_min:
            clampees.append(k)
        r_bas, r_haut = rang(bas_v, pas), rang(haut_v, pas)
        if r_bas == r_haut:
            cotes.append(Fraction(r_bas) * pas)
        else:
            indeterminees.append(k)
            cotes.append(Fraction(rang((bas_v + haut_v) / 2, pas)) * pas)
    return cotes, indeterminees, clampees


def masse_exacte(cote_mm: Fraction) -> Fraction:
    """masse = cote² × épaisseur × masse volumique, sur une échelle d'entiers séparée."""
    n = cote_mm.numerator * 100 // cote_mm.denominator          # la cote en centièmes de mm
    return Fraction(n * n * EPAISSEUR * DENSITE[0], 10 ** 4 * DENSITE[1] * 10 ** 6)


# ─── 1. re-dérivation ---------------------------------------------------------

class TestReDerivation(unittest.TestCase):
    def test_les_semences_sont_bien_celles_du_theoreme(self):
        self.assertEqual((CB.MIZAN, CB.LIGNE_REF), (MIZAN, LIGNE_REF))
        self.assertEqual((CB.CADRE_MM, CB.PAS_AFFICHAGE), (CADRE, PAS))
        self.assertEqual(CB.MASSE_VOL_KG_MM3, Fraction(*DENSITE) / 10 ** 6)

    def test_le_bracket_de_rho_est_le_meme_que_celui_d_un_autre_algorithme(self):
        for dec in (5, 15):
            a, b, m = borne_rho(dec)
            self.assertEqual((a, b, m), CB._rho_entiers(dec), f"{dec} décimales")
            self.assertLess(Fraction(a, m), Fraction(b, m))
            self.assertTrue(a ** 12 * 400 < 249 * m ** 12 <= b ** 12 * 400,
                            "la double inégalité entière est ce qui fonde les deux bornes")

    def test_les_quarante_trois_cotes_sont_re_calculees_a_l_identique(self):
        cotes, indeterminees, clampees = fabrique()
        table = CERT["crans"]["table"]
        self.assertEqual((len(cotes), len(table)), (CB.NB_CRANS, CB.NB_CRANS))
        for k, (c, x) in enumerate(zip(cotes, table)):
            self.assertEqual(fmt(c, 2), x["cote_mm"], f"cran {k}")
            self.assertEqual(c, x["cote_exacte"], f"cran {k}")
        self.assertEqual(indeterminees, [])
        self.assertEqual(CERT["crans"]["cotes_indeterminees"], 0)
        self.assertEqual(clampees, [x["cran"] for x in table if x["clamp"]])

    def test_les_masses_sont_re_calculees_par_une_autre_echelle(self):
        total = Fraction(0)
        for x in CERT["crans"]["table"]:
            m = masse_exacte(Fraction(x["cote_mm"]))
            total += m
            self.assertEqual(fmt(m, 3), x["masse_kg"], x["cran"])
        self.assertEqual(fmt(total, 3), CERT["crans"]["masse_totale_kg"])

    def test_le_clamp_est_lecture_du_theoreme_et_non_calcul_ici(self):
        sortie = {r["k"]: bool(r["sortie_de_D"]) for r in CB.continuite_cert()["chaine"]["table"]}
        for x in CERT["crans"]["table"]:
            self.assertEqual(sortie.get(x["cran"], False), x["clamp"], x["cran"])
        self.assertEqual(CERT["crans"]["premier_clampe"], [42])
        self.assertEqual([x["cran"] for x in CERT["crans"]["table"] if x["clamp"]], [42])

    def test_la_plage_de_rapport_ouvre_le_seul_ecart_du_clamp(self):
        table = CERT["crans"]["table"]
        demi = PAS / 2
        bas_rho, haut_rho = CB.rho_encadre(15)
        un_sur_rho = (Fraction(1) / haut_rho, Fraction(1) / bas_rho)
        for x in CERT["crans"]["rapports_consecutifs"]:
            k = x["k"]
            a, b = table[k - 1]["cote_exacte"], table[k]["cote_exacte"]
            r = a / b
            marge = r * (demi / a + demi / b)
            self.assertEqual(fmt(marge, 8), x["marge_de_quantification"], k)
            bande = (un_sur_rho[0] - marge, un_sur_rho[1] + marge)
            self.assertEqual(x["dans_la_plage_de_1_sur_rho"], bande[0] <= r <= bande[1], k)
            self.assertEqual(fmt(r, 6), x["rapport"], k)
        self.assertEqual([x["k"] for x in CERT["crans"]["rapports_consecutifs"]
                          if not x["dans_la_plage_de_1_sur_rho"]],
                         CERT["crans"]["rapports_hors_plage"])

    def test_la_cascade_est_redite_par_une_sommation_inverse(self):
        bas = Fraction(borne_rho(15)[0], 10 ** 15)
        haut = Fraction(borne_rho(15)[1], 10 ** 15)
        pour_bas = sum((bas ** (2 * j) for j in reversed(range(CB.NB_CRANS))), Fraction(0))
        pour_haut = sum((haut ** (2 * j) for j in reversed(range(CB.NB_CRANS))), Fraction(0))
        ca = CERT["cascade"]
        self.assertEqual(fmt(pour_bas, 4), ca["facteur_43_crans"]["inferieur"])
        self.assertEqual(fmt(pour_haut, 4), ca["facteur_43_crans"]["superieur"])
        self.assertEqual(fmt(1 / (1 - bas ** 2), 4), ca["facteur_infini"]["inferieur"])
        self.assertEqual(fmt(1 / (1 - haut ** 2), 4), ca["facteur_infini"]["superieur"])
        self.assertLess(pour_bas, 1 / (1 - bas ** 2))
        self.assertTrue(ca["identite_partielle"] and ca["encadrement_valide"])

    def test_l_outillage_est_re_assigne_sans_appeler_le_module(self):
        capacites = [("scie à ruban", Fraction(1, 2)), ("dégauchisseuse-rabot", Fraction(1, 10)),
                     ("fraiseuse verticale", Fraction(2, 100)), ("rectifieuse", Fraction(5, 1000))]
        attendu = {}
        for x in CERT["crans"]["table"]:
            t = Fraction(x["tolerance_mm"])
            nom = next((n for n, c in capacites if c <= t), "aucun outil déclaré")
            attendu[nom] = attendu.get(nom, 0) + 1
        self.assertEqual(attendu, CERT["outillage"]["repartition"])
        self.assertEqual(sum(attendu.values()), CB.NB_CRANS)
        self.assertEqual(CERT["outillage"]["hors_ligne"], 0)

    def test_le_temps_total_est_bien_la_somme_des_lignes_declarees(self):
        lignes = [Fraction(p["heures_declarees"]) for p in CERT["cout"]["par_cran"]]
        self.assertEqual(fmt(sum(lignes, Fraction(0)), 2), CERT["cout"]["total_heures"])
        self.assertEqual(len(lignes), CB.NB_CRANS)

    def test_la_tolerance_suite_la_cote_sur_les_quarante_trois_crans(self):
        for x in CERT["crans"]["table"]:
            self.assertEqual(fmt(Fraction(x["cote_mm"]) / 1000, 5), x["tolerance_mm"], x["cran"])


# ─── 2. le théorème ne tient pas à ρ ------------------------------------------

class TestStructureEtrangere(unittest.TestCase):
    def test_la_meme_fabrique_de_cotes_marche_sur_un_rapport_demi(self):
        """Une pile à rapport 1/2 : cotes, clamp et plage suivent les mêmes écritures."""
        cotes, indeterminees, clampees = fabrique(contraction=Fraction(1, 2))
        self.assertEqual([fmt(c, 2) for c in cotes[:4]],
                         ["622.50", "311.25", "155.63", "122.00"])
        self.assertTrue(all(cotes[k] >= cotes[k + 1] for k in range(len(cotes) - 1)))
        self.assertTrue(all(c >= CADRE * LIGNE_REF for c in cotes))
        self.assertEqual(indeterminees, [])
        self.assertEqual(clampees[0], 3, "le clamp apparaît aussi sans 0,6225")

    def test_l_encadrement_du_theoreme_laisse_quarante_et_une_cotes_indeterminees(self):
        _, a_cinq, _ = fabrique(decimales=5)
        _, a_quinze, _ = fabrique(decimales=15)
        sen = CERT["sensibilite"]
        self.assertEqual(a_cinq, list(range(1, CB.NB_CRANS - 1)))
        self.assertEqual(len(a_cinq), sen["theoreme_5_decimales"]["crans_indetermines"])
        self.assertEqual(a_quinze, [])
        self.assertEqual(sen["plans_15_decimales"]["crans_indetermines"], 0)
        self.assertGreater(Fraction(sen["theoreme_5_decimales"]["largeur_encadrement"]),
                           Fraction(sen["plans_15_decimales"]["largeur_encadrement"]))

    def test_a_pas_constant_c_est_l_encadrement_qui_decisionne(self):
        """Un tick dix fois plus fin ne change rien au théorème : c'est la plage qui borne."""
        _, a_quinze, _ = fabrique(decimales=15, pas=Fraction(1, 10 ** 6))
        _, a_cinq, _ = fabrique(decimales=5, pas=Fraction(1, 10 ** 6))
        self.assertEqual(a_quinze, [], "sinon C13 ne mesure que la grille")
        self.assertGreater(len(a_cinq), 20)


# ─── 3. les artefacts relus sur disque ----------------------------------------

class TestArtefactsSurDisque(unittest.TestCase):
    def setUp(self):
        self._td = TemporaryDirectory(prefix="construction-artefacts-")
        self.vers = Path(self._td.name)
        self.ecrit = CB.ecrire_artefacts(CERT, self.vers)

    def tearDown(self):
        self._td.cleanup()

    def csv(self):
        octets = (self.vers / "nomenclature_crans.csv").read_bytes()
        return octets, list(csv.reader(io.StringIO(octets.decode("utf-8-sig")), delimiter=";"))

    def test_treize_colonnes_quarante_cinq_lignes_et_le_bom(self):
        octets, lignes = self.csv()
        self.assertEqual(octets[:3], b"\xef\xbb\xbf")
        self.assertEqual(octets.count(b"\r\n"), len(lignes), "toute fin de ligne est CRLF")
        self.assertEqual(octets.count(b"\n"), octets.count(b"\r\n"))
        self.assertEqual(len(lignes), CB.NB_CRANS + 2)
        self.assertTrue(all(len(l) == 13 for l in lignes), [len(l) for l in lignes])
        self.assertEqual(lignes[0], CB.COLONNES)
        self.assertEqual(lignes[-1][0], "total")

    def test_le_csv_relu_redonne_les_cotes_du_calcul(self):
        _, lignes = self.csv()
        ou = {x["cran"]: x["outil_declare"] for x in CERT["outillage"]["par_cran"]}
        he = {x["cran"]: x["heures_declarees"] for x in CERT["cout"]["par_cran"]}
        for l, x in zip(lignes[1:-1], CERT["crans"]["table"]):
            self.assertEqual(l[0], str(x["cran"]))
            self.assertEqual(l[1].replace(",", "."), x["cote_mm"])
            self.assertEqual(l[6], "OUI" if x["clamp"] else "NON")
            self.assertEqual(l[7].replace(",", "."), x["tolerance_mm"])
            self.assertEqual(l[8], ou[x["cran"]])
            self.assertEqual(l[9].replace(",", "."), he[x["cran"]])
            self.assertEqual(l[10].replace(",", "."), x["masse_kg"])
            self.assertEqual(l[11], CB.PHRASE_ABSENCE)

    def test_un_nombre_mut_sur_disque_ne_passe_plus_la_relecture(self):
        _, avant = self.csv()
        octets = (self.vers / "nomenclature_crans.csv").read_bytes()
        (self.vers / "nomenclature_crans.csv").write_bytes(octets.replace(b"622,50", b"622,51", 1))
        _, apres = self.csv()
        self.assertNotEqual(avant[1], apres[1], "la relecture est sensible à l'octet")
        self.assertEqual(apres[1][1], "622,51")

    def test_le_svg_porte_quarante_trois_rectangles_cotes_au_dixieme(self):
        texte = (self.vers / "plan_emboitement.svg").read_text(encoding="utf-8")
        largeurs = re.findall(r'(?<![-\w])width="([0-9.]+)"', texte)
        self.assertEqual(len(largeurs), CB.NB_CRANS + 1, "le <svg> porte sa propre largeur")
        self.assertEqual(largeurs[1:], [fmt(Fraction(x["cote_mm"]) / 10, 2)
                                        for x in CERT["crans"]["table"]])
        self.assertEqual(len(re.findall(r"<rect ", texte)), CB.NB_CRANS)
        self.assertEqual(len(re.findall(r"<text ", texte)), CB.NB_CRANS)
        self.assertEqual(texte.count("mm ±"), CB.NB_CRANS)
        self.assertIn(CB.PHRASE_ABSENCE, texte)

    def test_le_md_a_six_lignes_de_prediction_toutes_vides_en_mesure(self):
        lignes = (self.vers / "predictions_falsifiables.md").read_text(
            encoding="utf-8").splitlines()
        tableau = [l for l in lignes if l.startswith("| P")]
        self.assertEqual(len(tableau), 6)
        for l in tableau:
            cellules = [c.strip() for c in l.strip("|").split("|")]
            self.assertEqual(len(cellules), 7)
            self.assertEqual(cellules[-1], "aucune")
            self.assertTrue(all(cellules[:6]))
        self.assertIn("aucune ligne de ce tableau n'a été remplie par une mesure",
                      "\r\n".join(lignes))

    def test_le_json_relu_porte_la_meme_racine(self):
        charge = json.loads((self.vers / "certificat.json").read_bytes())
        self.assertEqual(charge["racine_merkle_sha256"], CERT["racine_merkle_sha256"])
        self.assertEqual(charge["crans"]["masse_totale_kg"], CERT["crans"]["masse_totale_kg"])
        self.assertEqual(sorted(charge["prototypes"]["fichiers"]), [])
        self.assertEqual(sorted(charge), sorted(CERT))

    def test_les_quatre_artefacts_sont_ecrits_et_nommes(self):
        self.assertEqual(sorted(self.ecrit), ["certificat.json", "nomenclature_crans.csv",
                                              "plan_emboitement.svg",
                                              "predictions_falsifiables.md"])
        self.assertEqual(CERT["ecritures"]["noms"], sorted(self.ecrit))
        ec = CERT["ecritures"]
        for nom in self.ecrit:
            octets = (self.vers / nom).read_bytes()
            self.assertEqual(self.ecrit[nom], f"{len(octets)} octets", nom)
            self.assertGreater(len(octets), 200, nom)
            if nom == ec["nom_sans_empreinte"]:
                self.assertNotIn(nom, ec["tailles"], "auto-référence mesurée : mensonge")
                self.assertNotIn(nom, ec["empreintes"], nom)
                self.assertIn(nom, ec["auto_reference"])
            else:
                self.assertEqual(ec["tailles"][nom], len(octets), nom)
                self.assertEqual(ec["empreintes"][nom],
                                 hashlib.sha256(octets).hexdigest()[:16], nom)
        # relier la chaîne du nœud à l'octet : le JSON publié est plus gros que le nœud qu'il scelle
        charge = json.loads((self.vers / "certificat.json").read_bytes())
        self.assertGreater(len((self.vers / "certificat.json").read_bytes()),
                           sum(charge["ecritures"]["tailles"].values()))

    def test_sceller_certificat_json_dans_son_propre_noeud_rougit_c12(self):
        etat = muter(("ecritures", "tailles"), {**CERT["ecritures"]["tailles"],
                                                "certificat.json": 45961})
        cs = {c["id"]: c for c in CB.controles(EQS, etat)}
        self.assertFalse(cs["C12"]["ok"])
        self.assertEqual([k for k, c in cs.items() if not c["ok"]], ["C12"])


# ─── 4. non-vacuité : une mutation par contrôle --------------------------------

MUTATIONS = [
    ("C01", ("semences", "concorde_avec_continuite"), False),
    ("C02", ("crans", "cotes_indeterminees"), 1),
    ("C03", ("crans", "premier_clampe"), [41]),
    ("C04", ("crans", "table", 7, "tolerance_mm"), "0.50000"),
    ("C05", ("cascade", "encadrement_valide"), False),
    ("C06", ("nomenclature", "cotes_identiques_au_calcul"), False),
    ("C07", ("plans", "rectangles"), 42),
    ("C08", ("echelle_humaine", "pile_portable_par_un"), True),
    ("C09", ("outillage", "hors_ligne"), 1),
    ("C10", ("cout", "total_heures"), "99.00"),
    ("C11", ("predictions", "liste", 0, "mesure"), "620,0 mm"),
    ("C12", ("prototypes", "nb_prototypes"), 3),
    ("C13", ("sensibilite", "plans_15_decimales", "crans_indetermines"), 4),
    ("C14", ("lien_catalogue", "catalogue_sous_la_borne_ecriture"), False),
    ("C15", ("rejoue_identique",), False),
    ("C16", ("limites_ouvertes", "remplies_dans_ce_lot"), 5),
]


def muter(chemin, valeur):
    """Copie profonde des nœuds scellés, puis une seule écriture au bout du chemin."""
    etat = copy.deepcopy({k: v for k, v in CERT.items() if k not in HORS_NOEUDS})
    etat["empreinte_execution"] = CERT["empreinte_execution"]
    etat["taille_octets"] = CERT["taille_octets"]
    etat["rejoue_identique"] = CERT["rejoue_identique"]
    noeud = etat
    for cle in chemin[:-1]:
        noeud = noeud[cle]
    cle = chemin[-1]
    if isinstance(cle, int):
        cible = noeud[cle]
        cle = "mesure" if "mesure" in cible else "cote_mm"
    else:
        cible = noeud
    cible[cle] = copy.deepcopy(valeur) if isinstance(valeur, list) else valeur
    return etat


class TestNonVacuite(unittest.TestCase):
    """Chaque mutation ci-dessus doit faire rougir le contrôle qu'elle nomme, et lui seul."""

    def test_la_baseline_du_certificat_est_verte(self):
        self.assertEqual(len(CS), 16)
        self.assertEqual([k for k, c in CS.items() if not c["ok"]], [])

    def test_chaque_mutation_fait_rougir_le_controle_nomme_et_lui_seul(self):
        for cid, chemin, valeur in MUTATIONS:
            cs = {c["id"]: c for c in CB.controles(EQS, muter(chemin, valeur))}
            self.assertFalse(cs[cid]["ok"], f"{cid} reste vert sous {chemin} = {valeur}")
            self.assertEqual([k for k, c in cs.items() if not c["ok"]], [cid],
                             f"{cid} : d'autres contrôles rougissent sous {chemin}")

    def test_les_mutations_ne_sont_pas_toutes_les_memes(self):
        self.assertEqual(len({tuple(m[1]) for m in MUTATIONS}), 16,
                         "deux mutations porteraient sur le même champ")

    def test_deplacer_la_chaine_publiee_de_continuite_rougit_aussi_c01(self):
        """C01 ne se contente pas du booléen : les deux chaînes publiées sont comparées ici."""
        for champ in ("inferieur", "superieur"):
            publie = dict(CERT["semences"]["rho_publie_par_continuite"])
            publie[champ] = "247/400"
            cs = {c["id"]: c for c in
                  CB.controles(EQS, muter(("semences", "rho_publie_par_continuite"), publie))}
            self.assertFalse(cs["C01"]["ok"], champ)

    def test_ne_rien_muter_laisse_la_baseline_verte(self):
        cs = {c["id"]: c for c in CB.controles(EQS, muter(("cout", "moyenne_par_cran"),
                                                          CERT["cout"]["moyenne_par_cran"]))}
        self.assertEqual([k for k, c in cs.items() if not c["ok"]], [])

    def test_retirer_les_nombres_d_un_resultat_le_rend_visible(self):
        eqs = copy.deepcopy(list(EQS.values()))
        eqs[0]["resultat"] = ""
        self.assertTrue(any(not e["resultat"] for e in eqs))
        self.assertEqual(len(eqs), 16)


# ─── 5. les verdicts défavorables restent écrits -------------------------------

class TestVerdictsDefavorables(unittest.TestCase):
    def test_la_pile_ne_se_porte_pas_et_c_est_ecrit(self):
        eh = CERT["echelle_humaine"]
        self.assertTrue(eh["toutes_dans_le_geste"])
        self.assertFalse(eh["pile_portable_par_un"])
        self.assertTrue(eh["tete_portable_par_un"])
        self.assertGreater(Fraction(eh["masse_totale_kg"]), Fraction(eh["portage_un_kg"]))
        self.assertIn(eh["masse_totale_kg"], EQS["EQ-08"]["resultat"])
        self.assertIn("ne se porte pas", CB.resume_markdown(CERT).decode("utf-8"))

    def test_zero_prototype_et_la_phrase_d_absence_partout(self):
        self.assertEqual(CERT["prototypes"]["nb_prototypes"], 0)
        self.assertFalse(CERT["prototypes"]["repertoire_existe"])
        self.assertTrue(CERT["ecritures"]["absence_partout"])
        for octets in CB._artefacts_octets(CERT).values():
            self.assertIn(CB.PHRASE_ABSENCE.encode("utf-8"), octets)

    def test_les_predictions_attendent_leurs_mesures(self):
        pr = CERT["predictions"]
        self.assertTrue(pr["aucune_mesure_effectuee"])
        self.assertEqual([p["mesure"] for p in pr["liste"]], [None] * 6)
        self.assertEqual([set(p) for p in pr["liste"]], [set(pr["champs_attendus"])] * 6)
        self.assertEqual(len(pr["instruments"]), len(set(pr["instruments"])))

    def test_les_limites_ouvertes_ne_sont_pas_declarees_franchies(self):
        lo = CERT["limites_ouvertes"]
        self.assertGreaterEqual(lo["nb"], 5)
        self.assertEqual(lo["remplies_dans_ce_lot"], 0)
        self.assertTrue(lo["toutes_au_dela_de_20"])
        self.assertEqual(len(CERT["limites"]), lo["nb"] + 1)

    def test_le_rapport_hors_plage_du_clamp_est_compte_pas_cache(self):
        cr = CERT["crans"]
        self.assertEqual(cr["rapports_hors_plage"], [42],
                         "le cran clampe sort de la plage 1/ρ : c'est écrit, pas gommé")
        self.assertIn("42", EQS["EQ-03"]["resultat"])
        self.assertGreater(Fraction(cr["ecart_max_a_la_plage"]), 0)

    def test_le_lien_au_catalogue_compare_deux_finesses_de_representation(self):
        li = CERT["lien_catalogue"]
        self.assertTrue(li["catalogue_sous_la_borne_ecriture"])
        self.assertTrue(li["plan_plus_fin_que_ecriture"])
        self.assertLess(Fraction(li["ecart_hors_borne_plan"]), Fraction(li["borne_propagee"]))
        self.assertGreater(Fraction(li["rapport_des_finesses"]), 1)

    def test_aucune_phrase_ne_pretend_decrire_un_objet_reel(self):
        texte = json.dumps(CB.resoudre(), ensure_ascii=False, default=str)
        for interdit in ("prouvé par l'objet", "mesuré sur l'objet", "construit et mesuré",
                         "certifié conforme", "testé en atelier", "prototype construit : 1"):
            self.assertNotIn(interdit, texte)


# ─── 6. déterminisme, sceau et transmission ------------------------------------

class TestDeterminismeEtSceau(unittest.TestCase):
    def test_deux_appels_de_certificat_concordent_octet_par_octet(self):
        self.assertEqual(CB.canonique(CERT), CB.canonique(CB.certificat()))
        self.assertTrue(CERT["rejoue_identique"])

    def test_la_racine_ne_scelle_que_quatorze_noeuds_tries(self):
        nc = {k: v for k, v in CERT.items() if k not in HORS_NOEUDS}
        self.assertEqual(len(nc), 14)
        racine = hashlib.sha256(CB.canonique(
            {c: hashlib.sha256(CB.canonique(nc[c])).hexdigest() for c in sorted(nc)})).hexdigest()
        self.assertEqual(racine, CERT["racine_merkle_sha256"])

    def test_chaque_noeud_mut_change_la_racine(self):
        nc = {k: v for k, v in CERT.items() if k not in HORS_NOEUDS}
        for nom in sorted(nc):
            alt = copy.deepcopy(nc)
            alt[nom] = {"mute": True}
            racine = hashlib.sha256(CB.canonique(
                {c: hashlib.sha256(CB.canonique(alt[c])).hexdigest()
                 for c in sorted(alt)})).hexdigest()
            self.assertNotEqual(racine, CERT["racine_merkle_sha256"], nom)

    def test_l_ecriture_canonique_ne_depend_pas_de_l_ordre_des_cles(self):
        un = {"a": 1, "b": {"c": 2, "d": [3, "4"]}}
        deux = {"b": {"d": [3, "4"], "c": 2}, "a": 1}
        self.assertEqual(CB.canonique(un), CB.canonique(deux))

    def test_resoudre_et_verifier_forment_la_porte_de_sortie(self):
        donnees = CB.resoudre()
        self.assertTrue(CB.verifier(donnees))
        self.assertEqual(donnees["conclusion"]["controles_verts"], 16)
        self.assertEqual(donnees["conclusion"]["controles_total"], 16)
        self.assertEqual(donnees["conclusion"]["nb_crans"], CB.NB_CRANS)
        self.assertEqual(donnees["conclusion"]["prototypes_construits"], 0)


class TestPiliersEtTransmission(unittest.TestCase):
    def test_equations_et_controles_sont_apparies_et_etiquetes(self):
        cs = CB.controles(EQS, CERT)
        self.assertEqual({c["equation"] for c in cs}, set(EQS))
        for e in EQS.values():
            self.assertIn(e["statut"], CB.FB.STATUTS, e["id"])
            self.assertIn(e["couche"], CB.FB.COUCHES, e["id"])
            self.assertIn("→", e["chemin"], e["id"])
            self.assertTrue(e["chemin"].startswith("construction_base.py"), e["id"])
            self.assertTrue(e["resultat"] and e["limite"] and e["formule"], e["id"])

    def test_toute_equation_porte_un_controle_non_rouge(self):
        for c in CB.controles(EQS, CERT):
            self.assertTrue(c["ok"], c["id"])
            self.assertTrue(c["attendu"] and c["obtenu"] and c["verifie"], c["id"])

    def test_le_module_ne_depend_que_de_la_bibliotheque_standard(self):
        autorises = {"__future__", "hashlib", "json", "sys", "decimal", "fractions", "pathlib",
                     "typing", "CONTINUITE", "FONDATION", "bibliotheques"}
        texte = (RACINE_DEPOT / "CONSTRUCTION" / "construction_base.py").read_text("utf-8")
        noms = set()
        for ligne in texte.splitlines():
            m = re.match(r"\s*(?:from|import)\s+([A-Za-z_][\w.]*)", ligne)
            if m:
                noms.add(m.group(1).split(".")[0])
        self.assertTrue(noms, "aucun import trouvé : le contrôle ne contrôle rien")
        self.assertEqual(noms - autorises, set())
        for attendu in ("CONTINUITE", "FONDATION", "bibliotheques"):
            self.assertIn(attendu, noms, attendu)


if __name__ == "__main__":
    unittest.main(verbosity=2)
